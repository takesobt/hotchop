import argparse, sys, logging, pdb
from pathlib import Path
from .extractor import HOTchopper

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

def setup_logger(enable_log: bool):
    if enable_log:
        logging.basicConfig(
            filename="hotchop.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            encoding="utf-8",
            filemode="a",  # append mode
        )
    else:
        logging.basicConfig(level=logging.CRITICAL)  # logging.CRITICAL

def criteria_error_check(wk_criteria_type: str, wk_criteria_list: list) -> dict:
    # initialize dictionaries
    chop_criteria = {}
    error_item = {}
    # if criteria is empty 
    if wk_criteria_list == [""]:
        return {"ERR":"Please input criteria!"}

    # Criteria error check
    for i in range(0, len(wk_criteria_list)):
        wk_criteria_list[i] = wk_criteria_list[i].replace(" ", "")
        if not wk_criteria_list[i].isnumeric():  # Numeric error
            error_item[i] = [
                wk_criteria_list[i],
                "Numeric ERR",
            ]  # add to error_item dictionary
        elif wk_criteria_type == "TDNR" and len(wk_criteria_list[i]) != 13:  # Length error
            error_item[i] = [
                wk_criteria_list[i],
                "Length ERR (not 13 digit)",
            ]  # add to error_item dictionary
        elif wk_criteria_type == "TRNN" and (
            len(wk_criteria_list[i]) < 1 or len(wk_criteria_list[i]) > 6
        ):  # Length error
            error_item[i] = [
                wk_criteria_list[i],
                "Length ERR (1<n<999999)",
            ]  # add to error_item dictionary
        else:  # so far no error
            if wk_criteria_type == "TDNR":
                wk_len = 13
            else:
                wk_len = 6
            if (
                wk_criteria_list[i].zfill(wk_len) in chop_criteria
            ):  # Duplicate error
                error_item[i] = [
                    wk_criteria_list[i],
                    "Duplicate ERR",
                ]  # add to duplicate dictionary
            else:  # No error is detected
                chop_criteria[wk_criteria_list[i].zfill(wk_len)] = (
                    ""  # add to chop criteria
                )

    # if error item found, output error message
    if len(error_item) > 0:
        wk_msg = "Criteria error found!"
        for c1, [c2, c3] in error_item.items():
            wk_msg += "\n L:" + str(c1 + 1) + " Val:" + c2 + " " + c3
        return {"ERR":wk_msg}
    # No errors
    return chop_criteria

def main():
    args = parse_args()
    setup_logger(args.log)
    # Display start message
    logging.info("👉 HOT chopper starts!") 
    print("👉 HOT chopper starts!")
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
        HOTchopper_ins = HOTchopper(
            args.input_path, args.output_path, args.criteria_type, dict_chop_criteria
        )
        HOTchopper_ins.HOT_chop()
        # Result get by the dictionary
        result_number = HOTchopper_ins.getresult_number()
        logging.info(f"Processed Number Result⬇️\n{result_number}")
        print(f"Processed Number Result⬇️\n{result_number}")
        # Result get by the dictionary
        result_criteria = HOTchopper_ins.getresult_criteria()
        wk_msg = "Chop criteria : " + args.criteria_type + "\n"
        for c1, c2 in result_criteria.items():
            wk_msg += c1 + " " + c2 + "\n"
        logging.info(f"Processed Criteria Result⬇️\n{wk_msg}")
        print(f"Processed Criteria Result⬇️\n{wk_msg}")
        # Display result message
        logging.info("✅ The HOT file was chopped successfully.") 
        print("✅ The HOT file was chopped successfully.")
    except Exception as e:
        logging.error(f"Chop Failed: {args.input_path} → {args.output_path} ({e})")
        print(f"Error chopping {args.input_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
