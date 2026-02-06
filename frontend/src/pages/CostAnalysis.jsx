import { Card, Table, Typography, Row, Col, Statistic, Tag, Space } from 'antd'
import { DollarOutlined, RiseOutlined, FallOutlined } from '@ant-design/icons'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell,
} from 'recharts'
import useApi from '../hooks/useApi'

const { Title, Text } = Typography
const COLORS = ['#1677ff', '#52c41a', '#722ed1', '#faad14', '#ff4d4f', '#13c2c2']

export default function CostAnalysis() {
  const { data: summary } = useApi('/api/cost/summary')
  const { data: trend } = useApi('/api/cost/trend', { defaultValue: [] })
  const { data: teams } = useApi('/api/teams/stats', { defaultValue: [] })

  if (!summary) return null

  const pipelineCostColumns = [
    {
      title: '管道', dataIndex: 'pipeline_name', key: 'pipeline_name',
      render: (name, record) => (
        <Space direction="vertical" size={0}>
          <Text strong>{name}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>{record.pipeline_id}</Text>
        </Space>
      ),
    },
    {
      title: '30天总成本', dataIndex: 'cost', key: 'cost', width: 140,
      sorter: (a, b) => a.cost - b.cost,
      defaultSortOrder: 'descend',
      render: v => <Text strong style={{ color: '#722ed1' }}>¥{v.toFixed(2)}</Text>,
    },
    {
      title: '执行次数', dataIndex: 'runs', key: 'runs', width: 100,
      sorter: (a, b) => a.runs - b.runs,
    },
    {
      title: '平均单次成本', dataIndex: 'avg_cost_per_run', key: 'avg_cost_per_run', width: 130,
      sorter: (a, b) => a.avg_cost_per_run - b.avg_cost_per_run,
      render: v => `¥${v.toFixed(2)}`,
    },
    {
      title: '成本占比', key: 'ratio', width: 120,
      render: (_, record) => {
        const ratio = ((record.cost / summary.total_cost_30d) * 100).toFixed(1)
        return <Tag color={ratio > 30 ? 'red' : ratio > 20 ? 'orange' : 'blue'}>{ratio}%</Tag>
      },
    },
  ]

  const teamColumns = [
    { title: '团队', dataIndex: 'team_name', key: 'team_name' },
    {
      title: '管道数', dataIndex: 'pipeline_count', key: 'pipeline_count', width: 80,
    },
    {
      title: '成功率', dataIndex: 'success_rate', key: 'success_rate', width: 100,
      sorter: (a, b) => a.success_rate - b.success_rate,
      render: v => (
        <Text style={{ color: v >= 90 ? '#52c41a' : v >= 80 ? '#faad14' : '#ff4d4f' }}>
          {v}%
        </Text>
      ),
    },
    {
      title: '质量评分', dataIndex: 'quality_score', key: 'quality_score', width: 100,
      sorter: (a, b) => a.quality_score - b.quality_score,
      render: v => (
        <Text style={{ color: v >= 90 ? '#52c41a' : v >= 80 ? '#faad14' : '#ff4d4f', fontWeight: 600 }}>
          {v}分
        </Text>
      ),
    },
    {
      title: '30天成本', dataIndex: 'total_cost', key: 'total_cost', width: 120,
      sorter: (a, b) => a.total_cost - b.total_cost,
      render: v => `¥${v.toFixed(2)}`,
    },
    {
      title: '处理数据量', dataIndex: 'total_rows', key: 'total_rows', width: 130,
      render: v => `${(v / 10000).toFixed(1)} 万行`,
    },
  ]

  // 前两周 vs 后两周成本对比
  const firstHalf = trend.slice(0, 15).reduce((s, d) => s + d.cost, 0)
  const secondHalf = trend.slice(15).reduce((s, d) => s + d.cost, 0)
  const costChange = firstHalf > 0 ? ((secondHalf - firstHalf) / firstHalf * 100).toFixed(1) : 0

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>成本分析</Title>

      {/* 成本概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="30天总成本"
              value={summary.total_cost_30d}
              precision={2}
              prefix={<DollarOutlined style={{ color: '#722ed1' }} />}
              suffix="元"
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="日均成本"
              value={summary.avg_daily_cost}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="成本环比"
              value={Math.abs(costChange)}
              precision={1}
              prefix={costChange >= 0 ? <RiseOutlined style={{ color: '#ff4d4f' }} /> : <FallOutlined style={{ color: '#52c41a' }} />}
              suffix="%"
              valueStyle={{ color: costChange >= 0 ? '#ff4d4f' : '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={14}>
          <Card title="每日成本趋势" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={d => d.slice(5)} />
                <YAxis />
                <Tooltip formatter={(v) => `¥${v.toFixed(2)}`} />
                <Line type="monotone" dataKey="cost" name="成本(元)" stroke="#722ed1" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="管道成本占比" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={summary.by_pipeline}
                  dataKey="cost"
                  nameKey="pipeline_name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ pipeline_name, percent }) =>
                    `${pipeline_name} ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine
                >
                  {summary.by_pipeline.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => `¥${v.toFixed(2)}`} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 管道成本明细 */}
      <Card title="管道成本明细" size="small" style={{ marginBottom: 24 }}>
        <Table
          columns={pipelineCostColumns}
          dataSource={summary.by_pipeline}
          rowKey="pipeline_id"
          size="small"
          pagination={false}
        />
      </Card>

      {/* 团队统计 */}
      <Card title="团队效能概览" size="small">
        <Table
          columns={teamColumns}
          dataSource={teams}
          rowKey="team_id"
          size="small"
          pagination={false}
        />
      </Card>
    </div>
  )
}
