import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Typography, Space, Alert } from 'antd'
import {
  ApiOutlined, CheckCircleOutlined, DollarOutlined,
  WarningOutlined, ClockCircleOutlined, DatabaseOutlined,
  ArrowUpOutlined, ArrowDownOutlined,
} from '@ant-design/icons'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

const { Title, Text } = Typography

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [trend, setTrend] = useState([])
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    fetch('/api/dashboard/stats').then(r => r.json()).then(setStats)
    fetch('/api/dashboard/execution-trend').then(r => r.json()).then(setTrend)
    fetch('/api/dashboard/alerts?limit=10').then(r => r.json()).then(setAlerts)
  }, [])

  if (!stats) return null

  const alertColumns = [
    {
      title: '时间', dataIndex: 'time', key: 'time', width: 180,
      render: t => t?.slice(0, 16).replace('T', ' '),
    },
    {
      title: '级别', dataIndex: 'severity', key: 'severity', width: 80,
      render: s => (
        <Tag color={s === 'critical' ? 'red' : s === 'warning' ? 'orange' : 'blue'}>
          {s === 'critical' ? '严重' : s === 'warning' ? '警告' : '信息'}
        </Tag>
      ),
    },
    {
      title: '类型', dataIndex: 'type', key: 'type', width: 100,
      render: t => t === 'execution_failure' ? '执行失败' : '质量违规',
    },
    { title: '详情', dataIndex: 'message', key: 'message', ellipsis: true },
    {
      title: '状态', dataIndex: 'resolved', key: 'resolved', width: 80,
      render: r => r ? <Tag color="green">已解决</Tag> : <Tag color="red">未解决</Tag>,
    },
  ]

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>运维看板</Title>

      {/* 核心指标卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="活跃管道"
              value={stats.active_pipelines}
              suffix={`/ ${stats.total_pipelines}`}
              prefix={<ApiOutlined style={{ color: '#1677ff' }} />}
            />
            {stats.degraded_pipelines > 0 && (
              <Text type="warning" style={{ fontSize: 12 }}>
                <WarningOutlined /> {stats.degraded_pipelines} 个降级
              </Text>
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="今日执行次数"
              value={stats.executions_today}
              prefix={<ClockCircleOutlined style={{ color: '#52c41a' }} />}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              30天处理 {(stats.total_rows_30d / 10000).toFixed(0)} 万行
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="数据质量评分"
              value={stats.quality_score}
              suffix="分"
              precision={1}
              prefix={<CheckCircleOutlined style={{
                color: stats.quality_score >= 90 ? '#52c41a' : stats.quality_score >= 80 ? '#faad14' : '#ff4d4f'
              }} />}
              valueStyle={{
                color: stats.quality_score >= 90 ? '#52c41a' : stats.quality_score >= 80 ? '#faad14' : '#ff4d4f'
              }}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              {stats.enabled_rules}/{stats.total_quality_rules} 规则启用
              {stats.disabled_rules > 0 && (
                <Text type="danger" style={{ fontSize: 12 }}> ({stats.disabled_rules}个未启用)</Text>
              )}
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="30日总成本"
              value={stats.total_cost_30d}
              precision={2}
              prefix={<DollarOutlined style={{ color: '#722ed1' }} />}
              suffix="元"
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              未解决告警 <Text type="danger">{stats.unresolved_alerts}</Text> 条
            </Text>
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={14}>
          <Card title="执行趋势 (近14天)" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={d => d.slice(5)} />
                <YAxis />
                <Tooltip labelFormatter={d => d} />
                <Legend />
                <Bar dataKey="success" name="成功" fill="#52c41a" stackId="a" />
                <Bar dataKey="failed" name="失败" fill="#ff4d4f" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="管道状态分布" size="small">
            <Row gutter={[8, 16]} style={{ padding: '20px 0' }}>
              {[
                { label: '运行中', value: stats.active_pipelines, color: '#52c41a', icon: <CheckCircleOutlined /> },
                { label: '降级', value: stats.degraded_pipelines, color: '#faad14', icon: <WarningOutlined /> },
                { label: '已暂停', value: stats.paused_pipelines, color: '#d9d9d9', icon: <ClockCircleOutlined /> },
              ].map(item => (
                <Col span={8} key={item.label} style={{ textAlign: 'center' }}>
                  <div style={{
                    width: 80, height: 80, borderRadius: '50%',
                    background: `${item.color}20`, border: `3px solid ${item.color}`,
                    display: 'flex', flexDirection: 'column',
                    alignItems: 'center', justifyContent: 'center', margin: '0 auto 8px',
                  }}>
                    <span style={{ fontSize: 28, fontWeight: 'bold', color: item.color }}>{item.value}</span>
                  </div>
                  <Text>{item.label}</Text>
                </Col>
              ))}
            </Row>
            <Alert
              message={`${stats.disabled_rules} 条质量规则未启用`}
              description="存在未启用的质量检查规则，可能导致数据质量问题未被发现"
              type="warning"
              showIcon
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 告警列表 */}
      <Card title="最近告警" size="small">
        <Table
          columns={alertColumns}
          dataSource={alerts}
          rowKey="id"
          size="small"
          pagination={{ pageSize: 8 }}
        />
      </Card>
    </div>
  )
}
