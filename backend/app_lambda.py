"""
Lambda用の請求書処理LangGraphアプリケーション
FastAPIを使わないバージョン
"""
from typing import TypedDict, Dict, List, Any
from langgraph.graph import StateGraph, END

# ===== デモ用の事前抽出済みデータ =====
PREBUILT = {
    "A": {
        "vendor_name": "ABC商事",
        "invoice_no": "INV-A-001",
        "invoice_date": "2025-12-01",
        "due_date": "2026-01-10",
        "subtotal": 120000,
        "tax": 12000,
        "total": 132000,
    },
    "B": {
        "vendor_name": "さくら部品株式会社",
        "invoice_no": "2025/11/30-7788",
        "invoice_date": "2025-11-30",
        "due_date": "2026-01-05",
        "subtotal": 98000,
        "tax": 9800,
        "total": 107800,
    },
    "C": {
        "vendor_name": "TOYO INDUSTRIES",
        "invoice_no": "C-INV-00042",
        "invoice_date": "2025-10-15",
        "due_date": "2025-11-30",
        "subtotal": 250000,
        "tax": 25000,
        "total": 275000,
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

# ===== State定義 =====
class State(TypedDict, total=False):
    user_text: str
    doc_id: str
    normalized: Dict[str, Any]
    fill_plan: List[Dict[str, Any]]

# ===== ノード定義 =====
def pick_doc(state: State) -> State:
    """ユーザー指示から対象ドキュメントを決定"""
    user_text = (state.get("user_text") or "").upper()
    doc_id = "A"  # デフォルト
    
    # 超単純判定：A/B/C含むか
    if "B" in user_text:
        doc_id = "B"
    if "C" in user_text:
        doc_id = "C"
    if "A" in user_text:
        doc_id = "A"
    
    return {"doc_id": doc_id}

def load_or_extract(state: State) -> State:
    """請求書データを読み込み（デモでは事前抽出データを使用）"""
    doc_id = state.get("doc_id", "A")
    normalized = PREBUILT.get(doc_id, PREBUILT["A"])
    return {"normalized": normalized}

def make_plan(state: State) -> State:
    """入力計画を作成"""
    normalized = state.get("normalized", {})
    fill_plan = []
    
    for field in TARGET_FIELDS_ORDER:
        value = normalized.get(field)
        if value is not None:
            fill_plan.append({
                "type": "fill",
                "field": field,
                "value": value
            })
    
    return {"fill_plan": fill_plan}

def stream_fill(state: State) -> State:
    """何もしない（イベントは後で生成）"""
    return {}

# ===== グラフ構築 =====
workflow = StateGraph(State)
workflow.add_node("pick_doc", pick_doc)
workflow.add_node("load_or_extract", load_or_extract)
workflow.add_node("make_plan", make_plan)
workflow.add_node("stream_fill", stream_fill)

workflow.set_entry_point("pick_doc")
workflow.add_edge("pick_doc", "load_or_extract")
workflow.add_edge("load_or_extract", "make_plan")
workflow.add_edge("make_plan", "stream_fill")
workflow.add_edge("stream_fill", END)

graph = workflow.compile()

# ===== カスタムイベント生成用の関数 =====
def generate_events(state: State):
    """LangGraphの実行結果からイベントを生成"""
    doc_id = state.get("doc_id", "")
    fill_plan = state.get("fill_plan", [])
    
    # ログイベント
    yield {"type": "log", "message": f"対象ドキュメントを決定: {doc_id}"}
    yield {"type": "log", "message": f"請求書{doc_id}を読み取り中…（デモ：事前抽出データ使用）"}
    yield {"type": "log", "message": "項目候補を抽出中…"}
    yield {"type": "log", "message": "表記ゆれを正規化中…（請求書番号/日付/金額）"}
    yield {"type": "log", "message": "別システム項目へのマッピングを作成中…"}
    yield {"type": "log", "message": f"入力計画を作成（{len(fill_plan)}項目）"}
    yield {"type": "log", "message": "別システムへの入力を開始"}
    
    # fillイベント
    for item in fill_plan:
        yield item
    
    yield {"type": "log", "message": "入力完了"}

# ===== Lambda用の実行関数 =====
def run_langgraph(user_text: str):
    """
    LangGraphを実行し、イベントのジェネレータを返す
    
    Args:
        user_text: ユーザー入力テキスト
        
    Yields:
        dict: イベント（log または fill）
    """
    # LangGraphを実行
    final_state = graph.invoke({"user_text": user_text})
    
    # イベントを生成
    for event in generate_events(final_state):
        yield event

