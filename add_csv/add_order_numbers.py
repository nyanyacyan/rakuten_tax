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

        try:
            self.df = pd.read_csv(self.read_csv_data, encoding='SHIFT_JIS')
        except FileNotFoundError:
            self.logger.error(f"ファイルが見つかりません: {self.read_csv_data}")
        except pd.errors.UnicodeDecodeError:
            self.logger.error(f"ファイルの種類が違います（'SHIFT_JIS'にする必要があります）: {self.read_csv_data}")
        except Exception as e:
            self.logger.error(f"ファイル読み込み中に予期せぬエラーが発生しました: {e}")

# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# 注文番号をすべて埋める

    def add_order_number(self):

        # 空白の場所を定義する箱
        first_blank_index = None

        # 箱がない場合に１行ごとに確認する
        for i in range(len(self.df)):

            # 現在の行が空白であり、まだ最初の空白行を記録してない場合
            if pd.isnull(self.df.loc[i, '注文番号']) and first_blank_index is None:
                first_blank_index = i

            # 注文番号が見つかった場合、かつ以前に空白の行が記載されている場合
            elif pd.notnull(self.df.loc[i, '注文番号']) and first_blank_index is not None:

                # 空白ではない部分=注文番号
                order_number = self.df.loc[i, '注文番号']

                # 記録したさいしょの空白の行から現在の行までを見つかった注文番号で更新
                # [first_blank_index:i-1, 'P']first_blank_index（記憶された空白のindex）から注文番号が見つかった直前の数字のPの行という意味
                #* first_blank_index（記憶された空白のindex）から注文番号が見つかった直前の数字のPの行すべてを「order_number」に置換
                self.df.loc[first_blank_index:i-1, '注文番号'] = order_number

                # 置換したらリセットしての注文番号に備える
                first_blank_index = None

        self.df.to_csv('data/csv_fixed.csv', index=False)
        self.logger.debug('注文番号、書き込み完了')


# ----------------------------------------------------------------------------------
# 価格をコンマがあるフォーマットに変更

    def price_fixed(self):
        pd.read_csv('data/csv_fixed.csv', encoding='utf-8')
        self.logger.debug('価格のフォーマット変更 開始')
        self.df['単価(税込)'] = self.df['単価(税込)'].apply(lambda x: "{:,}".format(x))
        self.logger.debug(f"df['単価(税込)'] :{self.df['単価(税込)']}")
        self.logger.debug('価格のフォーマット変更 終了')

        self.df.to_csv('data/csv_fixed.csv', index=False)
        self.logger.debug('注文番号、書き込み完了')


# ----------------------------------------------------------------------------------