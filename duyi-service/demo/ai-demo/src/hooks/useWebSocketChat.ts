import { useState, useCallback, useRef } from 'react'
import { createChatWebSocket } from '../services/websocket'
import { getConversationHistory } from '../services/api'
import type { AiMessageItem } from '../services/api'
import type { ChatMessage } from './useSSEChat'

function toChatMessages(items: AiMessageItem[]): ChatMessage[] {
  return items.map((item, index) => ({
    id: `hist-${index}-${Date.now()}`,
    role: item.role,
    content: item.content,
  }))
}

interface UseWebSocketChatReturn {
  messages: ChatMessage[]
  streaming: boolean
  sending: boolean
  loadingHistory: boolean
  connected: boolean
  loadHistory: (productId: number) => Promise<boolean>
  initChat: (productId: number) => void
  sendMessage: (content: string) => void
  close: () => void
  setMessages: (msgs: ChatMessage[]) => void
  clearMessages: () => void
}

export function useWebSocketChat(): UseWebSocketChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streaming, setStreaming] = useState(false)
  const [sending, setSending] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<ReturnType<typeof createChatWebSocket> | null>(null)
  const streamMsgIdRef = useRef<string | null>(null)

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  const close = useCallback(() => {
    wsRef.current?.close()
    wsRef.current = null
    setConnected(false)
  }, [])

  const loadHistory = useCallback(async (productId: number): Promise<boolean> => {
    setLoadingHistory(true)
    clearMessages()
    try {
      const res = await getConversationHistory(productId)
      const items = res.data || []
      setMessages(toChatMessages(items))
      return items.length > 0
    } catch (err) {
      console.error('Load history failed:', err)
      return false
    } finally {
      setLoadingHistory(false)
    }
  }, [clearMessages])

  const handleInit = useCallback((productId: number) => {
    setStreaming(true)
    const token = localStorage.getItem('token') || ''

    const aiMsgId = `ai-init-${Date.now()}`
    streamMsgIdRef.current = aiMsgId
    const aiMessage: ChatMessage = { id: aiMsgId, role: 'ai', content: '' }
    setMessages((prev) => [...prev, aiMessage])

    const ws = createChatWebSocket()
    wsRef.current = ws

    ws.onMessage((data) => {
      if (data.type === 'chunk') {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === streamMsgIdRef.current
              ? { ...m, content: (m.content || '') + (data.content || '') }
              : m,
          ),
        )
      } else if (data.type === 'done') {
        setStreaming(false)
        setConnected(true)
      } else if (data.type === 'error') {
        console.error('WebSocket error:', data.message)
        setStreaming(false)
      }
    })

    ws.connect(token, productId)
    ws.sendInitialize()
  }, [])

  const handleSendMessage = useCallback((content: string) => {
    setSending(true)
    const userMsgId = `user-${Date.now()}`
    const aiMsgId = `ai-${Date.now()}`
    streamMsgIdRef.current = aiMsgId

    setMessages((prev) => [
      ...prev,
      { id: userMsgId, role: 'user', content },
      { id: aiMsgId, role: 'ai', content: '' },
    ])

    wsRef.current?.onMessage((data) => {
      if (data.type === 'chunk') {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === streamMsgIdRef.current
              ? { ...m, content: (m.content || '') + (data.content || '') }
              : m,
          ),
        )
      } else if (data.type === 'done') {
        setSending(false)
      } else if (data.type === 'error') {
        console.error('WebSocket error:', data.message)
        setSending(false)
      }
    })

    wsRef.current?.sendMessage(content)
  }, [])

  return {
    messages,
    streaming,
    sending,
    loadingHistory,
    connected,
    loadHistory,
    initChat: handleInit,
    sendMessage: handleSendMessage,
    close,
    setMessages,
    clearMessages,
  }
}
