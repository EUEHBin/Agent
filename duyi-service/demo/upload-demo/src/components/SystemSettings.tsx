import { useState, useEffect } from 'react'
import { Form, Input, Button, Spin, message } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'
import {
  API_BASE,
  type SettingGroupResponse,
  type SettingUpdateItem,
  type ApiResponse,
} from '../types'

export default function SystemSettings() {
  const [groups, setGroups] = useState<SettingGroupResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()

  const fetchSettings = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/settings`)
      const json: ApiResponse<SettingGroupResponse[]> = await res.json()
      if (json.code === '0') {
        setGroups(json.data)
        const fields: Record<string, string> = {}
        json.data.forEach((group) => {
          group.settings.forEach((item) => {
            fields[item.key] = item.value
          })
        })
        form.setFieldsValue(fields)
      } else {
        message.error(json.message || '获取设置失败')
      }
    } catch {
      message.error('请求失败，请确认服务已启动')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSettings()
  }, [])

  const handleSave = async () => {
    const values = form.getFieldsValue()
    const items: SettingUpdateItem[] = Object.entries(values).map(
      ([key, value]) => ({ key, value: String(value ?? '') }),
    )
    setSaving(true)
    try {
      const res = await fetch(`${API_BASE}/api/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(items),
      })
      const json: ApiResponse<unknown> = await res.json()
      if (json.code === '0') {
        message.success('设置已保存')
        fetchSettings()
      } else {
        message.error(json.message || '保存失败')
      }
    } catch {
      message.error('请求失败，请确认服务已启动')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Spin spinning={loading}>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          loading={saving}
          onClick={handleSave}
        >
          保存设置
        </Button>
        <Button icon={<ReloadOutlined />} onClick={fetchSettings}>
          重新加载
        </Button>
      </div>
      <Form form={form} layout="vertical">
        {groups.map((group) => (
          <div key={group.key} style={{ marginBottom: 16 }}>
            <h4>
              {group.display_name}
              {group.description && (
                <span style={{ fontWeight: 'normal', fontSize: 13, color: '#999', marginLeft: 8 }}>
                  — {group.description}
                </span>
              )}
            </h4>
            {group.settings.map((item) => (
              <Form.Item
                key={item.key}
                name={item.key}
                label={item.display_name}
                extra={item.description || undefined}
              >
                <Input placeholder={item.description || `请输入 ${item.display_name}`} />
              </Form.Item>
            ))}
          </div>
        ))}
      </Form>
    </Spin>
  )
}
