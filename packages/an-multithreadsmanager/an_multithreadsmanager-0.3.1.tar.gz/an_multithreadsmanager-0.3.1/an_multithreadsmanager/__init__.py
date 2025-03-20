# __init__.py

# multithreadsmanager.py からクラスや関数をインポート
from .multithreadsmanager import MultiThreadsManager  # 相対インポート

# __all__ を使用して公開するクラスや関数を制限
__all__ = ["MultiThreadsManager"]
