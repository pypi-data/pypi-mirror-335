from collections import Counter


class ExpectUtils:

    @staticmethod
    def assert_fields(resp_data: dict, expect_fields, msg=None,subset=False):
        """
        断言字段是否存在或值是否匹配，支持列表、字典、嵌套结构
        :param resp_data: 响应数据
        :param expect_fields: 期望的字段或值
        :param msg: 自定义错误信息
        :param subset: 是否允许部分字段匹配（默认False，完全匹配）
        """
        #
        if isinstance(expect_fields, list):
            resp_keys = list(resp_data.keys())
            if subset:
                # 允许部分字段匹配
                assert set(expect_fields).issubset(resp_keys), (
                    f"response data:{resp_data}\n expect_fields:{expect_fields} \n {msg}")
            else:
                assert Counter(resp_keys) == Counter(
                    expect_fields), f"response data:{resp_data}\n expect_fields:{expect_fields} \n {msg}"

        elif isinstance(expect_fields, dict):
            for key, value in expect_fields.items():
                assert key in resp_data, f"Key '{key}' not found in response data. {msg}"
                if isinstance(value, dict) and isinstance(resp_data[key], dict):
                    # 递归检查嵌套字典
                    ExpectUtils.assert_fields(resp_data[key], value, msg)
                else:
                    assert resp_data[key] == value, (
                        f"response data:{resp_data}\n expect_fields:{expect_fields} \n {msg}")

