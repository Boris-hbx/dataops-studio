import { useState, useEffect } from 'react'
import { Card, Table, Tag, Typography, Space, Progress, Modal, Descriptions, Timeline } from 'antd'
import {
  CheckCircleOutlined, CloseCircleOutlined, PauseCircleOutlined,
  WarningOutlined, ClockCircleOutlined,
} from '@ant-design/icons'

const { Title, Text } = Typography

const statusConfig = {
  active: { color: 'green', text: '运行中', icon: <CheckCircleOutlined /> },
  paused: { color: 'default', text: '已暂停', icon: <PauseCircleOutlined /> },
  failed: { color: 'red', text: '失败', icon: <CloseCircleOutlined /> },
  degraded: { color: 'orange', text: '降级', icon: <WarningOutlined /> },
}

export default function Pipelines() {
  const [pipelines, setPipelines] = useState([])
  const [detail, setDetail] = useState(null)
  const [executions, setExecutions] = useState([])

  useEffect(() => {
    fetch('/api/pipelines').then(r => r.json()).then(setPipelines)
  }, [])

  const showDetail = async (record) => {
    const res = await fetch(`/api/pipelines/${record.id}/executions?limit=20`)
    const data = await res.json()
    setExecutions(data)
    setDetail(record)
  }

  const columns = [
    {
      title: '管道名称', dataIndex: 'name', key: 'name',
      render: (name, record) => (
        <Space direction="vertical" size={0}>
          <a onClick={() => showDetail(record)}>{name}</a>
          <Text type="secondary" style={{ fontSize: 12 }}>{record.id}</Text>
        </Space>
      ),
    },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 100,
      render: s => {
        const cfg = statusConfig[s] || { color: 'default', text: s }
        return <Tag color={cfg.color} icon={cfg.icon}>{cfg.text}</Tag>
      },
      filters: Object.entries(statusConfig).map(([k, v]) => ({ text: v.text, value: k })),
      onFilter: (value, record) => record.status === value,
    },
    {
      title: '负责团队', dataIndex: 'team_name', key: 'team_name', width: 130,
    },
    {
      title: '调度频率', dataIndex: 'schedule', key: 'schedule', width: 140,
      render: s => <Text code>{s}</Text>,
    },
    {
      title: '30天成功率', dataIndex: 'success_rate_30d', key: 'success_rate_30d', width: 150,
      sorter: (a, b) => a.success_rate_30d - b.success_rate_30d,
      render: v => (
        <Progress
          percent={v}
          size="small"
          strokeColor={v >= 90 ? '#52c41a' : v >= 80 ? '#faad14' : '#ff4d4f'}
          format={p => `${p}%`}
        />
      ),
    },
    {
      title: '平均耗时', dataIndex: 'avg_duration_30d', key: 'avg_duration_30d', width: 100,
      sorter: (a, b) => a.avg_duration_30d - b.avg_duration_30d,
      render: v => `${v} 分钟`,
    },
    {
      title: '30天成本', dataIndex: 'total_cost_30d', key: 'total_cost_30d', width: 110,
      sorter: (a, b) => a.total_cost_30d - b.total_cost_30d,
      render: v => `¥${v.toFixed(2)}`,
    },
    {
      title: '最后执行', key: 'last_exec', width: 140,
      render: (_, record) => {
        const exec = record.last_execution
        if (!exec) return <Text type="secondary">无</Text>
        return (
          <Space direction="vertical" size={0}>
            <Text style={{ fontSize: 12 }}>{exec.start_time?.slice(0, 16).replace('T', ' ')}</Text>
            <Tag size="small" color={exec.status === 'success' ? 'green' : 'red'}>
              {exec.status === 'success' ? '成功' : '失败'}
            </Tag>
          </Space>
        )
      },
    },
    {
      title: '标签', dataIndex: 'tags', key: 'tags', width: 180,
      render: tags => tags?.map(t => (
        <Tag key={t} color={
          t === 'sla-critical' ? 'red' : t === 'legacy-debt' ? 'orange' :
          t === 'core' ? 'blue' : t === 'revenue' ? 'green' : 'default'
        }>{t}</Tag>
      )),
    },
  ]

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>数据管道管理</Title>

      <Card>
        <Table
          columns={columns}
          dataSource={pipelines}
          rowKey="id"
          size="middle"
          pagination={false}
        />
      </Card>

      <Modal
        title={detail?.name}
        open={!!detail}
        onCancel={() => setDetail(null)}
        footer={null}
        width={700}
      >
        {detail && (
          <div>
            <Descriptions bordered size="small" column={2} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="管道ID">{detail.id}</Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={statusConfig[detail.status]?.color}>{statusConfig[detail.status]?.text}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="负责团队">{detail.team_name}</Descriptions.Item>
              <Descriptions.Item label="调度">{detail.schedule}</Descriptions.Item>
              <Descriptions.Item label="源表" span={2}>
                {detail.source_tables?.map(t => <Tag key={t}>{t}</Tag>)}
              </Descriptions.Item>
              <Descriptions.Item label="目标表" span={2}>
                <Tag color="blue">{detail.target_table}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>{detail.description}</Descriptions.Item>
            </Descriptions>

            <Title level={5}>最近执行记录</Title>
            <Timeline
              items={executions.slice(0, 10).map(e => ({
                color: e.status === 'success' ? 'green' : 'red',
                children: (
                  <Space>
                    <Text style={{ fontSize: 12 }}>{e.start_time?.slice(0, 16).replace('T', ' ')}</Text>
                    <Tag color={e.status === 'success' ? 'green' : 'red'}>{e.status}</Tag>
                    <Text type="secondary">{e.duration_minutes}分钟</Text>
                    <Text type="secondary">¥{e.cost_yuan}</Text>
                    <Text type="secondary">{(e.rows_processed / 10000).toFixed(1)}万行</Text>
                  </Space>
                ),
              }))}
            />
          </div>
        )}
      </Modal>
    </div>
  )
}
