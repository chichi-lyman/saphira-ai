/*
 * Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
 * Public chat endpoint so visitors can talk to Saphira on the website.
 */

import type { NextApiRequest, NextApiResponse } from 'next';

const SYSTEM_PROMPT = `You are Saphira AI, created by Chelsea Megan Woods.
You are warm, confident, concise, and helpful.
You are the user's personal AI assistant and multi-agent operator.
Never sound robotic. Keep replies under 3 sentences unless the user asks for detail.
Signature style: "I'm here. What are we tackling?"`;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { message } = req.body;
  if (!message) {
    return res.status(400).json({ error: 'Missing message' });
  }

  // Prefer Gemini if key is present, otherwise return a graceful fallback
  const geminiKey = process.env.GEMINI_API_KEY;

  if (geminiKey) {
    try {
      const { GoogleGenerativeAI } = await import('@google/generative-ai');
      const genAI = new GoogleGenerativeAI(geminiKey);
      const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });
      const result = await model.generateContent([
        { role: 'user', parts: [{ text: SYSTEM_PROMPT + '\n\nUser: ' + message }] },
      ]);
      const reply = result.response.text();
      return res.status(200).json({ reply });
    } catch (e: any) {
      console.error(e);
    }
  }

  // Fallback personality replies so the widget never feels broken
  const fallbacks = [
    "I'm here. What are we tackling?",
    "Got it. Tell me a bit more and I'll handle the next step.",
    "On it. While I work, anything else you need?",
    "That part is tricky for most people. Here's the simplest path forward.",
  ];
  const reply = fallbacks[Math.floor(Math.random() * fallbacks.length)];
  return res.status(200).json({ reply });
}
