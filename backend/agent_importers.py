"""
Agent 工具调用标注 — 多格式导入器
支持 OpenAI / Anthropic / 自定义 格式自动检测与转换
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any


class DataImporter(ABC):
    @abstractmethod
    def detect(self, raw_data: Dict) -> float:
        """检测数据格式，返回 0-1 之间的置信度"""

    @abstractmethod
    def transform(self, raw_data: Dict) -> Dict:
        """转换为标准内部格式"""


class OpenAIImporter(DataImporter):
    def detect(self, raw_data: Dict) -> float:
        score = 0.0
        if "messages" in raw_data:
            score += 0.5
        if isinstance(raw_data.get("messages"), list) and raw_data["messages"]:
            score += 0.3
            first_msg = raw_data["messages"][0]
            if "role" in first_msg and "content" in first_msg:
                score += 0.2
        return min(score, 1.0)

    def transform(self, raw_data: Dict) -> Dict:
        messages = []
        for msg in raw_data["messages"]:
            message_dict = {
                "role": msg["role"],
                "content": msg.get("content", ""),
            }
            if "tool_calls" in msg:
                message_dict["tool_calls"] = msg["tool_calls"]
            if "tool_call_id" in msg:
                message_dict["tool_call_id"] = msg["tool_call_id"]
            messages.append(message_dict)

        return {
            "session_id": raw_data.get("id", "unknown"),
            "created_at": raw_data.get("created", raw_data.get("created_at", "")),
            "model": raw_data.get("model", "unknown"),
            "metadata": {"source_format": "openai"},
            "messages": messages,
        }


class AnthropicImporter(DataImporter):
    def detect(self, raw_data: Dict) -> float:
        score = 0.0
        if "messages" in raw_data:
            score += 0.4
        if "created_at" in raw_data:
            score += 0.3
        if raw_data.get("model", "").startswith("claude"):
            score += 0.3
        return min(score, 1.0)

    def transform(self, raw_data: Dict) -> Dict:
        messages = []
        for msg in raw_data["messages"]:
            message_dict = {
                "role": msg["role"],
                "content": msg.get("content", ""),
            }
            if "tool_calls" in msg:
                message_dict["tool_calls"] = msg["tool_calls"]
            if "tool_call_id" in msg:
                message_dict["tool_call_id"] = msg["tool_call_id"]
            messages.append(message_dict)

        return {
            "session_id": raw_data.get("id", "unknown"),
            "created_at": raw_data.get("created_at", ""),
            "model": raw_data.get("model", "unknown"),
            "metadata": {"source_format": "anthropic"},
            "messages": messages,
        }


class CustomImporter(DataImporter):
    def detect(self, raw_data: Dict) -> float:
        score = 0.0
        if "trace_id" in raw_data:
            score += 0.4
        if "conversation_turns" in raw_data:
            score += 0.4
        if "agent_config" in raw_data:
            score += 0.2
        return min(score, 1.0)

    def transform(self, raw_data: Dict) -> Dict:
        messages: List[Dict[str, Any]] = []

        for turn in raw_data.get("conversation_turns", []):
            speaker = turn.get("speaker_type")

            if speaker == "user":
                messages.append({"role": "user", "content": turn["text"]})

            elif speaker == "assistant":
                msg_dict: Dict[str, Any] = {
                    "role": "assistant",
                    "content": turn["text"],
                }
                if "actions" in turn:
                    tool_calls = []
                    for action in turn["actions"]:
                        tool_calls.append(
                            {
                                "id": action["action_id"],
                                "type": "function",
                                "function": {
                                    "name": action["tool_name"],
                                    "arguments": json.dumps(
                                        action["tool_input"], ensure_ascii=False
                                    ),
                                },
                            }
                        )
                    msg_dict["tool_calls"] = tool_calls
                messages.append(msg_dict)

            elif speaker == "tool":
                messages.append(
                    {
                        "role": "tool",
                        "content": turn["text"],
                        "tool_call_id": turn["action_ref_id"],
                    }
                )

        return {
            "session_id": raw_data.get("trace_id", "unknown"),
            "created_at": str(raw_data.get("timestamp", "")),
            "model": raw_data.get("agent_config", {}).get("model_name", "unknown"),
            "metadata": {
                "source_format": "custom",
                "temperature": raw_data.get("agent_config", {}).get("temperature"),
            },
            "messages": messages,
        }


class ImporterRegistry:
    def __init__(self):
        self.importers: List[DataImporter] = [
            OpenAIImporter(),
            AnthropicImporter(),
            CustomImporter(),
        ]

    def auto_detect(self, raw_data: Dict) -> DataImporter:
        best_importer = None
        best_score = 0.0

        for importer in self.importers:
            score = importer.detect(raw_data)
            if score > best_score:
                best_score = score
                best_importer = importer

        if best_score >= 0.5 and best_importer is not None:
            return best_importer

        raise ValueError(
            "无法识别数据格式，请检查 JSON 结构是否符合 OpenAI/Anthropic/自定义格式"
        )

    def import_data(self, raw_data: Dict) -> Dict:
        importer = self.auto_detect(raw_data)
        return importer.transform(raw_data)
