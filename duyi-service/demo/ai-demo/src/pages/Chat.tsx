import { useState } from 'react'
import { Layout, Menu, Button, Spin } from 'antd'
import { ApiOutlined, WifiOutlined, LogoutOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useChatMode, type ChatMode } from '../context/ChatModeContext'
import ProductList from '../components/ProductList'
import ChatWindow from '../components/ChatWindow'
import type { Product } from '../services/api'

const { Header, Content } = Layout

const menuItems = [
  { key: 'sse', icon: <ApiOutlined />, label: 'SSE 模式' },
  { key: 'websocket', icon: <WifiOutlined />, label: 'WebSocket 模式' },
]

export default function Chat() {
  const { logout } = useAuth()
  const { mode, setMode } = useChatMode()
  const navigate = useNavigate()
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: '#001529',
          padding: '0 24px',
        }}
      >
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[mode]}
          onClick={({ key }) => setMode(key as ChatMode)}
          items={menuItems}
          style={{ flex: 1, minWidth: 0 }}
        />
        <Button
          type="text"
          icon={<LogoutOutlined />}
          onClick={handleLogout}
          style={{ color: '#fff' }}
        >
          退出登录
        </Button>
      </Header>
      <Content style={{ padding: 16, height: 'calc(100vh - 64px)' }}>
        <div style={{ display: 'flex', gap: 16, height: '100%' }}>
          <div style={{ width: 320, flexShrink: 0 }}>
            <ProductList
              onSelect={(product) => {
                setSelectedProduct(product)
              }}
              selectedId={selectedProduct?.id}
            />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            {selectedProduct ? (
              <ChatWindow
                key={`${mode}-${selectedProduct.id}`}
                product={selectedProduct}
                mode={mode}
              />
            ) : (
              <div
                style={{
                  height: '100%',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  background: '#fff',
                  borderRadius: 8,
                }}
              >
                <Spin><span>请选择左侧产品开始对话</span></Spin>
              </div>
            )}
          </div>
        </div>
      </Content>
    </Layout>
  )
}
