# SSE EventSource onmessage が呼ばれない問題の診断と解決

## 問題の要約

AWS Amplifyにデプロイしたアプリケーションで、SSEイベントは受信できているが、`es.onmessage`が呼ばれていない。

## 考えられる原因

### 1. React StrictModeの影響
`main.jsx`で`<React.StrictMode>`が使用されている場合、開発モードでコンポーネントが2回レンダリングされ、EventSourceが2回作成される可能性がある。

### 2. EventSourceの接続状態
EventSourceが作成された直後にイベントリスナーを設定する必要があるが、タイミングの問題がある可能性。

### 3. SSEフォーマットの問題
バックエンドから返されるSSEのフォーマットが正しくない可能性。`data: `プレフィックスが必要。

### 4. クロージャの問題
`form`がクロージャにキャプチャされていて、古い値を見ている可能性。

### 5. useEffectの欠如
EventSourceのライフサイクル管理が適切でない可能性。

## 解決策

### 解決策1: useEffectでEventSourceを管理（推奨）

```javascript
import { useEffect, useRef, useState } from "react";

function run() {
  if (!prompt.trim()) return;

  resetOutput();
  setRunning(true);
  appendLog(`指示: ${prompt}`);

  const apiUrl = import.meta.env.VITE_API_URL || "";
  const url = `${apiUrl}/run?user_text=${encodeURIComponent(prompt)}`;
  
  console.log("🔴 Creating EventSource:", url);
  const es = new EventSource(url);
  esRef.current = es;

  // 接続状態の確認
  console.log("🔴 EventSource readyState:", es.readyState);
  // 0: CONNECTING, 1: OPEN, 2: CLOSED

  // イベントリスナーを即座に設定
  es.onopen = () => {
    console.log("🟢 EventSource OPENED");
  };

  es.onmessage = (event) => {
    console.log("🔵 RAW EVENT:", event.data);
    // ... 既存の処理
  };

  es.onerror = (error) => {
    console.error("🔴 EventSource ERROR:", error);
    console.log("🔴 EventSource readyState:", es.readyState);
  };
}
```

### 解決策2: より詳細なデバッグログを追加

```javascript
function run() {
  if (!prompt.trim()) return;

  resetOutput();
  setRunning(true);
  appendLog(`指示: ${prompt}`);

  const apiUrl = import.meta.env.VITE_API_URL || "";
  const url = `${apiUrl}/run?user_text=${encodeURIComponent(prompt)}`;
  
  console.log("🔴 [DEBUG] Creating EventSource");
  console.log("🔴 [DEBUG] URL:", url);
  console.log("🔴 [DEBUG] API URL from env:", import.meta.env.VITE_API_URL);
  
  const es = new EventSource(url);
  esRef.current = es;

  // 接続状態を定期的に確認
  const checkInterval = setInterval(() => {
    console.log("🔴 [DEBUG] EventSource state:", {
      readyState: es.readyState,
      url: es.url,
      withCredentials: es.withCredentials
    });
  }, 1000);

  es.onopen = () => {
    console.log("🟢 [DEBUG] EventSource OPENED");
    clearInterval(checkInterval);
  };

  es.onmessage = (event) => {
    console.log("🔵 [DEBUG] onmessage called!");
    console.log("🔵 RAW EVENT:", event.data);
    // ... 既存の処理
  };

  es.onerror = (error) => {
    console.error("🔴 [DEBUG] EventSource ERROR:", error);
    clearInterval(checkInterval);
  };
}
```

### 解決策3: addEventListenerを使用

```javascript
es.addEventListener('message', (event) => {
  console.log("🔵 RAW EVENT:", event.data);
  // ... 既存の処理
});

es.addEventListener('error', (error) => {
  console.error("🔴 EventSource ERROR:", error);
});
```

### 解決策4: React StrictModeを一時的に無効化（デバッグ用）

```javascript
// main.jsx
ReactDOM.createRoot(document.getElementById("root")).render(
  // <React.StrictMode>  // 一時的にコメントアウト
    <App />
  // </React.StrictMode>
);
```

## 診断手順

1. **ConsoleでEventSourceの作成を確認**
   ```javascript
   console.log("🔴 Creating EventSource:", url);
   ```

2. **EventSourceの状態を確認**
   ```javascript
   console.log("🔴 EventSource readyState:", es.readyState);
   ```

3. **onopenイベントを確認**
   ```javascript
   es.onopen = () => {
     console.log("🟢 EventSource OPENED");
   };
   ```

4. **NetworkタブでSSEレスポンスを確認**
   - `Content-Type: text/event-stream` が正しいか
   - `data: `プレフィックスが付いているか

5. **ブラウザの開発者ツールでEventSourceを確認**
   ```javascript
   // Consoleで実行
   window.esRef = esRef.current;
   console.log(window.esRef);
   ```

## 期待される動作

1. `🔴 Creating EventSource` が表示される
2. `🟢 EventSource OPENED` が表示される
3. `🔵 RAW EVENT` が表示される
4. `🟢 PARSED DATA` が表示される
5. `🟡 FILL EVENT` が表示される
6. `🟢 CALLING handleFill` が表示される

