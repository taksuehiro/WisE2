# GitHubリポジトリへのプッシュ手順

このプロジェクトをGitHubリポジトリ（https://github.com/taksuehiro/WisE1）にプッシュする手順です。

## 前提条件

- Gitがインストールされていること
- GitHubアカウントにアクセス権限があること

## 手順

### 1. Gitリポジトリの初期化（まだの場合）

```bash
git init
```

### 2. リモートリポジトリの追加

```bash
git remote add origin https://github.com/taksuehiro/WisE1.git
```

既にリモートが設定されている場合は、以下で確認・更新：

```bash
git remote -v
git remote set-url origin https://github.com/taksuehiro/WisE1.git
```

### 3. ファイルをステージング

```bash
git add .
```

### 4. コミット

```bash
git commit -m "Initial commit: 請求書AIエージェントデモプロジェクト"
```

### 5. メインブランチにプッシュ

```bash
git branch -M main
git push -u origin main
```

## 注意事項

- `.gitignore` に含まれるファイル（`node_modules/`, `__pycache__/`, `.venv/` など）はプッシュされません
- 初回プッシュ時は認証が必要な場合があります
- リポジトリが既に存在する場合は、`git pull` で最新の状態を取得してからプッシュしてください

## トラブルシューティング

### 認証エラーが発生する場合

GitHubのPersonal Access Tokenを使用するか、SSHキーを設定してください。

### リポジトリが既に存在する場合

```bash
git pull origin main --allow-unrelated-histories
```

その後、再度プッシュしてください。

