import { useState, useRef, useEffect } from 'react'
import { Button, Input, Typography, Space, Avatar, Spin } from 'antd'
import { RobotOutlined, SendOutlined, CloseOutlined, MessageOutlined } from '@ant-design/icons'

const { Text, Paragraph } = Typography
const { TextArea } = Input

export default function AiAssistant() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '你好！我是 DataOps Studio AI 助手，可以帮你解答平台运维、数据质量、RLHF 标注等方面的问题。' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return

    const userMsg = { role: 'user', content: text }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    const assistantMsg = { role: 'assistant', content: '' }
    setMessages([...newMessages, assistantMsg])

    try {
      const resp = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: newMessages.filter(m => m.role !== 'system').map(m => ({
            role: m.role, content: m.content,
          })),
        }),
      })

      if (!resp.ok) {
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = { role: 'assistant', content: 'AI 服务暂时不可用，请稍后再试。' }
          return updated
        })
        setLoading(false)
        return
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let accumulated = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ') && line !== 'data: [DONE]') {
            try {
              const json = JSON.parse(line.slice(6))
              const delta = json.choices?.[0]?.delta?.content || ''
              accumulated += delta
              setMessages(prev => {
                const updated = [...prev]
                updated[updated.length - 1] = { role: 'assistant', content: accumulated }
                return updated
              })
            } catch {}
          }
        }
      }
    } catch {
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'assistant', content: '网络错误，请检查连接后重试。' }
        return updated
      })
    }
    setLoading(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!open) {
    return (
      <Button
        type="primary"
        shape="circle"
        size="large"
        icon={<MessageOutlined />}
        onClick={() => setOpen(true)}
        style={{
          position: 'fixed', right: 24, bottom: 24, zIndex: 1000,
          width: 56, height: 56, fontSize: 24,
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        }}
      />
    )
  }

  return (
    <div style={{
      position: 'fixed', right: 24, bottom: 24, zIndex: 1000,
      width: 400, height: 520, background: '#fff',
      borderRadius: 12, boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
      display: 'flex', flexDirection: 'column', overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding: '12px 16px', background: '#1677ff', color: '#fff',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <Space>
          <RobotOutlined style={{ fontSize: 18 }} />
          <Text strong style={{ color: '#fff' }}>AI 助手</Text>
        </Space>
        <Button type="text" size="small" icon={<CloseOutlined />}
          style={{ color: '#fff' }} onClick={() => setOpen(false)} />
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 12 }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: 12,
          }}>
            {msg.role === 'assistant' && (
              <Avatar size={28} icon={<RobotOutlined />}
                style={{ background: '#1677ff', marginRight: 8, flexShrink: 0 }} />
            )}
            <div style={{
              maxWidth: '80%', padding: '8px 12px', borderRadius: 8,
              background: msg.role === 'user' ? '#1677ff' : '#f5f5f5',
              color: msg.role === 'user' ? '#fff' : '#333',
              fontSize: 13, lineHeight: 1.5, whiteSpace: 'pre-wrap',
            }}>
              {msg.content || (loading && idx === messages.length - 1 ? <Spin size="small" /> : '')}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ padding: '8px 12px', borderTop: '1px solid #f0f0f0' }}>
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            rows={1}
            autoSize={{ minRows: 1, maxRows: 3 }}
            placeholder="输入问题..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{ resize: 'none' }}
          />
          <Button type="primary" icon={<SendOutlined />}
            onClick={sendMessage} loading={loading} />
        </Space.Compact>
      </div>
    </div>
  )
}
