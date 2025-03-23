from ..date_ope import *


def test_get_current_time():
    print(get_current_time())


def test_add_or_subtract_date():
    print(add_or_subtract_date(get_current_time(), "subtract", 1, "week"))
