# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2023/9/5 17:14
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : __init__.py.py
# @Software: PyCharm
"""
from typing import Dict, Optional
import os

from .s3 import S3BlobStore
from .blobstore import KIND_S3, CONFIG_HOST, blobstore_config, CONFIG_DISABLE_SSL, CONFIG_AK, CONFIG_SK
from .local import KIND_LOCAL, LocalBlobStore


def blobstore(filesystem=None, kind: str = None,  endpoint: str = None, config: Optional[Dict] = None):
    """
    Initialize a blobstore.

    Args:
        kind: blobstore kind
        filesystem: filesystem
        endpoint: blobstore endpoint
        config: blobstore config
    """
    if filesystem is not None:
        kind, endpoint, config = blobstore_config(filesystem=filesystem)

    if kind == KIND_S3:
        return S3BlobStore(endpoint=endpoint, config=config)
    elif kind == KIND_LOCAL:
        return LocalBlobStore(endpoint=endpoint, config=config)
    else:
        raise ValueError("Unsupported filesystem kind: {}".format(kind))


def delete_by_filesystem(filesystem, file_path: str):
    """
    delete a file or dir by filesystem.
    """
    client = blobstore(filesystem=filesystem)
    # 删除文件
    if client.head_object(file_path):
        client.delete_file(file_path)
        return

    # 删除文件夹
    client.delete_dir(file_path)


def download_by_filesystem(filesystem, file_path: str, dest_path: str):
    """
    Download a file by filesystem.
    """
    client = blobstore(filesystem=filesystem)

    if client.head_object(file_path):
        client.download_file(file_path, dest_path)
        return

    meta_list = client.list_meta(path=file_path)
    for meta in meta_list:
        dest_file = os.path.join(dest_path, meta.name)
        if not os.path.exists(os.path.dirname(dest_file)):
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        client.download_file(path=meta.url_path, file_name=dest_file)


def upload_by_filesystem(filesystem, file_path: str, dest_path: str, source_filesystem: Optional[dict] = None):
    """
    Upload a file by filesystem.
    """
    if source_filesystem is None:
        client = blobstore(filesystem=filesystem)

        if os.path.isfile(file_path):
            client.upload_file(file_name=file_path, path=dest_path)

        if os.path.isdir(file_path):
            for root, _, files in os.walk(file_path):
                for file in files:
                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, file_path)
                    remote_path = os.path.join(dest_path, relative_path)
                    client.upload_file(file_name=local_path, path=remote_path)
    else:
        # 本地磁盘保存到磁盘或 s3
        if source_filesystem["kind"] == KIND_LOCAL:
            upload_by_filesystem(filesystem, file_path, dest_path)
        else:
            if filesystem["kind"] == KIND_LOCAL:  # s3 保存到本地
                download_by_filesystem(source_filesystem, file_path, dest_path)
            else:  # TODO: s3 保存到 s3, 暂不支持
                raise NotImplementedError("Not support yet to copy files between two s3")


def init_py_filesystem(filesystem):
    """
    Initialize a py filesystem.
    Args:
        filesystem: filesystem
    """
    import s3fs
    from pyarrow.fs import PyFileSystem, FSSpecHandler

    _, _, config = blobstore_config(filesystem=filesystem)

    endpoint_url = config[CONFIG_HOST]
    if not endpoint_url.startswith("http"):
        if config[CONFIG_DISABLE_SSL] == "true":
            endpoint_url = "http://" + endpoint_url
        else:
            endpoint_url = "https://" + endpoint_url

    s3_fs = s3fs.S3FileSystem(
        key=config[CONFIG_AK],
        secret=config[CONFIG_SK],
        client_kwargs={
            'endpoint_url': endpoint_url
        }
    )

    return PyFileSystem(FSSpecHandler(s3_fs))
