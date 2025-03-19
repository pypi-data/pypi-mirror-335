from dataclasses import dataclass, fields

from ._utils import Utils


class FilteredDataclass(type):
    """过滤kwargs中多余的键"""

    def __call__(cls, *args, **kwargs):
        valid_fields = {f.name for f in fields(cls)}
        kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        return super().__call__(*args, **kwargs)


class BaseType(metaclass=FilteredDataclass):
    pass


@dataclass
class BaseVideoMetrics(BaseType):
    """作品指标统计数据基础类"""

    comment_count: int = None
    comment_rate: float = None
    favorite_count: int = None
    favorite_rate: float = None
    like_count: int = None
    like_rate: float = None
    share_count: int = None
    share_rate: float = None
    view_count: int = None

    def __post_init__(self):
        for k, v in self.__dict__.items():
            if v == '' or not isinstance(v, (int, str)):
                setattr(self, k, None)
                continue

            if k.endswith('_count'):
                setattr(self, k, int(v))
                continue

            if k.endswith('_rate'):
                setattr(self, k, round(float(v) * 100, 2))
                continue

    def as_dict(self):
        """以字典形式返回对象数据"""

        return self.__dict__.copy()


@dataclass
class BaseVideo(BaseType):
    """作品对象基础类"""

    id: str = None
    """作品ID"""
    cover: str = None
    create_time: str = None
    create_timestamp: int = None
    description: str = None
    """视频标题"""
    metrics: BaseVideoMetrics = None
    """指标统计数据"""
    metrics_offline_update_time: str = None
    metrics_offline_update_timestamp: int = None
    user_id: str = None
    type: int = None
    video_info: dict = None
    duration: str = None

    def __post_init__(self):
        for k in ['id', 'user_id']:
            v = getattr(self, k)
            if not isinstance(v, int):
                continue
            setattr(self, k, str(v))

        if isinstance(self.cover, dict) and 'url_list' in self.cover:
            self.cover = self.cover['url_list'][0]

        for k in ['create_time', 'metrics_offline_update_time']:
            v = getattr(self, k)
            if not isinstance(v, (int, str)):
                continue
            v = int(v)
            setattr(self, k, Utils.timestamp_to_str(v))
            setattr(self, f'{k}stamp', v * 1000)

        if isinstance(self.metrics, dict):
            self.metrics = BaseVideoMetrics(**self.metrics)

        if (
            isinstance(self.video_info, dict)
            and 'duration' in self.video_info
            and isinstance((duration := self.video_info['duration']), (int, str))
        ):
            self.duration = Utils.seconds_to_time(round(int(duration) / 1000))

    def as_dict(self):
        """以字典形式返回对象数据"""

        _dict = self.__dict__.copy()
        _dict.pop('metrics')
        _dict.pop('video_info')

        _dict.update(self.metrics.as_dict())

        return _dict
