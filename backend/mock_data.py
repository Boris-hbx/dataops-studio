"""
模拟数据生成 — 确定性随机，每次启动数据一致
"""

import hashlib
import random
from datetime import datetime, timedelta

TEAM_NAMES = {
    "pretrain-data": "预训练数据组",
    "pretrain-infra": "预训练基建组",
    "posttrain-data": "后训练数据组",
    "data-quality": "数据质量组",
    "data-science": "数据科学组",
    "annotation-ops": "标注运营组",
}

PIPELINE_SUCCESS_RATE = {
    "web_crawl_clean": 0.95,
    "dedup_pipeline": 0.91,
    "quality_filter": 0.70,
    "sft_data_gen": 0.93,
    "data_mix_tokenize": 0.88,
    "rlhf_export": 0.0,  # paused
}

PIPELINE_AVG_DURATION = {
    "web_crawl_clean": 95,
    "dedup_pipeline": 65,
    "quality_filter": 140,
    "sft_data_gen": 45,
    "data_mix_tokenize": 180,
    "rlhf_export": 0,
}

PIPELINE_COST_PER_RUN = {
    "web_crawl_clean": 18.5,
    "dedup_pipeline": 12.0,
    "quality_filter": 35.0,
    "sft_data_gen": 22.0,
    "data_mix_tokenize": 28.0,
    "rlhf_export": 0.0,
}


def _generate_executions(pipelines: list[dict]) -> list[dict]:
    """生成过去 30 天的 pipeline 执行历史"""
    executions = []
    now = datetime.now().replace(second=0, microsecond=0)
    for p in pipelines:
        pid = p["id"]
        if p["status"] == "paused":
            continue
        schedule = p["schedule"]
        if (
            "* * * *" in schedule
            and schedule.startswith("0 ") is False
            and schedule.startswith("15 ")
        ):
            runs_per_day = 24
        elif "* * 1" in schedule:
            runs_per_day = 1 / 7
        else:
            runs_per_day = 1

        for day_offset in range(30, 0, -1):
            day = now - timedelta(days=day_offset)
            n_runs = (
                max(1, int(runs_per_day))
                if runs_per_day >= 1
                else (1 if day_offset % 7 == 0 else 0)
            )
            for run_idx in range(n_runs):
                success = random.random() < PIPELINE_SUCCESS_RATE.get(pid, 0.9)
                base_dur = PIPELINE_AVG_DURATION.get(pid, 30)
                duration = max(5, int(base_dur * (0.7 + random.random() * 0.6)))
                cost = round(
                    PIPELINE_COST_PER_RUN.get(pid, 5) * (0.8 + random.random() * 0.4),
                    2,
                )
                rows_processed = (
                    random.randint(10000, 500000)
                    if success
                    else random.randint(0, 5000)
                )
                start_time = day.replace(
                    hour=random.randint(0, 23), minute=random.randint(0, 59)
                )
                exec_id = hashlib.md5(
                    f"{pid}-{start_time.isoformat()}-{run_idx}".encode()
                ).hexdigest()[:12]
                executions.append(
                    {
                        "id": exec_id,
                        "pipeline_id": pid,
                        "pipeline_name": p["name"],
                        "start_time": start_time.isoformat(),
                        "end_time": (
                            start_time + timedelta(minutes=duration)
                        ).isoformat(),
                        "duration_minutes": duration,
                        "status": "success"
                        if success
                        else random.choice(["failed", "timeout"]),
                        "rows_processed": rows_processed,
                        "cost_yuan": cost,
                        "owner": p["owner"],
                    }
                )
    executions.sort(key=lambda x: x["start_time"], reverse=True)
    return executions


def _generate_quality_checks(quality_rules: list[dict]) -> list[dict]:
    """基于质量规则生成检查结果"""
    checks = []
    now = datetime.now()
    for rule in quality_rules:
        if not rule["enabled"]:
            continue
        for day_offset in range(30, 0, -1):
            day = now - timedelta(days=day_offset)
            passed = random.random() > 0.12
            value = 0.0 if passed else round(random.uniform(0.001, 0.05), 4)
            checks.append(
                {
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "pipeline_id": rule["pipeline_id"],
                    "target_table": rule["target_table"],
                    "check_type": rule["check_type"],
                    "severity": rule["severity"],
                    "check_time": day.replace(
                        hour=5, minute=random.randint(0, 59)
                    ).isoformat(),
                    "passed": passed,
                    "violation_ratio": value,
                    "threshold": rule["threshold"],
                }
            )
    checks.sort(key=lambda x: x["check_time"], reverse=True)
    return checks


def _generate_alerts(
    executions: list[dict], quality_checks: list[dict]
) -> list[dict]:
    """从执行失败和质量违规中提取告警"""
    alerts = []
    for ex in executions:
        if ex["status"] != "success":
            alerts.append(
                {
                    "id": f"ALT-{ex['id'][:8]}",
                    "type": "execution_failure",
                    "severity": "critical" if ex["status"] == "failed" else "warning",
                    "pipeline_id": ex["pipeline_id"],
                    "pipeline_name": ex["pipeline_name"],
                    "message": f"管道 [{ex['pipeline_name']}] 执行{ex['status']}, 耗时{ex['duration_minutes']}分钟",
                    "time": ex["end_time"],
                    "resolved": random.random() > 0.3,
                }
            )
    for qc in quality_checks:
        if not qc["passed"]:
            alerts.append(
                {
                    "id": f"ALT-Q-{qc['rule_id']}-{qc['check_time'][:10]}",
                    "type": "quality_violation",
                    "severity": qc["severity"],
                    "pipeline_id": qc["pipeline_id"],
                    "pipeline_name": qc["rule_name"],
                    "message": f"质量规则 [{qc['rule_name']}] 违反, 违规比率 {qc['violation_ratio']}",
                    "time": qc["check_time"],
                    "resolved": random.random() > 0.4,
                }
            )
    alerts.sort(key=lambda x: x["time"], reverse=True)
    return alerts


def generate_all(
    pipelines: list[dict], quality_rules: list[dict]
) -> tuple[list[dict], list[dict], list[dict]]:
    """生成所有模拟数据，返回 (executions, quality_checks, alerts)"""
    random.seed(42)
    executions = _generate_executions(pipelines)
    quality_checks = _generate_quality_checks(quality_rules)
    alerts = _generate_alerts(executions, quality_checks)
    return executions, quality_checks, alerts
