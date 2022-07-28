import itertools
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Any

# 関数を引数に取るクラス
class Spinner:
    def __init__(self,func) -> None:
        self.done = False # funcが実行終了するとTrueになる
        self.func = func  # 目的の関数

    # ぐるぐるをコンソールに表示するメソッド
    def spinner(self):
        # 無限に繰り返すイテレータ
        chars = itertools.cycle(r'/-\|')

        while not self.done:
        # ぐるぐるを表示
            sys.stdout.write( '\b' + next(chars))
            sys.stdout.flush()
            # 待機
            time.sleep(0.1)

        # ぐるぐるを削除
        sys.stdout.write('\b')
        sys.stdout.flush()

    # インスタンスを実行できるようにする特殊メソッド
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.run(*args, **kwds)

    # ぐるぐると目的の関数を並列処理するメソッド
    def run(self, *args: Any, **kwds: Any) -> Any:
        # ThreadPoolExecutor(2): 最大二つの処理を並行処理してくれるスレッドプール
        with ThreadPoolExecutor(2) as executor:
            # ぐるぐるメソッドをスレッドプールに登録
            executor.submit(self.spinner)
            # 目的の関数をスレッドプールに登録
            # 戻り値が欲しいのでFutureインスタンスを変数に格納
            future = executor.submit(self.func, *args, **kwds)

            # 実行結果を得る
            result = future.result()
            self.done = True
        return result