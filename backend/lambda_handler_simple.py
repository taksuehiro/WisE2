"""
Lambda用のハンドラ（FastAPIなし版）
API GatewayのREST API統合用
"""
import json
from app_lambda import run_langgraph

def handler(event, context):
    """
    Lambdaハンドラ関数
    
    Args:
        event: API Gatewayイベント
        context: Lambdaコンテキスト
        
    Returns:
        dict: API Gatewayレスポンス
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
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET,OPTIONS"
                },
                "body": json.dumps({"error": "user_text parameter is required"}, ensure_ascii=False)
            }
        
        # OPTIONSリクエスト（CORS preflight）の処理
        if event.get("httpMethod") == "OPTIONS":
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
        # 注意: API Gatewayはストリーミングを直接サポートしないため、
        # すべてのイベントを一度に返すか、別の方法（WebSocket等）を検討
        
        # 簡易版: すべてのイベントをJSON配列で返す
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
            "body": "\n".join([
                f"data: {json.dumps(event, ensure_ascii=False)}\n"
                for event in events
            ]) + "\n\n"
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

