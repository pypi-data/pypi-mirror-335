from typing import Callable

from DrissionPage import Chromium
from DrissionPage._pages.mix_tab import MixTab


class Urls:
    home = 'https://creator.douyin.com/creator-micro/home'


class DataPacketUrls:
    qrcode = 'https://sso.douyin.com/get_qrcode'
    qrcode_type2 = 'https://creator.douyin.com/passport/web/get_qrcode'
    """扫码登录二维码"""
    account_info = 'https://creator.douyin.com/web/api/media/user/info'


class Login:
    def __init__(self, browser: Chromium):
        self._browser = browser

    def _wait__account_info(
        self, page: MixTab, callback: Callable, timeout: float = None
    ):
        """登录账号信息数据包"""

        _timeout = timeout if isinstance(timeout, (int, float)) else 8

        page.listen.start(
            targets=DataPacketUrls.account_info, method='GET', res_type='Fetch'
        )
        callback()
        packet = page.listen.wait(timeout=_timeout)
        if not packet:
            return

        resp = packet.response.body
        if not isinstance(resp, dict):
            raise RuntimeError('账号信息数据包非预期的 dict 类型')

        if 'user' not in resp:
            raise RuntimeError('账号信息数据包中未找到 user 字段')

        user = resp['user']
        if not isinstance(user, dict):
            raise RuntimeError('账号信息数据包中 user 字段非预期的 dict 类型')

        return user

    def login_by_cookie(
        self,
        uid: str,
        cookies: dict,
        local_storage: dict = None,
        session_storage: dict = None,
        timeout: float = None,
    ):
        """
        通过 cookie 登录

        Args:
            timeout: 判断是否已登录的数据包返回超时时间, 默认为 8 秒
        Returns:
            如果登录成功将返回用户信息
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else 8

        page = self._browser.latest_tab
        page.listen.start(
            targets=[DataPacketUrls.qrcode, DataPacketUrls.qrcode_type2],
            method='GET',
            res_type='XHR',
        )
        page.get(Urls.home)
        page.listen.wait(count=1, timeout=_timeout)

        # 不管是否成功获取到二维码数据包，都需要设置 cookies
        page.set.cookies(cookies)

        if isinstance(local_storage, dict):
            for k, v in local_storage.items():
                page.set.local_storage(k, v)

        if isinstance(session_storage, dict):
            for k, v in session_storage.items():
                page.set.session_storage(k, v)

        account_info = self._wait__account_info(
            page, lambda: page.get(Urls.home), timeout=_timeout
        )
        if not account_info:
            raise RuntimeError('登录失败，请检查账号有效性')

        if (_uid := account_info.get('uid')) != uid:
            raise RuntimeError(
                f'登录异常, 登录已登录 uid<{_uid}> 与预期 uid<{uid}> 不一致'
            )

        return account_info
