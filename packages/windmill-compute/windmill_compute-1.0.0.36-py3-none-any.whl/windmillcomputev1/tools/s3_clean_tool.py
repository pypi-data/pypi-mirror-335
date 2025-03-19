#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/9/10
# @Author  : zhangzhijun
# @File    : download_kubeconfig.py
"""
import os
from argparse import ArgumentParser
from windmillcomputev1.client.compute_api_filesystem import Policy
from concurrent.futures import ThreadPoolExecutor
import bcelogger
import yaml
from windmillcomputev1.filesystem import blobstore
import fnmatch
from datetime import datetime
import dateparser


def parse_args():
    """
    Parse arguments.
    """

    parser = ArgumentParser()
    parser.add_argument("--config", required=True, type=str, default=os.environ.get("CONFIG"),
                        help="config.yaml")
    parser.add_argument("--max-worker", required=False, type=int,
                        default=3 if os.environ.get("MAX_WORKER") is None else int(os.environ.get("MAX_WORKER")))
    args, _ = parser.parse_known_args()

    return args


def run():
    """
    download kubeconfig.
    """
    bcelogger.info("start clean_filesystem")
    args = parse_args()
    bcelogger.info(f"args: {args}")
    if not os.path.exists(args.config):
        raise FileNotFoundError(args.config)
    with open(args.config, 'r') as f:
        data = yaml.load(f, Loader=yaml.Loader)
    with ThreadPoolExecutor(max_workers=args.max_worker) as executor:
        for filesystem_file_clean in data:
            s3 = filesystem_file_clean['s3']
            s3['kind'] = 's3'
            store = blobstore(filesystem=s3)
            buckets_response = store.list_bucket()
            bucket_name = filesystem_file_clean['bucket']
            policy = Policy(policy=filesystem_file_clean['policy'], expiration=filesystem_file_clean['expiration'],
                            max_size=filesystem_file_clean['maxSize'])
            for bucket in buckets_response['Buckets']:
                if fnmatch.fnmatch(bucket['Name'], bucket_name):
                    # 修改endpoint 用来修改bucket 原来的endpoint的值为 bucket/path
                    s3['endpoint'] = bucket['Name']
                    store = blobstore(filesystem=s3)
                    for path in filesystem_file_clean['paths']:
                        bcelogger.info(
                            f"delete_filesystem_files host: {s3['host']} "
                            f"region: {s3['config']['region']} bucket: {bucket['Name']} path: {path} ")
                        executor.submit(delete_filesystem_files, store, path, policy)


def delete_filesystem_files(store, path, policy):
    """
    delete filesystem files

    {
    "workspace_id":"test"
    "filesystem":"test"
    }
    :param path
    :param policy
    {
    "policy":"Expiration",
    "expiration": "60s",
    "maxSize":100 单位GB
    }
    :return:
    @type store: S3BlobStore
    @type path: str
    @type policy: Policy
    """
    if path == '' or os.path.abspath(path) == '/':
        raise ValueError(f'No Allow clean root path')
    if policy.policy == "Expiration":
        delete_files_with_expire_policy(store, policy.expiration, path)
    elif policy.policy == "MaxSize":
        delete_files_with_maxsize_policy(store, policy.max_size, path)
    else:
        raise ValueError(f"policy {policy.policy} not supported")


def delete_files_with_expire_policy(store, time, path):
    """
    delete files with expire policy
    """
    next_start = None
    # 任务启动当前时间
    current_seconds = datetime.now().timestamp()

    # 过期时间 60d 60s 固定时间 相对时间 60s expire_time expire_time =  current_time - 60  17:23:00 17:22:00
    expire_time = dateparser.parse(time).timestamp()
    if current_seconds - expire_time < 60:
        raise ValueError(f'Expiration time {expire_time} is less than 60s')
    clean_files = []
    while True:
        metas = store.list_objects_v2(path, continuation_token=next_start)  # replace with your error handling
        if 'Contents' in metas and len(metas['Contents']) != 0:
            for meta in metas['Contents']:
                if meta["LastModified"].timestamp() < expire_time:
                    key = meta["Key"]
                    clean_files.append(key)
            if 'NextContinuationToken' in metas:
                next_start = metas['NextContinuationToken']
        if not metas['IsTruncated']:
            break
    for key in clean_files:
        try:
            store.delete_file(key)  # replace with your error
            bcelogger.trace(f" delete file {key}")
        except Exception as e:
            bcelogger.error(f"delete file {key} failed", e)


def delete_files_with_maxsize_policy(store, max_storage, path):
    """
    delete files with maxsize policy
    """
    next_start = None
    all_metas = list()

    while True:
        metas = store.list_objects_v2(path, continuation_token=next_start)
        if 'Contents' in metas:
            all_metas += metas['Contents']
            if 'NextContinuationToken' in metas:
                next_start = metas['NextContinuationToken']
        if not metas['IsTruncated']:
            break
    sum_size = sum([meta['Size'] for meta in all_metas])

    all_metas.sort(key=lambda meta: meta['LastModified'])
    # 待清理
    clean_size = sum_size - max_storage * 1024 * 1024 * 1024
    for meta in all_metas:
        if meta['Size'] <= clean_size:
            key = meta["Key"]
            try:
                store.delete_file(os.path.dirname(key))  # replace with your error
                bcelogger.trace(f" delete file {key}")
            except Exception as e:
                bcelogger.error(f"delete file {key} failed", e)
            clean_size -= meta.Size
        else:
            break


if __name__ == "__main__":
    run()
