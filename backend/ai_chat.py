"""
AI 助手模块 — 火山引擎 Doubao API SSE 流式代理
挂载方式: app.include_router(router)
"""

import json
import os
import time

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from system_log import log_llm_call

router = APIRouter(tags=["ai"])

ARK_API_KEY = os.getenv("ARK_API_KEY", "")
ARK_ENDPOINT_ID = os.getenv("ARK_ENDPOINT_ID", "")

AI_SYSTEM_PROMPT = """你是 DataOps Studio 的 AI 助手。这是一个大模型训练数据管理和探索平台，你了解以下功能：
- 数据管道：Web 语料清洗、数据去重 (MinHash LSH)、质量过滤、SFT 数据生成、数据混合与 Tokenization、RLHF 数据导出
- 数据质量：语料语言纯度、文档长度合规、去重时效、数据指纹唯一性、SFT 指令完整性、毒性评分、数据污染检测、Token 分布均衡度
- 质量研究室：知识密度分析、维度覆盖度分析、数据污染检测
- 数据 Insight：前沿论文追踪、开源工具生态、社区动态
- 成本分析：GPU 算力成本、存储成本、标注成本
- RLHF 标注：偏好排序、DPO 偏好对、KTO 二元反馈、SFT 数据改写、Reward 评分
- 团队：预训练数据组、预训练基建组、后训练数据组、数据质量组、数据科学组、标注运营组

请用简洁专业的中文回答用户关于 LLM 训练数据管理、数据质量研究、标注任务等方面的问题。"""


@router.post("/api/ai/chat")
async def ai_chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    if not ARK_API_KEY:
        return {"error": "AI 服务未配置"}

    api_messages = [{"role": "system", "content": AI_SYSTEM_PROMPT}] + messages
    user_prompt = messages[-1].get("content", "") if messages else ""

    async def stream_response():
        full_response = ""
        start_ts = time.time()
        llm_status = "ok"
        llm_error = None
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
                    headers={
                        "Authorization": f"Bearer {ARK_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": ARK_ENDPOINT_ID,
                        "messages": api_messages,
                        "stream": True,
                    },
                ) as resp:
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            yield line + "\n\n"
                            payload = line[6:]
                            try:
                                delta = (
                                    json.loads(payload)
                                    .get("choices", [{}])[0]
                                    .get("delta", {})
                                    .get("content", "")
                                )
                                if delta:
                                    full_response += delta
                            except (json.JSONDecodeError, IndexError):
                                pass
                        elif line == "data: [DONE]":
                            yield "data: [DONE]\n\n"
        except Exception as exc:
            llm_status = "error"
            llm_error = str(exc)
            yield "data: [DONE]\n\n"
        finally:
            duration = round((time.time() - start_ts) * 1000, 2)
            log_llm_call(
                source="ai_assistant",
                model=ARK_ENDPOINT_ID,
                prompt=user_prompt,
                response=full_response,
                duration_ms=duration,
                status=llm_status,
                error=llm_error,
                metadata={"history_length": len(messages)},
            )

    return StreamingResponse(stream_response(), media_type="text/event-stream")
