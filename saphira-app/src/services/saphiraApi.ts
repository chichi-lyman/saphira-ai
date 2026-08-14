/**
 * Saphira AI™ API Integration Client
 * Initializes the API client, attaches credentials, handles background
 * tool/workflow calls, and sends prompt requests to language model endpoints.
 */

import { SAPHIRA_CONFIG } from '../config/saphiraConfig';
import type { SaphiraMessage, SaphiraChatRequest, SaphiraChatResponse } from '../types/saphira';

const API_BASE =
  import.meta.env.VITE_SAPHIRA_API_BASE_URL || 'http://localhost:8000';
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

/**
 * Send a non-streaming chat request to the Saphira backend.
 */
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

  const res = await fetch(`${API_BASE}/api/chat`, {
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
 * Stream a chat response. Yields text chunks as they arrive.
 * Compatible with Server-Sent Events or chunked transfer from the backend.
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

  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Saphira API error ${res.status}: ${text}`);
  }

  if (!res.body) {
    throw new Error('No response body for streaming');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      // Support both raw text chunks and simple SSE "data: ..." lines
      const lines = chunk.split('\n');
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        if (trimmed.startsWith('data:')) {
          const data = trimmed.slice(5).trim();
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
            if (data) yield data;
          }
        } else {
          yield trimmed;
        }
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
