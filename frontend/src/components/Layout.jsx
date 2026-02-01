import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Typography, Space, Tag } from 'antd'
import {
  DashboardOutlined,
  ApiOutlined,
  SafetyCertificateOutlined,
  DollarOutlined,
  DatabaseOutlined,
} from '@ant-design/icons'

const { Header, Sider, Content } = Layout
const { Title, Text } = Typography

const menuItems = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '运维看板' },
  { key: '/pipelines', icon: <ApiOutlined />, label: '数据管道' },
  { key: '/quality', icon: <SafetyCertificateOutlined />, label: '数据质量' },
  { key: '/cost', icon: <DollarOutlined />, label: '成本分析' },
]

export default function AppLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
        width={220}
        style={{ background: '#001529' }}
      >
        <div style={{
          height: 64, display: 'flex', alignItems: 'center',
          justifyContent: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)'
        }}>
          <Space>
            <DatabaseOutlined style={{ fontSize: 24, color: '#1677ff' }} />
            {!collapsed && (
              <Title level={4} style={{ color: '#fff', margin: 0, whiteSpace: 'nowrap' }}>
                DataOps Studio
              </Title>
            )}
          </Space>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{
          background: '#fff', padding: '0 24px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          borderBottom: '1px solid #f0f0f0', height: 64,
        }}>
          <Space>
            <Text strong style={{ fontSize: 16 }}>数据运维平台</Text>
            <Tag color="blue">Demo</Tag>
          </Space>
          <Space>
            <Tag color="green">系统正常</Tag>
            <Text type="secondary">admin@dataops.io</Text>
          </Space>
        </Header>
        <Content style={{ margin: 24, minHeight: 280 }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}
