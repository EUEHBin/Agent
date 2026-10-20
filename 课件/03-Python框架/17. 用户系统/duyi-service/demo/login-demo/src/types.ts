export const API_BASE = ''

export interface ApiResponse<T> {
  code: string
  data: T
  message: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserResponse {
  id: number
  username: string
}

export interface SettingItemResponse {
  key: string
  value: string
  display_name: string
  description: string
}

export interface SettingGroupResponse {
  key: string
  display_name: string
  description: string
  settings: SettingItemResponse[]
}

export interface SettingUpdateItem {
  key: string
  value: string
}
