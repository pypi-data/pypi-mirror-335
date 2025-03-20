class AssertUtils:

    @staticmethod
    def assert_equal(actual, expected, msg=None):
        """
        断言两个值相等
        """
        assert actual == expected, f"{msg or ''} \nAssert Equal Failed: Expected:{expected},Actual:{actual}"

    @staticmethod
    def assert_not_equal(actual, expected, msg=None):
        """
        断言两个值不相等
        """
        assert actual != expected, f"{msg or ''} \nAssert Not Equal Failed: Expected:{expected},Actual:{actual}"

    @staticmethod
    def assert_in(expect_text, actual_text, msg=None):
        """
        断言actual在expected中
        """
        assert expect_text in actual_text, f"{msg or ''} \nAssert In Failed: Expected:{expect_text}"

    @staticmethod
    def assert_not_in(expect_text, actual_text, msg=None):
        """
        断言actual不在expected中
        """
        assert expect_text not in actual_text, f"{msg or ''} \nAssert Not In Failed"

    @staticmethod
    def assert_not_none(actual, msg=None):
        assert actual is not None, f"{msg or ''} \nAssert Not None Failed: Actual:{actual}"

    @staticmethod
    def assert_is_none(actual, msg=None):
        assert actual is None, f"{msg or ''} \nAssert Not None Failed: Actual:{actual}"

    @staticmethod
    def assert_true(actual, msg=None):
        assert actual is True, f"{msg or ''} \nAssert True Failed: Actual:{actual}"

    @staticmethod
    def assert_false(actual, msg=None):
        assert actual is False, f"{msg or ''} \nAssert False Failed: Actual:{actual}"

    @staticmethod
    def assert_equal_ignore_type(actual, expected, msg=None):
        assert str(actual) == str(
            expected), f"{msg or ''} \nAssert Equal (Ignore Type) Failed: Expected:{expected}, Actual:{actual}"

    @staticmethod
    def assert_is_empty(value, msg=None):
        assert value in (None, '', [], {}, set()), f"{msg or ''} \nAssert Empty Failed: Actual:{value}"

    @staticmethod
    def assert_not_empty(value, msg=None):
        """
        排除0， False
        """
        assert value not in (None, '', [], {}, set()), f"{msg or ''} \nAssert Not Empty Failed: Actual:{value}"

    @staticmethod
    def assert_greater(actual, expected, msg=None):
        """
        断言actual大于expected
        """
        assert actual > expected, f"{msg or ''} \nAssert Greater Failed: Expected greater than {expected}, Actual:{actual}"

    @staticmethod
    def assert_less(actual, expected, msg=None):
        """
        断言actual小于expected
        """
        assert actual < expected, f"{msg or ''} \nAssert Less Failed: Expected less than {expected}, Actual:{actual}"

    @staticmethod
    def assert_between(actual, min_value, max_value, msg=None):
        """
        断言actual在min_value和max_value之间
        """
        assert min_value <= actual <= max_value, f"{msg or ''} \nAssert Between Failed: Expected between {min_value} and {max_value}, Actual:{actual}"

    @staticmethod
    def assert_starts_with(actual, prefix, msg=None):
        """
        断言actual以prefix开头
        """
        assert str(actual).startswith(str(prefix)), f"{msg or ''} \nAssert Starts With Failed: Expected prefix {prefix}, Actual:{actual}"

    @staticmethod
    def assert_ends_with(actual, suffix, msg=None):
        """
        断言actual以suffix结尾
        """
        assert str(actual).endswith(str(suffix)), f"{msg or ''} \nAssert Ends With Failed: Expected suffix {suffix}, Actual:{actual}"

    @staticmethod
    def assert_regex_match(actual, pattern, msg=None):
        import re
        assert re.match(pattern, str(actual)), f"{msg or ''} \nAssert Regex Match Failed: Expected pattern {pattern}, Actual:{actual}"

