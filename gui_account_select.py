# coding: utf-8
# ----------------------------------------------------------------------------------
#? GUIクラス
# ----------------------------------------------------------------------------------
import tkinter as tk
from tkinter import filedialog, ttk
from dotenv import load_dotenv
import os
import pandas as pd

# 自作モジュール
from logger.debug_logger import Logger
from add_csv.add_order_numbers import AddOrderNumbers
from main import Main

# ----------------------------------------------------------------------------------


class App:
    def __init__(self, root, debug_mode=False):
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.root = root

        root.title("消費税率 追加アプリ")
        root.geometry("400x350")
        root.configure(bg='#f0f0f0')

        # ウィンドウの列の設定
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)
        root.columnconfigure(3, weight=1)
        root.columnconfigure(4, weight=1)

        self.accounts_var = tk.StringVar()
        self.account_options = ['User-1', 'User-2', 'User-3']
        self.account_dropdown = ttk.Combobox(root, textvariable=self.accounts_var, values=self.account_options, state='readonly')
        self.account_dropdown.grid(row=0, column=1, columnspan=2, padx=20, pady=20, sticky="ew")  # 中央の列に配置

        self.file_select_btn = ttk.Button(root, text="CSVファイル選択", command=self.select_csv_file)
        self.file_select_btn.grid(row=1, column=1, columnspan=2, padx=20, pady=20, sticky="ew")

        self.file_select_btn = ttk.Button(root, text="SHIFT-JISに変換", command=self.encoding_change)
        self.file_select_btn.grid(row=2, column=1, columnspan=2, padx=20, pady=20, sticky="ew")

        self.process_btn = ttk.Button(root, text="処理スタート", command=self.submit)
        self.process_btn.grid(row=3, column=1, padx=20, pady=20, sticky="ew")

        self.cancel_btn = ttk.Button(root, text="キャンセル", command=root.quit)
        self.cancel_btn.grid(row=3, column=2, padx=20, pady=20, sticky="ew")

        self.message_box = tk.Text(root, height=2,state='disabled', bg='#f0f0f0', bd=0, highlightthickness=0)
        self.message_box.grid(row=4, column=1, columnspan=2, padx=20, pady=20, sticky="ew")


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------


    def update_message_box(self, message):
        # Textウィジェットの状態を変更してメッセージを追加
        self.message_box.configure(state='normal')  # 書き込み可能に変更
        self.message_box.insert(tk.END, message)  # メッセージを追加
        self.message_box.configure(state='disabled')  # 書き込み禁止に戻す
        self.message_box.see(tk.END)  # スクロールして最新のメッセージを表示


# ----------------------------------------------------------------------------------
# CSVファイルの選択

    def select_csv_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.logger.debug(f" file_pathは : {file_path}")

        # インスタンス化
        self.add_order_number = AddOrderNumbers(file_path)

        self.add_order_number.price_fixed()
        self.logger.debug("CSVファイル修正、完了")

        return print("CSVファイル選択完了")


# ----------------------------------------------------------------------------------
# エンコードの変換

    def encoding_change(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.logger.debug(f" file_pathは : {file_path}")
        if file_path:
            df = pd.read_csv(file_path, encoding='utf-8')

            dir_name, original_file_name = os.path.split(file_path)

            base_name = os.path.splitext(original_file_name)[0]

            new_file_name = f"{base_name}(変更済).csv"

            new_file_path = os.path.join(dir_name, new_file_name)

            # encodingを「SHIFT_JIS」へ変更
            df.to_csv(new_file_path, encoding='shift_jis', index=False)

            print(f"「SHIFT_JIS」への変更が 完了しました: {new_file_path} ")

        else:
            print("ファイルが選択されませんでした。")


# ----------------------------------------------------------------------------------


    def submit(self):
        selected_account = self.accounts_var.get()
        selected_env_file = f"{selected_account}.env"
        load_dotenv(selected_env_file)

        login_url = os.getenv("RAKUTEN_LOGIN_URL")
        user_id = os.getenv("LOGIN_ID")
        password = os.getenv("LOGIN_PASS")


        # インスタンス作成
        # main
        self.main = Main(login_url, user_id, password)

        self.main.main()


# ----------------------------------------------------------------------------------


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()