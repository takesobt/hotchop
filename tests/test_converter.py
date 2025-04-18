from md2pt_jp.converter import convert_markdown_to_plaintext
# Test cases for convert_markdown_to_plaintext 
# poetry run pytest -s で実行
def test_markdown_to_plaintext_heading_and_bold():
    input_text = "###見出し３\n涼子のテレキネシスが**暴発**した"
    expected_output = "【見出し３】\n涼子のテレキネシスが暴発した"
    assert convert_markdown_to_plaintext(input_text) == expected_output

def test_custom_heading_levels():
    input_text = "#第一話\n##登場人物\n###涼子の能力"
    expected_output = "☆EPISODE☆第一話\n☆☆登場人物☆☆\n【涼子の能力】"
    assert convert_markdown_to_plaintext(input_text) == expected_output

def test_horizontal_rule_conversion():
    input_text = "本文\n---\nつづき"
    expected_output = "本文\n＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝\nつづき"
    assert convert_markdown_to_plaintext(input_text) == expected_output

def test_custom_heading_clear():
    input_text = "#☆EPISODE☆第一話\n##☆☆登場人物☆☆\n###【涼子の能力】"
    expected_output = "☆EPISODE☆第一話\n☆☆登場人物☆☆\n【涼子の能力】"
    assert convert_markdown_to_plaintext(input_text) == expected_output
