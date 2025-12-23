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
    try:
        # クエリパラメータからuser_textを取得
        query_params = event.get("queryStringParameters") or {}
        user_text = query_params.get("user_text", "")
        
        if not user_text:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "user_text parameter is required"}, ensure_ascii=False)
            }
        
        # OPTIONSリクエスト（CORS preflight）の処理
        if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET,OPTIONS"
                },
                "body": ""
            }
        
        # LangGraphを実行してイベントを収集
        events = list(run_langgraph(user_text))
        
        # Server-Sent Events形式で返す
        # Lambda Function URLはストリーミングをサポート
        sse_body = "\n".join([
            f"data: {json.dumps(event, ensure_ascii=False)}\n"
            for event in events
        ]) + "\n\n"
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            },
            "body": sse_body
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            }, ensure_ascii=False)
        }

