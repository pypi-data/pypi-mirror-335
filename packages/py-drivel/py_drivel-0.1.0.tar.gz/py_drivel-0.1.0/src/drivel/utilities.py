from importlib import resources


asset_root = resources.files(f"{__package__}.assets")


def asset_path(file_name: str):
    return asset_root / file_name
