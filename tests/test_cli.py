# test_cli.py
from hotchop.cli import parse_comma_list

def test_parse_comma_list():
    assert parse_comma_list("A,B,C") == ["A", "B", "C"]
