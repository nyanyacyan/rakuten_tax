# coding: utf-8
# ----------------------------------------------------------------------------------
# 非同期処理 自動ログインクラス
# headlessモード、reCAPTCHA回避
# 2023/3/8制作

#! webdriverをどこが開いているのかを確認しながら実装が必要。
# ----------------------------------------------------------------------------------


import asyncio
import functools
import os
import pickle
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

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

# スクショ用のタイムスタンプ
timestamp = datetime.now().strftime("%m-%d_%H-%M")

# ----------------------------------------------------------------------------------


class NoCookieLogin:
    '''一連の流れをここにいれる'''
    def __init__(self, chrome, config, debug_mode=False):
        '''config_xpathにパスを集約させて子クラスで引き渡す'''

        self.chrome = chrome

        # xpath全体で使えるように初期化
        self.site_name = config["site_name"]
        self.userid = config["userid"]
        self.password = config["password"]
        self.userid_xpath = config["userid_xpath"]
        self.password_xpath = config["password_xpath"]
        self.login_button_xpath = config["login_button_xpath"]
        self.login_checkbox_xpath = config["login_checkbox_xpath"]
        self.user_element_xpath = config["user_element_xpath"]
        self.buy_history = config["buy_history"]

        self.logger = self.setup_logger(debug_mode=debug_mode)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------


    # IDとパスを入力
    def id_pass_input(self):
        try:
            userid_field = self.chrome.find_element_by_xpath(self.userid_xpath)
            userid_field.send_keys(self.userid)
            self.logger.debug(f"{self.site_name} ID入力完了")

            time.sleep(1)

            password_field = self.chrome.find_element_by_xpath(self.password_xpath)
            password_field.send_keys(self.password)
            self.logger.debug(f"{self.site_name} パスワード入力完了")

        except NoSuchElementException as e:
            print(f"要素が見つからない: {e}")


        # ページが完全に読み込まれるまで待機
        WebDriverWait(self.chrome, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        self.logger.debug("ページは完全に表示されてる")


        WebDriverWait(self.chrome, 10).until(
            EC.visibility_of_element_located((By.XPATH, self.login_button_xpath))
        )
        self.logger.debug(f"{self.site_name} ボタンDOMの読み込みは完了してる")

        time.sleep(1)


# ----------------------------------------------------------------------------------


    def login_checkbox(self):
        '''チェックボックスにチェックいれる'''
        # ログインを維持するチェックボックスを探す
        try:
            login_checkbox = self.chrome.find_element_by_xpath(self.login_checkbox_xpath)
            self.logger.debug(f"{self.site_name} チェックボタンが見つかりました。")

        except ElementNotInteractableException as e:
            self.logger.error(f"{self.site_name} チェックボックスが見つかりません。{e}")

        except InvalidSelectorException:
            self.logger.debug(f"{self.site_name} チェックボックスないためスキップ")

        try:
            if login_checkbox:
            # remember_boxをクリックする
                login_checkbox.click()
            self.logger.debug(f"{self.site_name} チェックボタンをクリック")

        except UnboundLocalError:
            self.logger.debug(f"{self.site_name} チェックボタンなし")

        time.sleep(1)


# ----------------------------------------------------------------------------------


    def recaptcha_sleep(self):
        '''reCAPTCHA検知してある場合は2CAPTCHAメソッドを実行'''
        try:
            # 現在のURL
            current_url = self.chrome.current_url
            self.logger.debug(current_url)
            # sitekeyを検索
            elements = self.chrome.find_elements_by_css_selector('[data-sitekey]')
            if len(elements) > 0:
                self.logger.info(f"{self.site_name} reCAPTCHA発見したため手動にて入力")
                time.sleep(120)

            # 通知いれるか検討

            # reCAPTCHAなし
            else:
                self.logger.info(f"reCAPTCHAなし")

        except Exception as e:
            self.logger.error(f"reCAPTCHA処理中にエラーが発生しました: {e}")


# ----------------------------------------------------------------------------------


    def login_btnPush(self):
        try:
            #  login_btnPush を探して押す
            self.logger.debug(" login_btnPush を特定開始")
            buy_history_btn = self.chrome.find_element_by_xpath(self.login_button_xpath)
            self.logger.debug(" login_btnPush を発見")

        except NoSuchElementException as e:
            self.logger.error(f" login_btnPush が見つかりません:{e}")

        buy_history_btn.click()

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
# すべてのメソッドを集めて、カプセル化


    def login(self):
        '''ログインしてCookieを取得する。'''

        self.logger.debug(f"{__name__}: 処理開始")

        self.id_pass_input()
        self.login_checkbox()
        self.recaptcha_sleep()
        self.login_btnPush()
        self.buy_history_btnPush()

        self.logger.debug(f"{__name__}: 処理完了")

        # self.chrome.quit()  # 最終、閉じる


# ----------------------------------------------------------------------------------