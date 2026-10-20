import { Tabs, Typography, Layout } from 'antd'
import { SettingOutlined, UploadOutlined } from '@ant-design/icons'
import SystemSettings from './components/SystemSettings'
import UploadPanel from './components/UploadPanel'

const { Title } = Typography
const { Content } = Layout

const tabItems = [
  {
    key: 'settings',
    label: (
      <span>
        <SettingOutlined />
        系统设置
      </span>
    ),
    children: <SystemSettings />,
  },
  {
    key: 'upload',
    label: (
      <span>
        <UploadOutlined />
        文件上传
      </span>
    ),
    children: <UploadPanel />,
  },
]

export default function App() {
  document.title = '文件上传 Demo'

  return (
    <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Content style={{ width: '80%', margin: '0 auto', padding: '24px 16px' }}>
        <Title level={3} style={{ textAlign: 'center', marginBottom: 32 }}>
          文件上传 Demo
        </Title>
        <Tabs defaultActiveKey="settings" items={tabItems} />
      </Content>
    </Layout>
  )
}
