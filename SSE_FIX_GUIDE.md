# SSE EventSource エラー解決ガイド

## 問題の診断

コンソールログから：
- ✅ EventSourceは正常に作成されている
- ✅ 接続は開いている（`🟢 EventSource OPENED`）
- ❌ その後、エラーが発生（`🔴 EventSource ERROR`）
- ❌ `readyState: 0` のまま

## 原因

**API Gateway REST APIは、SSEストリーミングを直接サポートしていません。**

API Gateway REST APIは、Lambdaから一度にすべてのレスポンスを返す必要があります。現在のコードではすべてのイベントを一度に返していますが、EventSourceがエラーになっているということは：

1. レスポンスが正しいSSEフォーマットになっていない可能性
2. API Gatewayがレスポンスを正しく処理していない可能性

## 解決策1: Networkタブでレスポンスを確認

1. ブラウザの開発者ツールを開く（F12）
2. **Network**タブを開く
3. `run?user_text=...` のリクエストをクリック
4. **Response**タブで実際のレスポンスを確認

期待されるレスポンス形式：
```
data: {"type":"log","message":"対象ドキュメントを決定: A"}

data: {"type":"fill","field":"vendor_name","value":"ABC商事"}

```

もしレスポンスが空、または不正な形式の場合は、Lambdaハンドラの問題です。

## 解決策2: Lambda Function URLに移行（推奨）

Lambda Function URLは、SSEストリーミングをサポートしています。

### 手順

1. **Lambda Function URLを作成**
   - Lambda関数の設定 → Function URL
   - 認証タイプ: NONE
   - CORSを有効化

2. **Lambdaハンドラを更新**
   - `lambda_handler_streaming.py` を使用

3. **フロントエンドのURLを更新**
   - `VITE_API_URL` を Lambda Function URL に変更

## 解決策3: 一時的な回避策（ポーリング）

SSEが使えない場合、ポーリングで代替：

```javascript
// SSEの代わりにポーリング
async function run() {
  const response = await fetch(`${apiUrl}/run?user_text=${encodeURIComponent(prompt)}`);
  const text = await response.text();
  
  // SSE形式のテキストをパース
  const events = text.split('\n\n')
    .filter(line => line.startsWith('data: '))
    .map(line => JSON.parse(line.substring(6)));
  
  // イベントを順次処理
  for (const event of events) {
    if (event.type === 'log') {
      appendLog(event.message);
    } else if (event.type === 'fill') {
      handleFill(event.field, event.value);
    }
  }
}
```

## 次のステップ

1. **Networkタブでレスポンスを確認**
2. レスポンスが正しい形式なら → Lambda Function URLに移行
3. レスポンスが不正なら → Lambdaハンドラを修正

