import json
import os
from typing import TypedDict, Dict, Any, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from langgraph.graph import StateGraph, START
from langgraph.config import get_stream_writer

# -----------------------------
# デモ用：抽出済み（正規化済み）データ
# -----------------------------
PREBUILT = {
    "A": {
        "vendor_name": "ABC商事",
        "invoice_no": "INV-A-001",
        "invoice_date": "2025-12-01",
        "subtotal": 120000,
        "tax": 12000,
        "total": 132000,
        "due_date": "2026-01-10",
    },
    "B": {
        "vendor_name": "さくら部品株式会社",
        "invoice_no": "2025/11/30-7788",
        "invoice_date": "2025-11-30",
        "subtotal": 98000,
        "tax": 9800,
        "total": 107800,
        "due_date": "2026-01-05",
    },
    "C": {
        "vendor_name": "TOYO INDUSTRIES",
        "invoice_no": "C-INV-00042",
        "invoice_date": "2025-10-15",
        "subtotal": 250000,
        "tax": 25000,
        "total": 275000,
        "due_date": "2025-11-30",
    },
}

TARGET_FIELDS_ORDER = [
    "vendor_name",
    "invoice_no",
    "invoice_date",
    "due_date",
    "subtotal",
    "tax",
    "total",
]

# -----------------------------
# LangGraph State
# -----------------------------
class State(TypedDict, total=False):
    user_text: str
    doc_id: str
    normalized: Dict[str, Any]
    fill_plan: List[Dict[str, Any]]

def pick_doc(state: State):
    writer = get_stream_writer()
    text = (state.get("user_text") or "").upper()

    # 超単純判定：A/B/C含むか
    doc_id = "A"
    if "B" in text:
        doc_id = "B"
    if "C" in text:
        doc_id = "C"
    if "A" in text:
        doc_id = "A"

    writer({"type": "log", "message": f"対象ドキュメントを決定: {doc_id}"})
    return {"doc_id": doc_id}

def load_or_extract(state: State):
    writer = get_stream_writer()
    doc_id = state["doc_id"]

    writer({"type": "log", "message": f"請求書{doc_id}を読み取り中…（デモ：事前抽出データ使用）"})
    normalized = PREBUILT[doc_id]

    # "作業してる感"のためのダミー工程ログ
    writer({"type": "log", "message": "項目候補を抽出中…"})
    writer({"type": "log", "message": "表記ゆれを正規化中…（請求書番号/日付/金額）"})

    return {"normalized": normalized}

def make_plan(state: State):
    writer = get_stream_writer()
    writer({"type": "log", "message": "別システム項目へのマッピングを作成中…"})

    normalized = state["normalized"]
    plan: List[Dict[str, Any]] = []

    for field in TARGET_FIELDS_ORDER:
        if field in normalized:
            plan.append({"type": "fill", "field": field, "value": normalized[field]})

    writer({"type": "log", "message": f"入力計画を作成（{len(plan)}項目）"})
    return {"fill_plan": plan}

def stream_fill(state: State):
    writer = get_stream_writer()
    writer({"type": "log", "message": "別システムへの入力を開始"})

    for step in state["fill_plan"]:
        # 1項目ずつイベントを吐く（フロントで入力アニメ）
        writer(step)

    writer({"type": "log", "message": "入力完了"})
    return {}

graph = (
    StateGraph(State)
    .add_node("pick_doc", pick_doc)
    .add_node("load_or_extract", load_or_extract)
    .add_node("make_plan", make_plan)
    .add_node("stream_fill", stream_fill)
    .add_edge(START, "pick_doc")
    .add_edge("pick_doc", "load_or_extract")
    .add_edge("load_or_extract", "make_plan")
    .add_edge("make_plan", "stream_fill")
    .compile()
)

app = FastAPI()

# フロントから叩けるようCORS（全て許可）
# 本番環境では特定ドメインに制限することを推奨
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 全てのオリジンを許可（開発・デモ用）
    allow_credentials=False,  # allow_origins=["*"]の場合はFalseにする必要がある
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/run")
def run(user_text: str):
    def event_stream():
        for chunk in graph.stream({"user_text": user_text}, stream_mode="custom"):
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/health")
def health():
    return {"ok": True}

