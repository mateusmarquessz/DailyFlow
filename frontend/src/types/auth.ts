export type ThemePreference = 'light' | 'dark'

export interface User {
  id: number
  email: string
  name: string
  avatar_url: string | null
  theme_preference: ThemePreference
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface AuthResponse extends AuthTokens {
  user: User
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
}

export interface UpdateProfilePayload {
  name?: string
  avatar_url?: string | null
  theme_preference?: ThemePreference
}

export interface ChangePasswordPayload {
  current_password: string
  new_password: string
}
