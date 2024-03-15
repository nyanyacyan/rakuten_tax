# coding: utf-8
# ----------------------------------------------------------------------------------
# 非同期処理 Cookie保存クラス
# 自動ログインするためのCookieを取得
# 今後、サイトを追加する場合にはクラスを追加していく=> 増え過ぎた場合は別ファイルへ

# 2023/3/9制作

# ----------------------------------------------------------------------------------


import os

from dotenv import load_dotenv

# 自作モジュール
from auto_login.no_cookie_login import NoCookieLogin

load_dotenv()  # .env ファイルから環境変数を読み込む


# 1----------------------------------------------------------------------------------


class RakutenLogin(NoCookieLogin):
    def __init__(self, chrome, userid, password, debug_mode=False):
        self.chrome = chrome
        self.userid = userid
        self.password = password

        # 親クラスにて定義した引数をここで引き渡すte
        # configの内容をここで全て定義
        self.config_xpath = {
            "site_name": "rakuten",
            "userid_xpath": "//input[@id='loginInner_u']",
            "password_xpath": "//input[@id='loginInner_p']",
            "login_button_xpath": "//input[@type='submit']",
            "login_checkbox_xpath": "",
            "user_element_xpath": "//div[@class='user']",
            "buy_history" : "//a[contains(text(), '購入履歴（楽天市場）')]"
        }

        super().__init__(chrome,userid, password, self.config_xpath, debug_mode=debug_mode)

    def process(self):
        self.login()




# ２----------------------------------------------------------------------------------


