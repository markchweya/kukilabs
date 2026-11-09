from kuki.study.text import clean


def test_clean_model_strings():
    assert clean('A"* ') == "A*"            # seen in real Llama 3.2 output
    assert clean('"Heuristic"') == "Heuristic"
    assert clean("“FIFO” means first in , first out .") == "“FIFO” means first in, first out."
    assert clean("  spaced \n out  ") == "spaced out"
    assert clean('He said "hi" twice') == 'He said "hi" twice'  # balanced quotes kept


def test_apostrophes_survive():
    # Regression: an earlier version turned "we'll" into "well".
    assert clean("In this guide we'll see why it’s optimal") == "In this guide we'll see why it’s optimal"
    assert clean("You'll learn") == "You'll learn"
