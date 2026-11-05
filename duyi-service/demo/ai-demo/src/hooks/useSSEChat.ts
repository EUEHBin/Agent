import { useState, useCallback, useRef } from 'react'
import { initConversationSSE, sendMessageSSE } from '../services/sse'
import { getConversationHistory } from '../services/api'
import type { AiMessageItem } from '../services/api'

export interface ChatMessage {
  id: string
  role: string
  content: string
}

function toChatMessages(items: AiMessageItem[]): ChatMessage[] {
  return items.map((item, index) => ({
    id: `hist-${index}-${Date.now()}`,
    role: item.role,
    content: item.content,
  }))
}

interface UseSSEChatReturn {
  messages: ChatMessage[]
  streaming: boolean
  sending: boolean
  loadingHistory: boolean
  loadHistory: (productId: number) => Promise<boolean>
  initChat: (productId: number) => void
  sendMessage: (productId: number, content: string) => void
  abort: () => void
  setMessages: (msgs: ChatMessage[]) => void
  clearMessages: () => void
}

export function useSSEChat(): UseSSEChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streaming, setStreaming] = useState(false)
  const [sending, setSending] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  const abort = useCallback(() => {
    abortRef.current?.abort()
    abortRef.current = null
    setStreaming(false)
    setSending(false)
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
    const aiMsgId = `ai-init-${Date.now()}`
    const aiMessage: ChatMessage = {
      id: aiMsgId,
      role: 'ai',
      content: '',
    }

    setMessages((prev) => [...prev, aiMessage])

    const controller = initConversationSSE(productId, {
      onMessage: (data) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === aiMsgId ? { ...m, content: m.content + data } : m,
          ),
        )
      },
      onDone: () => {
        setStreaming(false)
      },
      onError: () => {
        setStreaming(false)
      },
    })

    abortRef.current = controller
  }, [])

  const handleSendMessage = useCallback((productId: number, content: string) => {
    setSending(true)
    const userMsgId = `user-${Date.now()}`
    const userMessage: ChatMessage = {
      id: userMsgId,
      role: 'user',
      content,
    }
    const aiMsgId = `ai-${Date.now()}`
    const aiMessage: ChatMessage = {
      id: aiMsgId,
      role: 'ai',
      content: '',
    }

    setMessages((prev) => [...prev, userMessage, aiMessage])

    const controller = sendMessageSSE(productId, content, {
      onMessage: (data) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === aiMsgId ? { ...m, content: m.content + data } : m,
          ),
        )
      },
      onDone: () => {
        setSending(false)
      },
      onError: () => {
        setSending(false)
      },
    })

    abortRef.current = controller
  }, [])

  return {
    messages,
    streaming,
    sending,
    loadingHistory,
    loadHistory,
    initChat: handleInit,
    sendMessage: handleSendMessage,
    abort,
    setMessages,
    clearMessages,
  }
}
