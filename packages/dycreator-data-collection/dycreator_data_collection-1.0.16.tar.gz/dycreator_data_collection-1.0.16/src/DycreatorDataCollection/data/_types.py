import re
from dataclasses import dataclass

from .._types import BaseVideo, BaseVideoMetrics


@dataclass
class VideoMetrics(BaseVideoMetrics):
    """作品指标统计数据"""

    avg_view_proportion: float = None
    """平均观看率"""
    avg_view_second: float = None
    """平均观看时长"""
    bounce_rate_2s: float = None
    """2秒内跳出率"""
    completion_rate: float = None
    completion_rate_5s: float = None
    cover_show: int = None
    danmaku_count: int = None
    """弹幕数量"""
    dislike_count: int = None
    dislike_rate: float = None
    download_count: int = None
    fan_view_proportion: float = None
    """粉丝观看率"""
    homepage_visit_count: int = None
    """主页访问次数"""
    subscribe_count: int = None
    subscribe_rate: float = None
    unsubscribe_count: int = None
    unsubscribe_rate: float = None

    def __post_init__(self):
        super().__post_init__()

        for k, v in self.__dict__.items():
            if v is None:
                continue

            if k.endswith('_proportion'):
                setattr(self, k, round(float(v) * 100, 2))
                continue

            if re.match(r'.*\d+s$', k):
                setattr(self, k, round(float(v) * 100, 2))

        if (
            isinstance(self.avg_view_second, (str, float))
            and self.avg_view_second != ''
        ):
            self.avg_view_second = round(float(self.avg_view_second))

        if isinstance(self.cover_show, (str, int)) and self.cover_show != '':
            self.cover_show = int(self.cover_show)


@dataclass
class Video(BaseVideo):
    """作品对象"""

    metrics: VideoMetrics = None
    """指标统计数据"""
    visibility: dict = None
    """视频可见性"""
    status: int = None
    """1: 正常, 3: 私密"""

    def __post_init__(self):
        if isinstance(self.metrics, dict):
            self.metrics = VideoMetrics(**self.metrics)

        if isinstance(self.visibility, dict):
            self.status = self.visibility.get('status')

        super().__post_init__()

    def as_dict(self):
        """以字典形式返回对象数据"""

        _dict = super().as_dict()
        _dict.pop('visibility')

        return _dict
