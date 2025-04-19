# utils.py
import logging, sys

def criteria_error_check(wk_criteria_type: str, wk_criteria_list: list) -> dict:
    # initialize dictionaries
    chop_criteria = {}
    error_item = {}
    # if criteria is empty 
    if wk_criteria_list == [""]:
        return {"ERR":"Please input criteria!"}
    # if criteria is default value
    if wk_criteria_list[0] == "xxxyyyyyyyyyy" or wk_criteria_list[0] == "nnnnnn":
        return {"ERR":"Please input criteria!"}

    # Criteria error check
    for i in range(0, len(wk_criteria_list)):
        wk_criteria_list[i] = wk_criteria_list[i].replace(" ", "")
        wk_criteria_list[i] = wk_criteria_list[i].replace("OK", "")
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

def setup_logger(enable_log: bool):
    if enable_log:
        handlers = [
            logging.FileHandler("hotchop.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)  # ← stdoutにも出す！
        ]
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=handlers
        )
    else:
        logging.basicConfig(level=logging.CRITICAL)  # logging.CRITICAL