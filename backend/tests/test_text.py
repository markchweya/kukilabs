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


def test_strip_source_tags():
    from kuki.study.text import strip_source_tags

    # Real Llama 3.2 3B quiz question:
    assert strip_source_tags("Explain why BFS is considered complete. (Source: [S4] and [S8])") == "Explain why BFS is considered complete."
    assert strip_source_tags("A queue is FIFO [S2].") == "A queue is FIFO."
    assert strip_source_tags("Compare (S1, S2) carefully") == "Compare carefully"
    assert strip_source_tags("Keep (not a tag) here") == "Keep (not a tag) here"
