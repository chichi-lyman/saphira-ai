/**
 * Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
 * Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
 *
 * Client-side / hybrid AI helpers.
 * Uses Chrome Prompt API (window.ai / Gemini Nano) when available,
 * with a clear fallback path for unsupported browsers.
 */

/**
 * Run a prompt on-device via the browser language model (e.g. Gemini Nano).
 * @param {string} promptText
 * @returns {Promise<string>}
 */
export async function runLocalPrompt(promptText) {
  if (typeof window === "undefined") {
    throw new Error("Client-side AI requires a browser context.");
  }

  // Chrome Prompt API / Gemini Nano (window.ai)
  if (window.ai && window.ai.languageModel) {
    const availability = await window.ai.languageModel.availability?.();
    if (availability === "unavailable") {
      throw new Error("On-device language model is unavailable on this device.");
    }
    const session = await window.ai.languageModel.create();
    try {
      const response = await session.prompt(promptText);
      return response;
    } finally {
      session.destroy?.();
    }
  }

  // Alternate experimental global
  if (window.model && typeof window.model.prompt === "function") {
    return window.model.prompt(promptText);
  }

  throw new Error(
    "Client-side AI is not supported in this browser. Use Chrome with Gemini Nano / Prompt API enabled, or fall back to the cloud API."
  );
}

/**
 * Summarize long text on-device when possible.
 */
export async function summarizeLocal(text, maxSentences = 3) {
  const prompt = `Summarize the following in at most ${maxSentences} sentences. Be clear and neutral.\n\n${text}`;
  return runLocalPrompt(prompt);
}

/**
 * Suggest a short smart reply.
 */
export async function smartReplyLocal(message) {
  const prompt = `Suggest one short, professional reply to this message (under 25 words):\n\n${message}`;
  return runLocalPrompt(prompt);
}

/**
 * Check whether on-device AI is available.
 */
export async function isClientAIAvailable() {
  try {
    if (typeof window === "undefined") return false;
    if (!window.ai?.languageModel) return false;
    if (typeof window.ai.languageModel.availability === "function") {
      const status = await window.ai.languageModel.availability();
      return status === "available" || status === "readily";
    }
    return true;
  } catch {
    return false;
  }
}
