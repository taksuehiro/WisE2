"""
Lambda用のハンドラ（ストリーミング対応版）
API Gateway HTTP API + Lambda Function URL を使用
"""
import json
from app_lambda import run_langgraph

def handler(event, context):
    """
    Lambdaハンドラ関数（ストリーミング対応）
    
    Lambda Function URLを使用する場合のハンドラ
    API Gateway HTTP APIの$defaultルートで使用
    
    Args:
        event: Lambda Function URLイベント
        context: Lambdaコンテキスト
        
    Returns:
        dict: HTTPレスポンス（ストリーミング形式）
    """
    # 共通CORSヘッダー
    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    # OPTIONSリクエスト（CORS preflight）の処理
    http_method = event.get("requestContext", {}).get("http", {}).get("method") or event.get("httpMethod")
    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": ""
        }
    
    try:
        # クエリパラメータからuser_textを取得
        query_params = event.get("queryStringParameters") or {}
        user_text = query_params.get("user_text", "")
        
        if not user_text:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({"error": "user_text parameter is required"}, ensure_ascii=False)
            }
        
        # LangGraphを実行してイベントを収集
        events = list(run_langgraph(user_text))
        
        # Server-Sent Events形式で返す
        # Lambda Function URLはストリーミングをサポート
        sse_headers = {
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        
        sse_body = "\n".join([
            f"data: {json.dumps(event, ensure_ascii=False)}\n"
            for event in events
        ]) + "\n\n"
        
        return {
            "statusCode": 200,
            "headers": sse_headers,
            "body": sse_body
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({
                "error": str(e)
            }, ensure_ascii=False)
        }

