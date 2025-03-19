from datetime import datetime


class Utils:
    @staticmethod
    def timestamp_to_str(timestamp: int | str, pattern='%Y-%m-%d %H:%M:%S'):
        """
        将时间戳转为日期时间字符串

        Args:
            timestamp: 时间戳
            pattern: 日期时间格式
        Returns:
            日期时间字符串
        """

        return datetime.fromtimestamp(int(timestamp)).strftime(pattern)

    @staticmethod
    def seconds_to_time(seconds: int):
        """
        秒数转为时间字符串

        Args:
            seconds: 秒数
        Returns:
            时间字符串, 格式为 'xx:xx'
        """

        m, s = divmod(seconds, 60)
        _, m = divmod(m, 60)
        return f'{m:02d}:{s:02d}'

    @staticmethod
    def dict_mapping(data: dict, dict_table: dict[str, str]):
        """
        字典表字段映射

        Args:
            data: 待映射的字典
            dict_table: 字典表
        """

        result = {}
        for text, key in dict_table.items():
            result[text] = data.get(key)

        return result
