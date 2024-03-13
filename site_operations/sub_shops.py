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
from site_operations.site_operations import SiteOperations

load_dotenv()  # .env ファイルから環境変数を読み込む


# 1----------------------------------------------------------------------------------


class RakutenOperations(SiteOperations):
    def __init__(self, chrome, order_number, price, debug_mode=False):
        # 親クラスにて定義した引数をここで引き渡す
        # configの内容をここで全て定義
        self.order_number = order_number
        self.price = price

        self.config = {
            "site_name": "rakuten",
            "main_url": os.getenv('RAKUTEN_MAIN_URL'),
            "cookies_file_name": "rakuten_cookie_file.pkl",
            "buy_history" : "//a[contains(text(), '購入履歴（楽天市場）')]",
            "history_detail" : f"//li[contains(., '{self.order_number}')]/following-sibling::li[contains(@class, 'oDrDetailList')]/a",
            "tax_rate_part": f"//td[contains(@class, 'widthPrice') and contains(text(), '{self.price}円')]/following-sibling::td[@class='widthTax taRight']",
            "go_back_part": "//a[@aria-label='購入履歴']"
        }

        super().__init__(chrome, self.config, debug_mode=debug_mode)

    def start_move(self):
        self.operation()

    def process(self):
        self.operation_process()


# ２----------------------------------------------------------------------------------