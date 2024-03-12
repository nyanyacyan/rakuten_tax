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


class Rakuten(SiteOperations):
    def __init__(self, order_number, price, debug_mode=False):
        # 親クラスにて定義した引数をここで引き渡す
        # configの内容をここで全て定義
        self.order_number = order_number
        self.price = price

        self.config_xpath = {
            "site_name": "rakuten",
            "main_url": os.getenv('RAKUTEN_MAIN_URL'),
            "cookies_file_name": "rakuten_cookie_file.pkl",
            "buy_history" : "//a[@aria-label='購入履歴']",
            "history_detail" : f"//li[contains(., '{self.order_number}')]/following-sibling::li[contains(@class, 'oDrDetailList')]/a",
            "tax_rate_part": f"//td[contains(@class, 'widthPrice') and contains(text(), '{self.price}円')]/following-sibling::td[@class='widthTax taRight']"
        }

        super().__init__(self.config_xpath, debug_mode=debug_mode)

    # getOrElseは実行を試み、失敗した場合は引数で指定した値を返す
    async def getOrElse(self):
        # 継承してるクラスのメソッドを非同期処理して実行
        # initにて初期化済みのためconfig_xpathを渡すだけでOK
        await self.site_operation_async()


# ２----------------------------------------------------------------------------------