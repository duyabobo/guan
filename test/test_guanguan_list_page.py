from service.guanguan import LIST_FETCH_POOL_FACTOR, candidate_pool_limit, page_guanguan_items
from util.const.match import GUANGUAN_LIST_DEFAULT_LIMIT, GUANGUAN_LIST_MAX_OFFSET


def test_candidate_pool_limit_ignores_offset():
    """各页必须共用同一候选池，否则跨页会在不同集合上重排。"""
    page_limit = GUANGUAN_LIST_DEFAULT_LIMIT
    assert candidate_pool_limit(page_limit) == (
        GUANGUAN_LIST_MAX_OFFSET + page_limit + 1
    ) * LIST_FETCH_POOL_FACTOR


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


def test_page_empty_list():
    page, has_more = page_guanguan_items([], 0, 20)
    assert page == []
    assert has_more is False
