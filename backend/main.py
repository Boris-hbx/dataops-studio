"""
DataOps Studio — 大模型训练数据管理和探索平台 API 后端
启动: uvicorn main:app --reload --port 8000
"""

from datetime import datetime, timedelta
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_annotation import router as agent_annotation_router
from ai_chat import router as ai_chat_router
from data_insight import router as data_insight_router
from mock_data import TEAM_NAMES, generate_all
from quality_lab import router as quality_lab_router
from rlhf_annotation import (
    router as rlhf_annotation_router,
    init_annotation_config,
    reload_annotation_config,
)
from rlhf_lab import router as rlhf_lab_router
from roman_forum import router as roman_forum_router
from system_log import (
    router as system_log_router,
    LoggingMiddleware,
    log_audit,
)

app = FastAPI(title="DataOps Studio API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_annotation_router)
app.include_router(ai_chat_router)
app.include_router(quality_lab_router)
app.include_router(data_insight_router)
app.include_router(roman_forum_router)
app.include_router(rlhf_lab_router)
app.include_router(rlhf_annotation_router)
app.include_router(system_log_router)
app.add_middleware(LoggingMiddleware)

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
_annotation_cfg = _load_yaml("annotation.yaml")

PIPELINES = _pipelines_cfg["pipelines"]
QUALITY_RULES = _quality_cfg["rules"]

# 初始化 RLHF 标注模块
init_annotation_config(_annotation_cfg)

# 生成模拟数据
EXECUTIONS, QUALITY_CHECKS, ALERTS = generate_all(PIPELINES, QUALITY_RULES)


# ---------------------------------------------------------------------------
# API 路由
# ---------------------------------------------------------------------------


@app.get("/api/dashboard/stats")
def dashboard_stats():
    active_count = sum(1 for p in PIPELINES if p["status"] == "active")
    total_execs_today = sum(
        1
        for e in EXECUTIONS
        if e["start_time"][:10] == datetime.now().strftime("%Y-%m-%d")
    )
    if total_execs_today == 0:
        latest_date = EXECUTIONS[0]["start_time"][:10] if EXECUTIONS else ""
        total_execs_today = sum(
            1 for e in EXECUTIONS if e["start_time"][:10] == latest_date
        )

    failed_checks = sum(1 for qc in QUALITY_CHECKS[-200:] if not qc["passed"])
    total_checks = min(200, len(QUALITY_CHECKS))
    quality_score = round((1 - failed_checks / max(total_checks, 1)) * 100, 1)

    total_cost = round(sum(e["cost_yuan"] for e in EXECUTIONS), 2)
    total_tokens = sum(e["rows_processed"] for e in EXECUTIONS)
    unresolved_alerts = sum(1 for a in ALERTS if not a["resolved"])

    return {
        "active_pipelines": active_count,
        "total_pipelines": len(PIPELINES),
        "paused_pipelines": sum(1 for p in PIPELINES if p["status"] == "paused"),
        "degraded_pipelines": sum(1 for p in PIPELINES if p["status"] == "degraded"),
        "executions_today": total_execs_today,
        "quality_score": quality_score,
        "total_cost_30d": total_cost,
        "total_tokens_30d": total_tokens,
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
        trend.append(
            {
                "date": day_str,
                "success": sum(1 for e in day_execs if e["status"] == "success"),
                "failed": sum(1 for e in day_execs if e["status"] != "success"),
                "total": len(day_execs),
            }
        )
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
        success_rate = (
            sum(1 for e in recent if e["status"] == "success") / max(len(recent), 1)
        ) * 100
        avg_duration = sum(e["duration_minutes"] for e in recent) / max(len(recent), 1)
        total_cost = sum(e["cost_yuan"] for e in recent)
        last_exec = recent[0] if recent else None
        result.append(
            {
                **p,
                "success_rate_30d": round(success_rate, 1),
                "avg_duration_30d": round(avg_duration, 1),
                "total_cost_30d": round(total_cost, 2),
                "last_execution": last_exec,
                "team_name": TEAM_NAMES.get(p["owner"], p["owner"]),
            }
        )
    return result


@app.get("/api/pipelines/{pipeline_id}")
def get_pipeline(pipeline_id: str):
    for p in PIPELINES:
        if p["id"] == pipeline_id:
            recent = [e for e in EXECUTIONS if e["pipeline_id"] == pipeline_id][:50]
            return {
                **p,
                "recent_executions": recent,
                "team_name": TEAM_NAMES.get(p["owner"], p["owner"]),
            }
    return {"error": "not found"}


@app.get("/api/pipelines/{pipeline_id}/executions")
def pipeline_executions(pipeline_id: str, limit: int = 50):
    return [e for e in EXECUTIONS if e["pipeline_id"] == pipeline_id][:limit]


@app.get("/api/quality/rules")
def list_quality_rules():
    result = []
    for r in QUALITY_RULES:
        recent_checks = [qc for qc in QUALITY_CHECKS if qc["rule_id"] == r["id"]][:30]
        pass_rate = (
            sum(1 for qc in recent_checks if qc["passed"]) / max(len(recent_checks), 1)
        ) * 100
        result.append(
            {
                **r,
                "pass_rate_30d": round(pass_rate, 1),
                "total_checks_30d": len(recent_checks),
                "recent_violations": sum(1 for qc in recent_checks if not qc["passed"]),
            }
        )
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
            score = round(
                (sum(1 for qc in day_checks if qc["passed"]) / len(day_checks)) * 100,
                1,
            )
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
        by_pipeline.setdefault(
            pid,
            {
                "pipeline_id": pid,
                "pipeline_name": e["pipeline_name"],
                "cost": 0,
                "runs": 0,
            },
        )
        by_pipeline[pid]["cost"] += e["cost_yuan"]
        by_pipeline[pid]["runs"] += 1
    for v in by_pipeline.values():
        v["cost"] = round(v["cost"], 2)
        v["avg_cost_per_run"] = round(v["cost"] / max(v["runs"], 1), 2)
    sorted_pipelines = sorted(
        by_pipeline.values(), key=lambda x: x["cost"], reverse=True
    )
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
        day_cost = sum(
            e["cost_yuan"] for e in EXECUTIONS if e["start_time"][:10] == day_str
        )
        trend.append({"date": day_str, "cost": round(day_cost, 2)})
    return trend


@app.get("/api/teams/stats")
def team_stats():
    """按团队统计"""
    teams = {}
    for p in PIPELINES:
        owner = p["owner"]
        teams.setdefault(
            owner,
            {
                "team_id": owner,
                "team_name": TEAM_NAMES.get(owner, owner),
                "pipeline_count": 0,
                "active_count": 0,
                "total_cost": 0.0,
                "total_runs": 0,
                "success_runs": 0,
                "total_rows": 0,
            },
        )
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
            (t["success_runs"] / max(t["total_runs"], 1)) * 100, 1
        )
        team_pipelines = [p["id"] for p in PIPELINES if p["owner"] == t["team_id"]]
        team_checks = [
            qc for qc in QUALITY_CHECKS if qc["pipeline_id"] in team_pipelines
        ][:100]
        t["quality_score"] = round(
            (sum(1 for qc in team_checks if qc["passed"]) / max(len(team_checks), 1))
            * 100,
            1,
        )
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
            edges.append(
                {
                    "source": src,
                    "target": target,
                    "pipeline": p["name"],
                    "pipeline_id": p["id"],
                    "status": p["status"],
                }
            )
        for dep_id in p.get("dependencies", []):
            dep_pipe = next((pp for pp in PIPELINES if pp["id"] == dep_id), None)
            if dep_pipe:
                edges.append(
                    {
                        "source": dep_pipe["target_table"],
                        "target": target,
                        "pipeline": p["name"],
                        "pipeline_id": p["id"],
                        "status": p["status"],
                        "is_dependency": True,
                    }
                )
    return {
        "nodes": [
            {
                "id": n,
                "type": "ods"
                if n.startswith("ods_")
                else "dw"
                if n.startswith("dw_")
                else "dm",
            }
            for n in sorted(nodes)
        ],
        "edges": edges,
    }


@app.get("/api/config/reload")
def reload_config():
    """热重载 YAML 配置"""
    global PIPELINES, QUALITY_RULES, _pipelines_cfg, _quality_cfg, _permission_cfg
    _pipelines_cfg = _load_yaml("pipelines.yaml")
    _quality_cfg = _load_yaml("quality.yaml")
    _permission_cfg = _load_yaml("permission.yaml")
    _annotation_cfg = _load_yaml("annotation.yaml")
    PIPELINES = _pipelines_cfg["pipelines"]
    QUALITY_RULES = _quality_cfg["rules"]

    ann_result = reload_annotation_config(_annotation_cfg)

    result = {
        "status": "ok",
        "pipelines": len(PIPELINES),
        "quality_rules": len(QUALITY_RULES),
        "permissions": len(_permission_cfg.get("roles", [])),
        **ann_result,
    }
    log_audit(
        action="config_reload",
        resource_type="config",
        resource_id=None,
        summary="热重载 YAML 配置",
        details=result,
    )
    return result


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
