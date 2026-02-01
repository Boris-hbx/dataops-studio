import { useState, useEffect } from 'react'
import { Card, Table, Tag, Typography, Space, Row, Col, Statistic, Alert, Badge } from 'antd'
import {
  CheckCircleOutlined, CloseCircleOutlined, WarningOutlined,
  SafetyCertificateOutlined, ExclamationCircleOutlined,
} from '@ant-design/icons'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'

const { Title, Text } = Typography

const severityConfig = {
  critical: { color: 'red', text: '严重' },
  warning: { color: 'orange', text: '警告' },
  info: { color: 'blue', text: '信息' },
}

const checkTypeLabels = {
  null_check: 'NULL检查',
  range_check: '范围检查',
  uniqueness: '唯一性检查',
  freshness: '时效检查',
  custom_sql: '自定义SQL',
}

export default function QualityRules() {
  const [rules, setRules] = useState([])
  const [scoreTrend, setScoreTrend] = useState([])
  const [checks, setChecks] = useState([])

  useEffect(() => {
    fetch('/api/quality/rules').then(r => r.json()).then(setRules)
    fetch('/api/quality/score-trend').then(r => r.json()).then(setScoreTrend)
    fetch('/api/quality/checks?limit=50').then(r => r.json()).then(setChecks)
  }, [])

  const enabledRules = rules.filter(r => r.enabled)
  const disabledRules = rules.filter(r => !r.enabled)
  const avgPassRate = enabledRules.length > 0
    ? (enabledRules.reduce((sum, r) => sum + r.pass_rate_30d, 0) / enabledRules.length).toFixed(1)
    : 0
  const totalViolations = rules.reduce((sum, r) => sum + (r.recent_violations || 0), 0)

  const ruleColumns = [
    {
      title: '规则', key: 'name',
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Space>
            <Text strong>{record.name}</Text>
            {!record.enabled && <Badge status="error" text="未启用" />}
          </Space>
          <Text type="secondary" style={{ fontSize: 12 }}>{record.id} · {record.description}</Text>
        </Space>
      ),
    },
    {
      title: '状态', dataIndex: 'enabled', key: 'enabled', width: 90,
      render: v => v
        ? <Tag color="green" icon={<CheckCircleOutlined />}>启用</Tag>
        : <Tag color="red" icon={<CloseCircleOutlined />}>禁用</Tag>,
      filters: [{ text: '启用', value: true }, { text: '禁用', value: false }],
      onFilter: (value, record) => record.enabled === value,
    },
    {
      title: '级别', dataIndex: 'severity', key: 'severity', width: 80,
      render: s => <Tag color={severityConfig[s]?.color}>{severityConfig[s]?.text}</Tag>,
    },
    {
      title: '检查类型', dataIndex: 'check_type', key: 'check_type', width: 120,
      render: t => checkTypeLabels[t] || t,
    },
    {
      title: '关联管道', dataIndex: 'pipeline_id', key: 'pipeline_id', width: 160,
      render: v => <Text code>{v}</Text>,
    },
    {
      title: '目标表', dataIndex: 'target_table', key: 'target_table', width: 180,
      render: v => <Tag>{v}</Tag>,
    },
    {
      title: '30天通过率', dataIndex: 'pass_rate_30d', key: 'pass_rate_30d', width: 120,
      sorter: (a, b) => a.pass_rate_30d - b.pass_rate_30d,
      render: (v, record) => {
        if (!record.enabled) return <Text type="secondary">—</Text>
        return (
          <Text style={{
            color: v >= 95 ? '#52c41a' : v >= 85 ? '#faad14' : '#ff4d4f',
            fontWeight: 600,
          }}>
            {v}%
          </Text>
        )
      },
    },
    {
      title: '近期违规', dataIndex: 'recent_violations', key: 'recent_violations', width: 100,
      sorter: (a, b) => a.recent_violations - b.recent_violations,
      render: (v, record) => {
        if (!record.enabled) return <Text type="secondary">—</Text>
        return v > 0 ? <Text type="danger">{v} 次</Text> : <Text type="success">0</Text>
      },
    },
  ]

  const recentCheckColumns = [
    {
      title: '时间', dataIndex: 'check_time', key: 'check_time', width: 140,
      render: t => t?.slice(0, 16).replace('T', ' '),
    },
    { title: '规则', dataIndex: 'rule_name', key: 'rule_name', ellipsis: true },
    {
      title: '结果', dataIndex: 'passed', key: 'passed', width: 80,
      render: v => v
        ? <Tag color="green">通过</Tag>
        : <Tag color="red">违规</Tag>,
    },
    {
      title: '违规比率', dataIndex: 'violation_ratio', key: 'violation_ratio', width: 100,
      render: v => v > 0 ? <Text type="danger">{(v * 100).toFixed(2)}%</Text> : '—',
    },
    {
      title: '级别', dataIndex: 'severity', key: 'severity', width: 80,
      render: s => <Tag color={severityConfig[s]?.color}>{severityConfig[s]?.text}</Tag>,
    },
  ]

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>数据质量管理</Title>

      {/* 质量问题提醒 */}
      {disabledRules.length > 0 && (
        <Alert
          message={`${disabledRules.length} 条质量规则未启用`}
          description={
            <ul style={{ margin: '8px 0 0', paddingLeft: 20 }}>
              {disabledRules.map(r => (
                <li key={r.id}>
                  <Text strong>{r.id}</Text>: {r.name}
                  ({r.severity === 'critical' ? '严重级别' : '警告级别'})
                  — 目标表 {r.target_table}
                </li>
              ))}
            </ul>
          }
          type="error"
          showIcon
          icon={<ExclamationCircleOutlined />}
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 概览卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} lg={6}>
          <Card>
            <Statistic
              title="质量规则总数"
              value={rules.length}
              prefix={<SafetyCertificateOutlined style={{ color: '#1677ff' }} />}
            />
          </Card>
        </Col>
        <Col xs={12} lg={6}>
          <Card>
            <Statistic
              title="已启用"
              value={enabledRules.length}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
              suffix={<Text type="secondary"> / {rules.length}</Text>}
            />
          </Card>
        </Col>
        <Col xs={12} lg={6}>
          <Card>
            <Statistic
              title="平均通过率"
              value={avgPassRate}
              suffix="%"
              valueStyle={{ color: avgPassRate >= 90 ? '#52c41a' : '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={12} lg={6}>
          <Card>
            <Statistic
              title="30天违规次数"
              value={totalViolations}
              valueStyle={{ color: totalViolations > 0 ? '#ff4d4f' : '#52c41a' }}
              prefix={<WarningOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 质量评分趋势 */}
      <Card title="质量评分趋势 (近14天)" size="small" style={{ marginBottom: 24 }}>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={scoreTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tickFormatter={d => d.slice(5)} />
            <YAxis domain={[60, 100]} />
            <Tooltip />
            <Line
              type="monotone" dataKey="score" name="质量评分"
              stroke="#1677ff" strokeWidth={2} dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* 规则列表 */}
      <Card title="质量规则列表" size="small" style={{ marginBottom: 24 }}>
        <Table
          columns={ruleColumns}
          dataSource={rules}
          rowKey="id"
          size="small"
          pagination={false}
          rowClassName={record => !record.enabled ? 'ant-table-row-disabled' : ''}
        />
      </Card>

      {/* 最近检查结果 */}
      <Card title="最近检查结果" size="small">
        <Table
          columns={recentCheckColumns}
          dataSource={checks}
          rowKey={(r, i) => `${r.rule_id}-${i}`}
          size="small"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  )
}
