import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Button,
  Radio,
  Select,
  Input,
  Tag,
  Spin,
  Empty,
  Divider,
  message,
} from "antd";
import {
  ArrowLeftOutlined,
  ToolOutlined,
  UserOutlined,
  RobotOutlined,
  CodeOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  QuestionCircleOutlined,
} from "@ant-design/icons";

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const ERROR_TYPE_OPTIONS = [
  { value: "wrong_tool", label: "工具选择错误" },
  { value: "wrong_params", label: "参数错误" },
  { value: "wrong_timing", label: "时机错误" },
  { value: "redundant", label: "冗余调用" },
  { value: "missing", label: "遗漏调用" },
];

const SEVERITY_OPTIONS = [
  { value: "critical", label: "致命" },
  { value: "major", label: "严重" },
  { value: "minor", label: "一般" },
  { value: "trivial", label: "轻微" },
];

const ROLE_CONFIG = {
  user: {
    color: "#e6f4ff",
    border: "#91caff",
    icon: <UserOutlined />,
    label: "用户",
  },
  assistant: {
    color: "#f6ffed",
    border: "#b7eb8f",
    icon: <RobotOutlined />,
    label: "助手",
  },
  tool: {
    color: "#fff7e6",
    border: "#ffd591",
    icon: <CodeOutlined />,
    label: "工具",
  },
};

const CORRECTNESS_TAG = {
  correct: { color: "green", icon: <CheckCircleOutlined />, label: "正确" },
  incorrect: { color: "red", icon: <CloseCircleOutlined />, label: "错误" },
  uncertain: {
    color: "orange",
    icon: <QuestionCircleOutlined />,
    label: "不确定",
  },
};

export default function AgentAnnotationWorkspace() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [toolCalls, setToolCalls] = useState([]);
  const [selectedTC, setSelectedTC] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    correctness: "",
    error_type: "",
    severity: "",
    comment: "",
  });

  const fetchSession = useCallback(async () => {
    setLoading(true);
    try {
      const [sessionRes, tcRes] = await Promise.all([
        fetch(
          `/api/agent-annotation/sessions/${encodeURIComponent(sessionId)}`,
        ),
        fetch(
          `/api/agent-annotation/sessions/${encodeURIComponent(sessionId)}/tool-calls`,
        ),
      ]);
      if (!sessionRes.ok) {
        message.error("会话不存在");
        navigate("/agent-annotation");
        return;
      }
      setSession(await sessionRes.json());
      setToolCalls(await tcRes.json());
    } catch {
      message.error("加载会话失败");
    } finally {
      setLoading(false);
    }
  }, [sessionId, navigate]);

  useEffect(() => {
    fetchSession();
  }, [fetchSession]);

  const handleSelectTC = (tc) => {
    setSelectedTC(tc);
    setForm({ correctness: "", error_type: "", severity: "", comment: "" });
  };

  const handleSubmit = async () => {
    if (!form.correctness) {
      message.warning("请选择正确性");
      return;
    }
    setSubmitting(true);
    try {
      const body = {
        session_id: sessionId,
        message_index: selectedTC.message_index,
        tool_call_index: selectedTC.tool_call_index,
        correctness: form.correctness,
      };
      if (form.correctness === "incorrect") {
        if (form.error_type) body.error_type = form.error_type;
        if (form.severity) body.severity = form.severity;
      }
      if (form.comment) body.comment = form.comment;

      const res = await fetch("/api/agent-annotation/annotations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "提交失败");
      }
      message.success("标注提交成功");
      setForm({ correctness: "", error_type: "", severity: "", comment: "" });
      fetchSession();
    } catch (e) {
      message.error(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Spin style={{ display: "block", margin: "120px auto" }} size="large" />
    );
  }

  if (!session) {
    return <Empty description="会话不存在" />;
  }

  const formatArgs = (args) => {
    try {
      return JSON.stringify(JSON.parse(args), null, 2);
    } catch {
      return args;
    }
  };

  const findAnnotationsForTC = (msgIdx, tcIdx) => {
    const tc = toolCalls.find(
      (t) => t.message_index === msgIdx && t.tool_call_index === tcIdx,
    );
    return tc?.annotations ?? [];
  };

  return (
    <div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          marginBottom: 16,
        }}
      >
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate("/agent-annotation")}
        />
        <Title level={4} style={{ margin: 0 }}>
          标注工作台
        </Title>
        <Tag color="blue">{session.model}</Tag>
        <Text type="secondary">{session.session_id}</Text>
      </div>

      <Row gutter={16}>
        {/* 左栏: 会话上下文 */}
        <Col xs={24} lg={12}>
          <Card
            title="会话上下文"
            size="small"
            style={{ height: "calc(100vh - 180px)", overflow: "auto" }}
          >
            {session.messages.map((msg, msgIdx) => {
              const cfg = ROLE_CONFIG[msg.role] || ROLE_CONFIG.user;
              return (
                <div
                  key={msgIdx}
                  style={{
                    marginBottom: 12,
                    padding: "8px 12px",
                    background: cfg.color,
                    border: `1px solid ${cfg.border}`,
                    borderRadius: 8,
                  }}
                >
                  <div style={{ marginBottom: 4 }}>
                    <Tag>
                      {cfg.icon} {cfg.label}
                    </Tag>
                    {msg.tool_call_id && (
                      <Tag color="orange">回复: {msg.tool_call_id}</Tag>
                    )}
                  </div>
                  <Paragraph
                    style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 13 }}
                  >
                    {msg.content}
                  </Paragraph>
                  {msg.tool_calls?.map((tc, tcIdx) => {
                    const annotations = findAnnotationsForTC(msgIdx, tcIdx);
                    const isSelected =
                      selectedTC?.message_index === msgIdx &&
                      selectedTC?.tool_call_index === tcIdx;
                    return (
                      <div
                        key={tcIdx}
                        onClick={() =>
                          handleSelectTC({
                            message_index: msgIdx,
                            tool_call_index: tcIdx,
                            tool_call: tc,
                            annotations,
                          })
                        }
                        style={{
                          marginTop: 8,
                          padding: "6px 10px",
                          background: isSelected
                            ? "rgba(22,119,255,0.15)"
                            : "rgba(102,126,234,0.08)",
                          border: isSelected
                            ? "2px solid #1677ff"
                            : "1px solid rgba(102,126,234,0.2)",
                          borderRadius: 6,
                          cursor: "pointer",
                        }}
                      >
                        <Space size={4}>
                          <ToolOutlined style={{ color: "#667eea" }} />
                          <Text strong style={{ fontSize: 13 }}>
                            {tc.function.name}
                          </Text>
                          {annotations.map((ann) => {
                            const t = CORRECTNESS_TAG[ann.correctness];
                            return (
                              <Tag
                                key={ann.id}
                                color={t?.color}
                                icon={t?.icon}
                                style={{ fontSize: 11 }}
                              >
                                {t?.label}
                              </Tag>
                            );
                          })}
                        </Space>
                        <div style={{ marginTop: 4 }}>
                          <Text
                            code
                            style={{
                              fontSize: 11,
                              wordBreak: "break-all",
                            }}
                          >
                            {tc.function.arguments}
                          </Text>
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            })}
          </Card>
        </Col>

        {/* 右栏: 标注面板 */}
        <Col xs={24} lg={12}>
          <Card
            title="标注面板"
            size="small"
            style={{ height: "calc(100vh - 180px)", overflow: "auto" }}
          >
            {!selectedTC ? (
              <Empty description="请在左侧点击工具调用开始标注" />
            ) : (
              <div>
                {/* 工具调用详情 */}
                <div style={{ marginBottom: 16 }}>
                  <Space style={{ marginBottom: 8 }}>
                    <ToolOutlined style={{ fontSize: 18, color: "#667eea" }} />
                    <Title level={5} style={{ margin: 0 }}>
                      {selectedTC.tool_call.function.name}
                    </Title>
                  </Space>
                  {selectedTC.tool_call.id && (
                    <div>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        ID: {selectedTC.tool_call.id}
                      </Text>
                    </div>
                  )}
                  <pre
                    style={{
                      marginTop: 8,
                      padding: 12,
                      background: "#f5f5f5",
                      borderRadius: 6,
                      fontSize: 12,
                      overflow: "auto",
                      maxHeight: 200,
                    }}
                  >
                    {formatArgs(selectedTC.tool_call.function.arguments)}
                  </pre>
                </div>

                <Divider />

                {/* 标注表单 */}
                <div style={{ marginBottom: 16 }}>
                  <Text strong style={{ display: "block", marginBottom: 8 }}>
                    正确性 *
                  </Text>
                  <Radio.Group
                    value={form.correctness}
                    onChange={(e) =>
                      setForm({ ...form, correctness: e.target.value })
                    }
                  >
                    <Radio.Button value="correct">
                      <CheckCircleOutlined /> 正确
                    </Radio.Button>
                    <Radio.Button value="incorrect">
                      <CloseCircleOutlined /> 错误
                    </Radio.Button>
                    <Radio.Button value="uncertain">
                      <QuestionCircleOutlined /> 不确定
                    </Radio.Button>
                  </Radio.Group>
                </div>

                {form.correctness === "incorrect" && (
                  <>
                    <div style={{ marginBottom: 16 }}>
                      <Text
                        strong
                        style={{ display: "block", marginBottom: 8 }}
                      >
                        错误类型
                      </Text>
                      <Select
                        value={form.error_type || undefined}
                        onChange={(v) => setForm({ ...form, error_type: v })}
                        options={ERROR_TYPE_OPTIONS}
                        placeholder="请选择"
                        style={{ width: "100%" }}
                        allowClear
                      />
                    </div>
                    <div style={{ marginBottom: 16 }}>
                      <Text
                        strong
                        style={{ display: "block", marginBottom: 8 }}
                      >
                        严重程度
                      </Text>
                      <Select
                        value={form.severity || undefined}
                        onChange={(v) => setForm({ ...form, severity: v })}
                        options={SEVERITY_OPTIONS}
                        placeholder="请选择"
                        style={{ width: "100%" }}
                        allowClear
                      />
                    </div>
                  </>
                )}

                <div style={{ marginBottom: 16 }}>
                  <Text strong style={{ display: "block", marginBottom: 8 }}>
                    备注
                  </Text>
                  <TextArea
                    value={form.comment}
                    onChange={(e) =>
                      setForm({ ...form, comment: e.target.value })
                    }
                    placeholder="添加说明或建议..."
                    rows={3}
                  />
                </div>

                <Button
                  type="primary"
                  block
                  loading={submitting}
                  onClick={handleSubmit}
                >
                  提交标注
                </Button>

                {/* 已有标注 */}
                {selectedTC.annotations.length > 0 && (
                  <>
                    <Divider />
                    <Text strong style={{ display: "block", marginBottom: 8 }}>
                      已有标注 ({selectedTC.annotations.length})
                    </Text>
                    {selectedTC.annotations.map((ann) => {
                      const t = CORRECTNESS_TAG[ann.correctness];
                      return (
                        <Card
                          key={ann.id}
                          size="small"
                          style={{ marginBottom: 8 }}
                        >
                          <Space wrap>
                            <Tag color={t?.color} icon={t?.icon}>
                              {t?.label}
                            </Tag>
                            {ann.error_type && (
                              <Tag>
                                {ERROR_TYPE_OPTIONS.find(
                                  (o) => o.value === ann.error_type,
                                )?.label ?? ann.error_type}
                              </Tag>
                            )}
                            {ann.severity && (
                              <Tag>
                                {SEVERITY_OPTIONS.find(
                                  (o) => o.value === ann.severity,
                                )?.label ?? ann.severity}
                              </Tag>
                            )}
                          </Space>
                          {ann.comment && (
                            <Paragraph
                              style={{
                                margin: "4px 0 0",
                                fontSize: 12,
                                color: "#666",
                              }}
                            >
                              {ann.comment}
                            </Paragraph>
                          )}
                          <Text
                            type="secondary"
                            style={{ fontSize: 11, display: "block" }}
                          >
                            {ann.annotator} ·{" "}
                            {ann.created_at?.slice(0, 16).replace("T", " ")}
                          </Text>
                        </Card>
                      );
                    })}
                  </>
                )}
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
