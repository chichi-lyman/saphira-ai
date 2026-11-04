/**
 * Saphira AI™ API Integration Client
 * Uses the signed-in Supabase user's access token; no shared browser API key.
 */
import { SAPHIRA_CONFIG } from '../config/saphiraConfig';
import { supabase } from '../lib/supabase';
import type { SaphiraMessage, SaphiraChatRequest, SaphiraChatResponse } from '../types/saphira';

const API_BASE = (import.meta.env.VITE_SAPHIRA_API_BASE_URL || '/api').replace(/\/$/, '');

async function getHeaders(): Promise<HeadersInit> {
  if (!supabase) throw new Error('Saphira sign-in is not configured.');
  const { data, error } = await supabase.auth.getSession();
  if (error) throw error;
  const token = data.session?.access_token;
  if (!token) throw new Error('Your Saphira session has expired. Sign in again.');
  return {
    'Content-Type': 'application/json',
    Authorization: 'Bearer ' + token,
  };
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
  const res = await fetch(API_BASE + '/chat', {
    method: 'POST',
    headers: await getHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error('Saphira API error ' + res.status + ': ' + await res.text());
  return res.json() as Promise<SaphiraChatResponse>;
}

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
  const headers = await getHeaders();
  const res = await fetch(API_BASE + '/chat', {
    method: 'POST',
    headers: { ...headers, Accept: 'text/event-stream, application/json, text/plain, */*' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error('Saphira API error ' + res.status + ': ' + await res.text());
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
        const data = trimmed.startsWith('data:') ? trimmed.slice(5).trim() : trimmed;
        if (data === '[DONE]') return;
        try {
          const parsed = JSON.parse(data);
          const content = parsed.choices?.[0]?.delta?.content ?? parsed.content ?? parsed.text ?? '';
          if (content) yield content;
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
        const content = parsed.choices?.[0]?.delta?.content ?? parsed.content ?? parsed.text ?? '';
        if (content) yield content;
      } catch {
        yield data;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export const saphiraApi = { sendChat, streamChat };
