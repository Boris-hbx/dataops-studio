"""
DataOps Studio — 数据运维平台 API 后端
启动: uvicorn main:app --reload --port 8000
"""
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    global PIPELINES, QUALITY_RULES, _pipelines_cfg, _quality_cfg
    _pipelines_cfg = _load_yaml("pipelines.yaml")
    _quality_cfg = _load_yaml("quality.yaml")
    PIPELINES = _pipelines_cfg["pipelines"]
    QUALITY_RULES = _quality_cfg["rules"]
    return {"status": "ok", "pipelines": len(PIPELINES), "quality_rules": len(QUALITY_RULES)}


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
