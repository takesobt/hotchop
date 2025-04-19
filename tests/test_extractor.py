# test_extractor.py
from hotchop.extractor import HOTchopper
from pathlib import Path

def test_hotchop_runs(tmp_path):
    # Set up test input/output
    input_path = Path("testdata") / "Plane.txt"
    output_path = tmp_path / "output.txt"
    criteria = {"000001": "", "000005": ""}
    
    chopper = HOTchopper(input_path, output_path, "TRNN", criteria)
    chopper.HOT_chop()
    
    assert output_path.exists()
    result = chopper.getresult_criteria()
    assert isinstance(result, dict)
    assert len(result) > 0
