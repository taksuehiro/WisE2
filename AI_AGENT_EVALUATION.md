# AIエージェントとしての評価

## 現状の実装分析

### 現在の実装

```python
PREBUILT = {
    "A": { ... },  # 事前定義されたデータ
    "B": { ... },
    "C": { ... },
}

def pick_doc(state: State):
    # 超単純判定：A/B/C含むか
    if "B" in text:
        doc_id = "B"
    # ...
```

### 評価：現状は「AIエージェント」ではない

**現状の実装は「AIエージェント」というより「デモ/モック」に近い状態です。**

#### ❌ 欠けている要素

1. **実際のAI処理がない**
   - OCR（画像/PDFからの文字抽出）なし
   - LLM（自然言語理解）なし
   - 機械学習モデルなし

2. **単純なルールベース**
   - `if "B" in text: doc_id = "B"` は単純な文字列マッチング
   - パターンマッチングやルールベースの判定

3. **学習・適応能力がない**
   - 過去のデータから学習しない
   - 新しいパターンに対応できない

#### ✅ ある要素（AIエージェントの基盤）

1. **ワークフロー構造**
   - LangGraphによる状態管理とノード実行
   - エージェント的な「判断→実行」の流れ

2. **拡張可能な設計**
   - `load_or_extract()` でOCR/LLMを差し替え可能
   - モジュラーな構造

3. **ストリーミング処理**
   - リアルタイムで進捗を返す
   - エージェントの「思考過程」を可視化

## 真のAIエージェントにするための要件

### レベル1: 基本的なAI処理（最小限）

```python
def load_or_extract(state: State):
    doc_id = state["doc_id"]
    
    # 実際のOCR処理
    pdf_path = f"invoices/{doc_id}.pdf"
    text = extract_text_with_ocr(pdf_path)  # AWS Textract等
    
    # LLMで構造化データ抽出
    extracted = llm_extract_fields(text)  # AWS Bedrock等
    
    # 正規化
    normalized = normalize_fields(extracted)
    
    return {"normalized": normalized}
```

**必要な技術:**
- AWS Textract（OCR）
- AWS Bedrock（LLM）
- または同等のサービス

### レベル2: 自然言語理解の強化

```python
def pick_doc(state: State):
    user_text = state.get("user_text", "")
    
    # LLMで意図を理解
    intent = llm_classify_intent(user_text)
    # 例: "最初の請求書を処理して" → doc_id = "A"
    # 例: "さくら部品の請求書" → doc_id = "B"
    
    return {"doc_id": intent.doc_id}
```

**必要な技術:**
- 意図分類（Intent Classification）
- エンティティ抽出（Entity Extraction）

### レベル3: 学習・適応能力

```python
# 過去の処理履歴から学習
def learn_from_history():
    # 類似の請求書パターンを学習
    # 表記ゆれのパターンを自動検出
    pass
```

**必要な技術:**
- 機械学習モデル
- ベクトルデータベース（類似検索）
- ファインチューニング

## 現状の位置づけ

### 「AIエージェントのプロトタイプ/デモ」

- ✅ エージェントの**構造**はある
- ✅ エージェントの**動作フロー**は実装済み
- ❌ 実際の**AI処理**は未実装

### より正確な表現

- **「請求書処理エージェントのデモ」**
- **「AIエージェントのプロトタイプ」**
- **「AIエージェントのUI/UXデモ」**

## 推奨される表現

### プロジェクト名・説明文

**現在:**
> 請求書AIエージェント

**推奨:**
> 請求書処理AIエージェント（デモ版）
> 請求書AIエージェント プロトタイプ
> 請求書処理エージェント（AI処理はモック）

### ドキュメント内の説明

**現在:**
> AIエージェントのデモアプリケーション

**推奨:**
> AIエージェントの**構造と動作フロー**を実装したデモアプリケーション。
> 実際のAI処理（OCR/LLM）は未実装で、事前定義データを使用しています。
> 後でAWS Textract/Bedrockに差し替えることで、真のAIエージェントになります。

## 結論

### 現状の評価

| 項目 | 評価 | 説明 |
|------|------|------|
| エージェント構造 | ⭕ | LangGraphによるワークフロー実装済み |
| AI処理 | ❌ | 事前定義データのみ、実際のAI処理なし |
| 拡張性 | ⭕ | 後でAI処理を追加可能な設計 |
| 全体評価 | △ | **「AIエージェントのプロトタイプ」** |

### 真のAIエージェントにするには

1. **OCR処理の追加**（AWS Textract等）
2. **LLM処理の追加**（AWS Bedrock等）
3. **自然言語理解の強化**（意図分類、エンティティ抽出）

これらを実装すれば、真の「AIエージェント」と呼べるようになります。

