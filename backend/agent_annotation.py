"""
Agent 工具调用标注 — API 路由 + SQLite 存储
挂载方式: app.include_router(router)
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional

from agent_importers import ImporterRegistry

router = APIRouter(prefix="/api/agent-annotation", tags=["agent-annotation"])

# ---------------------------------------------------------------------------
# SQLite 初始化
# ---------------------------------------------------------------------------
DB_DIR = Path(__file__).parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "agent_annotation.db"

importer_registry = ImporterRegistry()


def _get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db():
    conn = _get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS agent_sessions (
            session_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            model TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            messages TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agent_annotations (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            message_index INTEGER NOT NULL,
            tool_call_index INTEGER NOT NULL,
            annotator TEXT NOT NULL DEFAULT 'default_user',
            correctness TEXT NOT NULL,
            error_type TEXT,
            severity TEXT,
            comment TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id)
        );

        CREATE INDEX IF NOT EXISTS idx_annotations_session
            ON agent_annotations(session_id);
        """
    )
    conn.close()


_init_db()

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB


# ---------------------------------------------------------------------------
# Pydantic 模型
# ---------------------------------------------------------------------------
class AnnotationCreate(BaseModel):
    session_id: str
    message_index: int
    tool_call_index: int
    correctness: str  # correct / incorrect / uncertain
    error_type: Optional[str] = None
    severity: Optional[str] = None
    comment: Optional[str] = None


# ---------------------------------------------------------------------------
# API 端点
# ---------------------------------------------------------------------------


@router.get("/stats")
def get_stats():
    """统计概览"""
    conn = _get_db()
    try:
        total_sessions = conn.execute("SELECT COUNT(*) FROM agent_sessions").fetchone()[
            0
        ]

        # 计算总工具调用数
        total_tool_calls = 0
        rows = conn.execute("SELECT messages FROM agent_sessions").fetchall()
        for row in rows:
            messages = json.loads(row["messages"])
            for msg in messages:
                total_tool_calls += len(msg.get("tool_calls", []))

        total_annotations = conn.execute(
            "SELECT COUNT(*) FROM agent_annotations"
        ).fetchone()[0]

        # 正确性分布
        correctness_rows = conn.execute(
            "SELECT correctness, COUNT(*) as cnt FROM agent_annotations GROUP BY correctness"
        ).fetchall()
        correctness_distribution = {
            r["correctness"]: r["cnt"] for r in correctness_rows
        }

        # 错误类型分布
        error_rows = conn.execute(
            "SELECT error_type, COUNT(*) as cnt FROM agent_annotations "
            "WHERE error_type IS NOT NULL GROUP BY error_type"
        ).fetchall()
        error_type_distribution = {r["error_type"]: r["cnt"] for r in error_rows}

        annotation_rate = (
            round(total_annotations / total_tool_calls * 100, 2)
            if total_tool_calls > 0
            else 0
        )

        return {
            "total_sessions": total_sessions,
            "total_tool_calls": total_tool_calls,
            "total_annotations": total_annotations,
            "annotation_rate": annotation_rate,
            "correctness_distribution": correctness_distribution,
            "error_type_distribution": error_type_distribution,
        }
    finally:
        conn.close()


@router.get("/sessions")
def list_sessions():
    """会话列表"""
    conn = _get_db()
    try:
        rows = conn.execute(
            "SELECT session_id, created_at, model, messages FROM agent_sessions "
            "ORDER BY created_at DESC"
        ).fetchall()

        result = []
        for row in rows:
            messages = json.loads(row["messages"])
            tool_call_count = sum(len(msg.get("tool_calls", [])) for msg in messages)
            annotation_count = conn.execute(
                "SELECT COUNT(*) FROM agent_annotations WHERE session_id = ?",
                (row["session_id"],),
            ).fetchone()[0]

            result.append(
                {
                    "session_id": row["session_id"],
                    "created_at": row["created_at"],
                    "model": row["model"],
                    "message_count": len(messages),
                    "tool_call_count": tool_call_count,
                    "annotation_count": annotation_count,
                }
            )
        return result
    finally:
        conn.close()


@router.get("/sessions/{session_id}")
def get_session(session_id: str):
    """会话详情"""
    conn = _get_db()
    try:
        row = conn.execute(
            "SELECT * FROM agent_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="会话不存在")
        return {
            "session_id": row["session_id"],
            "created_at": row["created_at"],
            "model": row["model"],
            "metadata": json.loads(row["metadata"]),
            "messages": json.loads(row["messages"]),
        }
    finally:
        conn.close()


@router.post("/sessions/import")
async def import_session(file: UploadFile = File(...)):
    """导入会话数据（支持 OpenAI/Anthropic/自定义格式自动检测）"""
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="文件大小超过 10MB 限制")

    try:
        raw_data = json.loads(content.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="无效的 JSON 文件")

    try:
        session = importer_registry.import_data(raw_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    conn = _get_db()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO agent_sessions (session_id, created_at, model, metadata, messages) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                session["session_id"],
                session["created_at"],
                session["model"],
                json.dumps(session.get("metadata", {}), ensure_ascii=False),
                json.dumps(session["messages"], ensure_ascii=False),
            ),
        )
        conn.commit()

        msg_count = len(session["messages"])
        tc_count = sum(len(m.get("tool_calls", [])) for m in session["messages"])
        return {
            "success": True,
            "session_id": session["session_id"],
            "message": f"成功导入会话，包含 {msg_count} 条消息、{tc_count} 个工具调用",
        }
    finally:
        conn.close()


@router.get("/sessions/{session_id}/tool-calls")
def get_tool_calls(session_id: str):
    """获取会话中的所有工具调用（含已有标注）"""
    conn = _get_db()
    try:
        row = conn.execute(
            "SELECT messages FROM agent_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="会话不存在")

        messages = json.loads(row["messages"])
        tool_calls = []

        for msg_idx, message in enumerate(messages):
            if message.get("tool_calls"):
                for tc_idx, tool_call in enumerate(message["tool_calls"]):
                    annotations = conn.execute(
                        "SELECT * FROM agent_annotations "
                        "WHERE session_id = ? AND message_index = ? AND tool_call_index = ?",
                        (session_id, msg_idx, tc_idx),
                    ).fetchall()

                    tool_calls.append(
                        {
                            "message_index": msg_idx,
                            "tool_call_index": tc_idx,
                            "tool_call": tool_call,
                            "annotations": [dict(a) for a in annotations],
                        }
                    )

        return tool_calls
    finally:
        conn.close()


@router.post("/annotations")
def create_annotation(data: AnnotationCreate):
    """提交标注"""
    valid_correctness = {"correct", "incorrect", "uncertain"}
    if data.correctness not in valid_correctness:
        raise HTTPException(
            status_code=400,
            detail=f"correctness 必须为 {valid_correctness} 之一",
        )

    valid_error_types = {
        "wrong_tool",
        "wrong_params",
        "wrong_timing",
        "redundant",
        "missing",
    }
    if data.error_type and data.error_type not in valid_error_types:
        raise HTTPException(
            status_code=400,
            detail=f"error_type 必须为 {valid_error_types} 之一",
        )

    valid_severities = {"critical", "major", "minor", "trivial"}
    if data.severity and data.severity not in valid_severities:
        raise HTTPException(
            status_code=400,
            detail=f"severity 必须为 {valid_severities} 之一",
        )

    conn = _get_db()
    try:
        # 验证会话存在
        session_row = conn.execute(
            "SELECT messages FROM agent_sessions WHERE session_id = ?",
            (data.session_id,),
        ).fetchone()
        if not session_row:
            raise HTTPException(status_code=404, detail="会话不存在")

        messages = json.loads(session_row["messages"])
        if data.message_index >= len(messages):
            raise HTTPException(status_code=400, detail="消息索引无效")

        message = messages[data.message_index]
        tc_list = message.get("tool_calls", [])
        if data.tool_call_index >= len(tc_list):
            raise HTTPException(status_code=400, detail="工具调用索引无效")

        annotation_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn.execute(
            "INSERT INTO agent_annotations "
            "(id, session_id, message_index, tool_call_index, annotator, "
            "correctness, error_type, severity, comment, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                annotation_id,
                data.session_id,
                data.message_index,
                data.tool_call_index,
                "default_user",
                data.correctness,
                data.error_type,
                data.severity,
                data.comment,
                now,
            ),
        )
        conn.commit()

        return {
            "id": annotation_id,
            "session_id": data.session_id,
            "message_index": data.message_index,
            "tool_call_index": data.tool_call_index,
            "correctness": data.correctness,
            "error_type": data.error_type,
            "severity": data.severity,
            "comment": data.comment,
            "created_at": now,
        }
    finally:
        conn.close()


@router.get("/annotations")
def list_annotations(session_id: str = ""):
    """标注列表（可按 session_id 过滤）"""
    conn = _get_db()
    try:
        if session_id:
            rows = conn.execute(
                "SELECT * FROM agent_annotations WHERE session_id = ? ORDER BY created_at DESC",
                (session_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM agent_annotations ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
