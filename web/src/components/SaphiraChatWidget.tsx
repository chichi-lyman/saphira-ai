/*
 * Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
 * Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
 *
 * Public-facing interactive chat widget so visitors can talk to Saphira
 * directly on the landing page / business site.
 */

import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'saphira';
  text: string;
}

export default function SaphiraChatWidget() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'saphira',
      text: "Hey, I'm Saphira. What are we tackling today?",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');
    setMessages((m) => [...m, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch('/api/saphira-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg }),
      });
      const data = await res.json();
      setMessages((m) => [
        ...m,
        { role: 'saphira', text: data.reply || "I'm here. Try that again?" },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'saphira', text: "Connection hiccup. I'm still here — try once more." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating bubble */}
      <button
        onClick={() => setOpen(!open)}
        style={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          width: 64,
          height: 64,
          borderRadius: '50%',
          border: 'none',
          background: 'linear-gradient(135deg, #1a1a1a, #333)',
          color: '#fff',
          fontSize: 28,
          cursor: 'pointer',
          boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
          zIndex: 9999,
        }}
        aria-label="Talk to Saphira"
      >
        {open ? '✕' : '👩‍💻'}
      </button>

      {open && (
        <div
          style={{
            position: 'fixed',
            bottom: 100,
            right: 24,
            width: 340,
            maxHeight: 480,
            background: '#111',
            borderRadius: 16,
            boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            zIndex: 9998,
            border: '1px solid #333',
          }}
        >
          <div style={{ padding: '12px 16px', background: '#1a1a1a', borderBottom: '1px solid #333' }}>
            <strong style={{ color: '#fff' }}>Saphira</strong>
            <div style={{ fontSize: 12, color: '#aaa' }}>Your AI assistant · by Chelsea Megan Woods</div>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  marginBottom: 12,
                  textAlign: msg.role === 'user' ? 'right' : 'left',
                }}
              >
                <span
                  style={{
                    display: 'inline-block',
                    padding: '8px 12px',
                    borderRadius: 12,
                    background: msg.role === 'user' ? '#1877F2' : '#222',
                    color: '#fff',
                    maxWidth: '85%',
                    fontSize: 14,
                  }}
                >
                  {msg.text}
                </span>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          <div style={{ display: 'flex', padding: 12, borderTop: '1px solid #333', gap: 8 }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
              placeholder="Talk to Saphira..."
              style={{
                flex: 1,
                padding: '10px 12px',
                borderRadius: 8,
                border: '1px solid #444',
                background: '#1a1a1a',
                color: '#fff',
                outline: 'none',
              }}
            />
            <button
              onClick={send}
              disabled={loading}
              style={{
                padding: '10px 16px',
                borderRadius: 8,
                border: 'none',
                background: '#00c853',
                color: '#000',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>
        </div>
      )}
    </>
  );
}
