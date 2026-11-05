import { createContext, useContext, useState, type ReactNode } from 'react'

export type ChatMode = 'sse' | 'websocket'

interface ChatModeContextType {
  mode: ChatMode
  setMode: (mode: ChatMode) => void
}

const ChatModeContext = createContext<ChatModeContextType | null>(null)

export function ChatModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ChatMode>('sse')

  return (
    <ChatModeContext.Provider value={{ mode, setMode }}>
      {children}
    </ChatModeContext.Provider>
  )
}

export function useChatMode() {
  const ctx = useContext(ChatModeContext)
  if (!ctx) {
    throw new Error('useChatMode must be used within ChatModeProvider')
  }
  return ctx
}
