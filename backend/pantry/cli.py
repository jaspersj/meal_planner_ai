# backend/pantry/cli.py
import argparse
from .db import init_db, list_items, add_item, update_item, remove_item

def main():
    parser = argparse.ArgumentParser("Pantry Manager")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init")
    sub_list = sub.add_parser("list")

    sub_add = sub.add_parser("add")
    sub_add.add_argument("name")
    sub_add.add_argument("qty", type=float)
    sub_add.add_argument("--unit", default="")
    sub_add.add_argument("--expires")

    sub_up = sub.add_parser("update")
    sub_up.add_argument("name")
    sub_up.add_argument("--qty", type=float)
    sub_up.add_argument("--unit")
    sub_up.add_argument("--expires")

    sub_rm = sub.add_parser("remove")
    sub_rm.add_argument("name")

    args = parser.parse_args()
    if args.cmd == "init": init_db()
    elif args.cmd == "list":
        for row in list_items(): print(dict(row))
    elif args.cmd == "add":
        add_item(args.name, args.qty, args.unit or None, args.expires)
    elif args.cmd == "update":
        update_item(args.name, args.qty, args.unit, args.expires)
    elif args.cmd == "remove":
        remove_item(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()