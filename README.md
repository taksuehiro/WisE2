# 請求書AIエージェント デモプロジェクト

LangGraphとFastAPIを使用した請求書処理AIエージェントのデモアプリケーションです。

## 📋 プロジェクト概要

異なる表記形式の請求書（A/B/C）を正規化し、別システムへの入力フォームに1項目ずつ自動入力する「作業してる感」を可視化するデモです。

## 🚀 クイックスタート

### ローカル開発

#### バックエンド

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

#### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

ブラウザで `http://localhost:5173` を開いてください。

### AWSデプロイ

詳細は [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md) を参照してください。

## 📁 プロジェクト構造

```
invoice-agent-demo/
├── backend/          # FastAPI + LangGraph バックエンド
├── frontend/         # React + Vite フロントエンド
├── amplify.yml       # Amplify ビルド設定
├── AWS_DEPLOYMENT.md # AWSデプロイ手順
└── PROJECT_DOCUMENTATION.md # プロジェクト詳細ドキュメント
```

## 📚 ドキュメント

- [プロジェクト詳細ドキュメント](./PROJECT_DOCUMENTATION.md)
- [AWSデプロイ手順](./AWS_DEPLOYMENT.md)

## 🛠️ 技術スタック

- **バックエンド**: FastAPI, LangGraph, Python 3.11+
- **フロントエンド**: React 18, Vite
- **デプロイ**: AWS Amplify, Lambda, API Gateway

## 📝 ライセンス

このプロジェクトはデモ用です。

