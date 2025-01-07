from pathlib import Path

from prefect.blocks.core import Block
from prefect.filesystems import LocalFileSystem


def get_storage(storage_type: str, **kwargs):
    if storage_type.lower() == 'localfilesystem':
        basepath = kwargs.get('basepath', f'{Path.home()}/.prefect/storage')
        return LocalFileSystem(basepath=basepath)
    elif storage_type.lower() == 'block':
        block = kwargs.get('block')
        if block is None:
            raise KeyError("Missing argument 'block'")
        return Block.load(block)
    else:
        raise ValueError(f"Unsupported storage type: '{storage_type}'")
