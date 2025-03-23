from ..log_util import Logger


def test_log_util():
    s1 = Logger().get_logger()
    s2 = Logger().get_logger()
    print(id(s1))
    print(id(s2))
