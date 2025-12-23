# AWS環境でリポジトリをクローンするコマンド

AWS環境（EC2、Cloud9、CodeBuild、Lambda Layerなど）でGitHubリポジトリをクローンする方法です。

## 基本的なクローンコマンド

### 公開リポジトリの場合

```bash
git clone https://github.com/taksuehiro/WisE2.git
cd WisE2
```

### プライベートリポジトリの場合

#### 方法1: Personal Access Token (PAT) を使用

```bash
# Personal Access Tokenを環境変数に設定
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# クローン（トークンを含むURL）
git clone https://${GITHUB_TOKEN}@github.com/taksuehiro/WisE2.git
cd WisE2
```

または、URLに直接含める：

```bash
git clone https://ghp_xxxxxxxxxxxxxxxxxxxx@github.com/taksuehiro/WisE2.git
cd WisE2
```

#### 方法2: SSHキーを使用（推奨）

```bash
# SSHキーを設定済みの場合
git clone git@github.com:taksuehiro/WisE2.git
cd WisE2
```

## AWS環境別の手順

### EC2インスタンス

#### 1. EC2に接続

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

#### 2. Gitをインストール（未インストールの場合）

```bash
# Amazon Linux 2 / Amazon Linux 2023
sudo yum update -y
sudo yum install git -y

# Ubuntu
sudo apt update
sudo apt install git -y
```

#### 3. リポジトリをクローン

```bash
git clone https://github.com/taksuehiro/WisE2.git
cd WisE2
```

### AWS Cloud9

Cloud9には既にGitがインストールされているので、そのままクローン可能：

```bash
git clone https://github.com/taksuehiro/WisE2.git
cd WisE2
```

### CodeBuild

`buildspec.yml` でクローン：

```yaml
version: 0.2
phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - git clone https://github.com/taksuehiro/WisE2.git
      - cd WisE2
  build:
    commands:
      - echo Build started on `date`
      - cd backend
      - pip install -r requirements.txt -t package/
```

または、CodeBuildのソース設定でGitHubを直接指定（推奨）。

### Lambda Layer / コンテナイメージビルド

#### Lambda Layer用パッケージ作成

```bash
# EC2やローカルで実行
git clone https://github.com/taksuehiro/WisE2.git
cd WisE2/backend

# 依存関係をインストール
pip install -r requirements.txt -t python/

# アプリケーションファイルをコピー
cp app.py python/
cp lambda_handler.py python/

# zip化
zip -r lambda-layer.zip python/
```

#### Dockerfileでクローン

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

# リポジトリをクローン
RUN yum install -y git && \
    git clone https://github.com/taksuehiro/WisE2.git /tmp/WisE2 && \
    cp -r /tmp/WisE2/backend/* ${LAMBDA_TASK_ROOT}/ && \
    pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt && \
    rm -rf /tmp/WisE2

CMD [ "lambda_handler.handler" ]
```

### GitHub Actions / CI/CD

```yaml
name: Deploy to AWS
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          repository: taksuehiro/WisE2
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt -t package/
```

## セキュリティ考慮事項

### AWS Systems Manager Parameter Store を使用

```bash
# Personal Access TokenをParameter Storeに保存
aws ssm put-parameter \
  --name /github/token \
  --value "ghp_xxxxxxxxxxxxxxxxxxxx" \
  --type SecureString

# Lambda/EC2で取得
GITHUB_TOKEN=$(aws ssm get-parameter \
  --name /github/token \
  --with-decryption \
  --query Parameter.Value \
  --output text)

git clone https://${GITHUB_TOKEN}@github.com/taksuehiro/WisE2.git
```

### AWS Secrets Manager を使用

```bash
# Secret Managerから取得
GITHUB_TOKEN=$(aws secretsmanager get-secret-value \
  --secret-id github-token \
  --query SecretString \
  --output text | jq -r .token)

git clone https://${GITHUB_TOKEN}@github.com/taksuehiro/WisE2.git
```

### IAMロールを使用（CodeBuild/CodePipeline）

CodeBuildやCodePipelineでは、IAMロールにGitHubへのアクセス権限を付与できます。

## 特定のブランチ/タグをクローン

```bash
# 特定のブランチ
git clone -b branch-name https://github.com/taksuehiro/WisE2.git

# 特定のタグ
git clone -b v1.0.0 https://github.com/taksuehiro/WisE2.git

# 浅いクローン（履歴を最小限に）
git clone --depth 1 https://github.com/taksuehiro/WisE2.git
```

## トラブルシューティング

### Gitがインストールされていない

```bash
# Amazon Linux 2
sudo yum install git -y

# Amazon Linux 2023
sudo dnf install git -y

# Ubuntu/Debian
sudo apt update && sudo apt install git -y
```

### 認証エラー

- Personal Access Tokenが有効か確認
- SSHキーが正しく設定されているか確認
- IAMロールに適切な権限があるか確認

### ネットワークエラー

- セキュリティグループでアウトバウンドHTTPS（443）が許可されているか確認
- VPCエンドポイントを使用している場合は、GitHubへのアクセスが可能か確認

## 実用的な例：EC2でセットアップ

```bash
# 1. Gitをインストール
sudo yum install git -y

# 2. リポジトリをクローン
git clone https://github.com/taksuehiro/WisE2.git
cd WisE2

# 3. バックエンドのセットアップ
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. フロントエンドのセットアップ
cd ../frontend
npm install
npm run build
```

## 参考リンク

- [Git公式ドキュメント](https://git-scm.com/doc)
- [AWS CodeBuild ドキュメント](https://docs.aws.amazon.com/codebuild/)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

