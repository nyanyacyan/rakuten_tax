# coding: utf-8
# ----------------------------------------------------------------------------------
# 子クラス
# 2023/3/14制作

# ----------------------------------------------------------------------------------


import os

from dotenv import load_dotenv

# 自作モジュール
from site_operations.add_tax import AddTax

load_dotenv()  # .env ファイルから環境変数を読み込む


# 1----------------------------------------------------------------------------------


class RakutenAddTax(AddTax):
    def __init__(self, chrome, order_number, price, debug_mode=False):
        # 親クラスにて定義した引数をここで引き渡す
        # configの内容をここで全て定義
        self.order_number = order_number
        self.price = price

        self.config = {
            "site_name": "rakuten",
            "go_back_part": "//a[@aria-label='購入履歴']",
            "history_detail" : f"//span[@class='idNum' and contains(text(), '{self.order_number}')]/ancestor::li[contains(@class, 'orderID')]/following-sibling::li[contains(@class, 'oDrDetailList')]/a/img[contains(@class, 'listPageIcon')]",
            # "history_detail" : f"//li[contains(., '{self.order_number}')]/following-sibling::li[contains(@class, 'oDrDetailList')]/a",
            "tax_rate_part": f"//td[contains(@class, 'widthPrice') and contains(text(), '{self.price}円')]/following-sibling::td[@class='widthTax taRight']",
        }

        super().__init__(self.config, chrome, debug_mode=debug_mode)

    def process(self):
        tax_rate_value = self.operation_process()
        return tax_rate_value
