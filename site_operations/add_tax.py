# coding: utf-8
# ----------------------------------------------------------------------------------
# 修正されたcsvファイルから情報を取得して処理を加えてCSVファイルに書き込むクラス
# 2023/3/14制作

# ----------------------------------------------------------------------------------
import pandas as pd

import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# 自作モジュール
from logger.debug_logger import Logger

load_dotenv()


# ----------------------------------------------------------------------------------
# クラスにて使うものを初期化

class AddTax:
    def __init__(self, config, chrome, debug_mode=False):
        self.df = pd.read_csv('data/csv_fixed.csv', encoding='utf-8')
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.chrome = chrome

        # メソッド全体で使えるように定義（デバッグで使用）
        self.site_name = config["site_name"]
        self.history_detail = config["history_detail"]
        self.tax_rate_part = config["tax_rate_part"]
        self.go_back_part = config["go_back_part"]



# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# 購入履歴を見つけて押す（一個）戻る

    def go_back(self):
        try:
            # 購入履歴を探して押す
            self.logger.debug(f"{self.site_name} 購入履歴(戻る) を特定開始")
            go_back_btn = self.chrome.find_element_by_xpath(self.go_back_part)
            self.logger.debug(" 購入履歴(戻る) を発見")

            go_back_btn.click()

        except NoSuchElementException as e:
            self.logger.error(f" 購入履歴(戻る) が見つかりません:{e}")


        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

        time.sleep(1)


# ----------------------------------------------------------------------------------
# 注文詳細を表示を押す

    def history_detail_btnPush(self):
        while True:
            try:
                # 購入履歴を探して押す
                self.logger.debug("注文詳細を表示 を特定開始")
                history_detail_btn = self.chrome.find_element_by_xpath(self.history_detail)
                self.logger.debug("注文詳細を表示 を発見")

                self.logger.debug("クリック実施")
                history_detail_btn.click()
                self.logger.debug("クリック実施")

                break

            # もしこのページがなかったら次の25件を押して探す
            except NoSuchElementException:
                try:
                    self.logger.debug(" 現在のページでは「注文番号」ないため「次のページ」を捜索 開始")
                    next_page_link = self.chrome.find_element_by_xpath("//a[@data-ratid='ph_pc_pagi_next']")
                    self.logger.debug(" 「次のページ」を捜索 開始")


                    self.logger.debug(" 次のページをクリック 開始")
                    next_page_link.click()
                    self.logger.debug(" 次のページをクリック 完了")

                    time.sleep(1)

                # 次の25件がなくなったら終わり
                except NoSuchElementException:
                    self.logger.debug(" 次のページをクリック がない")
                    break

        self.logger.debug(" 注文番号 が見つかりません")



# ----------------------------------------------------------------------------------
# 消費税を取得

    def tax_rate(self):
        try:
            # 購入履歴を探して押す
            self.logger.debug(" tax_rate_part を特定開始")
            tax_rate_part = self.chrome.find_element_by_xpath(self.tax_rate_part)
            self.logger.debug(" tax_rate_part を発見")

            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

            time.sleep(1)

            tax_rate_text = tax_rate_part.text
            self.logger.debug(tax_rate_text)

            return tax_rate_text

        except NoSuchElementException:
            self.logger.error(" ファイルの入力に誤りがある可能性があります （金額が一致するものがない）")
            return "見つからない"


# ----------------------------------------------------------------------------------
# 検索始める前に必ず最初に戻るようにする

    def reverse(self):
        while True:
            try:
                self.logger.info(" 1つ前の購入履歴のページに戻ります")
                # 次のページへのリンクが存在するかチェック
                next_page_link = self.chrome.find_element_by_xpath("//a[@data-ratid='ph_pc_pagi_previous']")

                # リンクが見つかった場合、そのリンクをクリックして次のページに遷移
                next_page_link.click()

                # ページ遷移後に必要な処理をここで行う
                # 例: 特定の要素の検索やデータの抽出

            except NoSuchElementException:
                # 次のページへのリンクが見つからなかった場合、ループを終了
                self.logger.debug("一番最初の購入履歴のページにいます。")
                break




# ----------------------------------------------------------------------------------
# 繰り返し処理する部分（カプセル化）

    def operation_process(self):
        self.logger.debug(f"{__name__} process: 処理開始")

        self.go_back()
        self.reverse()
        self.history_detail_btnPush()
        tax_rate_value = self.tax_rate()

        self.logger.debug(f"{__name__} process: 処理完了")

        return tax_rate_value


# ----------------------------------------------------------------------------------