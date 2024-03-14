# coding: utf-8
# ----------------------------------------------------------------------------------
# 子クラス
# 2023/3/14制作

# ----------------------------------------------------------------------------------


import os

from dotenv import load_dotenv

# 自作モジュール
from site_operations.start_line import SiteOperations

load_dotenv()  # .env ファイルから環境変数を読み込む


# 1----------------------------------------------------------------------------------


class RakutenOperations(SiteOperations):
    def __init__(self, chrome, debug_mode=False):
        # 親クラスにて定義した引数をここで引き渡す
        # configの内容をここで全て定義

        self.config = {
            "site_name": "rakuten",
            "main_url": os.getenv('RAKUTEN_MAIN_URL'),
            "cookies_file_name": "rakuten_cookie_file.pkl",
            "buy_history" : "//a[contains(text(), '購入履歴（楽天市場）')]"
        }

        super().__init__(chrome, self.config, debug_mode=debug_mode)

    def start_move(self):
        self.operation()


# ２----------------------------------------------------------------------------------