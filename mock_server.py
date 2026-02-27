from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import time
import logging
import sys
import json

# 配置日志：同时输出到文件和控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler("mock_server.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# 1. 模拟模型列表接口
@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {"id": "test-model-1", "object": "model", "created": 1686935002, "owned_by": "custom"}
        ]
    }

# 2. 模拟对话接口
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    # 获取请求体内容
    body = await request.json()
    
    separator = "=" * 60
    current_time = time.strftime('%H:%M:%S')
    
    logger.info(f"\n{separator}")
    logger.info(f"[{current_time}] 收到请求！")
    
    # 验证关键字段是否注入成功
    if "api_key" in body:
        logger.info(f"✅ 成功检测到字段 'api_key': {body['api_key']}")
    else:
        logger.info("❌ 未检测到 'api_key' 字段！")

    if "conversation_id" in body:
        logger.info(f"✅ 成功检测到字段 'conversation_id': {body['conversation_id']}")
    else:
        logger.info("❌ 未检测到 'conversation_id' 字段！")
        
    # 格式化输出 Body
    logger.info(f"完整请求体 Body:\n{json.dumps(body, indent=2, ensure_ascii=False)}")
    logger.info(f"{separator}\n")

    # 返回响应
    return {
        "id": "chatcmpl-mock",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.get("model", "test-model-1"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"你好！我已经收到了你的请求。\n- api_key: {body.get('api_key', '未提供')}\n- conversation_id: {body.get('conversation_id', '未提供')}"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    }

if __name__ == "__main__":
    port_number = 9090
    logger.info(f"正在启动模拟服务器，监听端口 {port_number}...")
    logger.info(f"日志将实时保存到当前目录下的 'mock_server.log' 文件中。")
    uvicorn.run(app, host="0.0.0.0", port=port_number)
