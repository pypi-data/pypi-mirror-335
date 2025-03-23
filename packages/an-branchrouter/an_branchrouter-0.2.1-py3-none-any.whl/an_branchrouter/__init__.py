# __init__.py

# branchrouter.py からクラスや関数をインポート
from .branchrouter import BranchRouter  # 相対インポート

# __all__ を使用して公開するクラスや関数を制限
__all__ = ["BranchRouter"]
