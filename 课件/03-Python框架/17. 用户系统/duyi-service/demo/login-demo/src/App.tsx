import { useCallback, useMemo, useState } from 'react'
import { Tabs, Typography, Layout, App as AntApp } from 'antd'
import { SettingOutlined, UserOutlined } from '@ant-design/icons'
import LoginForm from './components/LoginForm'
import RegisterForm from './components/RegisterForm'
import SystemSettings from './components/SystemSettings'

const { Title } = Typography
const { Content } = Layout

function loadToken(): string | null {
  try {
    return localStorage.getItem('token')
  } catch {
    return null
  }
}

function saveToken(token: string | null) {
  try {
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  } catch {
    // ignore
  }
}

export default function App() {
  document.title = '登录注册 Demo'

  const [token, setToken] = useState<string | null>(loadToken)
  const [activeKey, setActiveKey] = useState('login')

  const onLoginSuccess = useCallback((accessToken: string) => {
    saveToken(accessToken)
    setToken(accessToken)
  }, [])

  const onRegisterSuccess = useCallback(() => {
    setActiveKey('login')
  }, [])

  const onLogout = useCallback(() => {
    saveToken(null)
    setToken(null)
  }, [])

  const tabItems = useMemo(() => [
    {
      key: 'login',
      label: (
        <span>
          <UserOutlined />
          登录
        </span>
      ),
      children: <LoginForm onSuccess={onLoginSuccess} />,
    },
    {
      key: 'register',
      label: (
        <span>
          <UserOutlined />
          注册
        </span>
      ),
      children: <RegisterForm onSuccess={onRegisterSuccess} />,
    },
    {
      key: 'settings',
      label: (
        <span>
          <SettingOutlined />
          系统设置
        </span>
      ),
      children: <SystemSettings token={token} onLogout={onLogout} />,
    },
  ], [token, onLoginSuccess, onRegisterSuccess, onLogout])

  return (
    <AntApp>
      <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
        <Content style={{ width: '80%', margin: '0 auto', padding: '24px 16px' }}>
          <Title level={3} style={{ textAlign: 'center', marginBottom: 32 }}>
            登录注册 Demo
          </Title>
          <Tabs activeKey={activeKey} onChange={setActiveKey} items={tabItems} />
        </Content>
      </Layout>
    </AntApp>
  )
}
