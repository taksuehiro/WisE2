# Gitプッシュエラーの解決方法

リモートリポジトリにローカルにない変更がある場合の対処法です。

## エラーの原因

リモートリポジトリ（GitHub）に、ローカルにない変更（例：README、LICENSEなど）が存在するため、プッシュが拒否されています。

## 解決方法

### 方法1: リモートの変更をマージ（推奨）

```powershell
# リモートの変更を取得してマージ
git pull origin main --allow-unrelated-histories

# マージ後、再度プッシュ
git push -u origin main
```

### 方法2: リベース（履歴をきれいに保ちたい場合）

```powershell
# リモートの変更をリベース
git pull origin main --rebase --allow-unrelated-histories

# リベース後、再度プッシュ
git push -u origin main
```

### 方法3: 強制プッシュ（注意：リモートの変更が失われます）

**⚠️ 警告**: この方法はリモートの変更を上書きします。他の人が作業している場合は使用しないでください。

```powershell
# 強制プッシュ（リモートの変更を無視）
git push -u origin main --force
```

## 推奨手順

1. まず方法1を試してください（最も安全）
2. マージコンフリクトが発生した場合は、手動で解決
3. 解決後、再度プッシュ
