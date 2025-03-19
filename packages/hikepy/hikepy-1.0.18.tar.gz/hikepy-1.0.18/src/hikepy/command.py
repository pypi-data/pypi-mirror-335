# -*- coding: utf8 -*-

"hikepy启动类"

__author__ = "hnck2000@126.com"

import os
import argparse

def main():
    "运行框架脚本"
     # 判断当前环境
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "arg1", help="命令", type=str, nargs="?", default="init"
    )
    args = parser.parse_args()
    current_path = os.getcwd()

    if args.arg1=="init":
        #项目脚手架生成
        print(current_path)
        #os.makedirs(os.path.join(root_path, "assets"), exist_ok=True)
        #os.makedirs(os.path.join(root_path, "assets", "etc"), exist_ok=True)
        #os.makedirs(os.path.join(root_path, "assets", "logs"), exist_ok=True)

if __name__ == "__main__":
    main()
