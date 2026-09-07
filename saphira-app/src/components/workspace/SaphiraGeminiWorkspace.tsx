/**
 * Saphira AI™ — Gemini-style single-screen workspace
 * Deep Obsidian & Cyberpunk Neon aesthetic
 *
 * Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
 * Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
 *
 * Reference component. Production chat remains driven by ChatContext + saphiraApi.
 * Requires lucide-react if used with the icon set below, or replace icons with inline SVGs.
 */

import React, { useEffect, useRef, useState } from 'react';

type ChatMessage = {
  id: number;
  sender: 'user' | 'saphira';
  text: string;
};

export default function SaphiraGeminiWorkspace() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      sender: 'saphira',
      text: 'Hello Chelsea Megan Woods™. Saphira AI™ is online and ready. How can I simplify your workflow today?',
    },
  ]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg: ChatMessage = { id: Date.now(), sender: 'user', text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');

    // Simulated response — replace with saphiraApi / stream hook in production
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: Date.now() + 1,
        sender: 'saphira',
        text: 'Processing request via model router… Executed task efficiently to save time and reduce friction.',
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    <div
      className="saphira-gemini-workspace"
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        width: '100vw',
        background: '#05030A',
        color: '#e2e8f0',
        fontFamily: 'ui-sans-serif, system-ui, sans-serif',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Ambient glow */}
      <div
        style={{
          position: 'absolute',
          top: '-10%',
          left: '-10%',
          width: '40%',
          height: '40%',
          borderRadius: '50%',
          background: 'rgba(138, 43, 226, 0.15)',
          filter: 'blur(120px)',
          pointerEvents: 'none',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '-10%',
          right: '-10%',
          width: '40%',
          height: '40%',
          borderRadius: '50%',
          background: 'rgba(255, 42, 141, 0.15)',
          filter: 'blur(120px)',
          pointerEvents: 'none',
        }}
      />

      {/* Header */}
      <header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 24px',
          borderBottom: '1px solid rgba(138, 43, 226, 0.2)',
          background: 'rgba(11, 8, 19, 0.4)',
          backdropFilter: 'blur(12px)',
          zIndex: 10,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div
            style={{
              padding: 8,
              borderRadius: 8,
              background: 'rgba(255, 42, 141, 0.1)',
              border: '1px solid rgba(255, 42, 141, 0.4)',
              color: '#FF2A8D',
              boxShadow: '0 0 10px rgba(255, 42, 141, 0.3)',
            }}
          >
            ✦
          </div>
          <h1
            style={{
              margin: 0,
              fontSize: 20,
              fontWeight: 800,
              letterSpacing: '0.04em',
              background: 'linear-gradient(to right, #FF2A8D, #00F0FF, #8A2BE2)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Saphira AI™
          </h1>
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: 12,
            color: '#00F0FF',
            background: 'rgba(0, 240, 255, 0.1)',
            border: '1px solid rgba(0, 240, 255, 0.3)',
            padding: '6px 12px',
            borderRadius: 999,
          }}
        >
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: '#00F0FF',
              display: 'inline-block',
              animation: 'pulse 2s infinite',
            }}
          />
          System Active
        </div>
      </header>

      {/* Messages */}
      <main
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '24px 16px',
          zIndex: 10,
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: 16,
            }}
          >
            <div
              style={{
                maxWidth: '80%',
                borderRadius: 16,
                padding: 16,
                border:
                  msg.sender === 'user'
                    ? '1px solid rgba(138, 43, 226, 0.4)'
                    : '1px solid rgba(255, 42, 141, 0.3)',
                background:
                  msg.sender === 'user'
                    ? 'rgba(138, 43, 226, 0.2)'
                    : 'rgba(11, 8, 19, 0.8)',
                color: msg.sender === 'user' ? '#fff' : '#e2e8f0',
                boxShadow:
                  msg.sender === 'saphira'
                    ? '0 0 15px rgba(255, 42, 141, 0.1)'
                    : undefined,
                borderBottomRightRadius: msg.sender === 'user' ? 0 : 16,
                borderBottomLeftRadius: msg.sender === 'saphira' ? 0 : 16,
              }}
            >
              <p style={{ margin: 0, fontSize: 15, lineHeight: 1.55 }}>{msg.text}</p>
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </main>

      {/* Prompt bar */}
      <footer style={{ padding: 16, zIndex: 10 }}>
        <form
          onSubmit={handleSend}
          style={{
            display: 'flex',
            alignItems: 'center',
            background: 'rgba(11, 8, 19, 0.9)',
            border: '1px solid rgba(0, 240, 255, 0.4)',
            borderRadius: 16,
            padding: '12px 16px',
            boxShadow: '0 0 20px rgba(0, 240, 255, 0.15)',
          }}
        >
          <button
            type="button"
            aria-label="Attach"
            style={{
              background: 'transparent',
              border: 0,
              color: '#94a3b8',
              cursor: 'pointer',
              padding: 4,
            }}
          >
            📎
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Saphira AI™ to automate a task, summarize, or generate…"
            style={{
              flex: 1,
              background: 'transparent',
              border: 0,
              outline: 'none',
              color: '#f1f5f9',
              padding: '0 12px',
              fontSize: 15,
            }}
          />
          <button
            type="button"
            aria-label="Microphone"
            onClick={() => setIsListening(!isListening)}
            style={{
              background: isListening ? '#FF2A8D' : 'transparent',
              border: 0,
              borderRadius: 12,
              color: isListening ? '#fff' : '#94a3b8',
              cursor: 'pointer',
              padding: 8,
              boxShadow: isListening ? '0 0 10px #FF2A8D' : undefined,
            }}
          >
            🎤
          </button>
          <button
            type="submit"
            aria-label="Send"
            style={{
              marginLeft: 8,
              padding: 8,
              borderRadius: 12,
              border: 0,
              background: 'linear-gradient(to right, #FF2A8D, #8A2BE2)',
              color: '#fff',
              cursor: 'pointer',
              boxShadow: '0 0 12px rgba(255, 42, 141, 0.4)',
            }}
          >
            ➤
          </button>
        </form>
        <p
          style={{
            textAlign: 'center',
            fontSize: 11,
            color: '#64748b',
            marginTop: 8,
          }}
        >
          Designed by Chelsea Megan Woods™ • Designed to simplify life by 1%.
        </p>
      </footer>
    </div>
  );
}
