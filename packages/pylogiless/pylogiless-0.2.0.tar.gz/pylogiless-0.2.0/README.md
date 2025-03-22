# pylogiless

LOGILESS APIのPythonクライアントライブラリ。在庫管理や物流管理のためのAPIを簡単に利用できるようにします。

## 機能

- 実在庫サマリAPI
  - 商品の実際の在庫状況の取得
  - 倉庫やロケーションごとの在庫情報の取得
- 論理在庫サマリAPI
  - 商品の論理的な在庫状況の取得
  - 在庫切れや再発注レベルの情報の取得
- 商品一覧API
  - 商品の基本情報の取得
  - 商品タイプ、税表示、温度管理などの設定情報の取得

## インストール

```bash
pip install pylogiless
```

## 必要条件

- Python 3.7以上
- requests >= 2.31.0
- python-dotenv >= 1.0.0

## 使用方法

### 環境変数の設定

1. `.env.example`ファイルを`.env`にコピーします：
```bash
cp .env.example .env
```

2. `.env`ファイルを編集し、実際の認証情報を設定します：
```
LOGILESS_ACCESS_TOKEN=your_access_token_here
LOGILESS_MERCHANT_ID=your_merchant_id_here
```

### サンプルコード

```python
from pylogiless import LogilessClient
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# クライアントの初期化
client = LogilessClient(
    access_token=os.getenv("LOGILESS_ACCESS_TOKEN"),
    merchant_id=os.getenv("LOGILESS_MERCHANT_ID")
)

# 実在庫サマリの取得
actual_inventory = client.actual_inventory_summary.list()
print(f"実在庫サマリ: {actual_inventory}")

# 論理在庫サマリの取得
logical_inventory = client.logical_inventory_summary.list()
print(f"論理在庫サマリ: {logical_inventory}")

# 商品一覧の取得
articles = client.article.list()
print(f"商品一覧: {articles}")
```

### エラーハンドリング

```python
try:
    # APIリクエスト
    inventory = client.actual_inventory_summary.list()
except Exception as e:
    print(f"エラーが発生しました: {str(e)}")
```

## 開発環境のセットアップ

1. リポジトリのクローン：
```bash
git clone https://github.com/logiless/pylogiless.git
cd pylogiless
```

2. 仮想環境の作成と有効化：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
.\venv\Scripts\activate  # Windows
```

3. 依存パッケージのインストール：
```bash
pip install -e .
```

## テスト

```bash
python -m pytest tests/
```

## 貢献

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

MIT License

## サポート

- バグ報告や機能要望は[GitHub Issues](https://github.com/logiless/pylogiless/issues)にお願いします
- ドキュメントは[GitHub Wiki](https://github.com/logiless/pylogiless/wiki)で確認できます

## 作者

LOGILESS API Python Client Contributors 