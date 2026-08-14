/**
 * Saphira AI™ System Configuration Module
 * Holds global parameters: model selection, temperature, safety settings,
 * and the primary systemInstruction that directs conversational behavior.
 */

export const SAPHIRA_CONFIG = {
  model: import.meta.env.VITE_SAPHIRA_MODEL || 'saphira-default',
  temperature: 0.7,
  maxTokens: 4096,
  stream: true,
  safetySettings: {
    harassment: 'BLOCK_MEDIUM_AND_ABOVE',
    hateSpeech: 'BLOCK_MEDIUM_AND_ABOVE',
    sexuallyExplicit: 'BLOCK_MEDIUM_AND_ABOVE',
    dangerousContent: 'BLOCK_MEDIUM_AND_ABOVE',
  },
  /**
   * Primary system instruction.
   * Directs Saphira to remain conversational upfront, complete background
   * tasks quietly, and address users dynamically by name when available.
   */
  systemInstruction: `You are Saphira AI™, a persistent multimodal intelligence operating system.
Remain conversational and clear in your responses.
Complete background tasks and tool calls quietly without narrating every internal step unless the user asks.
When the user's name is known, address them by name naturally.
Prioritize accuracy, helpfulness, and respect for user intent and policy boundaries.`,
} as const;

export type SaphiraConfig = typeof SAPHIRA_CONFIG;
