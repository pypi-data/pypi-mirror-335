#!/usr/bin/env python
"""命令行界面。"""

import argparse
import sys
from . import greet, get_simple_api, get_python_version

def main():
    parser = argparse.ArgumentParser(description="一个友好的问候和API调用工具。")
    parser.add_argument("--name", default="World", help="要问候的名称")
    parser.add_argument("--api", action="store_true", help="调用简单的API")
    parser.add_argument("--version", action="store_true", help="显示Python版本")
    
    args = parser.parse_args()
    
    if args.version:
        print(get_python_version())
    elif args.api:
        print(get_simple_api())
    else:
        print(greet(args.name))
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 