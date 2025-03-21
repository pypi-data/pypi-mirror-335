import re
class ObjectHelper:
    """

    """
    @staticmethod
    def is_none_or_empty(obj):
        """
        检查对象是否为 None 或空（适用于字符串、列表、字典等）。
        :param obj: 要检查的对象
        :return: bool
        """
        if obj is None:
            return True
        if isinstance(obj, (str, list, dict, set, tuple)):
            return len(obj) == 0
        return False

    @staticmethod
    def to_int(obj, default=0):
        """
        将对象转换为整数，如果转换失败则返回默认值。
        :param obj: 要转换的对象
        :param default: 转换失败时返回的默认值
        :return: int
        """
        try:
            return int(obj)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def to_float(obj, default=0.0):
        """
        将对象转换为浮点数，如果转换失败则返回默认值。
        :param obj: 要转换的对象
        :param default: 转换失败时返回的默认值
        :return: float
        """
        try:
            return float(obj)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def to_bool(obj, default=False):
        """
        将对象转换为布尔值，如果转换失败则返回默认值。
        :param obj: 要转换的对象
        :param default: 转换失败时返回的默认值
        :return: bool
        """
        if isinstance(obj, str):
            if obj.lower() in ('true', 'yes', '1'):
                return True
            elif obj.lower() in ('false', 'no', '0'):
                return False
        try:
            return bool(obj)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def merge_dicts(*dicts):
        """
        合并多个字典。如果有重复的键，后面的字典会覆盖前面的字典。
        :param dicts: 要合并的字典
        :return: dict
        """
        result = {}
        for d in dicts:
            result.update(d)
        return result

    @staticmethod
    def get_attr(obj, attr, default=None):
        """
        安全获取对象的属性，如果属性不存在则返回默认值。
        :param obj: 对象
        :param attr: 属性名
        :param default: 默认值
        :return: 属性值或默认值
        """
        try:
            return getattr(obj, attr, default)
        except AttributeError:
            return default

    @staticmethod
    def has_attr(obj, attr):
        """
        检查对象是否具有指定的属性。
        :param obj: 对象
        :param attr: 属性名
        :return: bool
        """
        return hasattr(obj, attr)

    @staticmethod
    def is_instance(obj, cls):
        """
        检查对象是否是某个类的实例。
        :param obj: 对象
        :param cls: 类
        :return: bool
        """
        return isinstance(obj, cls)

    @staticmethod
    def to_str(obj, default=""):
        """
        将对象转换为字符串，如果转换失败则返回默认值。
        :param obj: 要转换的对象
        :param default: 转换失败时返回的默认值
        :return: str
        """
        try:
            return str(obj)
        except (ValueError, TypeError):
            return default
 # 扩展：数据类型判断方法
    @staticmethod
    def is_int(obj):
        """
        检查对象是否为整数（int）。
        :param obj: 要检查的对象
        :return: bool
        """
        return isinstance(obj, int)

    @staticmethod
    def is_float(obj):
        """
        检查对象是否为浮点数（float）。
        :param obj: 要检查的对象
        :return: bool
        """
        return isinstance(obj, float)

    @staticmethod
    def is_str(obj):
        """
        检查对象是否为字符串（str）。
        :param obj: 要检查的对象
        :return: bool
        """
        return isinstance(obj, str)

    @staticmethod
    def is_list(obj):
        """
        检查对象是否为列表（list）。
        :param obj: 要检查的对象
        :return: bool
        """
        return isinstance(obj, list)

    @staticmethod
    def is_dict(obj):
        """
        检查对象是否为字典（dict）。
        :param obj: 要检查的对象
        :return: bool
        """
        return isinstance(obj, dict)

    @staticmethod
    def is_tuple(obj):
        """
        检查对象是否为元组（tuple）。
        :param obj: 要检查的对象
        :return: bool
        """
        return isinstance(obj, tuple)

    @staticmethod
    def is_set(obj):
        """
        检查对象是否为集合（set）。
        :param obj: 要检查的对象
        :return: bool
        """
        return isinstance(obj, set)

    @staticmethod
    def is_bool(obj):
        """
        检查对象是否为布尔值（bool）。
        :param obj: 要检查的对象
        :return: bool
        """
        return isinstance(obj, bool)

    @staticmethod
    def is_numeric(obj):
        """
        检查对象是否为数字类型（int 或 float）。
        :param obj: 要检查的对象
        :return: bool
        """
        return isinstance(obj, (int, float))

    @staticmethod
    def is_iterable(obj):
        """
        检查对象是否为可迭代对象（list、dict、set、tuple、str 等）。
        :param obj: 要检查的对象
        :return: bool
        """
        try:
            iter(obj)
            return True
        except TypeError:
            return False

    @staticmethod
    def get_type_name(obj) -> str:
        """
        获取对象的类型名称。
        :param obj: 任意对象
        :return: 类型名称（字符串）
        """
        return type(obj).__name__

    @staticmethod
    def parse_type_string(type_str: str) -> dict:
        """
        解析类型字符串，提取模块名和类型名。
        :param type_str: 类型字符串（如 "<class 'int'>"）
        :return: 包含模块名和类型名的字典
        """
        # 正则表达式匹配类型字符串
        pattern = r"<class '(?P<module>[\w\.]+)\.(?P<type>\w+)'>"
        match = re.match(pattern, type_str)
        if match:
            return match.groupdict()
        return {"module": None, "type": None}