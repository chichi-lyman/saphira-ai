/**
 * Saphira AI™ Code & Markdown Formatting Utility
 * Helpers for rendering and sanitizing markdown content in chat bubbles.
 */

/**
 * Basic escape of HTML special characters for safe insertion when needed.
 */
export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, (c) => map[c] || c);
}

/**
 * Detect whether content appears to contain fenced code blocks.
 */
export function hasCodeBlocks(content: string): boolean {
  return /```[\s\S]*?```/.test(content);
}

/**
 * Extract language hint from a fenced code block if present.
 */
export function extractCodeLanguage(fenceLine: string): string {
  const match = fenceLine.match(/^```(\w+)?/);
  return match?.[1] ?? '';
}
