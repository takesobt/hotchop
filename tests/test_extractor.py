# test_extractor.py
from hotchop.extractor import HOTchopper
from pathlib import Path

def test_hotchop_runs_TDNR(tmp_path):
    # Set up test input/output
    input_path = Path("tests") / "DummyHOTfile.txt"
    output_path = tmp_path / "output.txt"
    criteria = {"9994402553301": "", "9992423247383": ""}
    
    chopper = HOTchopper(input_path, output_path, "TDNR", criteria)
    chopper.HOT_chop()
    
    assert output_path.exists()
    result = chopper.getresult_criteria()
    assert isinstance(result, dict)
    assert len(result) > 0

def test_hotchop_runs_TRNN(tmp_path):
    # Set up test input/output
    input_path = Path("tests") / "DummyHOTfile.txt"
    output_path = tmp_path / "output.txt"
    criteria = {"000001": "", "000003": ""}
    
    chopper = HOTchopper(input_path, output_path, "TRNN", criteria)
    chopper.HOT_chop()
    
    assert output_path.exists()
    result = chopper.getresult_criteria()
    assert isinstance(result, dict)
    assert len(result) > 0
