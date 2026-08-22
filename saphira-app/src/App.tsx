import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useChat } from './context/ChatContext';
import { useSaphiraStream } from './hooks/useSaphiraStream';
import type { SaphiraMessage } from './types/saphira';

type View = 'home' | 'work' | 'chats' | 'settings';
type WorkItem = { id: string; title: string; status: 'ready' | 'running' | 'approval'; detail: string };

const starterPrompts = ['Plan my day', 'Research something for me', 'Help me build a business', 'Write something'];
const initialWork: WorkItem[] = [
  { id: '1', title: 'Roofing outreach campaign', status: 'approval', detail: '12 prospects are ready for review.' },
  { id: '2', title: 'Website deployment', status: 'ready', detail: 'Production build is ready for verification.' },
];

const makeMessage = (role: SaphiraMessage['role'], content: string): SaphiraMessage => ({
  id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
  role,
  content,
  createdAt: new Date().toISOString(),
});

const App: React.FC = () => {
  const { messages, addMessage, clearMessages, threads, setThreads, setActiveThreadId } = useChat();
  const { startStream, isStreaming, streamedContent, streamError, resetStream } = useSaphiraStream();
  const [view, setView] = useState<View>('home');
  const [draft, setDraft] = useState('');
  const [listening, setListening] = useState(false);
  const [work, setWork] = useState<WorkItem[]>(initialWork);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  const busy = isStreaming;
  const visibleMessages = useMemo(() => messages.filter((m) => m.role !== 'system'), [messages]);

  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), [messages, streamedContent, busy]);

  const send = async (value = draft) => {
    const text = value.trim();
    if (!text || busy) return;

    const userMessage = makeMessage('user', text);
    const requestMessages = [...messages, userMessage];
    addMessage(userMessage);
    setDraft('');
    resetStream();

    try {
      const reply = await startStream(requestMessages);
      if (reply.trim()) addMessage(makeMessage('model', reply));
    } catch {
      addMessage(makeMessage('model', 'I hit a connection problem reaching Saphira Core. Please try again.'));
    }

    if (messages.length === 0) {
      const thread = { id: userMessage.id!, title: text.slice(0, 42), updatedAt: new Date().toISOString(), messageCount: 2 };
      setThreads([thread, ...threads]);
      setActiveThreadId(thread.id);
    }
  };

  const startNewChat = () => {
    clearMessages();
    resetStream();
    setActiveThreadId(null);
    setView('home');
  };

  const approveWork = (id: string) => {
    setWork((items) => items.map((item) => item.id === id ? { ...item, status: 'running', detail: 'Approved. Execution is queued.' } : item));
  };

  return (
    <div className="saphira-app">
      <header className="topbar">
        <button className="brand" onClick={() => setView('home')} aria-label="Saphira home">
          <span className="brand-mark">✦</span><span>Saphira</span>
        </button>
        <div className="topbar-actions">
          <button className="icon-button" onClick={startNewChat} aria-label="New conversation">＋</button>
          <button className="profile-button" onClick={() => setView('settings')} aria-label="Settings">CW</button>
        </div>
      </header>

      <main className="app-body">
        {view === 'home' && (
          <section className="home-view">
            <div className={`orb ${listening ? 'orb-listening' : busy ? 'orb-thinking' : ''}`} onClick={() => setListening((v) => !v)} role="button" tabIndex={0} aria-label="Toggle voice mode">
              <div className="orb-core" /><div className="orb-ring ring-one" /><div className="orb-ring ring-two" /><div className="orb-glow" />
            </div>

            {visibleMessages.length === 0 && !streamedContent ? (
              <div className="welcome">
                <span className="eyebrow">SAPHIRA</span>
                <h1>{listening ? 'I’m listening.' : 'What are we doing?'}</h1>
                <p>Your conversational intelligence layer for thinking, research, execution, and follow-through.</p>
              </div>
            ) : (
              <div className="conversation">
                {visibleMessages.map((message) => (
                  <article key={message.id} className={`message ${message.role === 'user' ? 'message-user' : 'message-saphira'}`}>
                    {message.role !== 'user' && <span className="message-label">Saphira</span>}
                    <p>{message.content}</p>
                  </article>
                ))}
                {streamedContent && (
                  <article className="message message-saphira">
                    <span className="message-label">Saphira</span>
                    <p>{streamedContent}</p>
                  </article>
                )}
                {busy && <div className="thinking"><span /><span /><span /> Saphira is working</div>}
                {streamError && <div className="thinking">Connection error. Try again.</div>}
                <div ref={bottomRef} />
              </div>
            )}

            <div className="composer-wrap">
              <div className="quick-actions">
                {starterPrompts.map((prompt) => <button key={prompt} onClick={() => send(prompt)} disabled={busy}>{prompt}</button>)}
              </div>
              <form className="composer" onSubmit={(e) => { e.preventDefault(); send(); }}>
                <button type="button" className={`voice-button ${listening ? 'active' : ''}`} onClick={() => setListening((v) => !v)} aria-label="Voice input">⌁</button>
                <textarea value={draft} onChange={(e) => setDraft(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }} placeholder="Message Saphira..." rows={1} />
                <button className="send-button" disabled={!draft.trim() || busy} aria-label="Send message">↑</button>
              </form>
              <div className="composer-note">Saphira can make mistakes. Verify consequential actions before execution.</div>
            </div>
          </section>
        )}

        {view === 'work' && (
          <section className="content-view">
            <div className="section-heading"><div><span className="eyebrow">EXECUTION</span><h1>Work</h1></div><span className="quiet-status">{work.filter((x) => x.status === 'running').length} active</span></div>
            <div className="work-list">
              {work.map((item) => (
                <article className="work-card" key={item.id}>
                  <div className={`status-dot status-${item.status}`} />
                  <div className="work-copy"><h2>{item.title}</h2><p>{item.detail}</p></div>
                  {item.status === 'approval' && <button className="primary-small" onClick={() => approveWork(item.id)}>Review</button>}
                  {item.status !== 'approval' && <span className="status-text">{item.status === 'ready' ? 'Ready' : 'Queued'}</span>}
                </article>
              ))}
            </div>
          </section>
        )}

        {view === 'chats' && (
          <section className="content-view">
            <div className="section-heading"><div><span className="eyebrow">MEMORY</span><h1>Chats</h1></div><button className="primary-small" onClick={startNewChat}>New chat</button></div>
            <div className="chat-history">
              {threads.length === 0 ? <div className="empty-state"><span>✦</span><p>Your conversations will appear here.</p></div> : threads.map((thread) => <button className="history-item" key={thread.id} onClick={() => setView('home')}><span>{thread.title}</span><small>{thread.messageCount ?? 0} messages</small></button>)}
            </div>
          </section>
        )}

        {view === 'settings' && (
          <section className="content-view settings-view">
            <div className="section-heading"><div><span className="eyebrow">CONFIGURATION</span><h1>Settings</h1></div></div>
            <div className="settings-list">
              <label><span><strong>Voice responses</strong><small>Allow Saphira to speak responses when voice mode is active.</small></span><input type="checkbox" checked={voiceEnabled} onChange={(e) => setVoiceEnabled(e.target.checked)} /></label>
              <div><strong>Personality</strong><small>Warm, direct, intelligent, conversational.</small></div>
              <div><strong>Memory</strong><small>Saphira uses the connected memory layer when available.</small></div>
              <div><strong>Privacy & permissions</strong><small>Consequential tools remain behind explicit governance controls.</small></div>
            </div>
          </section>
        )}
      </main>

      <nav className="bottom-nav" aria-label="Primary navigation">
        <button className={view === 'home' ? 'selected' : ''} onClick={() => setView('home')}><span>◉</span>Home</button>
        <button className={view === 'work' ? 'selected' : ''} onClick={() => setView('work')}><span>◇</span>Work</button>
        <button className={view === 'chats' ? 'selected' : ''} onClick={() => setView('chats')}><span>◌</span>Chats</button>
      </nav>
    </div>
  );
};

export default App;
