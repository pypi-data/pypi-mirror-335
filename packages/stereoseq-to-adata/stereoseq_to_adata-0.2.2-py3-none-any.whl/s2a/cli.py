import tyro

def process_stereo_folder() -> None:
    from . import process_stereo_folder as process_stereo_folder_impl

    tyro.cli(process_stereo_folder_impl)
