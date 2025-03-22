# __init__.py

# debughelper.py からクラスや関数をインポート
from .debughelper import DebugHelper  # 相対インポート

# __all__ を使用して公開するクラスや関数を制限
__all__ = ["DebugHelper"]
