# 技術コンテキスト: sgmap

## 使用技術

### プログラミング言語

- **Python 3.6+**: 主要な開発言語
  - 理由: クロスプラットフォーム対応、AWS SDK の充実、豊富なライブラリ

### 主要ライブラリ

- **boto3**: AWS SDK for Python

  - バージョン: 1.20.0 以上
  - 用途: AWS API との通信、セキュリティグループ情報の取得
  - ドキュメント: [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

- **click**: Python コマンドラインインターフェースフレームワーク
  - バージョン: 8.0.0 以上
  - 用途: コマンドラインオプションの定義と処理
  - ドキュメント: [Click Documentation](https://click.palletsprojects.com/)

### 出力形式

- **mermaid**: フローチャート記法

  - 用途: セキュリティグループの接続関係を視覚的に表現
  - ドキュメント: [Mermaid Documentation](https://mermaid-js.github.io/mermaid/#/)

- **JSON**: 構造化データ形式
  - 用途: プログラムによる処理や他のツールとの連携

## 開発環境のセットアップ

### 必要条件

- Python 3.6 以上
- pip（Python パッケージマネージャー）
- AWS 認証情報の設定

### 開発環境のセットアップ手順

1. リポジトリのクローン:

   ```bash
   git clone https://github.com/youyo/sgmap.git
   cd sgmap
   ```

2. 仮想環境の作成と有効化:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linuxの場合
   # または
   venv\Scripts\activate  # Windowsの場合
   ```

3. 依存関係のインストール:

   ```bash
   pip install -r requirements.txt
   ```

4. 開発モードでのインストール:

   ```bash
   pip install -e .
   ```

5. AWS 認証情報の設定:
   ```bash
   # ~/.aws/credentials に認証情報を設定
   # または
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=your_region
   ```

## 技術的制約

### AWS API 制限

- AWS API には、リクエスト数やレート制限があります。大規模な VPC や多数のセキュリティグループがある場合、API の制限に達する可能性があります。

### AWS 認証

- ツールを使用するには、適切な AWS 認証情報と権限が必要です。最低限、以下の権限が必要です：
  - `ec2:DescribeSecurityGroups`
  - `ec2:DescribeVpcs`

### クロスアカウント分析

- 現在のバージョンでは、単一の AWS アカウント内のセキュリティグループのみを分析できます。クロスアカウント分析には、追加の認証と権限設定が必要になります。

### 出力サイズ

- 大規模な VPC や多数のセキュリティグループがある場合、mermaid 記法の出力が複雑になり、可読性が低下する可能性があります。

## 依存関係

### 直接的な依存関係

- boto3: AWS SDK for Python
- click: コマンドラインインターフェースフレームワーク

### 間接的な依存関係

- botocore: boto3 の基盤となるライブラリ
- six: Python 2 と 3 の互換性ライブラリ
- python-dateutil: 日付操作ライブラリ
- jmespath: JSON クエリ言語

## デプロイと配布

### パッケージング

- setuptools: Python パッケージングツール
- wheel: バイナリパッケージ形式

### 配布方法

- PyPI（Python Package Index）を通じた配布
- GitHub リリースを通じたソースコード配布

## テスト戦略

### ユニットテスト

- unittest: Python の標準テストフレームワーク
- pytest: より高度なテストフレームワーク（推奨）

### モック

- unittest.mock: AWS API のモック
- moto: AWS API のモックライブラリ

### テストカバレッジ

- coverage: コードカバレッジ測定ツール
- 目標カバレッジ: 80%以上
