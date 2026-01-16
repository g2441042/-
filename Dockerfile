# ベースイメージ（Python 3.9）
FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なファイルをコンテナ内にコピー
COPY requirements.txt .
COPY app.py .
COPY schema.sql .
# (.envはセキュリティのためコピーしないのが一般的ですが、課題用ならコピーしてもOK)

# ライブラリのインストール
# ※PostgreSQLに接続するために必要なシステムライブラリも追加
RUN apt-get update && apt-get install -y libpq-dev gcc && \
    pip install --no-cache-dir -r requirements.txt

# アプリの起動（外部からアクセスできるように 0.0.0.0 で待機）
CMD ["flask", "run", "--host=0.0.0.0"]
