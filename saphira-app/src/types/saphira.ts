/**
 * Saphira AI™ TypeScript Type Definitions
 * Data schema / type contract for requests, roles, token counts,
 * and API response structures.
 */

export type SaphiraRole = 'user' | 'model' | 'system' | 'assistant';

export interface SaphiraMessage {
  id?: string;
  role: SaphiraRole;
  content: string;
  createdAt?: string;
  tokenCount?: number;
}

export interface SaphiraChatRequest {
  messages: SaphiraMessage[];
  model?: string;
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
  system_instruction?: string;
  user_name?: string;
}

export interface SaphiraChatChoice {
  index: number;
  message: SaphiraMessage;
  finish_reason?: string;
}

export interface SaphiraUsage {
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
}

export interface SaphiraChatResponse {
  id?: string;
  object?: string;
  created?: number;
  model?: string;
  choices?: SaphiraChatChoice[];
  usage?: SaphiraUsage;
  content?: string;
  message?: SaphiraMessage;
}

export interface SaphiraThread {
  id: string;
  title: string;
  updatedAt: string;
  messageCount?: number;
}
