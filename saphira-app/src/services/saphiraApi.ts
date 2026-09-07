/**
 * Saphira AI™ API Integration Client
 * Central browser-side transport for the Saphira Core chat boundary.
 */

import { SAPHIRA_CONFIG } from '../config/saphiraConfig';
import type { SaphiraMessage, SaphiraChatRequest, SaphiraChatResponse } from '../types/saphira';

// Vercel supplies SAPHIRA_API_URL at build time through vite.config.ts.
// Keep /api as the local same-origin development default.
const API_BASE = (
  import.meta.env.VITE_SAPHIRA_API_BASE_URL || '/api'
).replace(/\/$/, '');
const API_KEY = import.meta.env.VITE_SAPHIRA_API_KEY || '';

function getHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (API_KEY) {
    headers['Authorization'] = `Bearer ${API_KEY}`;
  }
  return headers;
}

export async function sendChat(
  messages: SaphiraMessage[],
  options?: Partial<SaphiraChatRequest>
): Promise<SaphiraChatResponse> {
  const body: SaphiraChatRequest = {
    messages,
    model: options?.model ?? SAPHIRA_CONFIG.model,
    temperature: options?.temperature ?? SAPHIRA_CONFIG.temperature,
    max_tokens: options?.max_tokens ?? SAPHIRA_CONFIG.maxTokens,
    stream: false,
    system_instruction: SAPHIRA_CONFIG.systemInstruction,
    ...options,
  };

  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Saphira API error ${res.status}: ${text}`);
  }

  return res.json() as Promise<SaphiraChatResponse>;
}

/**
 * Stream text from /api/chat. Supports SSE and newline-delimited/raw chunks.
 */
export async function* streamChat(
  messages: SaphiraMessage[],
  options?: Partial<SaphiraChatRequest>
): AsyncGenerator<string, void, unknown> {
  const body: SaphiraChatRequest = {
    messages,
    model: options?.model ?? SAPHIRA_CONFIG.model,
    temperature: options?.temperature ?? SAPHIRA_CONFIG.temperature,
    max_tokens: options?.max_tokens ?? SAPHIRA_CONFIG.maxTokens,
    stream: true,
    system_instruction: SAPHIRA_CONFIG.systemInstruction,
    ...options,
  };

  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      ...getHeaders(),
      Accept: 'text/event-stream, application/json, text/plain, */*',
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Saphira API error ${res.status}: ${text}`);
  }

  if (!res.body) throw new Error('No response body for streaming');

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split(/\r?\n/);
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        const data = trimmed.startsWith('data:')
          ? trimmed.slice(5).trim()
          : trimmed;

        if (data === '[DONE]') return;

        try {
          const parsed = JSON.parse(data);
          const text =
            parsed.choices?.[0]?.delta?.content ??
            parsed.content ??
            parsed.text ??
            '';
          if (text) yield text;
        } catch {
          yield data;
        }
      }
    }

    const remainder = buffer.trim();
    if (remainder && remainder !== '[DONE]') {
      const data = remainder.startsWith('data:') ? remainder.slice(5).trim() : remainder;
      try {
        const parsed = JSON.parse(data);
        const text = parsed.choices?.[0]?.delta?.content ?? parsed.content ?? parsed.text ?? '';
        if (text) yield text;
      } catch {
        yield data;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export const saphiraApi = {
  sendChat,
  streamChat,
};
