import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Space,
  Button,
  Upload,
  Tag,
  Spin,
  Empty,
  message,
} from "antd";
import {
  RobotOutlined,
  ToolOutlined,
  CheckCircleOutlined,
  PercentageOutlined,
  UploadOutlined,
  InboxOutlined,
  ClockCircleOutlined,
  MessageOutlined,
} from "@ant-design/icons";

const { Title, Text } = Typography;
const { Dragger } = Upload;

export default function AgentAnnotation() {
  const [stats, setStats] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [statsRes, sessionsRes] = await Promise.all([
        fetch("/api/agent-annotation/stats"),
        fetch("/api/agent-annotation/sessions"),
      ]);
      if (statsRes.ok) setStats(await statsRes.json());
      const sessionsData = sessionsRes.ok ? await sessionsRes.json() : [];
      setSessions(Array.isArray(sessionsData) ? sessionsData : []);
    } catch {
      message.error("加载数据失败");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const uploadProps = {
    name: "file",
    accept: ".json",
    action: "/api/agent-annotation/sessions/import",
    showUploadList: false,
    beforeUpload(file) {
      if (file.size > 10 * 1024 * 1024) {
        message.error("文件大小不能超过 10MB");
        return Upload.LIST_IGNORE;
      }
      return true;
    },
    onChange(info) {
      if (info.file.status === "done") {
        const resp = info.file.response;
        if (resp.success) {
          message.success(resp.message);
          fetchData();
        } else {
          message.error(resp.detail || "导入失败");
        }
      } else if (info.file.status === "error") {
        const resp = info.file.response;
        message.error(resp?.detail || "上传失败");
      }
    },
  };

  if (loading && !stats) {
    return (
      <Spin style={{ display: "block", margin: "120px auto" }} size="large" />
    );
  }

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 24,
        }}
      >
        <Title level={4} style={{ margin: 0 }}>
          Agent 工具调用标注
        </Title>
        <Upload {...uploadProps}>
          <Button icon={<UploadOutlined />} type="primary">
            上传会话文件
          </Button>
        </Upload>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="会话数"
              value={stats?.total_sessions ?? 0}
              prefix={<RobotOutlined style={{ color: "#1677ff" }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="工具调用数"
              value={stats?.total_tool_calls ?? 0}
              prefix={<ToolOutlined style={{ color: "#52c41a" }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="已标注数"
              value={stats?.total_annotations ?? 0}
              prefix={<CheckCircleOutlined style={{ color: "#722ed1" }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="标注率"
              value={stats?.annotation_rate ?? 0}
              suffix="%"
              precision={1}
              prefix={<PercentageOutlined style={{ color: "#faad14" }} />}
            />
          </Card>
        </Col>
      </Row>

      {/* 会话列表 */}
      {sessions.length === 0 ? (
        <Card>
          <Dragger {...uploadProps} style={{ padding: "40px 0" }}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽 JSON 文件到此处上传</p>
            <p className="ant-upload-hint">
              支持 OpenAI / Anthropic / 自定义格式，自动检测转换
            </p>
          </Dragger>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {sessions.map((s) => (
            <Col xs={24} sm={12} lg={8} key={s.session_id}>
              <Card
                hoverable
                onClick={() =>
                  navigate(
                    `/agent-annotation/workspace/${encodeURIComponent(s.session_id)}`,
                  )
                }
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    marginBottom: 12,
                  }}
                >
                  <Text strong style={{ fontSize: 14 }}>
                    {s.session_id}
                  </Text>
                  <Tag color="blue">{s.model}</Tag>
                </div>
                <Space size="large">
                  <span>
                    <MessageOutlined /> {s.message_count} 消息
                  </span>
                  <span>
                    <ToolOutlined /> {s.tool_call_count} 调用
                  </span>
                  <span>
                    <CheckCircleOutlined />{" "}
                    <Text
                      type={
                        s.annotation_count === s.tool_call_count
                          ? "success"
                          : "warning"
                      }
                    >
                      {s.annotation_count}/{s.tool_call_count}
                    </Text>
                  </span>
                </Space>
                <div style={{ marginTop: 8 }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    <ClockCircleOutlined />{" "}
                    {s.created_at?.slice(0, 16).replace("T", " ")}
                  </Text>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}
