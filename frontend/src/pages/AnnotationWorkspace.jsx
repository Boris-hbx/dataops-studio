import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Card, Typography, Space, Row, Col, Tag, Radio, Button, Input, Rate,
  Divider, Alert, Select, Descriptions, Badge, Segmented, Progress, Statistic,
  message,
} from 'antd'
import {
  SwapOutlined, LikeOutlined, DislikeOutlined, EditOutlined,
  StarOutlined, OrderedListOutlined, ExperimentOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input

const taskTypeIcons = {
  rlhf_ranking: <OrderedListOutlined />,
  dpo_pairwise: <SwapOutlined />,
  kto_binary: <LikeOutlined />,
  sft_editing: <EditOutlined />,
  reward_scoring: <StarOutlined />,
}

const taskTypeColors = {
  rlhf_ranking: 'blue',
  dpo_pairwise: 'purple',
  kto_binary: 'orange',
  sft_editing: 'green',
  reward_scoring: 'cyan',
}

export default function AnnotationWorkspace() {
  const [searchParams] = useSearchParams()
  const [tasks, setTasks] = useState([])
  const [selectedTaskId, setSelectedTaskId] = useState(null)
  const [samples, setSamples] = useState([])
  const [sampleTotal, setSampleTotal] = useState(0)
  const [currentIdx, setCurrentIdx] = useState(0)

  // Annotation state
  const [ranking, setRanking] = useState([])
  const [chosenIdx, setChosenIdx] = useState(null)
  const [feedback, setFeedback] = useState(null)
  const [editedText, setEditedText] = useState('')
  const [scores, setScores] = useState({})
  const [rationale, setRationale] = useState('')
  const [safetyCategory, setSafetyCategory] = useState('none')

  // Submit state
  const [submitting, setSubmitting] = useState(false)
  const [submitResult, setSubmitResult] = useState(null)
  const startTimeRef = useRef(null)

  // Load tasks + read URL param
  useEffect(() => {
    fetch('/api/annotation/tasks').then(r => r.json()).then(data => {
      setTasks(data.filter(t => t.status === 'active'))
      const taskParam = searchParams.get('task')
      if (taskParam) {
        const match = data.find(t => t.id === taskParam)
        if (match) setSelectedTaskId(taskParam)
      }
    })
  }, [])

  // Load samples when task changes
  useEffect(() => {
    if (selectedTaskId) {
      fetch(`/api/annotation/tasks/${selectedTaskId}/samples`).then(r => r.json()).then(data => {
        const sampleList = data.samples || []
        setSamples(sampleList)
        setSampleTotal(data.total || sampleList.length)
        // Jump to first unannotated sample
        const firstUnannotated = sampleList.findIndex(s => !s.annotated)
        setCurrentIdx(firstUnannotated >= 0 ? firstUnannotated : 0)
        resetAnnotation()
        setSubmitResult(null)
      })
    }
  }, [selectedTaskId])

  // Track start time when sample changes
  useEffect(() => {
    startTimeRef.current = Date.now()
  }, [currentIdx, selectedTaskId])

  const resetAnnotation = () => {
    setRanking([])
    setChosenIdx(null)
    setFeedback(null)
    setEditedText('')
    setScores({})
    setRationale('')
    setSafetyCategory('none')
    setSubmitResult(null)
  }

  const selectedTask = tasks.find(t => t.id === selectedTaskId)
  const currentSample = samples[currentIdx]

  // Compute completed count from samples
  const completedCount = samples.filter(s => s.annotated).length

  const handleNext = () => {
    if (currentIdx < samples.length - 1) {
      setCurrentIdx(currentIdx + 1)
      resetAnnotation()
    }
  }

  const handlePrev = () => {
    if (currentIdx > 0) {
      setCurrentIdx(currentIdx - 1)
      resetAnnotation()
    }
  }

  // Submit validation
  const canSubmit = () => {
    if (!selectedTask || !currentSample || currentSample.annotated) return false
    const { task_type } = selectedTask
    if (task_type === 'rlhf_ranking') {
      return ranking.length === (currentSample.responses || []).length && rationale.trim().length > 0
    }
    if (task_type === 'dpo_pairwise') {
      return chosenIdx !== null && rationale.trim().length > 0
    }
    if (task_type === 'kto_binary') {
      return feedback !== null
    }
    if (task_type === 'sft_editing') {
      return editedText.trim().length > 0
    }
    if (task_type === 'reward_scoring') {
      return Object.keys(scores).length === 4 && Object.values(scores).every(v => v > 0)
    }
    return false
  }

  const handleSubmit = async () => {
    if (!canSubmit()) return
    setSubmitting(true)
    setSubmitResult(null)

    const durationSeconds = Math.round((Date.now() - (startTimeRef.current || Date.now())) / 1000)
    const body = {
      sample_id: currentSample.id,
      annotator: 'zhang.wei',
      duration_seconds: durationSeconds,
    }

    const { task_type } = selectedTask
    if (task_type === 'rlhf_ranking') {
      body.ranking = ranking
      body.rationale = rationale
    } else if (task_type === 'dpo_pairwise') {
      body.chosen_index = chosenIdx
      body.rationale = rationale
    } else if (task_type === 'kto_binary') {
      body.feedback = feedback
      body.safety_category = safetyCategory
      body.rationale = rationale
    } else if (task_type === 'sft_editing') {
      body.edited_response = editedText
    } else if (task_type === 'reward_scoring') {
      body.scores = scores
    }

    try {
      const resp = await fetch(`/api/annotation/tasks/${selectedTaskId}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const result = await resp.json()
      if (result.status === 'ok') {
        setSubmitResult({ type: 'success', message: `提交成功 (${result.submission_id})，进度: ${result.task_progress.completed}/${result.task_progress.total}` })
        message.success('标注提交成功')
        // Mark current sample as annotated locally
        setSamples(prev => prev.map((s, i) => i === currentIdx ? { ...s, annotated: true } : s))
        // Auto-advance to next unannotated after 1.5s
        setTimeout(() => {
          const nextUnannotated = samples.findIndex((s, i) => i > currentIdx && !s.annotated)
          if (nextUnannotated >= 0) {
            setCurrentIdx(nextUnannotated)
            resetAnnotation()
          }
        }, 1500)
      } else {
        setSubmitResult({ type: 'error', message: result.message || '提交失败' })
        message.error(result.message || '提交失败')
      }
    } catch (err) {
      setSubmitResult({ type: 'error', message: '网络错误' })
      message.error('网络错误')
    } finally {
      setSubmitting(false)
    }
  }

  const renderAnnotationPanel = () => {
    if (!selectedTask || !currentSample) return null
    const { task_type } = selectedTask
    const responses = currentSample.responses || []

    if (task_type === 'rlhf_ranking') {
      return (
        <div>
          <Alert message="请对以下模型回复按质量从高到低排序" type="info" showIcon style={{ marginBottom: 16 }} />
          {responses.map((resp, idx) => (
            <Card key={idx} size="small" style={{ marginBottom: 12 }}
              title={<Space><Tag color="blue">回复 {String.fromCharCode(65 + idx)}</Tag><Text type="secondary">{resp.model}</Text></Space>}
              extra={
                <Select placeholder="排名" style={{ width: 80 }} value={ranking.includes(idx) ? ranking.indexOf(idx) + 1 : undefined}
                  disabled={currentSample.annotated}
                  onChange={v => {
                    const newRanking = [...ranking]
                    const existIdx = newRanking.indexOf(idx)
                    if (existIdx >= 0) newRanking.splice(existIdx, 1)
                    newRanking.splice(v - 1, 0, idx)
                    setRanking(newRanking.slice(0, responses.length))
                  }}
                  options={responses.map((_, i) => ({ label: `第 ${i + 1}`, value: i + 1 }))}
                />
              }
            >
              <Paragraph style={{ whiteSpace: 'pre-wrap', fontSize: 13 }}>{resp.text}</Paragraph>
            </Card>
          ))}
          <TextArea rows={2} placeholder="排序理由（必填）" value={rationale} onChange={e => setRationale(e.target.value)} disabled={currentSample.annotated} />
        </div>
      )
    }

    if (task_type === 'dpo_pairwise') {
      return (
        <div>
          <Alert message="请选择更好的回复作为 Chosen，另一个自动标记为 Rejected" type="info" showIcon style={{ marginBottom: 16 }} />
          <Row gutter={16}>
            {responses.slice(0, 2).map((resp, idx) => (
              <Col span={12} key={idx}>
                <Card size="small"
                  style={{ borderColor: chosenIdx === idx ? '#52c41a' : chosenIdx !== null && chosenIdx !== idx ? '#ff4d4f' : undefined, borderWidth: 2 }}
                  title={
                    <Space>
                      <Tag color="blue">{resp.model}</Tag>
                      {chosenIdx === idx && <Badge status="success" text="Chosen" />}
                      {chosenIdx !== null && chosenIdx !== idx && <Badge status="error" text="Rejected" />}
                    </Space>
                  }
                >
                  <Paragraph style={{ whiteSpace: 'pre-wrap', fontSize: 13, minHeight: 120 }}>{resp.text}</Paragraph>
                  <Button type={chosenIdx === idx ? 'primary' : 'default'} block
                    disabled={currentSample.annotated}
                    onClick={() => setChosenIdx(idx)}>
                    {chosenIdx === idx ? '已选为 Chosen' : '选择此回复'}
                  </Button>
                </Card>
              </Col>
            ))}
          </Row>
          <div style={{ marginTop: 12 }}>
            <TextArea rows={2} placeholder="选择理由（必填）" value={rationale} onChange={e => setRationale(e.target.value)} disabled={currentSample.annotated} />
          </div>
        </div>
      )
    }

    if (task_type === 'kto_binary') {
      const resp = responses[0] || { model: 'unknown', text: '...' }
      return (
        <div>
          <Alert message="对模型回复给出二元反馈：好/不好，如不好请标注安全类别" type="info" showIcon style={{ marginBottom: 16 }} />
          <Card size="small" title={<Tag color="blue">{resp.model}</Tag>}>
            <Paragraph style={{ whiteSpace: 'pre-wrap', fontSize: 13 }}>{resp.text}</Paragraph>
          </Card>
          <div style={{ margin: '16px 0', textAlign: 'center' }}>
            <Space size="large">
              <Button type={feedback === 'thumbs_up' ? 'primary' : 'default'} size="large"
                icon={<LikeOutlined />} style={{ width: 150, height: 60, fontSize: 18 }}
                disabled={currentSample.annotated}
                onClick={() => setFeedback('thumbs_up')}>
                好
              </Button>
              <Button danger type={feedback === 'thumbs_down' ? 'primary' : 'default'} size="large"
                icon={<DislikeOutlined />} style={{ width: 150, height: 60, fontSize: 18 }}
                disabled={currentSample.annotated}
                onClick={() => setFeedback('thumbs_down')}>
                不好
              </Button>
            </Space>
          </div>
          {feedback === 'thumbs_down' && (
            <Card size="small" title="安全分类">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Select value={safetyCategory} onChange={setSafetyCategory} style={{ width: '100%' }}
                  disabled={currentSample.annotated}
                  options={[
                    { label: '毒性内容', value: 'toxicity' },
                    { label: '偏见歧视', value: 'bias' },
                    { label: '隐私泄露', value: 'privacy_leak' },
                    { label: '有害指导', value: 'harmful_instruction' },
                    { label: '其他', value: 'other' },
                  ]}
                />
                <TextArea rows={2} placeholder="补充说明" value={rationale} onChange={e => setRationale(e.target.value)} disabled={currentSample.annotated} />
              </Space>
            </Card>
          )}
        </div>
      )
    }

    if (task_type === 'sft_editing') {
      const resp = responses[0] || { model: 'unknown', text: '...' }
      return (
        <div>
          <Alert message="请修改优化模型回复，使其质量达到标注标准" type="info" showIcon style={{ marginBottom: 16 }} />
          <Row gutter={16}>
            <Col span={12}>
              <Card size="small" title="原始回复">
                <Paragraph style={{ whiteSpace: 'pre-wrap', fontSize: 13, minHeight: 200 }}>{resp.text}</Paragraph>
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title={<Space>修改后回复 <Tag color="green">SFT 数据</Tag></Space>}>
                <TextArea rows={10} value={editedText || resp.text}
                  onChange={e => setEditedText(e.target.value)}
                  style={{ fontSize: 13 }}
                  disabled={currentSample.annotated}
                />
              </Card>
            </Col>
          </Row>
        </div>
      )
    }

    if (task_type === 'reward_scoring') {
      const resp = responses[0] || { model: 'unknown', text: '...' }
      const dimensions = ['coherence', 'relevance', 'informativeness', 'engagement']
      const dimLabels = { coherence: '连贯性', relevance: '相关性', informativeness: '信息量', engagement: '互动性' }
      return (
        <div>
          <Alert message="请对模型回复在各维度打分（1-10分）" type="info" showIcon style={{ marginBottom: 16 }} />
          <Card size="small" title={<Tag color="blue">{resp.model}</Tag>} style={{ marginBottom: 16 }}>
            <Paragraph style={{ whiteSpace: 'pre-wrap', fontSize: 13 }}>{resp.text}</Paragraph>
          </Card>
          <Card size="small" title="评分面板">
            {dimensions.map(dim => (
              <Row key={dim} align="middle" style={{ marginBottom: 12 }}>
                <Col span={4}><Text strong>{dimLabels[dim]}</Text></Col>
                <Col span={14}>
                  <Rate count={10} value={scores[dim] || 0} onChange={v => setScores({ ...scores, [dim]: v })} disabled={currentSample.annotated} />
                </Col>
                <Col span={6}><Text type="secondary">{scores[dim] || 0} / 10</Text></Col>
              </Row>
            ))}
            <Divider />
            <Statistic title="综合评分" value={
              Object.values(scores).length > 0
                ? (Object.values(scores).reduce((a, b) => a + b, 0) / Object.values(scores).length).toFixed(1)
                : '—'
            } />
          </Card>
        </div>
      )
    }

    return <Alert message="未知的标注类型" type="warning" />
  }

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>标注工作台</Title>

      {/* 任务选择 + 进度 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row align="middle" gutter={16}>
          <Col flex="auto">
            <Space>
              <Text strong>选择标注任务:</Text>
              <Select
                placeholder="请选择任务"
                style={{ width: 400 }}
                value={selectedTaskId}
                onChange={v => { setSelectedTaskId(v); setSubmitResult(null) }}
                options={tasks.map(t => ({
                  label: <Space>{taskTypeIcons[t.task_type]}<Text>{t.name}</Text><Tag>{t.type_label}</Tag></Space>,
                  value: t.id,
                }))}
              />
            </Space>
          </Col>
          {selectedTask && (
            <Col>
              <Space size="middle">
                <Tag color={taskTypeColors[selectedTask.task_type]}>{selectedTask.type_label}</Tag>
                <Progress
                  type="circle"
                  size={40}
                  percent={sampleTotal > 0 ? Math.round((completedCount / sampleTotal) * 100) : 0}
                  format={p => `${p}%`}
                />
                <Text type="secondary">{completedCount}/{sampleTotal}</Text>
              </Space>
            </Col>
          )}
        </Row>
      </Card>

      {/* 提交反馈 */}
      {submitResult && (
        <Alert
          message={submitResult.message}
          type={submitResult.type}
          showIcon
          closable
          style={{ marginBottom: 16 }}
          onClose={() => setSubmitResult(null)}
        />
      )}

      {currentSample ? (
        <Row gutter={16}>
          {/* 左侧: Prompt */}
          <Col xs={24} lg={8}>
            <Card title="Prompt" size="small"
              extra={<Text type="secondary">{currentIdx + 1} / {samples.length}</Text>}>
              <Descriptions column={1} size="small" style={{ marginBottom: 12 }}>
                <Descriptions.Item label="ID">{currentSample.id}</Descriptions.Item>
                <Descriptions.Item label="领域"><Tag>{currentSample.domain}</Tag></Descriptions.Item>
                <Descriptions.Item label="难度">
                  <Tag color={currentSample.difficulty === 'hard' ? 'red' : currentSample.difficulty === 'medium' ? 'orange' : 'green'}>
                    {currentSample.difficulty}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="状态">
                  {currentSample.annotated
                    ? <Badge status="success" text="已标注" />
                    : <Badge status="warning" text="待标注" />}
                </Descriptions.Item>
              </Descriptions>
              <Card type="inner" style={{ background: '#fafafa' }}>
                <Paragraph style={{ fontSize: 14, margin: 0 }}>{currentSample.prompt}</Paragraph>
              </Card>
              <div style={{ marginTop: 16 }}>
                <Space>
                  <Button onClick={handlePrev} disabled={currentIdx === 0}>上一条</Button>
                  <Button onClick={handleNext} disabled={currentIdx >= samples.length - 1}>下一条</Button>
                  <Button
                    type="primary"
                    onClick={handleSubmit}
                    loading={submitting}
                    disabled={!canSubmit() || currentSample.annotated}
                    icon={currentSample.annotated ? <CheckCircleOutlined /> : undefined}
                  >
                    {currentSample.annotated ? '已标注' : '提交标注'}
                  </Button>
                </Space>
              </div>
            </Card>
          </Col>

          {/* 右侧: 标注面板 */}
          <Col xs={24} lg={16}>
            <Card title={
              <Space>
                标注面板
                {selectedTask && <Tag color={taskTypeColors[selectedTask.task_type]}>{selectedTask.type_label}</Tag>}
              </Space>
            } size="small">
              {renderAnnotationPanel()}
            </Card>
          </Col>
        </Row>
      ) : (
        <Card>
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <ExperimentOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
            <Title level={5} type="secondary" style={{ marginTop: 16 }}>请先选择一个标注任务开始工作</Title>
          </div>
        </Card>
      )}
    </div>
  )
}
