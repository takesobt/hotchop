# gui.py
import argparse
from gui.app import main
from hotchop.utils import setup_logger

def parse_gui_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", action="store_true", help="Enable logging to hotchop.log")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_gui_args()
    setup_logger(args.log)
    main()
