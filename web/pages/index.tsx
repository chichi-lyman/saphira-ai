/*
 * Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
 * Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
 */

import SEOHead from '../src/components/SEOHead';
import SaphiraChatWidget from '../src/components/SaphiraChatWidget';
import { useState } from 'react';

export default function LandingPage() {
  const [loading, setLoading] = useState(false);

  const startCheckout = async (tier: string) => {
    setLoading(true);
    try {
      const res = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier }),
      });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SEOHead />
      <main style={{
        minHeight: '100vh',
        background: '#0a0a0a',
        color: '#eee',
        fontFamily: 'system-ui, sans-serif',
        padding: '2rem',
        textAlign: 'center'
      }}>
        <h1 style={{ fontSize: '2.8rem', marginBottom: '0.5rem' }}>
          Saphira AI
        </h1>
        <p style={{ fontSize: '1.3rem', opacity: 0.85, maxWidth: 620, margin: '0 auto 1rem' }}>
          Speak upfront. Automate in silence.<br />
          Created by Chelsea Megan Woods
        </p>

        <p style={{ opacity: 0.7, marginBottom: '2rem' }}>
          Talk to her right now — the chat bubble is live in the bottom-right corner.
        </p>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '3rem' }}>
          <button onClick={() => startCheckout('free')} disabled={loading}
            style={btnStyle}>Start Free</button>
          <button onClick={() => startCheckout('monthly')} disabled={loading}
            style={{ ...btnStyle, background: '#1877F2' }}>$19 / mo</button>
          <button onClick={() => startCheckout('pro')} disabled={loading}
            style={{ ...btnStyle, background: '#00c853' }}>$49 Pro</button>
        </div>

        <section style={{ maxWidth: 700, margin: '0 auto', textAlign: 'left', opacity: 0.9 }}>
          <h2>Meet Saphira</h2>
          <ul>
            <li>Warm conversational companion you can see and talk to</li>
            <li>Silent multi-agent task execution in the background</li>
            <li>Camera vision, voice, smart-home & code automation</li>
            <li>Persistent memory that remembers your projects for weeks</li>
          </ul>
        </section>

        <footer style={{ marginTop: '4rem', fontSize: '0.85rem', opacity: 0.6 }}>
          Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.<br />
          Woods AI Studio / Lyman Legacies
        </footer>
      </main>

      {/* Live public chat widget */}
      <SaphiraChatWidget />
    </>
  );
}

const btnStyle: React.CSSProperties = {
  padding: '14px 28px',
  borderRadius: 8,
  border: 'none',
  background: '#333',
  color: '#fff',
  fontWeight: 600,
  cursor: 'pointer',
  fontSize: '1rem'
};
