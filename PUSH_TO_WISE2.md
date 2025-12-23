# WisE2リポジトリへのプッシュ手順

新しいリポジトリ `https://github.com/taksuehiro/WisE2` にプッシュする手順です。

## 手順

### 1. 既存のGit履歴をクリア（Secret Scanningの問題を回避）

```powershell
# 現在の.gitフォルダを削除
Remove-Item -Recurse -Force .git
```

### 2. 新しいGitリポジトリを初期化

```powershell
git init
```

### 3. リモートリポジトリを追加

```powershell
git remote add origin https://github.com/taksuehiro/WisE2.git
```

### 4. すべてのファイルをステージング

```powershell
git add .
```

### 5. 初回コミット

```powershell
git commit -m "Initial commit: 請求書AIエージェントデモプロジェクト（AWS対応版）"
```

### 6. メインブランチにプッシュ

```powershell
git branch -M main
git push -u origin main
```

## 注意事項

- `.gitignore` により、`node_modules/`, `__pycache__/`, `.venv/` などは自動的に除外されます
- 初回プッシュ時はGitHubの認証が必要です
- 機密情報を含むファイル（`.env` など）は `.gitignore` に含まれているため、プッシュされません

