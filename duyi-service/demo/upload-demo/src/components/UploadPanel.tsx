import { useState } from 'react'
import {
  Upload,
  Button,
  Card,
  Image,
  List,
  Typography,
  Space,
  Tag,
  message,
} from 'antd'
import {
  InboxOutlined,
  EyeOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd'
import type {
  ApiResponse,
  UploadSignRequest,
  UploadSignResponse,
} from '../types'

const API_BASE = ''

const { Dragger } = Upload
const { Text } = Typography

interface FileRecord {
  uid: string
  name: string
  size: number
  type: string
  url?: string
  status: 'uploading' | 'done' | 'error'
  percent?: number
  errorMsg?: string
}

export default function UploadPanel() {
  const [fileList, setFileList] = useState<FileRecord[]>([])

  const handleChange: UploadProps['onChange'] = (info) => {
    const records: FileRecord[] = info.fileList.map((f: UploadFile) => ({
      uid: f.uid,
      name: f.name,
      size: f.size ?? 0,
      type: f.type ?? '',
      url: f.response?.url || f.url,
      status: (f.status as FileRecord['status']) || 'uploading',
      percent: f.percent ?? 0,
      errorMsg: f.error?.message,
    }))
    setFileList(records)

    if (info.file.status === 'done') {
      message.success(`${info.file.name} 上传成功`)
    } else if (info.file.status === 'error') {
      message.error(`${info.file.name} 上传失败`)
    }
  }

  const handleRemove = (uid: string) => {
    setFileList((prev) => prev.filter((f) => f.uid !== uid))
  }

  const customRequest = async (options: any) => {
    const { file, onProgress, onSuccess, onError } = options
    const f = file as File

    onProgress({ percent: 0 })

    try {
      const signBody: UploadSignRequest = {
        filename: f.name,
        file_size: f.size,
      }

      const signRes = await fetch(`${API_BASE}/api/upload/sign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signBody),
      })

      if (!signRes.ok) {
        throw new Error(`获取上传签名失败: ${signRes.status}`)
      }

      const signJson: ApiResponse<UploadSignResponse> = await signRes.json()
      if (signJson.code !== '0') {
        throw new Error(signJson.message || '获取上传签名失败')
      }

      const { host, access_id, policy, signature, key, content_type } =
        signJson.data

      const formData = new FormData()
      formData.append('OSSAccessKeyId', access_id)
      formData.append('policy', policy)
      formData.append('Signature', signature)
      formData.append('key', key)
      formData.append('Content-Type', content_type)
      formData.append('file', f)

      const xhr = new XMLHttpRequest()
      xhr.open('POST', host)

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          onProgress({ percent: (e.loaded / e.total) * 100 })
        }
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          const fileUrl = `${signJson.data.bucket_domain}/${key}`
          onSuccess({ url: fileUrl }, xhr)
        } else {
          onError(
            new Error(`上传失败: ${xhr.status} ${xhr.statusText}`),
          )
        }
      }

      xhr.onerror = () => {
        onError(new Error('网络错误，上传失败'))
      }

      xhr.send(formData)

      return {
        abort() {
          xhr.abort()
        },
      }
    } catch (err: any) {
      onError(err)
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div>
      <Dragger
        name="file"
        multiple
        showUploadList={false}
        customRequest={customRequest}
        onChange={handleChange}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p className="ant-upload-hint">支持单次上传多个文件</p>
      </Dragger>

      {fileList.length > 0 && (
        <Card
          title={`已上传文件（${fileList.length}）`}
          style={{ marginTop: 16 }}
        >
          <List
            dataSource={fileList}
            renderItem={(file) => (
              <List.Item
                actions={[
                  file.url && (
                    <Button
                      key="preview"
                      type="link"
                      icon={<EyeOutlined />}
                      onClick={() => window.open(file.url, '_blank')}
                    >
                      预览
                    </Button>
                  ),
                  <Button
                    key="delete"
                    type="link"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleRemove(file.uid)}
                  >
                    移除
                  </Button>,
                ].filter(Boolean)}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Text>{file.name}</Text>
                      <Tag
                        color={
                          file.status === 'done'
                            ? 'success'
                            : file.status === 'error'
                              ? 'error'
                              : 'processing'
                        }
                      >
                        {file.status === 'done'
                          ? '已完成'
                          : file.status === 'error'
                            ? '失败'
                            : '上传中'}
                      </Tag>
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size={0}>
                      <Text type="secondary">
                        {formatSize(file.size)}
                        {file.type && ` · ${file.type}`}
                      </Text>
                      {file.status === 'error' && file.errorMsg && (
                        <Text type="danger">{file.errorMsg}</Text>
                      )}
                      {file.url && file.type?.startsWith('image/') && (
                        <Image
                          src={file.url}
                          width={120}
                          style={{ marginTop: 8, borderRadius: 4 }}
                        />
                      )}
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  )
}
