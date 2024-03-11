# coding: utf-8
# ----------------------------------------------------------------------------------
# recaptcha回避　クラス
# 2023/1/20制作
# 2023/3/8修正
# 仮想環境 / source autologin-v1/bin/activate

# ----------------------------------------------------------------------------------
import sys, os, requests
from selenium.common.exceptions import NoSuchElementException

from dotenv import load_dotenv

# 自作モジュール
from logger.debug_logger import Logger

load_dotenv()

class RecaptchaBreakthrough:
    def __init__(self, chrome_driver, debug_mode=False):
        # Loggerクラスを初期化
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        self.logger_instance = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.logger_instance.get_logger()
        self.debug_mode = debug_mode


        load_dotenv()
        self.chrome = chrome_driver

        # APIKeyなどを.envから取得
        self.rapid_url = os.getenv('RAPID_URL')
        self.rapid_api = os.getenv('RAPID_API')
        self.rapid_api_host = os.getenv('RAPID_API_HOST')


# ----------------------------------------------------------------------------------


    def solve_whirl_captcha(self, url1, url2, cap_type="whirl"):
        api_url = self.rapid_url
        payload = {
            "cap_type": cap_type,
            "url1": url1,
            "url2": url2
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": self.rapid_api,
            "X-RapidAPI-Host": self.rapid_api_host
        }

        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            x1_value = response_json["captcha_solution"]["x1"]
            print(x1_value)
        else:
            self.logger.debug("Error:", response.status_code)

        # この数値をtransformに入力する
        return x1_value




# ----------------------------------------------------------------------------------


    def solve_3d_captcha(self, image_base64, cap_type="3d"):
        api_url = self.rapid_url
        payload = {
            "cap_type": cap_type,
            "image_base64": image_base64
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": self.rapid_api,
            "X-RapidAPI-Host": self.rapid_api_host
        }

        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            x1_value = response_json["captcha_solution"]["x1"]
            print(x1_value)
        else:
            self.logger.debug("Error:", response.status_code)

        return x1_value

        #! ３ｄの箇所を指定するためのもの
        # # WebDriverを初期化
        # driver = webdriver.Chrome()  # ChromeDriverを使用する場合

        # # 対象のWebページを開く
        # driver.get("https://example.com")

        # # 画像要素を見つける（適切なロケーター方法を使用）
        # image = driver.find_element_by_xpath("//img[@alt='target_image']")

        # # クリックする座標を計算
        # x1, y1 = 281, 40
        # x2, y2 = 98, 177
        # click_x = (x1 + x2) // 2
        # click_y = (y1 + y2) // 2

        # # アクションチェーンを使用して座標をクリック
        # actions = ActionChains(driver)
        # actions.move_to_element_with_offset(image, click_x, click_y).click().perform()

        # # WebDriverを閉じる
        # driver.quit()


# ----------------------------------------------------------------------------------

    def recaptchaIfNeeded(self, current_url):
        try:
            self.logger.debug("display:noneを削除開始")

            # display:noneを[""](空欄)に書き換え
            #! この部分のIDを書き換え必要
            self.chrome.execute_script('var element=document.getElementById("この部分を書き換え必要"); element.style.display="";')

            # 現在のdisplayプロパティ内の値を抽出
            #! この部分のIDを書き換え必要
            style = self.chrome.execute_script('return document.getElementById("g-recaptcha-response").style.display')

            self.logger.debug(style)

            if style == "":
                self.logger.debug("display:noneの削除に成功しました")
            else:
                raise Exception("display:noneの削除に失敗しました")

        except NoSuchElementException as e:
            print(f"要素が見つからない: {e}")

        except Exception as e:
            self.logger.error(f"display:noneの削除に失敗しましたので確認が必要です:{e}")
            sys.exit(1)


        # data-sitekeyを検索
        recaptcha_element = self.chrome.find_element_by_css_selector('[data-sitekey]')

        # sitekeyの値を抽出
        data_sitekey_value = recaptcha_element.get_attribute('data-sitekey')

        self.logger.debug(f"data_sitekey_value: {data_sitekey_value}")
        self.logger.debug(f"current_url: {current_url}")

        self.logger.info("solve_captcha開始")

        result = self.checkKey(
            data_sitekey_value,
            current_url
        )

        try:
            # レスポンスがあった中のトークン部分を抽出
            code = result['code']

        except Exception as e:
            self.logger.error(f"エラーが発生しました: {e}")


        try:
            # トークンをtextareaに入力
            textarea = self.chrome.find_element_by_id('g-recaptcha-response')
            self.chrome.execute_script(f'arguments[0].value = "{code}";', textarea)

            # textareaの値を取得
            textarea_value = self.chrome.execute_script('return document.getElementById("g-recaptcha-response").value;')

            if code == textarea_value:
                self.logger.debug("textareaにトークン入力完了")

        except Exception as e:
            self.logger.error(f"トークンの入力に失敗: {e}")
