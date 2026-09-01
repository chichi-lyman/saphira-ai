/**
 * Saphira AI - Chat Interface Component
 * Author: Chelsea Megan Woods
 * Organization: Woods Legacies
 */

import { useState, useRef, useEffect, FormEvent } from 'react';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
}

interface ChatApiResponse {
  message: string;
  session_id?: string;
  avatar_state?: string;
  status?: string;
  intent?: string;
  owner?: string;
}

export default function SaphiraChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessageText = input.trim();
    setInput('');

    const newUserMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: userMessageText,
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessageText,
          session_id: sessionId || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: ChatApiResponse = await response.json();

      if (data.session_id) {
        setSessionId(data.session_id);
      }

      const newAssistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: data.message || 'Response received.',
      };

      setMessages((prev) => [...prev, newAssistantMsg]);
    } catch (err) {
      console.error('Error connecting to /api/chat:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: 'Unable to reach Saphira AI service.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <header style={{ marginBottom: '1.5rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>Saphira AI Chat</h1>
        <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.25rem' }}>
          Architected & Built by Chelsea Megan Woods | Woods Legacies
        </p>
      </header>

      <div
        style={{
          minHeight: '400px',
          maxHeight: '600px',
          overflowY: 'auto',
          border: '1px solid #e2e8f0',
          borderRadius: '0.5rem',
          padding: '1rem',
          backgroundColor: '#ffffff',
          marginBottom: '1rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem',
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              backgroundColor: msg.sender === 'user' ? '#2563eb' : '#f1f5f9',
              color: msg.sender === 'user' ? '#ffffff' : '#0f172a',
              padding: '0.625rem 1rem',
              borderRadius: '0.5rem',
              maxWidth: '80%',
              wordBreak: 'break-word',
            }}
          >
            {msg.text}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: 'flex-start', color: '#94a3b8', fontSize: '0.875rem' }}>
            Saphira is processing...
          </div>
        )}
        <div ref={chatBottomRef} />
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Send a message to Saphira..."
          style={{
            flex: 1,
            padding: '0.75rem',
            border: '1px solid #cbd5e1',
            borderRadius: '0.375rem',
            fontSize: '1rem',
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#2563eb',
            color: '#ffffff',
            border: 'none',
            borderRadius: '0.375rem',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
}
