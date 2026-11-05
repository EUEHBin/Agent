import { type FC, useState } from 'react'
import { Form, Input, Button, App as AntApp } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import type { ApiResponse, TokenResponse } from '../types'
import { API_BASE } from '../types'

interface LoginFormProps {
  onSuccess: (token: string) => void
}

const LoginForm: FC<LoginFormProps> = ({ onSuccess }) => {
  const [loading, setLoading] = useState(false)
  const { message } = AntApp.useApp()

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      })
      const json: ApiResponse<TokenResponse> = await res.json()
      if (json.code === '0') {
        message.success('登录成功')
        onSuccess(json.data.access_token)
      } else {
        message.error(json.message || '登录失败')
      }
    } catch {
      message.error('网络错误，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Form
      name="login"
      onFinish={onFinish}
      layout="vertical"
      style={{ maxWidth: 400, margin: '0 auto' }}
    >
      <Form.Item
        name="username"
        label="用户名"
        rules={[{ required: true, message: '请输入用户名' }]}
      >
        <Input prefix={<UserOutlined />} placeholder="请输入用户名" />
      </Form.Item>
      <Form.Item
        name="password"
        label="密码"
        rules={[{ required: true, message: '请输入密码' }]}
      >
        <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block>
          登录
        </Button>
      </Form.Item>
    </Form>
  )
}

export default LoginForm
