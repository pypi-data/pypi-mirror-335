# an_DebugHelper

an_DebugHelper は、Python スクリプトのデバッグを簡単に行うための便利なツールです。  
ログ出力、エラーハンドリング、デバッグメッセージの管理を容易にする機能を提供します。

## 🚀 特徴

- **簡単なログ管理**: 標準出力、ファイル出力の両方に対応
- **エラーハンドリング**: スクリプトのエラーメッセージを分かりやすく記録
- **デバッグメッセージの統一管理**: コードの流れを追いやすくする設計

## 📦 インストール

PyPI からインストール:

```bash
pip install an_debughelper

または、GitHub から直接インストール:

pip install git+https://github.com/Atsushi888/an_DebugHelper.git

📌 使い方

基本的なデバッグメッセージの出力

from an_debughelper import DebugHelper

debug = DebugHelper()

debug.log_step("処理開始", success=None)
debug.log_step("ファイルを読み込み中...", char="📂")
debug.log_step("エラーが発生しました！", success=False)
debug.log_step("処理完了", success=True)

出力結果:

[DebugHelper] 🔹 処理開始
[DebugHelper] 📂 ファイルを読み込み中...
[DebugHelper] ❌ エラーが発生しました！
[DebugHelper] ✅ 処理完了

例外処理との統合

try:
    result = 10 / 0  # ゼロ除算エラー
except Exception as e:
    debug.log_step(f"エラー発生: {e}", success=False)

🛠 開発者向け情報

環境変数を利用する場合

import os
from dotenv import load_dotenv

load_dotenv()

DEBUG_MODE = os.getenv("DEBUG_MODE", "False")  # デフォルトは False

📜 ライセンス

このプロジェクトは MIT ライセンス のもとで提供されます。詳細は LICENSE を参照してください。

📞 お問い合わせ

バグ報告・機能リクエストは GitHub の Issues にて受け付けています。
ご質問があれば、Atsushi888 までお問い合わせください。

---

## **使い方**
- `LICENSE` を `an_DebugHelper/` ディレクトリに配置
- `README.md` を `an_DebugHelper/` ディレクトリに配置

この `README.md` は、GitHub リポジトリと PyPI のパッケージページの両方で表示されるようになります。  
特に **PyPI のフォーマット** では `long_description_content_type="text/markdown"` を設定する必要がありますので、`pyproject.toml` にこの設定を追加してください。

もし内容を修正したい点があれば教えてください！