class Works:
    video__detail = {
        '视频ID': 'id',
        '视频标题': 'description',
        '封面链接': 'cover',
        '发布时间': 'create_time',
        '发布时间_时间戳': 'create_timestamp',
        '最后更新时间': 'metrics_offline_update_time',
        '最后更新时间_时间戳': 'metrics_offline_update_timestamp',
        '用户ID': 'user_id',
        '视频时长': 'duration',
        '评论数': 'comment_count',
        '评论率': 'comment_rate',
        '收藏数': 'favorite_count',
        '收藏率': 'favorite_rate',
        '点赞量': 'like_count',
        '点赞率': 'like_rate',
        '分享数': 'share_count',
        '分享率': 'share_rate',
        '播放量': 'view_count',
    }


class BaseDictionary:
    works = Works()
