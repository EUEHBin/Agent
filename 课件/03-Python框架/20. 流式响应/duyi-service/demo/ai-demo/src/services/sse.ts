const BASE_URL = '/api'

function getToken() {
  return localStorage.getItem('token') || ''
}

export type SSEEventHandler = {
  onMessage?: (data: string) => void
  onDone?: () => void
  onError?: (error: Error) => void
}

async function readSSEStream(
  response: Response,
  handlers: SSEEventHandler,
  signal: AbortSignal,
) {
  const reader = response.body?.getReader()
  if (!reader) return

  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      if (signal.aborted) {
        reader.cancel()
        break
      }

      const { done, value } = await reader.read()
      if (done) {
        handlers.onDone?.()
        break
      }

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line || line === '\r') continue

        if (line.startsWith('data:')) {
          const raw = line.slice(5)
          const content = raw.trim()

          if (!content && !raw) continue

          if (content === '[DONE]') {
            handlers.onDone?.()
            return
          }

          const data = content || '\n'

          try {
            const parsed = JSON.parse(data)
            handlers.onMessage?.(parsed.content ?? data)
          } catch {
            handlers.onMessage?.(data)
          }
        }
      }
    }
  } catch (err: any) {
    if (!signal.aborted) {
      handlers.onError?.(err)
    }
  } finally {
    reader.releaseLock()
  }
}

export function initConversationSSE(
  productId: number,
  handlers: SSEEventHandler,
): AbortController {
  const controller = new AbortController()

  fetch(`${BASE_URL}/ai/sse/initialize/${productId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
    signal: controller.signal,
  })
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return readSSEStream(res, handlers, controller.signal)
    })
    .catch((err) => {
      if (!controller.signal.aborted) {
        handlers.onError?.(err)
      }
    })

  return controller
}

export function sendMessageSSE(
  productId: number,
  content: string,
  handlers: SSEEventHandler,
): AbortController {
  const controller = new AbortController()

  fetch(`${BASE_URL}/ai/sse/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ product_id: productId, content }),
    signal: controller.signal,
  })
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return readSSEStream(res, handlers, controller.signal)
    })
    .catch((err) => {
      if (!controller.signal.aborted) {
        handlers.onError?.(err)
      }
    })

  return controller
}
