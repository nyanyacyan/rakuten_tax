# coding: utf-8
# ----------------------------------------------------------------------------------
# 既存csvに注文番号を入れ込むクラス
# 2023/3/12制作

# ----------------------------------------------------------------------------------
import os
import pandas as pd

# 自作モジュール
from logger.debug_logger import Logger

class AddOrderNumbers:
    def __init__(self, read_csv_data):
        self.logger = self.setup_logger()
        self.read_csv_data = read_csv_data


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------


    def add_order_number(self):
        # 一番最初の空白を見つける

        # データを読み込む
        df = pd.read_csv(self.read_csv_data)

        # 空白の場所を定義する箱
        first_blank_index = None

        # 箱がない場合に１行ごとに確認する
        for i in range(len(df)):

            # 現在の行が空白であり、まだ最初の空白行を記録してない場合
            if pd.isnull(df.loc[i, 'P']) and first_blank_index is None:
                first_blank_index = i

            # 注文番号が見つかった場合、かつ以前に空白の行が記載されている場合
            elif pd.notnull(df.loc[i, 'P']) and first_blank_index is not None:

                # 空白ではない部分=注文番号
                order_number = df.loc[i, 'P']

                # 記録したさいしょの空白の行から現在の行までを見つかった注文番号で更新
                # [first_blank_index:i-1, 'P']first_blank_index（記憶された空白のindex）から注文番号が見つかった直前の数字のPの行という意味
                #* first_blank_index（記憶された空白のindex）から注文番号が見つかった直前の数字のPの行すべてを「order_number」に置換
                df.loc[first_blank_index:i-1, 'P'] = order_number

                # 置換したらリセットしての注文番号に備える
                first_blank_index = None

        df.to_csv('data/add_order_number.csv', index=False)


# ----------------------------------------------------------------------------------