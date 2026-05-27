export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:3001'

export const WS_BASE_URL: string = import.meta.env.VITE_WS_BASE_URL ?? ''

export const BYPASS_AUTH: boolean =
  String(import.meta.env.VITE_BYPASS_AUTH ?? 'false').toLowerCase() === 'true'

export const BYPASS_USER_ID: string =
  import.meta.env.VITE_BYPASS_USER_ID ?? 'user-1'

export function isUsingFastApiBackend(): boolean {
  return /:8000(\b|\/)/.test(API_BASE_URL) || WS_BASE_URL.length > 0
}
