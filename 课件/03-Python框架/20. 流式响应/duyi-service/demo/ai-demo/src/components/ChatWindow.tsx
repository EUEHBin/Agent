import { useEffect, useState, useRef } from 'react'
import { Card, Spin, Typography, Button } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { Bubble, Sender, Welcome } from '@ant-design/x'
import type { BubbleListRef } from '@ant-design/x/es/bubble'
import type { Product } from '../services/api'
import type { ChatMode } from '../context/ChatModeContext'
import { useSSEChat } from '../hooks/useSSEChat'
import { useWebSocketChat } from '../hooks/useWebSocketChat'

const { Text } = Typography

function inlineMd(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code style="background:#f5f5f5;padding:2px 4px;border-radius:3px;font-size:0.9em;">$1</code>')
}

function mdToHtml(text: string): string {
  if (!text) return ''

  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // 提取代码块（避免内部内容被正则处理）
  const codeBlocks: string[] = []
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, (_match, _lang, code) => {
    codeBlocks.push(
      `<pre style="background:#f5f5f5;padding:12px;border-radius:4px;overflow:auto;"><code>${code}</code></pre>`,
    )
    return `__CODE_BLOCK_${codeBlocks.length - 1}__`
  })

  // 逐行处理，每行生成独立的 div，避免流式时产生未闭合标签
  const lines = html.split('\n')
  const result: string[] = []

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue

    if (trimmed === '---') {
      result.push('<hr style="border:none;border-top:1px solid #e0e0e0;margin:12px 0;"/>')
      continue
    }

    if (trimmed.startsWith('### ')) {
      result.push(
        `<div style="font-weight:bold;font-size:1.1em;margin:8px 0;">${inlineMd(trimmed.slice(4))}</div>`,
      )
      continue
    }

    if (trimmed.startsWith('## ')) {
      result.push(
        `<div style="font-weight:bold;font-size:1.2em;margin:8px 0;">${inlineMd(trimmed.slice(3))}</div>`,
      )
      continue
    }

    if (trimmed.startsWith('# ')) {
      result.push(
        `<div style="font-weight:bold;font-size:1.3em;margin:8px 0;">${inlineMd(trimmed.slice(2))}</div>`,
      )
      continue
    }

    if (trimmed.startsWith('- ')) {
      result.push(
        `<div style="margin:2px 0;padding-left:16px;">• ${inlineMd(trimmed.slice(2))}</div>`,
      )
      continue
    }

    result.push(`<div style="margin:4px 0;">${inlineMd(line)}</div>`)
  }

  let output = result.join('\n')

  codeBlocks.forEach((block, i) => {
    output = output.replace(`__CODE_BLOCK_${i}__`, block)
  })

  return output
}

interface Props {
  product: Product
  mode: ChatMode
}

export default function ChatWindow({ product, mode }: Props) {
  const sseChat = useSSEChat()
  const wsChat = useWebSocketChat()

  const chat = mode === 'sse' ? sseChat : wsChat
  const {
    messages,
    streaming,
    sending,
    loadingHistory,
    loadHistory,
    initChat,
    clearMessages,
  } = chat

  const [initialized, setInitialized] = useState(false)
  const [hasHistory, setHasHistory] = useState(false)
  const [inputValue, setInputValue] = useState('')
  const listRef = useRef<BubbleListRef>(null)

  useEffect(() => {
    let cancelled = false

    async function bootstrap() {
      const result = await loadHistory(product.id)
      if (cancelled) return
      setHasHistory(result)

      if (!result) {
        initChat(product.id)
      }
      setInitialized(true)
    }

    clearMessages()
    setInitialized(false)
    setHasHistory(false)
    bootstrap()

    return () => {
      cancelled = true
      if (mode === 'sse') {
        ;(chat as ReturnType<typeof useSSEChat>).abort()
      } else {
        ;(chat as ReturnType<typeof useWebSocketChat>).close()
      }
    }
  }, [product.id, mode])

  useEffect(() => {
    requestAnimationFrame(() => {
      try {
        listRef.current?.scrollTo({ top: 'bottom', behavior: 'smooth' })
      } catch {
        // DOM 尚未就绪
      }
    })
  }, [messages])

  const isBlocked = !initialized || (!hasHistory && (streaming || sending)) || streaming

  const handleSend = (content: string) => {
    if (isBlocked) return

    setInputValue('')
    if (mode === 'sse') {
      ;(chat as ReturnType<typeof useSSEChat>).sendMessage(product.id, content)
    } else {
      ;(chat as ReturnType<typeof useWebSocketChat>).sendMessage(content)
    }
  }

  const bubbleItems = messages.map((msg, i) => {
    const isLastAi = msg.role === 'ai' && i === messages.length - 1
    const isStreaming = isLastAi && (streaming || sending)
    const isLoading = isLastAi && !msg.content && (streaming || sending)

    return {
      key: msg.id,
      role: msg.role,
      content: msg.content,
      placement: (msg.role === 'user' ? 'end' : 'start') as 'start' | 'end',
      variant: (msg.role === 'user' ? 'outlined' : 'filled') as 'filled' | 'outlined',
      loading: isLoading,
      streaming: isStreaming && !!msg.content,
      contentRender: (content: string, info: { status?: string }) => {
        if (info.status === 'loading') return null
        return (
          <div
            style={{
              wordBreak: 'break-word',
              lineHeight: 1.6,
            }}
            dangerouslySetInnerHTML={{ __html: mdToHtml(content) }}
          />
        )
      },
    }
  })

  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Text strong>{product.name}</Text>
          <Button
            size="small"
            icon={<ReloadOutlined />}
            onClick={() => {
              if (mode === 'sse') {
                ;(chat as ReturnType<typeof useSSEChat>).abort()
              } else {
                ;(chat as ReturnType<typeof useWebSocketChat>).close()
              }
              clearMessages()
              setInitialized(false)
              setHasHistory(false)
              loadHistory(product.id).then((result) => {
                setHasHistory(result)
                if (!result) {
                  initChat(product.id)
                }
                setInitialized(true)
              })
            }}
          >
            重置对话
          </Button>
        </div>
      }
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
      styles={{ body: { flex: 1, display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' } }}
    >
      <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
        {loadingHistory ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin><span>加载历史消息...</span></Spin>
          </div>
        ) : messages.length === 0 && initialized ? (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Welcome
              variant="borderless"
              icon="🤖"
              title={`你好，我是 ${product.name} 的 AI 助手`}
              description="有什么可以帮助你的吗？"
            />
          </div>
        ) : (
          <Bubble.List
            ref={listRef}
            items={bubbleItems as any}
            autoScroll
            role={{
              ai: { placement: 'start', variant: 'filled' },
              user: { placement: 'end', variant: 'outlined' },
            }}
          />
        )}
      </div>
      <div style={{ borderTop: '1px solid #f0f0f0', padding: '12px 16px' }}>
        <Sender
          loading={streaming || sending}
          disabled={isBlocked}
          value={inputValue}
          onChange={setInputValue}
          placeholder={
            streaming || sending
              ? 'AI 正在回复中...'
              : !initialized
                ? '正在初始化...'
                : '输入消息...'
          }
          onSubmit={handleSend}
        />
      </div>
    </Card>
  )
}
