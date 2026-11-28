from service.guanguan import page_guanguan_items


def test_page_first_slice_and_has_more():
    items = list(range(25))
    page, has_more = page_guanguan_items(items, 0, 20)
    assert page == list(range(20))
    assert has_more is True


def test_page_second_slice_is_last():
    items = list(range(25))
    page, has_more = page_guanguan_items(items, 20, 20)
    assert page == list(range(20, 25))
    assert has_more is False


def test_page_exact_limit_has_no_more():
    items = list(range(20))
    page, has_more = page_guanguan_items(items, 0, 20)
    assert page == items
    assert has_more is False


def test_page_offset_beyond_end():
    page, has_more = page_guanguan_items(list(range(5)), 20, 20)
    assert page == []
    assert has_more is False


def test_page_negative_offset_treated_as_zero():
    page, has_more = page_guanguan_items(list(range(3)), -5, 2)
    assert page == [0, 1]
    assert has_more is True
