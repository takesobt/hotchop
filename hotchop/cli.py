# cli.py
import argparse, sys, logging, pdb
from pathlib import Path
from .extractor import HOTchopper
from .utils import criteria_error_check, setup_logger

def parse_args():
    parser = argparse.ArgumentParser(
        description="Exstract HOT file based on the criteria given in the arguments."
    )
    parser.add_argument("input_path", type=Path, help="Path to input file")
    parser.add_argument("output_path", type=Path, help="Path to output file")
    parser.add_argument("chop_criteria",type=parse_comma_list
                        ,help='Comma-separated list, e.g. "9990123456789,9990123456790,9990123456791"')
    parser.add_argument("--criteria_type", choices=["TDNR", "TRNN"], default="TDNR", help="Chop criteria type")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
    parser.add_argument("--log", action="store_true", help="Output onversion log to hotchop.log")
    return parser.parse_args()

def parse_comma_list(arg_str: str) -> list:
    return arg_str.split(",")

def main():
    args = parse_args()
    setup_logger(args.log)
    # Display start message
    logging.info("👉 HOT chopper starts!") 
    # Input HOT File path check
    if not args.input_path.exists():
        logging.error(f"Error: Input file does not exist: {args.input_path}")
        sys.exit(f"Error: Input file does not exist: {args.input_path}")

    # Output HOT File path check
    if not args.overwrite and args.output_path.exists():
        logging.error(f"Error: Output file already exists: {args.output_path}")
        sys.exit(f"Error: Output file already exists: {args.output_path}")

    # chop_criteria
    dict_chop_criteria = criteria_error_check(args.criteria_type, args.chop_criteria)
    if "ERR" in dict_chop_criteria:
        logging.error(f"Error: There are some errors in chop criteria: {dict_chop_criteria['ERR']}")
        sys.exit(f"There is an error in chop criteria: {dict_chop_criteria['ERR']}")

    # Call main program
    try:
        logging.info(f"Input: {args.input_path}")
        logging.info(f"Output: {args.output_path}")        
        HOTchopper_ins = HOTchopper(
            args.input_path, args.output_path, args.criteria_type, dict_chop_criteria
        )
        HOTchopper_ins.HOT_chop()
        # Result get by the dictionary
        result_number = HOTchopper_ins.getresult_number()
        logging.info(f"Processed Number Result⬇️\n{result_number}")
        # Result get by the dictionary
        result_criteria = HOTchopper_ins.getresult_criteria()
        wk_msg = "Chop criteria : " + args.criteria_type
        for c1, c2 in result_criteria.items():
            wk_msg += "\n" + c1 + " " + c2
        logging.info(f"Processed Criteria Result⬇️\n{wk_msg}")
        # Display result message
        logging.info("✅ The HOT file was chopped successfully.") 
    except Exception as e:
        logging.error(f"Chop Failed: {args.input_path} → {args.output_path} ({e})")

if __name__ == "__main__":
    main()
