# test_extractor.py
from hotchop.extractor import HOTchopper
from pathlib import Path

def test_hotchop_runs(tmp_path):
    # Set up test input/output
    input_path = Path("testdata") / "Input.txt"
    output_path = tmp_path / "output.txt"
    criteria = {"9992423207406": "", "9992423239061": ""}
    
    chopper = HOTchopper(input_path, output_path, "TDNR", criteria)
    chopper.HOT_chop()
    
    assert output_path.exists()
    result = chopper.getresult_criteria()
    assert isinstance(result, dict)
    assert len(result) > 0
