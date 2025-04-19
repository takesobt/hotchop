# utils.py
from hotchop.utils import criteria_error_check

def test_valid_tdnr_criteria():
    result = criteria_error_check("TDNR", ["9992423207406", "9992423239061"])
    assert "ERR" not in result
    assert len(result) == 2

def test_invalid_tdnr_length():
    result = criteria_error_check("TDNR", ["123"])
    assert "ERR" in result
    assert "Length ERR" in result["ERR"]

def test_duplicate_criteria():
    result = criteria_error_check("TDNR", ["9992423207406", "9992423207406"])
    assert "ERR" in result
    assert "Duplicate ERR" in result["ERR"]
