"""
DataOps Studio — 数据运维平台 API 后端
启动: uvicorn main:app --reload --port 8000
"""
import os
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

import yaml
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

load_dotenv()

ARK_API_KEY = os.getenv("ARK_API_KEY", "")
ARK_ENDPOINT_ID = os.getenv("ARK_ENDPOINT_ID", "")

app = FastAPI(title="DataOps Studio API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# 加载 YAML 配置
# ---------------------------------------------------------------------------
CONFIG_DIR = Path(__file__).parent / "configs"

def _load_yaml(name: str):
    with open(CONFIG_DIR / name, encoding="utf-8") as f:
        return yaml.safe_load(f)

_pipelines_cfg = _load_yaml("pipelines.yaml")
_quality_cfg = _load_yaml("quality.yaml")
_permission_cfg = _load_yaml("permission.yaml")

PIPELINES = _pipelines_cfg["pipelines"]
QUALITY_RULES = _quality_cfg["rules"]

# ---------------------------------------------------------------------------
# 模拟数据生成 (确定性随机，每次启动数据一致)
# ---------------------------------------------------------------------------
random.seed(42)

TEAM_NAMES = {
    "data-platform": "数据平台组",
    "fintech-data": "金融数据组",
    "user-growth": "用户增长组",
    "risk-engine": "风控引擎组",
    "marketing-analytics": "营销分析组",
    "supply-chain": "供应链组",
}

PIPELINE_SUCCESS_RATE = {
    "orders_daily": 0.95,
    "payments_hourly": 0.91,
    "user_profile_sync": 0.88,
    "risk_score_calc": 0.70,
    "marketing_attribution": 0.93,
    "inventory_snapshot": 0.0,  # paused
}

PIPELINE_AVG_DURATION = {
    "orders_daily": 45,
    "payments_hourly": 15,
    "user_profile_sync": 75,
    "risk_score_calc": 100,
    "marketing_attribution": 35,
    "inventory_snapshot": 0,
}

PIPELINE_COST_PER_RUN = {
    "orders_daily": 12.5,
    "payments_hourly": 3.2,
    "user_profile_sync": 18.0,
    "risk_score_calc": 25.0,
    "marketing_attribution": 8.5,
    "inventory_snapshot": 0.0,
}


def _generate_executions():
    """生成过去 30 天的 pipeline 执行历史"""
    executions = []
    now = datetime.now().replace(second=0, microsecond=0)
    for p in PIPELINES:
        pid = p["id"]
        if p["status"] == "paused":
            continue
        schedule = p["schedule"]
        # 简化: daily → 1次/天, hourly → 24次/天, weekly → 1次/周
        if "* * * *" in schedule and schedule.startswith("0 ") is False and schedule.startswith("15 "):
            runs_per_day = 24
        elif "* * 1" in schedule:
            runs_per_day = 1 / 7
        else:
            runs_per_day = 1

        for day_offset in range(30, 0, -1):
            day = now - timedelta(days=day_offset)
            n_runs = max(1, int(runs_per_day)) if runs_per_day >= 1 else (1 if day_offset % 7 == 0 else 0)
            for run_idx in range(n_runs):
                success = random.random() < PIPELINE_SUCCESS_RATE.get(pid, 0.9)
                base_dur = PIPELINE_AVG_DURATION.get(pid, 30)
                duration = max(5, int(base_dur * (0.7 + random.random() * 0.6)))
                cost = round(PIPELINE_COST_PER_RUN.get(pid, 5) * (0.8 + random.random() * 0.4), 2)
                rows_processed = random.randint(10000, 500000) if success else random.randint(0, 5000)
                start_time = day.replace(hour=random.randint(0, 23), minute=random.randint(0, 59))
                exec_id = hashlib.md5(f"{pid}-{start_time.isoformat()}-{run_idx}".encode()).hexdigest()[:12]
                executions.append({
                    "id": exec_id,
                    "pipeline_id": pid,
                    "pipeline_name": p["name"],
                    "start_time": start_time.isoformat(),
                    "end_time": (start_time + timedelta(minutes=duration)).isoformat(),
                    "duration_minutes": duration,
                    "status": "success" if success else random.choice(["failed", "timeout"]),
                    "rows_processed": rows_processed,
                    "cost_yuan": cost,
                    "owner": p["owner"],
                })
    executions.sort(key=lambda x: x["start_time"], reverse=True)
    return executions


def _generate_quality_checks():
    """基于质量规则生成检查结果"""
    checks = []
    now = datetime.now()
    for rule in QUALITY_RULES:
        if not rule["enabled"]:
            continue
        for day_offset in range(30, 0, -1):
            day = now - timedelta(days=day_offset)
            passed = random.random() > 0.12
            value = 0.0 if passed else round(random.uniform(0.001, 0.05), 4)
            checks.append({
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "pipeline_id": rule["pipeline_id"],
                "target_table": rule["target_table"],
                "check_type": rule["check_type"],
                "severity": rule["severity"],
                "check_time": day.replace(hour=5, minute=random.randint(0, 59)).isoformat(),
                "passed": passed,
                "violation_ratio": value,
                "threshold": rule["threshold"],
            })
    checks.sort(key=lambda x: x["check_time"], reverse=True)
    return checks


def _generate_alerts(executions, quality_checks):
    """从执行失败和质量违规中提取告警"""
    alerts = []
    for ex in executions:
        if ex["status"] != "success":
            alerts.append({
                "id": f"ALT-{ex['id'][:8]}",
                "type": "execution_failure",
                "severity": "critical" if ex["status"] == "failed" else "warning",
                "pipeline_id": ex["pipeline_id"],
                "pipeline_name": ex["pipeline_name"],
                "message": f"管道 [{ex['pipeline_name']}] 执行{ex['status']}, 耗时{ex['duration_minutes']}分钟",
                "time": ex["end_time"],
                "resolved": random.random() > 0.3,
            })
    for qc in quality_checks:
        if not qc["passed"]:
            alerts.append({
                "id": f"ALT-Q-{qc['rule_id']}-{qc['check_time'][:10]}",
                "type": "quality_violation",
                "severity": qc["severity"],
                "pipeline_id": qc["pipeline_id"],
                "pipeline_name": qc["rule_name"],
                "message": f"质量规则 [{qc['rule_name']}] 违反, 违规比率 {qc['violation_ratio']}",
                "time": qc["check_time"],
                "resolved": random.random() > 0.4,
            })
    alerts.sort(key=lambda x: x["time"], reverse=True)
    return alerts


# 生成数据
EXECUTIONS = _generate_executions()
QUALITY_CHECKS = _generate_quality_checks()
ALERTS = _generate_alerts(EXECUTIONS, QUALITY_CHECKS)


# ---------------------------------------------------------------------------
# API 路由
# ---------------------------------------------------------------------------

@app.get("/api/dashboard/stats")
def dashboard_stats():
    active_count = sum(1 for p in PIPELINES if p["status"] == "active")
    total_execs_today = sum(1 for e in EXECUTIONS
                           if e["start_time"][:10] == datetime.now().strftime("%Y-%m-%d"))
    # 使用最近一天有数据的日期
    if total_execs_today == 0:
        latest_date = EXECUTIONS[0]["start_time"][:10] if EXECUTIONS else ""
        total_execs_today = sum(1 for e in EXECUTIONS if e["start_time"][:10] == latest_date)

    failed_checks = sum(1 for qc in QUALITY_CHECKS[-200:] if not qc["passed"])
    total_checks = min(200, len(QUALITY_CHECKS))
    quality_score = round((1 - failed_checks / max(total_checks, 1)) * 100, 1)

    total_cost = round(sum(e["cost_yuan"] for e in EXECUTIONS), 2)
    total_rows = sum(e["rows_processed"] for e in EXECUTIONS)
    unresolved_alerts = sum(1 for a in ALERTS if not a["resolved"])

    return {
        "active_pipelines": active_count,
        "total_pipelines": len(PIPELINES),
        "paused_pipelines": sum(1 for p in PIPELINES if p["status"] == "paused"),
        "degraded_pipelines": sum(1 for p in PIPELINES if p["status"] == "degraded"),
        "executions_today": total_execs_today,
        "quality_score": quality_score,
        "total_cost_30d": total_cost,
        "total_rows_30d": total_rows,
        "unresolved_alerts": unresolved_alerts,
        "total_quality_rules": len(QUALITY_RULES),
        "enabled_rules": sum(1 for r in QUALITY_RULES if r["enabled"]),
        "disabled_rules": sum(1 for r in QUALITY_RULES if not r["enabled"]),
    }


@app.get("/api/dashboard/execution-trend")
def execution_trend():
    """最近 14 天每天的执行成功/失败数"""
    now = datetime.now()
    trend = []
    for day_offset in range(14, 0, -1):
        day_str = (now - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        day_execs = [e for e in EXECUTIONS if e["start_time"][:10] == day_str]
        trend.append({
            "date": day_str,
            "success": sum(1 for e in day_execs if e["status"] == "success"),
            "failed": sum(1 for e in day_execs if e["status"] != "success"),
            "total": len(day_execs),
        })
    return trend


@app.get("/api/dashboard/alerts")
def dashboard_alerts(limit: int = 20):
    return ALERTS[:limit]


@app.get("/api/pipelines")
def list_pipelines():
    result = []
    for p in PIPELINES:
        pid = p["id"]
        recent = [e for e in EXECUTIONS if e["pipeline_id"] == pid][:30]
        success_rate = (sum(1 for e in recent if e["status"] == "success") / max(len(recent), 1)) * 100
        avg_duration = sum(e["duration_minutes"] for e in recent) / max(len(recent), 1)
        total_cost = sum(e["cost_yuan"] for e in recent)
        last_exec = recent[0] if recent else None
        result.append({
            **p,
            "success_rate_30d": round(success_rate, 1),
            "avg_duration_30d": round(avg_duration, 1),
            "total_cost_30d": round(total_cost, 2),
            "last_execution": last_exec,
            "team_name": TEAM_NAMES.get(p["owner"], p["owner"]),
        })
    return result


@app.get("/api/pipelines/{pipeline_id}")
def get_pipeline(pipeline_id: str):
    for p in PIPELINES:
        if p["id"] == pipeline_id:
            recent = [e for e in EXECUTIONS if e["pipeline_id"] == pipeline_id][:50]
            return {**p, "recent_executions": recent,
                    "team_name": TEAM_NAMES.get(p["owner"], p["owner"])}
    return {"error": "not found"}


@app.get("/api/pipelines/{pipeline_id}/executions")
def pipeline_executions(pipeline_id: str, limit: int = 50):
    return [e for e in EXECUTIONS if e["pipeline_id"] == pipeline_id][:limit]


@app.get("/api/quality/rules")
def list_quality_rules():
    result = []
    for r in QUALITY_RULES:
        recent_checks = [qc for qc in QUALITY_CHECKS if qc["rule_id"] == r["id"]][:30]
        pass_rate = (sum(1 for qc in recent_checks if qc["passed"]) / max(len(recent_checks), 1)) * 100
        result.append({
            **r,
            "pass_rate_30d": round(pass_rate, 1),
            "total_checks_30d": len(recent_checks),
            "recent_violations": sum(1 for qc in recent_checks if not qc["passed"]),
        })
    return result


@app.get("/api/quality/checks")
def list_quality_checks(limit: int = 100):
    return QUALITY_CHECKS[:limit]


@app.get("/api/quality/score-trend")
def quality_score_trend():
    """最近 14 天质量评分趋势"""
    now = datetime.now()
    trend = []
    for day_offset in range(14, 0, -1):
        day_str = (now - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        day_checks = [qc for qc in QUALITY_CHECKS if qc["check_time"][:10] == day_str]
        if day_checks:
            score = round((sum(1 for qc in day_checks if qc["passed"]) / len(day_checks)) * 100, 1)
        else:
            score = 0
        trend.append({"date": day_str, "score": score, "checks": len(day_checks)})
    return trend


@app.get("/api/cost/summary")
def cost_summary():
    total = sum(e["cost_yuan"] for e in EXECUTIONS)
    by_pipeline = {}
    for e in EXECUTIONS:
        pid = e["pipeline_id"]
        by_pipeline.setdefault(pid, {"pipeline_id": pid, "pipeline_name": e["pipeline_name"],
                                     "cost": 0, "runs": 0})
        by_pipeline[pid]["cost"] += e["cost_yuan"]
        by_pipeline[pid]["runs"] += 1
    for v in by_pipeline.values():
        v["cost"] = round(v["cost"], 2)
        v["avg_cost_per_run"] = round(v["cost"] / max(v["runs"], 1), 2)
    sorted_pipelines = sorted(by_pipeline.values(), key=lambda x: x["cost"], reverse=True)
    return {
        "total_cost_30d": round(total, 2),
        "avg_daily_cost": round(total / 30, 2),
        "by_pipeline": sorted_pipelines,
    }


@app.get("/api/cost/trend")
def cost_trend():
    now = datetime.now()
    trend = []
    for day_offset in range(30, 0, -1):
        day_str = (now - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        day_cost = sum(e["cost_yuan"] for e in EXECUTIONS if e["start_time"][:10] == day_str)
        trend.append({"date": day_str, "cost": round(day_cost, 2)})
    return trend


@app.get("/api/teams/stats")
def team_stats():
    """按团队统计"""
    teams = {}
    for p in PIPELINES:
        owner = p["owner"]
        teams.setdefault(owner, {
            "team_id": owner,
            "team_name": TEAM_NAMES.get(owner, owner),
            "pipeline_count": 0,
            "active_count": 0,
            "total_cost": 0.0,
            "total_runs": 0,
            "success_runs": 0,
            "total_rows": 0,
        })
        teams[owner]["pipeline_count"] += 1
        if p["status"] == "active":
            teams[owner]["active_count"] += 1

    for e in EXECUTIONS:
        owner = e["owner"]
        if owner in teams:
            teams[owner]["total_cost"] += e["cost_yuan"]
            teams[owner]["total_runs"] += 1
            teams[owner]["total_rows"] += e["rows_processed"]
            if e["status"] == "success":
                teams[owner]["success_runs"] += 1

    result = []
    for t in teams.values():
        t["total_cost"] = round(t["total_cost"], 2)
        t["success_rate"] = round(
            (t["success_runs"] / max(t["total_runs"], 1)) * 100, 1)
        # 质量评分: 该团队管道关联的质量规则通过率
        team_pipelines = [p["id"] for p in PIPELINES if p["owner"] == t["team_id"]]
        team_checks = [qc for qc in QUALITY_CHECKS if qc["pipeline_id"] in team_pipelines][:100]
        t["quality_score"] = round(
            (sum(1 for qc in team_checks if qc["passed"]) / max(len(team_checks), 1)) * 100, 1)
        result.append(t)

    result.sort(key=lambda x: x["quality_score"], reverse=True)
    return result


@app.get("/api/lineage")
def data_lineage():
    """数据血缘关系 — 从 pipeline 配置中提取"""
    nodes = set()
    edges = []
    for p in PIPELINES:
        target = p["target_table"]
        nodes.add(target)
        for src in p.get("source_tables", []):
            nodes.add(src)
            edges.append({"source": src, "target": target, "pipeline": p["name"],
                          "pipeline_id": p["id"], "status": p["status"]})
        for dep_id in p.get("dependencies", []):
            dep_pipe = next((pp for pp in PIPELINES if pp["id"] == dep_id), None)
            if dep_pipe:
                edges.append({"source": dep_pipe["target_table"], "target": target,
                              "pipeline": p["name"], "pipeline_id": p["id"],
                              "status": p["status"], "is_dependency": True})
    return {
        "nodes": [{"id": n, "type": "ods" if n.startswith("ods_") else "dw" if n.startswith("dw_") else "dm"}
                   for n in sorted(nodes)],
        "edges": edges,
    }


@app.get("/api/config/reload")
def reload_config():
    """热重载 YAML 配置"""
    global PIPELINES, QUALITY_RULES, _pipelines_cfg, _quality_cfg, _annotation_cfg, ANNOTATION_TASKS, ANNOTATORS, QUALITY_CONFIG, ANNOTATION_SAMPLES
    _pipelines_cfg = _load_yaml("pipelines.yaml")
    _quality_cfg = _load_yaml("quality.yaml")
    _annotation_cfg = _load_yaml("annotation.yaml")
    PIPELINES = _pipelines_cfg["pipelines"]
    QUALITY_RULES = _quality_cfg["rules"]
    ANNOTATION_TASKS = _annotation_cfg["annotation_tasks"]
    ANNOTATORS = _annotation_cfg["annotators"]
    QUALITY_CONFIG = _annotation_cfg["quality_config"]
    ANNOTATION_SAMPLES = {}
    for task_id, samples in _annotation_cfg.get("annotation_samples", {}).items():
        ANNOTATION_SAMPLES[task_id] = samples
    return {"status": "ok", "pipelines": len(PIPELINES), "quality_rules": len(QUALITY_RULES),
            "annotation_tasks": len(ANNOTATION_TASKS), "annotation_samples": sum(len(v) for v in ANNOTATION_SAMPLES.values())}


# ---------------------------------------------------------------------------
# RLHF / 后训练数据标注模块
# ---------------------------------------------------------------------------
_annotation_cfg = _load_yaml("annotation.yaml")
ANNOTATION_TASKS = _annotation_cfg["annotation_tasks"]
ANNOTATORS = _annotation_cfg["annotators"]
QUALITY_CONFIG = _annotation_cfg["quality_config"]

TASK_TYPE_LABELS = {
    "rlhf_ranking": "RLHF 偏好排序",
    "dpo_pairwise": "DPO 偏好对",
    "kto_binary": "KTO 二元反馈",
    "sft_editing": "SFT 数据改写",
    "reward_scoring": "Reward 评分",
}

# 从 YAML 加载样本
ANNOTATION_SAMPLES: dict[str, list[dict]] = {}
for _task_id, _samples in _annotation_cfg.get("annotation_samples", {}).items():
    ANNOTATION_SAMPLES[_task_id] = _samples

# 内存可变状态 (用户提交后追加, 重启清空)
ANNOTATION_SUBMISSIONS: list[dict] = []
_submission_counter = 0


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


_validate_annotation_config()


def _get_sample_by_id(task_id: str, sample_id: str) -> dict | None:
    """根据 task_id 和 sample_id 查找样本"""
    for s in ANNOTATION_SAMPLES.get(task_id, []):
        if s["id"] == sample_id:
            return s
    return None


@app.get("/api/annotation/tasks")
def list_annotation_tasks():
    result = []
    for t in ANNOTATION_TASKS:
        tid = t["id"]
        subs = [s for s in ANNOTATION_SUBMISSIONS if s["task_id"] == tid]
        completed = len(subs)
        approved = sum(1 for s in subs if s["review_status"] == "approved")
        rejected = sum(1 for s in subs if s["review_status"] == "rejected")
        pending = sum(1 for s in subs if s["review_status"] == "pending")
        avg_duration = sum(s["duration_seconds"] for s in subs) / max(len(subs), 1)
        sample_count = len(ANNOTATION_SAMPLES.get(tid, []))
        result.append({
            **t,
            "type_label": TASK_TYPE_LABELS.get(t["task_type"], t["task_type"]),
            "sample_count": sample_count,
            "total_samples": sample_count,
            "completed_samples": completed,
            "progress_percent": round((completed / max(sample_count, 1)) * 100, 1),
            "approved_count": approved,
            "rejected_count": rejected,
            "pending_review": pending,
            "approval_rate": round(approved / max(approved + rejected, 1) * 100, 1),
            "avg_duration_seconds": round(avg_duration),
            "annotator_names": [a["name"] for a in ANNOTATORS
                                if a["id"] in t.get("assigned_annotators", [])],
        })
    return result


@app.get("/api/annotation/tasks/{task_id}")
def get_annotation_task(task_id: str):
    for t in ANNOTATION_TASKS:
        if t["id"] == task_id:
            subs = [s for s in ANNOTATION_SUBMISSIONS if s["task_id"] == task_id]
            sample_count = len(ANNOTATION_SAMPLES.get(task_id, []))
            return {**t, "submissions": subs[:50],
                    "sample_count": sample_count,
                    "type_label": TASK_TYPE_LABELS.get(t["task_type"], t["task_type"])}
    return {"error": "not found"}


@app.get("/api/annotation/tasks/{task_id}/samples")
def get_task_samples(task_id: str, limit: int = 50):
    """获取任务的标注样本（含 prompt 和候选 responses）"""
    task = next((t for t in ANNOTATION_TASKS if t["id"] == task_id), None)
    if not task:
        return {"error": "not found"}
    task_samples = ANNOTATION_SAMPLES.get(task_id, [])
    samples = []
    for sp in task_samples[:limit]:
        existing_sub = next((s for s in ANNOTATION_SUBMISSIONS
                             if s["task_id"] == task_id and s["sample_id"] == sp["id"]), None)
        samples.append({
            **sp,
            "annotation": existing_sub,
            "annotated": existing_sub is not None,
        })
    return {"samples": samples, "total": len(task_samples), "task_id": task_id}


@app.post("/api/annotation/tasks/{task_id}/submit")
async def submit_annotation(task_id: str, request: Request):
    """提交标注"""
    global _submission_counter
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

    # 检查是否重复提交
    existing = next((s for s in ANNOTATION_SUBMISSIONS
                     if s["task_id"] == task_id and s["sample_id"] == sample_id), None)
    if existing:
        return {"status": "error", "message": f"样本 {sample_id} 已被标注"}

    _submission_counter += 1
    sub_id = f"SUB-{task_id}-{_submission_counter:04d}"
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

    # 按 task_type 解析标注数据
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
        sub["overall_score"] = round(sum(score_values) / max(len(score_values), 1), 1) if score_values else 0

    ANNOTATION_SUBMISSIONS.append(sub)

    # 计算任务进度
    task_subs = [s for s in ANNOTATION_SUBMISSIONS if s["task_id"] == task_id]
    sample_count = len(ANNOTATION_SAMPLES.get(task_id, []))

    return {
        "status": "ok",
        "submission_id": sub_id,
        "task_progress": {
            "completed": len(task_subs),
            "total": sample_count,
            "percent": round((len(task_subs) / max(sample_count, 1)) * 100, 1),
        },
    }


@app.post("/api/annotation/tasks/{task_id}/review")
async def review_annotation(task_id: str, request: Request):
    """审核标注"""
    body = await request.json()
    submission_id = body.get("submission_id")
    action = body.get("action")  # "approve" | "reject"
    comment = body.get("comment", "")

    if action not in ("approve", "reject"):
        return {"status": "error", "message": "action 必须为 approve 或 reject"}

    sub = next((s for s in ANNOTATION_SUBMISSIONS if s["id"] == submission_id), None)
    if not sub:
        return {"status": "error", "message": f"提交 {submission_id} 不存在"}
    if sub["task_id"] != task_id:
        return {"status": "error", "message": "提交不属于该任务"}
    if sub["review_status"] != "pending":
        return {"status": "error", "message": f"提交已被审核: {sub['review_status']}"}

    sub["review_status"] = "approved" if action == "approve" else "rejected"
    sub["review_comment"] = comment
    sub["review_time"] = datetime.now().isoformat()

    return {
        "status": "ok",
        "submission_id": submission_id,
        "review_status": sub["review_status"],
    }


@app.get("/api/annotation/tasks/{task_id}/submissions")
def list_task_submissions(task_id: str, review_status: str = "all"):
    """获取任务的提交列表"""
    subs = [s for s in ANNOTATION_SUBMISSIONS if s["task_id"] == task_id]
    if review_status != "all":
        subs = [s for s in subs if s["review_status"] == review_status]
    by_status = {
        "pending": sum(1 for s in ANNOTATION_SUBMISSIONS if s["task_id"] == task_id and s["review_status"] == "pending"),
        "approved": sum(1 for s in ANNOTATION_SUBMISSIONS if s["task_id"] == task_id and s["review_status"] == "approved"),
        "rejected": sum(1 for s in ANNOTATION_SUBMISSIONS if s["task_id"] == task_id and s["review_status"] == "rejected"),
    }
    return {"submissions": subs, "total": len(subs), "by_status": by_status}


@app.get("/api/annotation/annotators")
def list_annotators():
    result = []
    for a in ANNOTATORS:
        aid = a["id"]
        subs = [s for s in ANNOTATION_SUBMISSIONS if s["annotator"] == aid]
        approved = sum(1 for s in subs if s["review_status"] == "approved")
        rejected = sum(1 for s in subs if s["review_status"] == "rejected")
        avg_speed = sum(s["duration_seconds"] for s in subs) / max(len(subs), 1)
        tasks_involved = len(set(s["task_id"] for s in subs))
        result.append({
            **a,
            "total_submissions": len(subs),
            "approved": approved,
            "rejected": rejected,
            "computed_accuracy": round(approved / max(approved + rejected, 1) * 100, 1),
            "avg_speed_seconds": round(avg_speed),
            "samples_per_hour": round(3600 / max(avg_speed, 1), 1),
            "tasks_involved": tasks_involved,
        })
    result.sort(key=lambda x: x["computed_accuracy"], reverse=True)
    return result


@app.get("/api/annotation/quality")
def annotation_quality():
    """标注质量总览: 一致性、通过率、抽检结果"""
    total_subs = len(ANNOTATION_SUBMISSIONS)
    approved = sum(1 for s in ANNOTATION_SUBMISSIONS if s["review_status"] == "approved")
    rejected = sum(1 for s in ANNOTATION_SUBMISSIONS if s["review_status"] == "rejected")
    pending = sum(1 for s in ANNOTATION_SUBMISSIONS if s["review_status"] == "pending")

    by_task_type = {}
    for s in ANNOTATION_SUBMISSIONS:
        tt = s["task_type"]
        by_task_type.setdefault(tt, {"total": 0, "approved": 0, "rejected": 0})
        by_task_type[tt]["total"] += 1
        if s["review_status"] == "approved":
            by_task_type[tt]["approved"] += 1
        elif s["review_status"] == "rejected":
            by_task_type[tt]["rejected"] += 1
    for tt, v in by_task_type.items():
        v["approval_rate"] = round(v["approved"] / max(v["approved"] + v["rejected"], 1) * 100, 1)
        v["type_label"] = TASK_TYPE_LABELS.get(tt, tt)

    # 基于真实审核率计算 kappa 近似值
    if total_subs > 0 and (approved + rejected) > 0:
        approval_rate = approved / (approved + rejected)
        pe = approval_rate ** 2 + (1 - approval_rate) ** 2
        po = approval_rate  # 近似观测一致率
        kappa = round((po - pe) / max(1 - pe, 0.001), 2)
        kappa = max(0, min(1, kappa))
    else:
        kappa = 0.0

    return {
        "total_submissions": total_subs,
        "approved": approved,
        "rejected": rejected,
        "pending_review": pending,
        "overall_approval_rate": round(approved / max(approved + rejected, 1) * 100, 1),
        "fleiss_kappa": kappa,
        "kappa_interpretation": "substantial" if kappa >= 0.61 else "moderate" if kappa >= 0.41 else "fair" if kappa >= 0.21 else "slight",
        "spot_check_ratio": QUALITY_CONFIG["spot_check_ratio"],
        "by_task_type": by_task_type,
        "quality_config": QUALITY_CONFIG,
    }


@app.get("/api/annotation/stats")
def annotation_stats():
    """标注数据统计分析"""
    now = datetime.now()

    # 每日标注量趋势
    daily_trend = []
    for day_offset in range(14, 0, -1):
        day_str = (now - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        day_subs = [s for s in ANNOTATION_SUBMISSIONS if s["submit_time"][:10] == day_str]
        daily_trend.append({
            "date": day_str,
            "count": len(day_subs),
            "approved": sum(1 for s in day_subs if s["review_status"] == "approved"),
            "rejected": sum(1 for s in day_subs if s["review_status"] == "rejected"),
        })

    # 按 domain 分布
    domain_dist = {}
    for s in ANNOTATION_SUBMISSIONS:
        d = s.get("domain", "unknown")
        domain_dist.setdefault(d, 0)
        domain_dist[d] += 1
    domain_list = [{"domain": k, "count": v} for k, v in
                   sorted(domain_dist.items(), key=lambda x: x[1], reverse=True)]

    # 按 task_type 分布
    type_dist = {}
    for s in ANNOTATION_SUBMISSIONS:
        tt = s["task_type"]
        type_dist.setdefault(tt, 0)
        type_dist[tt] += 1
    type_list = [{"task_type": k, "label": TASK_TYPE_LABELS.get(k, k), "count": v}
                 for k, v in sorted(type_dist.items(), key=lambda x: x[1], reverse=True)]

    # 难度分布 — 从 YAML 样本中查找
    difficulty_dist = {}
    for s in ANNOTATION_SUBMISSIONS:
        sample = _get_sample_by_id(s["task_id"], s["sample_id"])
        diff = sample.get("difficulty", "medium") if sample else "medium"
        difficulty_dist.setdefault(diff, 0)
        difficulty_dist[diff] += 1

    # 安全类别分布 (KTO)
    safety_dist = {}
    for s in ANNOTATION_SUBMISSIONS:
        if s["task_type"] == "kto_binary":
            cat = s.get("safety_category", "none")
            safety_dist.setdefault(cat, 0)
            safety_dist[cat] += 1

    # SFT 编辑比率分布
    sft_edit_ratios = [s["edit_ratio"] for s in ANNOTATION_SUBMISSIONS
                       if s["task_type"] == "sft_editing" and "edit_ratio" in s]
    avg_edit_ratio = round(sum(sft_edit_ratios) / max(len(sft_edit_ratios), 1), 3)

    # 总样本数 (来自 YAML)
    total_samples = sum(len(v) for v in ANNOTATION_SAMPLES.values())

    return {
        "daily_trend": daily_trend,
        "domain_distribution": domain_list,
        "task_type_distribution": type_list,
        "difficulty_distribution": difficulty_dist,
        "safety_category_distribution": safety_dist,
        "sft_avg_edit_ratio": avg_edit_ratio,
        "total_annotated": len(ANNOTATION_SUBMISSIONS),
        "total_prompts": total_samples,
        "data_versions": [
            {"version": "v1.0", "date": "2025-12-15", "samples": 320, "format": "jsonl"},
            {"version": "v1.1", "date": "2026-01-05", "samples": 680, "format": "jsonl"},
            {"version": "v1.2-draft", "date": "2026-01-25", "samples": len(ANNOTATION_SUBMISSIONS), "format": "jsonl"},
        ],
    }


@app.get("/api/annotation/export/{task_id}")
def export_annotation_data(task_id: str, format: str = "jsonl"):
    """导出标注数据 (返回已审核通过的数据)"""
    subs = [s for s in ANNOTATION_SUBMISSIONS
            if s["task_id"] == task_id and s["review_status"] == "approved"]
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


# ---------------------------------------------------------------------------
# AI 助手 (火山引擎 Doubao API 代理)
# ---------------------------------------------------------------------------

AI_SYSTEM_PROMPT = """你是 DataOps Studio 的 AI 助手。你了解这个数据运维平台的所有功能：
- 数据管道管理：6 条核心管道（订单日聚合、支付流水、用户画像、风控评分、营销归因、库存快照）
- 数据质量监控：8 条质量规则，涵盖 NULL 检查、范围检查、唯一性检查、时效检查
- 成本分析：按管道和团队维度分析 30 天计算成本
- RLHF 数据标注：支持偏好排序、DPO 偏好对、KTO 二元反馈、SFT 数据改写、Reward 评分
- 团队：数据平台组、金融数据组、用户增长组、风控引擎组、营销分析组、供应链组

请用简洁专业的中文回答用户关于平台运维、数据质量、标注任务等方面的问题。"""


@app.post("/api/ai/chat")
async def ai_chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    if not ARK_API_KEY:
        return {"error": "AI 服务未配置"}

    api_messages = [{"role": "system", "content": AI_SYSTEM_PROMPT}] + messages

    async def stream_response():
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"https://ark.cn-beijing.volces.com/api/v3/chat/completions",
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
                    elif line == "data: [DONE]":
                        yield "data: [DONE]\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
