const BASE_URL = '/api'

interface ApiResponse<T> {
  code: string
  data: T
  message: string
}

function getToken() {
  return localStorage.getItem('token') || ''
}

async function request<T>(url: string, options?: RequestInit): Promise<ApiResponse<T>> {
  const res = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
      ...options?.headers,
    },
  })
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`)
  }
  return res.json()
}

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  access_token: string
  token_type: string
}

export function loginApi(params: LoginParams): Promise<ApiResponse<LoginResult>> {
  return request<LoginResult>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

export interface Product {
  id: number
  name: string
  description: string
  brand: string | null
  created_at: string
}

export interface ProductPageResult {
  items: Product[]
  total: number
  page: number
  page_size: number
}

export function getProducts(page: number, pageSize: number = 10): Promise<ApiResponse<ProductPageResult>> {
  return request<ProductPageResult>(`/products?page=${page}&page_size=${pageSize}`)
}

export interface AiMessageItem {
  role: string
  content: string
}

export function getConversationHistory(productId: number): Promise<ApiResponse<AiMessageItem[]>> {
  return request<AiMessageItem[]>(`/ai/conversation/${productId}`)
}

export function deleteConversation(productId: number): Promise<ApiResponse<null>> {
  return request<null>(`/ai/conversation/${productId}`, {
    method: 'DELETE',
  })
}
