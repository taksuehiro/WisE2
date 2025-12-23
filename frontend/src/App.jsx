import React, { useMemo, useRef, useState } from "react";
import { invoices } from "./invoices.js";

const FIELD_LABELS = {
  vendor_name: "取引先名",
  invoice_no: "請求書番号",
  invoice_date: "請求日",
  due_date: "支払期日",
  subtotal: "小計",
  tax: "消費税",
  total: "合計"
};

const FIELD_ORDER = ["vendor_name", "invoice_no", "invoice_date", "due_date", "subtotal", "tax", "total"];

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function typeInto(setter, fullValue, speedMs = 18) {
  const s = String(fullValue);
  let cur = "";
  for (let i = 0; i < s.length; i++) {
    cur += s[i];
    setter(cur);
    await sleep(speedMs);
  }
}

export default function App() {
  const [selected, setSelected] = useState("A");
  const [prompt, setPrompt] = useState("");
  const [logs, setLogs] = useState([]);
  const [running, setRunning] = useState(false);

  const [form, setForm] = useState(() =>
    Object.fromEntries(FIELD_ORDER.map((k) => [k, ""]))
  );
  const [activeField, setActiveField] = useState(null);

  const esRef = useRef(null);

  const chips = useMemo(
    () => [
      { label: "Aを入力", value: "資料Aを入力して" },
      { label: "Bを入力", value: "資料Bを入力して" },
      { label: "Cを入力", value: "資料Cを入力して" }
    ],
    []
  );

  function appendLog(msg) {
    setLogs((prev) => [...prev, { t: new Date().toLocaleTimeString(), msg }]);
  }

  function resetOutput() {
    setLogs([]);
    setForm(Object.fromEntries(FIELD_ORDER.map((k) => [k, ""])));
    setActiveField(null);
  }

  async function handleFill(field, value) {
    setActiveField(field);
    // フィールドを空にしてからタイプする（"入力してる感"）
    setForm((prev) => ({ ...prev, [field]: "" }));
    await sleep(120);
    await typeInto(
      (v) => setForm((prev) => ({ ...prev, [field]: v })),
      value,
      14
    );
    await sleep(120);
  }

  function stop() {
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }
    setRunning(false);
    setActiveField(null);
    appendLog("停止しました");
  }

  async function run() {
    if (!prompt.trim()) return;

    resetOutput();
    setRunning(true);
    appendLog(`指示: ${prompt}`);

    const apiUrl = import.meta.env.VITE_API_URL || "";
    const url = `${apiUrl}/run?user_text=${encodeURIComponent(prompt)}`;
    
    console.log("🔴 [DEBUG] Starting request");
    console.log("🔴 [DEBUG] URL:", url);
    
    try {
      // SSEが使えない場合の代替：fetch + ポーリング
      const response = await fetch(url);
      console.log("🔴 [DEBUG] Response status:", response.status);
      console.log("🔴 [DEBUG] Response headers:", Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const text = await response.text();
      console.log("🔴 [DEBUG] Response text length:", text.length);
      console.log("🔴 [DEBUG] Response text (first 500 chars):", text.substring(0, 500));
      
      // SSE形式のテキストをパース
      const lines = text.split('\n').filter(line => line.trim());
      console.log("🔴 [DEBUG] Parsed lines count:", lines.length);
      
      let queue = Promise.resolve();
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.substring(6).trim();
          if (!jsonStr) continue;
          
          try {
            const data = JSON.parse(jsonStr);
            console.log("🟢 PARSED DATA:", data);
            
            if (data.type === "log") {
              appendLog(data.message);
            } else if (data.type === "fill") {
              console.log("🟡 FILL EVENT:", data.field, data.value);
              if (!(data.field in form)) {
                console.warn("UI does not know this field:", data.field);
                continue;
              }
              console.log("🟢 CALLING handleFill:", data.field, data.value);
              queue = queue.then(() => handleFill(data.field, data.value));
            } else {
              console.warn("Unknown SSE event:", data);
            }
          } catch (e) {
            console.error("JSON parse error:", jsonStr, e);
          }
        }
      }
      
      await queue;
      setRunning(false);
      setActiveField(null);
      appendLog("実行完了");
      
    } catch (error) {
      console.error("🔴 [DEBUG] Fetch error:", error);
      appendLog(`エラー: ${error.message}`);
      setRunning(false);
      setActiveField(null);
    }
  }

  return (
    <div className="page">
      <header className="header">
        <div>
          <div className="title">請求書AIエージェント（デモ）</div>
          <div className="sub">A/B/Cの表記ゆれを吸収して、別システムへ1項目ずつ入力する "作業してる感" デモ</div>
        </div>
      </header>

      <div className="grid">
        {/* 左：請求書 */}
        <section className="card">
          <div className="cardTitle">請求書プレビュー</div>
          <div className="tabs">
            {["A", "B", "C"].map((k) => (
              <button
                key={k}
                className={`tab ${selected === k ? "active" : ""}`}
                onClick={() => setSelected(k)}
              >
                {k}
              </button>
            ))}
          </div>
          <pre className="invoice">{invoices[selected]}</pre>
        </section>

        {/* 中：指示＋ログ */}
        <section className="card">
          <div className="cardTitle">指示</div>
          <textarea
            className="prompt"
            placeholder="例：資料Aを入力して"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={running}
          />
          <div className="chips">
            {chips.map((c) => (
              <button
                key={c.label}
                className="chip"
                onClick={() => setPrompt(c.value)}
                disabled={running}
                title="クリックで入力欄に反映"
              >
                {c.label}
              </button>
            ))}
          </div>

          <div className="actions">
            <button className="btn" onClick={run} disabled={running || !prompt.trim()}>
              実行
            </button>
            <button className="btn ghost" onClick={stop} disabled={!running}>
              停止
            </button>
          </div>

          <div className="cardTitle" style={{ marginTop: 12 }}>実行ログ</div>
          <div className="log">
            {logs.length === 0 ? (
              <div className="logEmpty">ここに進捗が流れます（OCR→正規化→入力…）</div>
            ) : (
              logs.map((l, i) => (
                <div key={i} className="logLine">
                  <span className="logTime">{l.t}</span>
                  <span>{l.msg}</span>
                </div>
              ))
            )}
          </div>
        </section>

        {/* 右：別システム画面モック */}
        <section className="card">
          <div className="cardTitle">別システム画面（モック）</div>
          <div className="form">
            {FIELD_ORDER.map((k) => (
              <div key={k} className={`row ${activeField === k ? "activeRow" : ""}`}>
                <div className="label">{FIELD_LABELS[k] ?? k}</div>
                <input className="input" value={form[k]} readOnly />
              </div>
            ))}
          </div>
          <div className="hint">
            ※このフォームへの入力は、LangGraphが送る <code>fill</code> イベントを受けて1項目ずつアニメしています。
          </div>
        </section>
      </div>
    </div>
  );
}

