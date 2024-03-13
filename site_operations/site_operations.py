# coding: utf-8
# ----------------------------------------------------------------------------------
# サイトを操作して出品まで実装クラス
# headlessモード、reCAPTCHA回避
# 2023/3/9 制作
# ----------------------------------------------------------------------------------
import asyncio
import functools
import os
import pickle
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import (ElementNotInteractableException,
                                        InvalidSelectorException,
                                        NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# 自作モジュール
from logger.debug_logger import Logger

load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)

# スクショ用のタイムスタンプ
timestamp = datetime.now().strftime("%m-%d_%H-%M")


# ----------------------------------------------------------------------------------


class SiteOperations:
    '''Cookie利用してログインして処理を実行するクラス'''
    def __init__(self, chrome, config, debug_mode=False):
        '''config_xpathにパスを集約させて子クラスで引き渡す'''
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.chrome = chrome

        # メソッド全体で使えるように定義（デバッグで使用）
        self.site_name = config["site_name"]

        #* 利用してるものconfig
        self.cookies_file_name = config["cookies_file_name"]
        self.main_url = config["main_url"]
        self.buy_history = config["buy_history"]
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
# 購入履歴を見つけて押す

    def buy_history_btnPush(self):
        try:
            current_url = self.chrome.current_url
            self.logger.info(f"URL: {current_url}")


            # 購入履歴を探して押す
            self.logger.debug("購入履歴を特定開始")
            buy_history_btn = self.chrome.find_element_by_xpath(self.buy_history)
            self.logger.debug("購入履歴を発見")

            buy_history_btn.click()

        except NoSuchElementException as e:
            self.logger.error(f"購入履歴が見つかりません:{e}")


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
        try:
            # 購入履歴を探して押す
            self.logger.debug("注文詳細を表示 を特定開始")
            history_detail_btn = self.chrome.find_element_by_xpath(self.history_detail)
            self.logger.debug("注文詳細を表示 を発見")

            history_detail_btn.click()

        except NoSuchElementException as e:
            self.logger.error(f"注文詳細を表示 が見つかりません:{e}")

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
# tax_rate_part 部分へ移動のみ

    def start_line(self):
        try:
            # 購入履歴を探して押す
            self.logger.debug(" start_line へ移動開始")
            tax_rate_part = self.chrome.find_element_by_xpath(self.tax_rate_part)
            self.logger.debug(" start_line への移動完了")

        except NoSuchElementException as e:
            self.logger.error(f" tax_rate_part が見つかりません:{e}")

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
# 消費税を取得

    def tax_rate(self):
        try:
            # 購入履歴を探して押す
            self.logger.debug(" tax_rate_part を特定開始")
            tax_rate_part = self.chrome.find_element_by_xpath(self.tax_rate_part)
            self.logger.debug(" tax_rate_part を発見")

        except NoSuchElementException as e:
            self.logger.error(f" tax_rate_part が見つかりません:{e}")

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

        time.sleep(1)

        self.logger.debug(tax_rate_part.get_attribute('class'))
        tax_rate_text = tax_rate_part.text
        self.logger.debug(tax_rate_text)
        return tax_rate_text


# ----------------------------------------------------------------------------------
# 購入履歴を見つけて押す（一個）戻る

    def go_back(self):
        try:
            # 購入履歴を探して押す
            self.logger.debug(" 購入履歴(戻る) を特定開始")
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
# 処理するまで進むためのメソッド（カプセル化）

    def operation(self):
        self.logger.debug(f"{__name__}: 処理開始")

        self.buy_history_btnPush()
        self.history_detail_btnPush()
        self.start_line()

        self.logger.debug(f"{__name__}: 処理完了")


# ----------------------------------------------------------------------------------
# 繰り返し処理する部分（カプセル化）

    def operation_process(self):
        self.logger.debug(f"{__name__} process: 処理開始")

        self.go_back()
        self.history_detail_btnPush()
        self.tax_rate()

        self.logger.debug(f"{__name__} process: 処理完了")


# ----------------------------------------------------------------------------------