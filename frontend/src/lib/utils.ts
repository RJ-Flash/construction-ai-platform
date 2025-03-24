import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { format } from "date-fns"

/**
 * Combines class names with Tailwind's merge functionality
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a date with the specified format
 */
export function formatDate(date: Date | string | number, formatString: string = "PPP") {
  return format(new Date(date), formatString)
}

/**
 * Format a number as currency
 */
export function formatCurrency(amount: number, options: Intl.NumberFormatOptions = {}) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
    ...options,
  }).format(amount)
}

/**
 * Format a number as a percentage
 */
export function formatPercentage(value: number, options: Intl.NumberFormatOptions = {}) {
  return new Intl.NumberFormat("en-US", {
    style: "percent",
    maximumFractionDigits: 2,
    ...options,
  }).format(value / 100)
}

/**
 * Format file size in bytes to a human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes"
  
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`
}

/**
 * Get file extension from a filename
 */
export function getFileExtension(filename: string): string {
  return filename.slice(((filename.lastIndexOf(".") - 1) >>> 0) + 2).toLowerCase()
}

/**
 * Truncate a string to a specified length
 */
export function truncateString(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + "..."
}

/**
 * Check if string is a valid URL
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Sleep for specified milliseconds
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Debounce a function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  
  return function(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }
    
    if (timeout !== null) {
      clearTimeout(timeout)
    }
    
    timeout = setTimeout(later, wait)
  }
}

/**
 * Generate a random ID
 */
export function generateId(length: number = 8): string {
  return Math.random().toString(36).substring(2, 2 + length)
}

/**
 * Get element type color for UI
 */
export function getElementTypeColor(type: string): { bg: string; text: string; border: string } {
  switch (type.toLowerCase()) {
    case 'wall':
      return { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-500' }
    case 'column':
      return { bg: 'bg-indigo-100', text: 'text-indigo-800', border: 'border-indigo-500' }
    case 'beam':
      return { bg: 'bg-violet-100', text: 'text-violet-800', border: 'border-violet-500' }
    case 'door':
      return { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-500' }
    case 'window':
      return { bg: 'bg-teal-100', text: 'text-teal-800', border: 'border-teal-500' }
    case 'ceiling':
      return { bg: 'bg-sky-100', text: 'text-sky-800', border: 'border-sky-500' }
    case 'floor':
      return { bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-500' }
    case 'electrical':
      return { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-500' }
    case 'plumbing':
      return { bg: 'bg-cyan-100', text: 'text-cyan-800', border: 'border-cyan-500' }
    case 'hvac':
      return { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-500' }
    case 'annotation':
      return { bg: 'bg-fuchsia-100', text: 'text-fuchsia-800', border: 'border-fuchsia-500' }
    default:
      return { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-500' }
  }
}
