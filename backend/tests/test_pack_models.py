from kuki.study.pack_models import KeyPoint


def test_grounded_flag_is_serialised():
    assert KeyPoint(point="x", citations=[]).model_dump()["grounded"] is False
