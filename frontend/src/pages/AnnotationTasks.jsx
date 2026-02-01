import { useState, useEffect } from 'react'
import {
  Card, Table, Tag, Typography, Space, Row, Col, Statistic, Progress,
  Tabs, Badge, Tooltip,
} from 'antd'
import {
  ExperimentOutlined, CheckCircleOutlined, ClockCircleOutlined,
  TeamOutlined, FileTextOutlined, BarChartOutlined,
  PauseCircleOutlined, EditOutlined,
} from '@ant-design/icons'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip as ReTooltip,
  ResponsiveContainer, Legend,
} from 'recharts'

const { Title, Text } = Typography
const COLORS = ['#1677ff', '#52c41a', '#722ed1', '#faad14', '#ff4d4f', '#13c2c2']

const taskTypeColors = {
  rlhf_ranking: 'blue',
  dpo_pairwise: 'purple',
  kto_binary: 'orange',
  sft_editing: 'green',
  reward_scoring: 'cyan',
}

const statusConfig = {
  active: { color: 'green', text: '进行中' },
  draft: { color: 'default', text: '草稿' },
  paused: { color: 'orange', text: '已暂停' },
  completed: { color: 'blue', text: '已完成' },
}

export default function AnnotationTasks() {
  const [tasks, setTasks] = useState([])
  const [annotators, setAnnotators] = useState([])
  const [quality, setQuality] = useState(null)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetch('/api/annotation/tasks').then(r => r.json()).then(setTasks)
    fetch('/api/annotation/annotators').then(r => r.json()).then(setAnnotators)
    fetch('/api/annotation/quality').then(r => r.json()).then(setQuality)
    fetch('/api/annotation/stats').then(r => r.json()).then(setStats)
  }, [])

  const totalSamples = tasks.reduce((s, t) => s + t.total_samples, 0)
  const totalCompleted = tasks.reduce((s, t) => s + t.completed_samples, 0)
  const activeTasks = tasks.filter(t => t.status === 'active').length

  const taskColumns = [
    {
      title: '任务', key: 'name',
      render: (_, r) => (
        <Space direction="vertical" size={0}>
          <Text strong>{r.name}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>{r.id} · {r.model_source}</Text>
        </Space>
      ),
    },
    {
      title: '类型', dataIndex: 'type_label', key: 'type_label', width: 140,
      render: (v, r) => <Tag color={taskTypeColors[r.task_type]}>{v}</Tag>,
    },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 90,
      render: s => {
        const cfg = statusConfig[s] || { color: 'default', text: s }
        return <Tag color={cfg.color}>{cfg.text}</Tag>
      },
    },
    {
      title: '进度', key: 'progress', width: 200,
      render: (_, r) => (
        <Space direction="vertical" size={0} style={{ width: '100%' }}>
          <Progress
            percent={r.progress_percent}
            size="small"
            strokeColor={r.progress_percent >= 80 ? '#52c41a' : '#1677ff'}
          />
          <Text type="secondary" style={{ fontSize: 11 }}>
            {r.completed_samples} / {r.total_samples}
          </Text>
        </Space>
      ),
    },
    {
      title: '通过率', dataIndex: 'approval_rate', key: 'approval_rate', width: 90,
      render: v => (
        <Text style={{ color: v >= 90 ? '#52c41a' : v >= 75 ? '#faad14' : '#ff4d4f', fontWeight: 600 }}>
          {v}%
        </Text>
      ),
    },
    {
      title: '平均耗时', dataIndex: 'avg_duration_seconds', key: 'avg_duration', width: 100,
      render: v => v >= 60 ? `${Math.floor(v / 60)}分${v % 60}秒` : `${v}秒`,
    },
    {
      title: '标注员', dataIndex: 'annotator_names', key: 'annotators', width: 150,
      render: names => names?.map(n => <Tag key={n}>{n}</Tag>),
    },
    {
      title: '优先级', dataIndex: 'priority', key: 'priority', width: 80,
      render: p => (
        <Tag color={p === 'high' ? 'red' : p === 'medium' ? 'orange' : 'default'}>
          {p === 'high' ? '高' : p === 'medium' ? '中' : '低'}
        </Tag>
      ),
    },
  ]

  const annotatorColumns = [
    {
      title: '标注员', key: 'name',
      render: (_, r) => (
        <Space direction="vertical" size={0}>
          <Text strong>{r.name}</Text>
          <Tag size="small">{r.role === 'lead_annotator' ? '首席' : r.role === 'senior_annotator' ? '高级' : '标注员'}</Tag>
        </Space>
      ),
    },
    {
      title: '专长', dataIndex: 'specialties', key: 'specialties',
      render: v => v?.map(s => <Tag key={s} size="small">{s}</Tag>),
    },
    {
      title: '提交数', dataIndex: 'total_submissions', key: 'total', width: 80,
      sorter: (a, b) => a.total_submissions - b.total_submissions,
    },
    {
      title: '通过率', dataIndex: 'computed_accuracy', key: 'accuracy', width: 90,
      sorter: (a, b) => a.computed_accuracy - b.computed_accuracy,
      render: v => (
        <Text style={{ color: v >= 90 ? '#52c41a' : v >= 80 ? '#faad14' : '#ff4d4f', fontWeight: 600 }}>
          {v}%
        </Text>
      ),
    },
    {
      title: '标注速度', dataIndex: 'samples_per_hour', key: 'speed', width: 110,
      sorter: (a, b) => a.samples_per_hour - b.samples_per_hour,
      render: v => `${v} 条/小时`,
    },
    {
      title: '参与任务', dataIndex: 'tasks_involved', key: 'tasks', width: 90,
      render: v => `${v} 个`,
    },
  ]

  const tabItems = [
    {
      key: 'tasks',
      label: <span><FileTextOutlined /> 标注任务</span>,
      children: (
        <Card size="small">
          <Table columns={taskColumns} dataSource={tasks} rowKey="id" size="small" pagination={false} />
        </Card>
      ),
    },
    {
      key: 'annotators',
      label: <span><TeamOutlined /> 标注团队</span>,
      children: (
        <Card size="small">
          <Table columns={annotatorColumns} dataSource={annotators} rowKey="id" size="small" pagination={false} />
        </Card>
      ),
    },
    {
      key: 'quality',
      label: <span><CheckCircleOutlined /> 质量监控</span>,
      children: quality && (
        <div>
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Card size="small"><Statistic title="总提交数" value={quality.total_submissions} /></Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Statistic title="总体通过率" value={quality.overall_approval_rate} suffix="%" valueStyle={{ color: '#52c41a' }} />
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Statistic title="Fleiss' Kappa" value={quality.fleiss_kappa}
                  suffix={<Tag color={quality.fleiss_kappa >= 0.61 ? 'green' : 'orange'} style={{ marginLeft: 4 }}>
                    {quality.kappa_interpretation}
                  </Tag>} />
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small"><Statistic title="待审核" value={quality.pending_review} valueStyle={{ color: '#faad14' }} /></Card>
            </Col>
          </Row>
          <Card title="各任务类型通过率" size="small">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={Object.values(quality.by_task_type)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type_label" />
                <YAxis domain={[0, 100]} />
                <ReTooltip />
                <Bar dataKey="approval_rate" name="通过率%" fill="#1677ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>
      ),
    },
    {
      key: 'stats',
      label: <span><BarChartOutlined /> 数据分析</span>,
      children: stats && (
        <div>
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col xs={24} lg={14}>
              <Card title="每日标注量趋势" size="small">
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={stats.daily_trend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={d => d.slice(5)} />
                    <YAxis />
                    <ReTooltip />
                    <Legend />
                    <Bar dataKey="approved" name="已通过" fill="#52c41a" stackId="a" />
                    <Bar dataKey="rejected" name="已拒绝" fill="#ff4d4f" stackId="a" />
                    <Bar dataKey="count" name="总提交" fill="#1677ff" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col xs={24} lg={10}>
              <Card title="任务类型分布" size="small">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={stats.task_type_distribution} dataKey="count" nameKey="label"
                      cx="50%" cy="50%" outerRadius={90}
                      label={({ label, percent }) => `${label} ${(percent * 100).toFixed(0)}%`}>
                      {stats.task_type_distribution.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <ReTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col xs={24} lg={12}>
              <Card title="领域分布" size="small">
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={stats.domain_distribution} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis type="category" dataKey="domain" width={100} />
                    <ReTooltip />
                    <Bar dataKey="count" name="样本数" fill="#722ed1" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="数据版本" size="small">
                <Table
                  dataSource={stats.data_versions}
                  rowKey="version"
                  size="small"
                  pagination={false}
                  columns={[
                    { title: '版本', dataIndex: 'version', render: v => <Tag color="blue">{v}</Tag> },
                    { title: '日期', dataIndex: 'date' },
                    { title: '样本数', dataIndex: 'samples' },
                    { title: '格式', dataIndex: 'format', render: v => <Tag>{v}</Tag> },
                  ]}
                />
              </Card>
            </Col>
          </Row>
        </div>
      ),
    },
  ]

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>RLHF 数据标注管理</Title>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} lg={6}>
          <Card hoverable>
            <Statistic title="标注任务" value={tasks.length} prefix={<ExperimentOutlined style={{ color: '#1677ff' }} />}
              suffix={<Text type="secondary" style={{ fontSize: 14 }}>({activeTasks} 进行中)</Text>} />
          </Card>
        </Col>
        <Col xs={12} lg={6}>
          <Card hoverable>
            <Statistic title="标注进度" value={totalCompleted} prefix={<EditOutlined style={{ color: '#52c41a' }} />}
              suffix={<Text type="secondary" style={{ fontSize: 14 }}>/ {totalSamples}</Text>} />
          </Card>
        </Col>
        <Col xs={12} lg={6}>
          <Card hoverable>
            <Statistic title="标注团队" value={annotators.length} prefix={<TeamOutlined style={{ color: '#722ed1' }} />}
              suffix="人" />
          </Card>
        </Col>
        <Col xs={12} lg={6}>
          <Card hoverable>
            <Statistic title="整体进度" value={totalSamples > 0 ? ((totalCompleted / totalSamples) * 100).toFixed(1) : 0}
              prefix={<ClockCircleOutlined style={{ color: '#faad14' }} />} suffix="%" />
          </Card>
        </Col>
      </Row>

      <Tabs items={tabItems} size="large" />
    </div>
  )
}
