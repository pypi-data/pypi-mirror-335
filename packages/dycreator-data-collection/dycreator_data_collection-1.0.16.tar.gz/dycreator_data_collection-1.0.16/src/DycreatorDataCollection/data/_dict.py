from .._dict import BaseDictionary


class Works:
    video__detail = {
        **BaseDictionary.works.video__detail,
        '视频状态': 'status',
        '平均播放占比': 'avg_view_proportion',
        '平均播放时长': 'avg_view_second',
        '2秒跳出率': 'bounce_rate_2s',
        '完播率': 'completion_rate',
        '5秒完播率': 'completion_rate_5s',
        '封面浏览量': 'cover_show',
        '弹幕量': 'danmaku_count',
        '不喜欢量': 'dislike_count',
        '不喜欢率': 'dislike_rate',
        '下载量': 'download_count',
        '粉丝播放占比': 'fan_view_proportion',
        '主页浏览量': 'homepage_visit_count',
        '关注量': 'subscribe_count',
        '关注率': 'subscribe_rate',
        '取关量': 'unsubscribe_count',
        '取关率': 'unsubscribe_rate',
    }


class Dictionary:
    works = Works()
