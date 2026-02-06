"""
冒烟测试 — 验证核心 API 端点返回 200 且结构正确
"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_dashboard_stats():
    resp = client.get("/api/dashboard/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "active_pipelines" in data
    assert "quality_score" in data
    assert "total_cost_30d" in data


def test_pipelines():
    resp = client.get("/api/pipelines")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "success_rate_30d" in data[0]


def test_quality_rules():
    resp = client.get("/api/quality/rules")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "pass_rate_30d" in data[0]


def test_cost_summary():
    resp = client.get("/api/cost/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_cost_30d" in data
    assert "by_pipeline" in data


def test_config_reload():
    resp = client.get("/api/config/reload")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "pipelines" in data
    assert "quality_rules" in data
    assert "permissions" in data
    assert "annotation_tasks" in data


def test_annotation_tasks():
    resp = client.get("/api/annotation/tasks")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_lineage():
    resp = client.get("/api/lineage")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data


def test_teams_stats():
    resp = client.get("/api/teams/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "team_name" in data[0]
    assert "quality_score" in data[0]
