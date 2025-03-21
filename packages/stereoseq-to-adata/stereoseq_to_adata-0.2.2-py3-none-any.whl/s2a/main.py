# %%
import json
import time
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path
from typing import Literal, cast

import numpy as np
import pandas as pd
import polars as pl
import scanpy as sc
from joblib import Parallel, delayed
from scipy import sparse
from tqdm import tqdm


basicConfig(
    level=INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = getLogger(__name__)

pc = pl.col
# df = pl.read_parquet('/mnt/inner-data/sde/total_gene_2D/macaque-20240814-cla-all/total_gene_T67_macaque_f001_2D_macaque-20240814-cla-all.parquet')

# %%

def stereo_df_to_adata(
    df: pl.DataFrame | pd.DataFrame | Path | str, *, 
    obs_add_prefix='cell-', 
    remove_non_cell_expr=True,
    obs_src: Literal['cell_label', 'spot_bin']='cell_label',
    spot_bin_size: int=50,
    verbose=False
):
    '''
    Convert a single stereo dataframe to an AnnData object.
    
    Example:
    >>> stereo_df_to_adata('/path/to/total_gene_T89_macaque_f001_2D_macaque-20240814-cla-all.parquet')
    AnnData object with n_obs × n_vars = 228198 × 15863
        obs: 'region_global_id'
        obsm: 'spatial', 'spatial_r'

    df: pl.DataFrame | Path
        the dataframe to convert
    obs_add_prefix: str
        the prefix to add to the cell names
    verbose: bool
        whether to print debug information
    '''
    last_logger_level = logger.getEffectiveLevel()
    if verbose:
        logger.setLevel(DEBUG)

    t0 = time.time()
    if isinstance(df, str):
        df = Path(df)
    if isinstance(df, Path):
        logger.debug(f'reading {df}...')
        df = pl.read_parquet(df)
    elif isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)

    logger.debug(f'raw df shape: {df.shape}')
    if remove_non_cell_expr:
        df = df.filter(pl.col('cell_label') != 0)
        logger.debug(f'df after drop non-cell expr: {df.shape}')
    logger.debug(f'df columns: {df.columns}')
    has_rxry = 'rx' in df.columns and 'ry' in df.columns
    logger.debug(f'has_rxry: {has_rxry}')

    logger.debug('start mapping...')
    genes = df['gene'].unique().to_list()


    obs_key = 'cell_label'
    
    if obs_src == 'spot_bin':
        df = df.with_columns(
            (pl.col('x') // spot_bin_size).alias('bin_x'),
            (pl.col('y') // spot_bin_size).alias('bin_y'),
        ).with_columns(
            ('bin-'+pl.col('bin_x').cast(pl.String)+'-'+pl.col('bin_y').cast(pl.String)).alias('bin_xy')
        )
        obs_key = 'bin_xy'

    obs_ids: list[int] | list[str] = df[obs_key].unique().sort().to_list()

    gene_map = {g: i for i, g in enumerate(genes)}
    obs_map  = {o: i for i, o in enumerate(obs_ids)}

    df = df.with_columns(
        pl.col('gene').replace(gene_map).alias('gene_idx').cast(pl.Int64),
        pl.col(obs_key).replace(obs_map).alias('obs_idx').cast(pl.Int64),
    )
    gene_ids = df['gene_idx'].to_numpy()
    obs_idx = df['obs_idx'].to_numpy()
    counts = df['umi_count'].to_numpy()

    n_genes = len(genes)
    n_obs   = len(obs_ids)
    logger.debug(f'n_genes: {n_genes}, n_obs: {n_obs}')
    logger.debug('creating sparse matrix...')
    expr_matrix = sparse.csr_matrix((counts, (obs_idx, gene_ids)), shape=(n_obs, n_genes))
    logger.debug('creating AnnData...')
    adata = sc.AnnData(expr_matrix)
    adata.var_names = genes
    adata.obs_names = [f'{obs_add_prefix}{o}' for o in obs_ids]
    obs_id_with_area = df.group_by(obs_key).agg(
        pc('gene_area').first(),
        pc('x').mean().alias('x'),
        pc('y').mean().alias('y'),
        *([
            pc('rx').mean().alias('rx'),
            pc('ry').mean().alias('ry')
        ] if has_rxry else []),
        *([
            pc('bin_x').mean().alias('bin_x'),
            pc('bin_y').mean().alias('bin_y')
        ] if obs_src == 'spot_bin' else []),
    ).sort(obs_key)
    adata.obs['region_global_id'] = obs_id_with_area['gene_area'].to_numpy()
    adata.obs['region_global_id'] = adata.obs['region_global_id'].astype('category')
    adata.obsm['spatial'] = obs_id_with_area[['x', 'y']].to_numpy()
    if obs_src == 'spot_bin':
        adata.obsm['spatial_bin'] = obs_id_with_area[['bin_x', 'bin_y']].to_numpy()

    if has_rxry:
        adata.obsm['spatial_r'] = obs_id_with_area[['rx', 'ry']].to_numpy()
    logger.debug(f'done in {time.time() - t0:.2f} seconds')
    logger.setLevel(last_logger_level)
    return adata

def _load_region_info(region_info_p: Path):
    region_info = pd.read_csv(region_info_p)[['origin_name', 'global_id']]
    region_info.drop_duplicates(subset='global_id', inplace=True)
    region_info.set_index('global_id', inplace=True)
    return region_info

def process_stereo_folder(
    folder: Path|str, *, save_to: Path|str|None=None, 
    obs_add_prefix: str='{chip}-cell-', 
    obs_src: Literal['cell_label', 'spot_bin']='cell_label',
    spot_bin_size: int=50,
    verbose: bool=False, 
    workers: int=4, 
    enable_tqdm: bool=True
):
    '''
    Process a folder of stereo dataframes. Folder format should be zhengmingyuan's format: 
    /path/to/stereo_folder/
        region-*.csv                      # region id and region name  
        total_gene_{chip_a}_*.parquet     # gene expression matrix  
        total_gene_{chip_a}_*.meta.json   # meta data  
        ...  
        total_gene_{chip_z}_*.parquet     # gene expression matrix  
        total_gene_{chip_z}_*.meta.json   # meta data  
        ...
    
    save_to: Path | None
        the path to save the AnnData objects
    obs_add_prefix: str
        the prefix to add to the observation names
    verbose: bool
        whether to print debug information
    workers: int
        the number of workers to use
    '''
    folder = Path(folder)
    if save_to is not None:
        save_to = Path(save_to)
        save_to.mkdir(parents=True, exist_ok=True)

    all_data_files = list(folder.glob('total_gene_*.parquet'))
    # all_meta_files = list(folder.glob('total_gene_*.meta.json'))
    all_meta_files = [data_file.with_suffix('.meta.json') for data_file in all_data_files]
    all_meta_files = [f for f in all_meta_files if f.exists()]
    region_info_p = list(folder.glob('region-*.csv'))

    assert len(all_data_files) == len(all_meta_files), f'number of data files and meta files are not the same: {len(all_data_files)} != {len(all_meta_files)}'
    assert len(region_info_p) == 1, f'number of region info files is not 1: {len(region_info_p)}'
    region_info = _load_region_info(region_info_p[0])
    
    _tqdm = tqdm if enable_tqdm else lambda *args, **kwargs: args[0]
        
    def process_single_file(data_file: Path, meta_file: Path):
        meta = json.load(open(meta_file))
        chip = meta['chip']
        # if chip != 'T67':
        #     return

        if save_to is not None:
            save_to_p = save_to / data_file.with_suffix('.h5ad').name
            
            if save_to_p.exists():
                logger.debug(f'{save_to_p} exists, reading existing adata...')
                return sc.read_h5ad(save_to_p)

        curr_obs_add_prefix = obs_add_prefix.format(chip=chip)
        adata = stereo_df_to_adata(data_file, obs_add_prefix=curr_obs_add_prefix, obs_src=obs_src, spot_bin_size=spot_bin_size, verbose=verbose)
        adata.uns['export_meta'] = meta
        adata.obs['region_name'] = adata.obs['region_global_id'].map(region_info['origin_name'])
        if save_to is not None:
            logger.debug(f'saving adata to {save_to_p}...')
            adata.write_h5ad(save_to_p, compression='gzip')
        return adata
    
    tasks = [
        delayed(process_single_file)(data_file, meta_file) 
        for data_file, meta_file in zip(all_data_files, all_meta_files)
    ]
    adatas = []
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, 
                              message="A worker stopped while some jobs were given to the executor*")
        pbar = _tqdm(Parallel(
            n_jobs=workers,
            return_as='generator'
        )(tasks), total=len(tasks), desc='processing files')
        for adata in pbar:
            adatas.append(adata)

    return adatas


# df = pl.read_parquet('/data/data0-1/total_gene_T67_macaque_f001_2D_macaque-20240814-cla-all.parquet')
# r = stereo_df_to_adata(
#     df,
#     obs_src='spot_bin',
#     # obs_src='cell_label',
#     spot_bin_size=100,
#     verbose=True
# )
# cell_expr = r.X.sum(axis=1).A1
# %%
# import matplotlib.pyplot as plt
# plt.scatter(
#     r.obsm['spatial_bin'][:, 0], 
#     r.obsm['spatial_bin'][:, 1], 
#     s=1, c=cell_expr, alpha=0.5
# )
# %%
# bin_size = 100

# rdf = df.with_columns(
#     (pl.col('x') // bin_size).alias('bin_x'),
#     (pl.col('y') // bin_size).alias('bin_y'),
# ).group_by('bin_x', 'bin_y').agg(
#     pl.col('umi_count').sum().alias('umi_count')
# )
# rdf
# # %%
# plt.scatter(
#     rdf['bin_x'], 
#     rdf['bin_y'], 
#     s=1, c=rdf['umi_count'], alpha=0.5
# )
# # %%
# sc.pp.calculate_qc_metrics(
#     r, inplace=True, log1p=True
# )
# # %%
# plt.scatter(
#     r.obsm['spatial_bin'][:, 0], 
#     r.obsm['spatial_bin'][:, 1], 
#     s=1, c=r.obs['total_counts'], alpha=0.5
# )
# %%
# r = process_stereo_folder(
#     Path('/mnt/inner-data/sde/total_gene_2D/macaque-20240814-cla-all/'), 
#     verbose=True,
#     save_to=Path('/data/data0-1/transfer/cla/stereo/')
# )
# # %%
# r = process_stereo_folder(
#     Path('/mnt/inner-data/sde/total_gene_2D/macaque-20241106-mq179-F1-F7/'), 
#     verbose=True,
#     save_to=Path('/data/data0-1/transfer/motor/stereo/macaque-20241106-mq179-F1-F7')
# )
