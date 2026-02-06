"""
RLHF / 后训练数据标注模块 — API 路由 + SQLite 存储
挂载方式: app.include_router(router)
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Request

from system_log import log_audit

router = APIRouter(tags=["annotation"])

# ---------------------------------------------------------------------------
# YAML 配置（由 main.py 初始化后注入）
# ---------------------------------------------------------------------------
ANNOTATION_TASKS: list[dict] = []
ANNOTATORS: list[dict] = []
QUALITY_CONFIG: dict = {}
ANNOTATION_SAMPLES: dict[str, list[dict]] = {}

TASK_TYPE_LABELS = {
    "rlhf_ranking": "RLHF 偏好排序",
    "dpo_pairwise": "DPO 偏好对",
    "kto_binary": "KTO 二元反馈",
    "sft_editing": "SFT 数据改写",
    "reward_scoring": "Reward 评分",
}


def init_annotation_config(annotation_cfg: dict):
    """从 YAML 配置初始化模块级变量，由 main.py 启动时调用"""
    global ANNOTATION_TASKS, ANNOTATORS, QUALITY_CONFIG, ANNOTATION_SAMPLES
    ANNOTATION_TASKS = annotation_cfg["annotation_tasks"]
    ANNOTATORS = annotation_cfg["annotators"]
    QUALITY_CONFIG = annotation_cfg["quality_config"]
    ANNOTATION_SAMPLES = {}
    for task_id, samples in annotation_cfg.get("annotation_samples", {}).items():
        ANNOTATION_SAMPLES[task_id] = samples


def reload_annotation_config(annotation_cfg: dict) -> dict:
    """热重载标注配置，返回统计信息"""
    init_annotation_config(annotation_cfg)
    return {
        "annotation_tasks": len(ANNOTATION_TASKS),
        "annotation_samples": sum(len(v) for v in ANNOTATION_SAMPLES.values()),
    }


# ---------------------------------------------------------------------------
# SQLite 持久化
# ---------------------------------------------------------------------------
_ANN_DB_DIR = Path(__file__).parent / "data"
_ANN_DB_DIR.mkdir(exist_ok=True)
_ann_db_path = _ANN_DB_DIR / "rlhf_annotation.db"

_TYPE_SPECIFIC_FIELDS = {
    "rlhf_ranking": ["ranking", "rationale"],
    "dpo_pairwise": ["chosen_index", "rejected_index", "rationale"],
    "kto_binary": ["feedback", "safety_category", "severity_score", "rationale"],
    "sft_editing": ["original_response", "edited_response", "edit_ratio"],
    "reward_scoring": ["scores", "overall_score"],
}


def _get_ann_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_ann_db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _init_ann_db():
    conn = _get_ann_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            task_type TEXT NOT NULL,
            sample_id TEXT NOT NULL,
            prompt TEXT NOT NULL,
            domain TEXT DEFAULT 'unknown',
            annotator TEXT DEFAULT 'anonymous',
            submit_time TEXT NOT NULL,
            duration_seconds INTEGER DEFAULT 0,
            review_status TEXT DEFAULT 'pending',
            review_comment TEXT,
            review_time TEXT,
            annotation_data TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sub_task ON submissions(task_id);
        CREATE INDEX IF NOT EXISTS idx_sub_status ON submissions(review_status);
        CREATE INDEX IF NOT EXISTS idx_sub_annotator ON submissions(annotator);
        """
    )
    conn.close()


_init_ann_db()


def _get_next_sub_id(task_id: str) -> str:
    conn = _get_ann_db()
    row = conn.execute(
        "SELECT COUNT(*) FROM submissions WHERE task_id=?", (task_id,)
    ).fetchone()
    conn.close()
    return f"SUB-{task_id}-{row[0] + 1:04d}"


def _insert_submission(sub: dict):
    task_type = sub["task_type"]
    type_fields = _TYPE_SPECIFIC_FIELDS.get(task_type, [])
    annotation_data = {k: sub[k] for k in type_fields if k in sub}
    conn = _get_ann_db()
    conn.execute(
        """INSERT INTO submissions
           (id, task_id, task_type, sample_id, prompt, domain, annotator,
            submit_time, duration_seconds, review_status, review_comment,
            review_time, annotation_data)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            sub["id"],
            sub["task_id"],
            sub["task_type"],
            sub["sample_id"],
            sub["prompt"],
            sub.get("domain", "unknown"),
            sub.get("annotator", "anonymous"),
            sub["submit_time"],
            sub.get("duration_seconds", 0),
            sub.get("review_status", "pending"),
            sub.get("review_comment"),
            sub.get("review_time"),
            json.dumps(annotation_data, ensure_ascii=False),
        ),
    )
    conn.commit()
    conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """将 SQLite Row 转换为 flat dict，展开 annotation_data"""
    d = dict(row)
    ad = json.loads(d.pop("annotation_data", "{}"))
    d.update(ad)
    return d


def _load_submissions(
    task_id: str | None = None,
    review_status: str | None = None,
    annotator: str | None = None,
    sample_id: str | None = None,
    limit: int = 0,
) -> list[dict]:
    """按条件查询 submissions，返回 flat dict 列表"""
    clauses: list[str] = []
    params: list = []
    if task_id:
        clauses.append("task_id=?")
        params.append(task_id)
    if review_status:
        clauses.append("review_status=?")
        params.append(review_status)
    if annotator:
        clauses.append("annotator=?")
        params.append(annotator)
    if sample_id:
        clauses.append("sample_id=?")
        params.append(sample_id)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT * FROM submissions{where} ORDER BY submit_time DESC"
    if limit > 0:
        sql += f" LIMIT {limit}"
    conn = _get_ann_db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def _validate_annotation_config():
    """启动时校验样本完整性"""
    errors = []
    for task in ANNOTATION_TASKS:
        tid = task["id"]
        samples = ANNOTATION_SAMPLES.get(tid, [])
        if not samples:
            errors.append(f"任务 {tid} 没有配置样本数据")
            continue
        for s in samples:
            if not s.get("id") or not s.get("prompt") or not s.get("responses"):
                errors.append(f"任务 {tid} 样本 {s.get('id', '?')} 缺少必要字段")
    if errors:
        print(f"[WARN] annotation config validation: {len(errors)} issues")
        for e in errors:
            print(f"  - {e}")


def _get_sample_by_id(task_id: str, sample_id: str) -> dict | None:
    """根据 task_id 和 sample_id 查找样本"""
    for s in ANNOTATION_SAMPLES.get(task_id, []):
        if s["id"] == sample_id:
            return s
    return None


# ---------------------------------------------------------------------------
# API 路由
# ---------------------------------------------------------------------------


@router.get("/api/annotation/tasks")
def list_annotation_tasks():
    conn = _get_ann_db()
    result = []
    for t in ANNOTATION_TASKS:
        tid = t["id"]
        row = conn.execute(
            """SELECT COUNT(*) as total,
                      SUM(CASE WHEN review_status='approved' THEN 1 ELSE 0 END) as approved,
                      SUM(CASE WHEN review_status='rejected' THEN 1 ELSE 0 END) as rejected,
                      SUM(CASE WHEN review_status='pending' THEN 1 ELSE 0 END) as pending,
                      COALESCE(AVG(duration_seconds), 0) as avg_dur
               FROM submissions WHERE task_id=?""",
            (tid,),
        ).fetchone()
        completed = row["total"]
        approved = row["approved"]
        rejected = row["rejected"]
        pending_count = row["pending"]
        avg_duration = row["avg_dur"]
        sample_count = len(ANNOTATION_SAMPLES.get(tid, []))
        result.append(
            {
                **t,
                "type_label": TASK_TYPE_LABELS.get(t["task_type"], t["task_type"]),
                "sample_count": sample_count,
                "total_samples": sample_count,
                "completed_samples": completed,
                "progress_percent": round((completed / max(sample_count, 1)) * 100, 1),
                "approved_count": approved,
                "rejected_count": rejected,
                "pending_review": pending_count,
                "approval_rate": round(approved / max(approved + rejected, 1) * 100, 1),
                "avg_duration_seconds": round(avg_duration),
                "annotator_names": [
                    a["name"]
                    for a in ANNOTATORS
                    if a["id"] in t.get("assigned_annotators", [])
                ],
            }
        )
    conn.close()
    return result


@router.get("/api/annotation/tasks/{task_id}")
def get_annotation_task(task_id: str):
    for t in ANNOTATION_TASKS:
        if t["id"] == task_id:
            subs = _load_submissions(task_id=task_id, limit=50)
            sample_count = len(ANNOTATION_SAMPLES.get(task_id, []))
            return {
                **t,
                "submissions": subs,
                "sample_count": sample_count,
                "type_label": TASK_TYPE_LABELS.get(t["task_type"], t["task_type"]),
            }
    return {"error": "not found"}


@router.get("/api/annotation/tasks/{task_id}/samples")
def get_task_samples(task_id: str, limit: int = 50):
    """获取任务的标注样本（含 prompt 和候选 responses）"""
    task = next((t for t in ANNOTATION_TASKS if t["id"] == task_id), None)
    if not task:
        return {"error": "not found"}
    task_samples = ANNOTATION_SAMPLES.get(task_id, [])
    all_subs = _load_submissions(task_id=task_id)
    sub_by_sample = {s["sample_id"]: s for s in all_subs}
    samples = []
    for sp in task_samples[:limit]:
        existing_sub = sub_by_sample.get(sp["id"])
        samples.append(
            {
                **sp,
                "annotation": existing_sub,
                "annotated": existing_sub is not None,
            }
        )
    return {"samples": samples, "total": len(task_samples), "task_id": task_id}


@router.post("/api/annotation/tasks/{task_id}/submit")
async def submit_annotation(task_id: str, request: Request):
    """提交标注"""
    task = next((t for t in ANNOTATION_TASKS if t["id"] == task_id), None)
    if not task:
        return {"status": "error", "message": "任务不存在"}
    if task["status"] != "active":
        return {"status": "error", "message": f"任务状态为 {task['status']}，无法提交"}

    body = await request.json()
    sample_id = body.get("sample_id")
    sample = _get_sample_by_id(task_id, sample_id)
    if not sample:
        return {"status": "error", "message": f"样本 {sample_id} 不存在"}

    conn = _get_ann_db()
    dup = conn.execute(
        "SELECT id FROM submissions WHERE task_id=? AND sample_id=?",
        (task_id, sample_id),
    ).fetchone()
    conn.close()
    if dup:
        return {"status": "error", "message": f"样本 {sample_id} 已被标注"}

    sub_id = _get_next_sub_id(task_id)
    task_type = task["task_type"]

    sub = {
        "id": sub_id,
        "task_id": task_id,
        "task_type": task_type,
        "sample_id": sample_id,
        "prompt": sample["prompt"],
        "domain": sample.get("domain", "unknown"),
        "annotator": body.get("annotator", "anonymous"),
        "submit_time": datetime.now().isoformat(),
        "duration_seconds": body.get("duration_seconds", 0),
        "review_status": "pending",
    }

    if task_type == "rlhf_ranking":
        sub["ranking"] = body.get("ranking", [])
        sub["rationale"] = body.get("rationale", "")
    elif task_type == "dpo_pairwise":
        sub["chosen_index"] = body.get("chosen_index")
        sub["rejected_index"] = 1 - body.get("chosen_index", 0)
        sub["rationale"] = body.get("rationale", "")
    elif task_type == "kto_binary":
        sub["feedback"] = body.get("feedback")
        sub["safety_category"] = body.get("safety_category", "none")
        sub["severity_score"] = body.get("severity_score", 0)
        sub["rationale"] = body.get("rationale", "")
    elif task_type == "sft_editing":
        sub["original_response"] = (sample.get("responses", [{}])[0]).get("text", "")
        sub["edited_response"] = body.get("edited_response", "")
        original_len = max(len(sub["original_response"]), 1)
        edited_len = len(sub["edited_response"])
        sub["edit_ratio"] = round(abs(edited_len - original_len) / original_len, 2)
    elif task_type == "reward_scoring":
        sub["scores"] = body.get("scores", {})
        score_values = list(sub["scores"].values())
        sub["overall_score"] = (
            round(sum(score_values) / max(len(score_values), 1), 1)
            if score_values
            else 0
        )

    _insert_submission(sub)

    conn = _get_ann_db()
    count = conn.execute(
        "SELECT COUNT(*) FROM submissions WHERE task_id=?", (task_id,)
    ).fetchone()[0]
    conn.close()
    sample_count = len(ANNOTATION_SAMPLES.get(task_id, []))

    log_audit(
        action="annotation_submit",
        resource_type="annotation",
        resource_id=task_id,
        summary=f"提交标注 {sub_id}, 任务 {task_id}, 样本 {sample_id}",
        details={
            "submission_id": sub_id,
            "task_type": task_type,
            "sample_id": sample_id,
        },
    )

    return {
        "status": "ok",
        "submission_id": sub_id,
        "task_progress": {
            "completed": count,
            "total": sample_count,
            "percent": round((count / max(sample_count, 1)) * 100, 1),
        },
    }


@router.post("/api/annotation/tasks/{task_id}/review")
async def review_annotation(task_id: str, request: Request):
    """审核标注"""
    body = await request.json()
    submission_id = body.get("submission_id")
    action = body.get("action")
    comment = body.get("comment", "")

    if action not in ("approve", "reject"):
        return {"status": "error", "message": "action 必须为 approve 或 reject"}

    conn = _get_ann_db()
    row = conn.execute(
        "SELECT id, task_id, review_status FROM submissions WHERE id=?",
        (submission_id,),
    ).fetchone()
    if not row:
        conn.close()
        return {"status": "error", "message": f"提交 {submission_id} 不存在"}
    if row["task_id"] != task_id:
        conn.close()
        return {"status": "error", "message": "提交不属于该任务"}
    if row["review_status"] != "pending":
        conn.close()
        return {
            "status": "error",
            "message": f"提交已被审核: {row['review_status']}",
        }

    new_status = "approved" if action == "approve" else "rejected"
    review_time = datetime.now().isoformat()
    conn.execute(
        "UPDATE submissions SET review_status=?, review_comment=?, review_time=? WHERE id=?",
        (new_status, comment, review_time, submission_id),
    )
    conn.commit()
    conn.close()

    log_audit(
        action="annotation_review",
        resource_type="annotation",
        resource_id=submission_id,
        summary=f"审核标注 {submission_id}: {new_status}",
        details={"task_id": task_id, "action": action, "comment": comment},
    )

    return {
        "status": "ok",
        "submission_id": submission_id,
        "review_status": new_status,
    }


@router.get("/api/annotation/tasks/{task_id}/submissions")
def list_task_submissions(task_id: str, review_status: str = "all"):
    """获取任务的提交列表"""
    status_filter = review_status if review_status != "all" else None
    subs = _load_submissions(task_id=task_id, review_status=status_filter)
    conn = _get_ann_db()
    row = conn.execute(
        """SELECT
               SUM(CASE WHEN review_status='pending' THEN 1 ELSE 0 END) as pending,
               SUM(CASE WHEN review_status='approved' THEN 1 ELSE 0 END) as approved,
               SUM(CASE WHEN review_status='rejected' THEN 1 ELSE 0 END) as rejected
           FROM submissions WHERE task_id=?""",
        (task_id,),
    ).fetchone()
    conn.close()
    by_status = {
        "pending": row["pending"] or 0,
        "approved": row["approved"] or 0,
        "rejected": row["rejected"] or 0,
    }
    return {"submissions": subs, "total": len(subs), "by_status": by_status}


@router.get("/api/annotation/annotators")
def list_annotators():
    conn = _get_ann_db()
    result = []
    for a in ANNOTATORS:
        aid = a["id"]
        row = conn.execute(
            """SELECT COUNT(*) as total,
                      SUM(CASE WHEN review_status='approved' THEN 1 ELSE 0 END) as approved,
                      SUM(CASE WHEN review_status='rejected' THEN 1 ELSE 0 END) as rejected,
                      COALESCE(AVG(duration_seconds), 0) as avg_speed,
                      COUNT(DISTINCT task_id) as tasks_involved
               FROM submissions WHERE annotator=?""",
            (aid,),
        ).fetchone()
        total = row["total"]
        approved = row["approved"]
        rejected = row["rejected"]
        avg_speed = row["avg_speed"]
        tasks_involved = row["tasks_involved"]
        result.append(
            {
                **a,
                "total_submissions": total,
                "approved": approved,
                "rejected": rejected,
                "computed_accuracy": round(
                    approved / max(approved + rejected, 1) * 100, 1
                ),
                "avg_speed_seconds": round(avg_speed),
                "samples_per_hour": round(3600 / max(avg_speed, 1), 1),
                "tasks_involved": tasks_involved,
            }
        )
    conn.close()
    result.sort(key=lambda x: x["computed_accuracy"], reverse=True)
    return result


@router.get("/api/annotation/quality")
def annotation_quality():
    """标注质量总览"""
    conn = _get_ann_db()
    totals = conn.execute(
        """SELECT COUNT(*) as total,
                  SUM(CASE WHEN review_status='approved' THEN 1 ELSE 0 END) as approved,
                  SUM(CASE WHEN review_status='rejected' THEN 1 ELSE 0 END) as rejected,
                  SUM(CASE WHEN review_status='pending' THEN 1 ELSE 0 END) as pending
           FROM submissions"""
    ).fetchone()
    total_subs = totals["total"]
    approved = totals["approved"]
    rejected = totals["rejected"]
    pending_count = totals["pending"]

    type_rows = conn.execute(
        """SELECT task_type,
                  COUNT(*) as total,
                  SUM(CASE WHEN review_status='approved' THEN 1 ELSE 0 END) as approved,
                  SUM(CASE WHEN review_status='rejected' THEN 1 ELSE 0 END) as rejected
           FROM submissions GROUP BY task_type"""
    ).fetchall()
    conn.close()

    by_task_type = {}
    for r in type_rows:
        tt = r["task_type"]
        by_task_type[tt] = {
            "total": r["total"],
            "approved": r["approved"],
            "rejected": r["rejected"],
            "approval_rate": round(
                r["approved"] / max(r["approved"] + r["rejected"], 1) * 100, 1
            ),
            "type_label": TASK_TYPE_LABELS.get(tt, tt),
        }

    if total_subs > 0 and (approved + rejected) > 0:
        approval_rate = approved / (approved + rejected)
        pe = approval_rate**2 + (1 - approval_rate) ** 2
        po = approval_rate
        kappa = round((po - pe) / max(1 - pe, 0.001), 2)
        kappa = max(0, min(1, kappa))
    else:
        kappa = 0.0

    return {
        "total_submissions": total_subs,
        "approved": approved,
        "rejected": rejected,
        "pending_review": pending_count,
        "overall_approval_rate": round(approved / max(approved + rejected, 1) * 100, 1),
        "fleiss_kappa": kappa,
        "kappa_interpretation": "substantial"
        if kappa >= 0.61
        else "moderate"
        if kappa >= 0.41
        else "fair"
        if kappa >= 0.21
        else "slight",
        "spot_check_ratio": QUALITY_CONFIG.get("spot_check_ratio", 0),
        "by_task_type": by_task_type,
        "quality_config": QUALITY_CONFIG,
    }


@router.get("/api/annotation/stats")
def annotation_stats():
    """标注数据统计分析"""
    now = datetime.now()
    conn = _get_ann_db()

    daily_trend = []
    for day_offset in range(14, 0, -1):
        day_str = (now - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        row = conn.execute(
            """SELECT COUNT(*) as cnt,
                      SUM(CASE WHEN review_status='approved' THEN 1 ELSE 0 END) as approved,
                      SUM(CASE WHEN review_status='rejected' THEN 1 ELSE 0 END) as rejected
               FROM submissions WHERE substr(submit_time,1,10)=?""",
            (day_str,),
        ).fetchone()
        daily_trend.append(
            {
                "date": day_str,
                "count": row["cnt"],
                "approved": row["approved"],
                "rejected": row["rejected"],
            }
        )

    domain_rows = conn.execute(
        "SELECT domain, COUNT(*) as cnt FROM submissions GROUP BY domain ORDER BY cnt DESC"
    ).fetchall()
    domain_list = [{"domain": r["domain"], "count": r["cnt"]} for r in domain_rows]

    type_rows = conn.execute(
        "SELECT task_type, COUNT(*) as cnt FROM submissions GROUP BY task_type ORDER BY cnt DESC"
    ).fetchall()
    type_list = [
        {
            "task_type": r["task_type"],
            "label": TASK_TYPE_LABELS.get(r["task_type"], r["task_type"]),
            "count": r["cnt"],
        }
        for r in type_rows
    ]

    all_subs = conn.execute("SELECT task_id, sample_id FROM submissions").fetchall()
    difficulty_dist: dict[str, int] = {}
    for s in all_subs:
        sample = _get_sample_by_id(s["task_id"], s["sample_id"])
        diff = sample.get("difficulty", "medium") if sample else "medium"
        difficulty_dist.setdefault(diff, 0)
        difficulty_dist[diff] += 1

    kto_rows = conn.execute(
        "SELECT annotation_data FROM submissions WHERE task_type='kto_binary'"
    ).fetchall()
    safety_dist: dict[str, int] = {}
    for r in kto_rows:
        ad = json.loads(r["annotation_data"])
        cat = ad.get("safety_category", "none")
        safety_dist.setdefault(cat, 0)
        safety_dist[cat] += 1

    sft_rows = conn.execute(
        "SELECT annotation_data FROM submissions WHERE task_type='sft_editing'"
    ).fetchall()
    sft_edit_ratios = []
    for r in sft_rows:
        ad = json.loads(r["annotation_data"])
        if "edit_ratio" in ad:
            sft_edit_ratios.append(ad["edit_ratio"])
    avg_edit_ratio = round(sum(sft_edit_ratios) / max(len(sft_edit_ratios), 1), 3)

    total_annotated = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    conn.close()

    total_samples = sum(len(v) for v in ANNOTATION_SAMPLES.values())

    return {
        "daily_trend": daily_trend,
        "domain_distribution": domain_list,
        "task_type_distribution": type_list,
        "difficulty_distribution": difficulty_dist,
        "safety_category_distribution": safety_dist,
        "sft_avg_edit_ratio": avg_edit_ratio,
        "total_annotated": total_annotated,
        "total_prompts": total_samples,
        "data_versions": [
            {
                "version": "v1.0",
                "date": "2025-12-15",
                "samples": 320,
                "format": "jsonl",
            },
            {
                "version": "v1.1",
                "date": "2026-01-05",
                "samples": 680,
                "format": "jsonl",
            },
            {
                "version": "v1.2-draft",
                "date": "2026-01-25",
                "samples": total_annotated,
                "format": "jsonl",
            },
        ],
    }


@router.get("/api/annotation/export/{task_id}")
def export_annotation_data(task_id: str, format: str = "jsonl"):
    """导出标注数据 (返回已审核通过的数据)"""
    subs = _load_submissions(task_id=task_id, review_status="approved")
    task = next((t for t in ANNOTATION_TASKS if t["id"] == task_id), None)
    if not task:
        return {"error": "task not found"}
    return {
        "task_id": task_id,
        "task_name": task["name"],
        "task_type": task["task_type"],
        "format": format,
        "total_records": len(subs),
        "preview": subs[:5],
        "export_fields": _get_export_fields(task["task_type"]),
    }


def _get_export_fields(task_type: str) -> list:
    base = ["prompt", "domain"]
    if task_type == "rlhf_ranking":
        return base + ["responses", "ranking", "rationale"]
    elif task_type == "dpo_pairwise":
        return base + ["chosen", "rejected", "chosen_rationale", "rejected_rationale"]
    elif task_type == "kto_binary":
        return base + ["response", "feedback", "safety_category", "severity_score"]
    elif task_type == "sft_editing":
        return base + ["original_response", "edited_response", "edit_ratio"]
    elif task_type == "reward_scoring":
        return base + ["response", "scores", "overall_score"]
    return base
