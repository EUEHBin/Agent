import { type FC, useCallback, useEffect, useState } from 'react'
import {
  Form,
  Input,
  Button,
  Card,
  Space,
  Spin,
  Typography,
  App as AntApp,
  Divider,
} from 'antd'
import { LogoutOutlined, SaveOutlined, ReloadOutlined } from '@ant-design/icons'
import type {
  ApiResponse,
  SettingGroupResponse,
  SettingItemResponse,
  SettingUpdateItem,
} from '../types'
import { API_BASE } from '../types'

const { Text, Title } = Typography

interface SystemSettingsProps {
  token: string | null
  onLogout: () => void
}

const SystemSettings: FC<SystemSettingsProps> = ({ token, onLogout }) => {
  const [groups, setGroups] = useState<SettingGroupResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()
  const { message } = AntApp.useApp()

  const fetchSettings = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/settings`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      const json: ApiResponse<SettingGroupResponse[]> = await res.json()
      if (json.code === '0') {
        setGroups(json.data)
        const values: Record<string, string> = {}
        for (const group of json.data) {
          for (const item of group.settings) {
            values[item.key] = item.value
          }
        }
        form.setFieldsValue(values)
      } else {
        message.error(json.message || '获取设置失败')
      }
    } catch {
      message.error('网络错误，请稍后重试')
    } finally {
      setLoading(false)
    }
  }, [token, form, message])

  useEffect(() => {
    fetchSettings()
  }, [fetchSettings])

  const onSave = useCallback(async () => {
    const values = form.getFieldsValue()
    const items: SettingUpdateItem[] = Object.entries(values).map(
      ([key, value]) => ({
        key,
        value: String(value),
      }),
    )

    setSaving(true)
    try {
      const res = await fetch(`${API_BASE}/api/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(items),
      })
      const json: ApiResponse<SettingItemResponse[]> = await res.json()
      if (json.code === '0') {
        message.success('设置保存成功')
      } else {
        message.error(json.message || '保存失败')
      }
    } catch {
      message.error('网络错误，请稍后重试')
    } finally {
      setSaving(false)
    }
  }, [form, token, message])

  const onRefresh = useCallback(() => {
    fetchSettings()
  }, [fetchSettings])

  return (
    <Spin spinning={loading}>
      <Space
        style={{
          width: '100%',
          justifyContent: 'flex-end',
          marginBottom: 16,
        }}
      >
        <Button icon={<ReloadOutlined />} onClick={onRefresh}>
          刷新
        </Button>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          loading={saving}
          onClick={onSave}
        >
          保存设置
        </Button>
        <Button icon={<LogoutOutlined />} danger onClick={onLogout}>
          退出登录
        </Button>
      </Space>

      <Form form={form} layout="vertical" style={{ maxWidth: 600 }}>
        {groups.map((group) => (
          <Card
            key={group.key}
            title={
              <Space direction="vertical" size={0}>
                <Title level={5} style={{ margin: 0 }}>
                  {group.display_name}
                </Title>
                <Text type="secondary">{group.description}</Text>
              </Space>
            }
            style={{ marginBottom: 16 }}
          >
            {group.settings.map((item) => (
              <Form.Item
                key={item.key}
                name={item.key}
                label={item.display_name}
                help={item.description}
              >
                <Input />
              </Form.Item>
            ))}
          </Card>
        ))}
      </Form>

      {groups.length === 0 && !loading && (
        <Text type="secondary" style={{ display: 'block', textAlign: 'center' }}>
          暂无可用的系统设置
        </Text>
      )}

      <Divider />

      <div style={{ textAlign: 'center', marginTop: 16 }}>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          loading={saving}
          onClick={onSave}
          size="large"
        >
          保存全部设置
        </Button>
      </div>
    </Spin>
  )
}

export default SystemSettings
