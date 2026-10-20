export const API_BASE = ''

export interface ApiResponse<T> {
  code: string
  data: T
  message: string
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

export interface UploadSignRequest {
  filename: string
  file_size: number
}

export interface UploadSignResponse {
  host: string
  access_id: string
  policy: string
  signature: string
  key: string
  content_type: string
  bucket_domain: string
}
