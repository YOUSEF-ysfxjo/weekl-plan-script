import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.notion_task_manager import list_tasks

def list_cmd(args):
    list_tasks(args.database_id)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('list')
    parser_list.add_argument('--database-id', type=str, default="26692e6818f880179ee4d9119304e1ac")
    parser_list.set_defaults(func=list_cmd)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()