# coding: utf-8
# ----------------------------------------------------------------------------------
# ! 非同期処理→ まとめて非同期処理へ変換する
# サイトを操作して出品まで実装クラス
# headlessモード、reCAPTCHA回避
# 2023/3/9 制作
# ----------------------------------------------------------------------------------
import asyncio
import datetime
import functools
import os
import pickle
import time
import requests
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
from auto_login.solve_recaptcha import RecaptchaBreakthrough
from logger.debug_logger import Logger

from file_select.file_select import FileSelect

load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)

# スクショ用のタイムスタンプ
timestamp = datetime.now().strftime("%m-%d_%H-%M")


# ----------------------------------------------------------------------------------


class SiteOperations:
    '''Cookie利用してログインして処理を実行するクラス'''
    def __init__(self, config, debug_mode=False):
        '''config_xpathにパスを集約させて子クラスで引き渡す'''
        # Loggerクラスを初期化
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        self.logger_instance = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.logger_instance.get_logger()
        self.debug_mode = debug_mode

        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # ヘッドレスモードで実行
        chrome_options.add_argument("--window-size=1280,1000")  # ウィンドウサイズの指定

        # ChromeDriverManagerを使用して自動的に適切なChromeDriverをダウンロードし、サービスを設定
        service = Service(ChromeDriverManager().install())

        # WebDriverインスタンスを生成
        self.chrome = webdriver.Chrome(service=service, options=chrome_options)

        # 現在のURLを示すメソッドを定義
        self.current_url = self.chrome.current_url

        # メソッド全体で使えるように定義（デバッグで使用）
        self.site_name = config["site_name"]

        #! 使ってないものは削除する
        # xpath全体で使えるように初期化

        # self.userid = config["userid"]
        # self.password = config["password"]
        # self.userid_xpath = config["userid_xpath"]
        # self.password_xpath = config["password_xpath"]
        # self.login_button_xpath = config["login_button_xpath"]
        # self.login_checkbox_xpath = config["login_checkbox_xpath"]
        # self.user_element_xpath = config["user_element_xpath"]

        #* 利用してるものconfig
        self.cookies_file_name = config["cookies_file_name"]
        self.main_url = config["main_url"]
        self.lister_btn_xpath = config["lister_btn_xpath"]
        self.deploy_btn_xpath = config["deploy_btn_xpath"]

        # SolverRecaptchaクラスを初期化
        self.recaptcha_breakthrough = RecaptchaBreakthrough(self.chrome)
        FileSelect(self.chrome)


# ----------------------------------------------------------------------------------


    def cookie_login(self):
        '''Cookieを使ってログイン'''

        # Cookieファイルを展開
        try:
            cookies = pickle.load(open('auto_login/cookies/' + self.cookies_file_name, 'rb'))

        except FileNotFoundError as e:
            self.logger.error(f"ファイルが見つかりません:{e}")

        except Exception as e:
            self.logger.error(f"処理中にエラーが起きました:{e}")

        self.chrome.get(self.main_url)
        self.logger.info("メイン画面にアクセス")

        # Cookieを設定
        for c in cookies:
            self.chrome.add_cookie(c)

        self.chrome.get(self.main_url)
        self.logger.info("Cookieを使ってメイン画面にアクセス")


        if self.main_url != self.chrome.current_url:
            self.logger.info("Cookieでのログイン成功")

        else:
            self.logger.info("Cookieでのログイン失敗")
            session = requests.Session()

            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

            response = session.get(self.main_url)

            # テキスト化
            res_text = response.text
            self.logger.debug(f"res_text: {res_text}")

            #! 後で修正 テキストが確認できたらログインのできたこと内容をピックアップして「ログインの成功の条件」に追加
            # if "ログイン成功の条件" in res_text:
            #     self.logger.info("requestsによるCookieでのログイン成功")
            # else:
            #     self.logger.info("requestsによるCookieでのログイン失敗")

        try:
            # ログインした後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ログインページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} ログイン処理中にエラーが発生: {e}")

        #TODO スクリーンショット
        self.chrome.save_screenshot('cookie_login_after.png')
        self.logger.debug(f"{self.site_name} ログイン状態のスクショ撮影")

# ----------------------------------------------------------------------------------


    def lister_btnPush(self):
        '''出品ボタンを見つけて押す'''
        try:
            # 出品ボタンを探して押す
            self.logger.debug("出品ボタンを特定開始")
            lister_btn = self.chrome.find_element_by_xpath(self.lister_btn_xpath)
            self.logger.debug("出品ボタンを発見")

        except NoSuchElementException as e:
            self.logger.error(f"出品ボタンが見つかりません:{e}")

        lister_btn.click()

        try:
            # ボタンを押した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 処理中にエラーが発生: {e}")

        #TODO スクリーンショット
        filename = f"DebugScreenshot/lister_page_{timestamp}.png"
        self.chrome.save_screenshot(filename)
        self.logger.debug(f"{self.site_name} 出品ページにスクショ撮影")

        time.sleep(1)


# ----------------------------------------------------------------------------------

#! deployする際に「reCAPTCHAあり」の場合に利用
#TODO 手直し必要

    def recap_deploy(self):
        '''reCAPTCHA検知してある場合は2CAPTCHAメソッドを実行'''
        try:
            # 現在のURL
            current_url = self.chrome.current_url
            self.logger.debug(current_url)
            # sitekeyを検索
            elements = self.chrome.find_elements_by_css_selector('[data-sitekey]')
            if len(elements) > 0:
                self.logger.info(f"{self.site_name} reCAPTCHA処理実施中")


                # solveRecaptchaファイルを実行
                try:
                    self.recaptcha_breakthrough.recaptchaIfNeeded(current_url)
                    self.logger.info(f"{self.site_name} reCAPTCHA処理、完了")

                except Exception as e:
                    self.logger.error(f"{self.site_name} reCAPTCHA処理に失敗しました: {e}")
                    # ログイン失敗をライン通知


                self.logger.debug(f"{self.site_name} クリック開始")

                # deploy_btn 要素を見つける
                deploy_btn = self.chrome.find_element_by_xpath(self.deploy_btn_xpath)

                # ボタンが無効化されているか確認し、無効化されていれば有効にする
                self.chrome.execute_script("document.getElementByXPATH(self.deploy_btn_xpath).disabled = false;")

                # ボタンをクリックする
                deploy_btn.click()

            else:
                self.logger.info(f"{self.site_name} reCAPTCHAなし")

                login_button = self.chrome.find_element_by_xpath(self.login_button_xpath)
                self.logger.debug(f"{self.site_name} ボタン捜索完了")

                deploy_btn.click()
                self.logger.debug(f"{self.site_name} クリック完了")

        # recaptchaなし
        except NoSuchElementException:
            self.logger.info(f"{self.site_name} reCAPTCHAなし")

            login_button = self.chrome.find_element_by_xpath(self.login_button_xpath)
            self.logger.debug(f"{self.site_name} ボタン捜索完了")


            # ログインボタンクリック
            try:
                deploy_btn.click()
                self.logger.debug(f"{self.site_name} クリック完了")

            except ElementNotInteractableException:
                self.chrome.execute_script("arguments[0].click();", login_button)
                self.logger.debug(f"{self.site_name} JavaScriptを使用してクリック実行")

        # ページ読み込み待機
        try:
            # ログインした後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} ログインページ読み込み完了")


        except Exception as e:
            self.logger.error(f"{self.site_name} 2CAPTCHAの処理を実行中にエラーが発生しました: {e}")

        time.sleep(3)



# ----------------------------------------------------------------------------------

#! 「reCAPTCHAなし」でdeploy
    def deploy_btnPush(self):
        '''出品ページにあるすべての入力が完了したあとに押す「出品する」というボタン→ deploy_btn を見つけて押す'''
        try:
            # deploy_btnを探して押す
            self.logger.debug(" deploy_btn を特定開始")
            deploy_btn = self.chrome.find_element_by_xpath(self.deploy_btn_xpath)
            self.logger.debug(" deploy_btn を発見")

        except NoSuchElementException as e:
            self.logger.error(f" deploy_btn が見つかりません:{e}")

        deploy_btn.click()

        try:
            # 実行した後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{self.site_name} 次のページ読み込み完了")

        except Exception as e:
            self.logger.error(f"{self.site_name} 実行処理中にエラーが発生: {e}")

        #TODO スクリーンショット
        filename = f"DebugScreenshot/deploy_btnPush_after_{timestamp}.png"
        self.chrome.save_screenshot(filename)

        time.sleep(1)


# ----------------------------------------------------------------------------------

#TODO メインメソッド
#TODO ここにすべてを集約させる

    def site_operation(self):
        '''メインメソッド'''
        self.logger.debug(f"{__name__}: 処理開始")

        self.cookie_login()
        self.lister_btnPush()

        self.logger.debug(f"{__name__}: 処理完了")

        self.chrome.quit()


# ----------------------------------------------------------------------------------


#TODO メインメソッドを非同期処理に変換
    # 同期メソッドを非同期処理に変換
    async def site_operation_async(self):
        loop = asyncio.get_running_loop()

        # ブロッキング、実行タイミング、並列処理などを適切に行えるように「functools」にてワンクッション置いて実行
        await loop.run_in_executor(None, functools.partial(self.site_operation))