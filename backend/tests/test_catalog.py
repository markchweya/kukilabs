from kuki.openlib.catalog import COURSES, get_course


def test_catalog_is_well_formed():
    ids = [c.id for c in COURSES]
    assert len(ids) == len(set(ids))
    for course in COURSES:
        assert course.license.startswith("CC BY-NC-SA")
        assert course.lectures, course.id
        assert all(lec.url.startswith("https://") for lec in course.lectures)


def test_urls_and_attribution():
    ai = get_course("cs50-ai")
    assert ai.lecture(0).url == "https://cs50.harvard.edu/ai/notes/0/"
    phil = get_course("yale-phil-181")
    assert phil.lecture(14).title == "The Trolley Problem"
    assert phil.lecture(14).url == "https://oyc.yale.edu/philosophy/phil-181/lecture-14"
    assert "Tamar Gendler" in phil.attribution(phil.lecture(14))
    assert "CC BY-NC-SA 3.0" in phil.attribution(phil.lecture(14))
