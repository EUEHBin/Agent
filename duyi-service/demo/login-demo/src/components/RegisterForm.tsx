import { type FC, useState } from 'react'
import { Form, Input, Button, App as AntApp } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import type { ApiResponse, UserResponse } from '../types'
import { API_BASE } from '../types'

interface RegisterFormProps {
  onSuccess: () => void
}

const RegisterForm: FC<RegisterFormProps> = ({ onSuccess }) => {
  const [loading, setLoading] = useState(false)
  const { message } = AntApp.useApp()

  const onFinish = async (values: {
    username: string
    password: string
    confirm: string
  }) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: values.username,
          password: values.password,
        }),
      })
      const json: ApiResponse<UserResponse> = await res.json()
      if (json.code === '0') {
        message.success('注册成功，请登录')
        onSuccess()
      } else {
        message.error(json.message || '注册失败')
      }
    } catch {
      message.error('网络错误，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Form
      name="register"
      onFinish={onFinish}
      layout="vertical"
      style={{ maxWidth: 400, margin: '0 auto' }}
    >
      <Form.Item
        name="username"
        label="用户名"
        rules={[
          { required: true, message: '请输入用户名' },
          { max: 100, message: '用户名最多100个字符' },
        ]}
      >
        <Input prefix={<UserOutlined />} placeholder="请输入用户名" />
      </Form.Item>
      <Form.Item
        name="password"
        label="密码"
        rules={[
          { required: true, message: '请输入密码' },
          { min: 6, max: 100, message: '密码长度6-100位' },
        ]}
      >
        <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" />
      </Form.Item>
      <Form.Item
        name="confirm"
        label="确认密码"
        dependencies={['password']}
        rules={[
          { required: true, message: '请确认密码' },
          ({ getFieldValue }) => ({
            validator(_, value) {
              if (!value || getFieldValue('password') === value) {
                return Promise.resolve()
              }
              return Promise.reject(new Error('两次输入的密码不一致'))
            },
          }),
        ]}
      >
        <Input.Password prefix={<LockOutlined />} placeholder="请再次输入密码" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block>
          注册
        </Button>
      </Form.Item>
    </Form>
  )
}

export default RegisterForm
