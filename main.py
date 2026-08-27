#!/usr/bin/python3.12
# -*- coding: utf-8 -*-
#
# @Time  : 2026/8/24 16:14
# @File  : main.py

import traceback
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
from shutil import copy

import yaml
from loguru import logger

if not Path("cfg.yaml").exists():
    copy(Path('cfg.example.yaml'), Path('cfg.yaml'))
    logger.info('请填写配置文件 cfg.yaml 后再次运行')
    exit(0)
from register import Register

with open("cfg.yaml", "r", encoding="utf-8") as file:
    cfg = yaml.load(file, Loader=yaml.FullLoader)


def task():
    try:
        with Register() as register:
            register.run()
    except Exception:
        logger.error(traceback.format_exc())


def main():
    max_workers = cfg["max_workers"]
    executor = ThreadPoolExecutor(max_workers=max_workers)
    futures = {executor.submit(task) for _ in range(max_workers)}

    try:
        while True:
            done, pending = wait(futures, timeout=0.5, return_when=FIRST_COMPLETED)
            futures = pending
            for _ in done:
                futures.add(executor.submit(task))

    except KeyboardInterrupt:
        logger.warning(f"收到 Ctrl+C，不再创建新任务，等待当前 {len(futures)} 个任务完成...")
        executor.shutdown(wait=True, cancel_futures=True, )
        logger.success("当前任务全部完成，退出")


if __name__ == "__main__":
    main()
