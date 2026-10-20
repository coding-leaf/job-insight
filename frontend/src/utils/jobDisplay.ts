export const MISSING_VALUE_TEXT = '未注明'

/** Display a source value, keeping missing values explicit instead of inventing one. */
export function displayText(value: string | null | undefined): string {
  const trimmed = (value ?? '').trim()
  return trimmed === '' ? MISSING_VALUE_TEXT : trimmed
}

/** Only http(s) links may be opened as a job source; other protocols are rejected. */
export function toSafeExternalUrl(value: string | null | undefined): string | null {
  const trimmed = (value ?? '').trim()
  if (!trimmed) return null
  try {
    const parsed = new URL(trimmed)
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return null
    return parsed.href
  } catch {
    return null
  }
}
