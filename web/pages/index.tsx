/* Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved. */

import SEOHead from '../src/components/SEOHead';
import SaphiraChatWidget from '../src/components/SaphiraChatWidget';
import { useState } from 'react';

export default function LandingPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const startCheckout = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier: 'monthly' }),
      });
      const data = await res.json();
      if (!res.ok || !data.url) throw new Error(data.error || 'Checkout is unavailable.');
      window.location.href = data.url;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Checkout is unavailable.');
      setLoading(false);
    }
  };

  return (
    <>
      <SEOHead />
      <main style={styles.page}>
        <nav style={styles.nav}>
          <strong style={styles.logo}>Saphira AI</strong>
          <button onClick={startCheckout} disabled={loading} style={styles.smallButton}>Launch Saphira</button>
        </nav>

        <section style={styles.hero}>
          <div style={styles.badge}>AI CLIENT ACQUISITION · $199/MONTH</div>
          <h1 style={styles.h1}>Stop chasing leads.<br /><span style={styles.gradient}>Let Saphira work.</span></h1>
          <p style={styles.subhead}>
            Saphira helps local service businesses find qualified prospects, prepare personalized outreach, and organize the sales pipeline from one conversational workspace.
          </p>
          <div style={styles.actions}>
            <button onClick={startCheckout} disabled={loading} style={styles.primaryButton}>
              {loading ? 'Opening secure checkout…' : 'Start Saphira — $199/mo'}
            </button>
            <a href="#how" style={styles.secondaryButton}>See how it works</a>
          </div>
          {error && <p style={styles.error}>{error}</p>}
          <p style={styles.note}>Secure Stripe checkout · Cancel anytime</p>
        </section>

        <section id="how" style={styles.section}>
          <h2 style={styles.h2}>One system. Three jobs.</h2>
          <div style={styles.grid}>
            <Feature title="Find prospects" text="Define an industry and market. Saphira organizes qualified business prospects into your review queue." />
            <Feature title="Prepare outreach" text="Generate tailored messages from approved lead data, with governance before commercial actions are sent." />
            <Feature title="Track revenue" text="Keep customer, subscription, lead, and execution events connected to an auditable operating layer." />
          </div>
        </section>

        <section style={styles.offer}>
          <div>
            <span style={styles.offerLabel}>SAPHIRA AI</span>
            <h2 style={styles.offerTitle}>Your conversational sales operations layer.</h2>
            <p style={styles.offerText}>No giant dashboard maze. Tell Saphira what you need, review governed actions, and keep the execution history in one place.</p>
          </div>
          <button onClick={startCheckout} disabled={loading} style={styles.primaryButton}>Activate for $199/mo</button>
        </section>

        <footer style={styles.footer}>
          © 2026 Chelsea Megan Woods · Saphira AI · Nova Umbrella Systems
        </footer>
      </main>
      <SaphiraChatWidget />
    </>
  );
}

function Feature({ title, text }: { title: string; text: string }) {
  return <article style={styles.card}><h3 style={styles.cardTitle}>{title}</h3><p style={styles.cardText}>{text}</p></article>;
}

const styles: Record<string, React.CSSProperties> = {
  page: { minHeight: '100vh', background: 'linear-gradient(180deg,#fbfdff 0%,#f4f7fb 100%)', color: '#182033', fontFamily: 'Inter,system-ui,sans-serif', padding: '0 24px' },
  nav: { maxWidth: 1080, margin: '0 auto', padding: '24px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  logo: { fontSize: 24, letterSpacing: '-.04em' },
  smallButton: { border: '1px solid #d9dfeb', background: '#fff', borderRadius: 999, padding: '10px 18px', fontWeight: 700, cursor: 'pointer' },
  hero: { maxWidth: 900, margin: '0 auto', padding: '92px 0 100px', textAlign: 'center' },
  badge: { display: 'inline-block', fontSize: 11, letterSpacing: '.14em', fontWeight: 800, color: '#a00068', background: '#fff0fa', border: '1px solid #ffd3ee', borderRadius: 999, padding: '8px 12px' },
  h1: { fontSize: 'clamp(48px,8vw,84px)', lineHeight: .98, letterSpacing: '-.06em', margin: '24px 0' },
  gradient: { background: 'linear-gradient(90deg,#ff007f,#00bcd4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
  subhead: { maxWidth: 700, margin: '0 auto', color: '#667085', fontSize: 19, lineHeight: 1.6 },
  actions: { display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap', marginTop: 34 },
  primaryButton: { border: 0, borderRadius: 14, padding: '16px 24px', color: '#fff', background: 'linear-gradient(90deg,#00bcd4,#ff007f)', fontWeight: 800, fontSize: 16, cursor: 'pointer', boxShadow: '0 14px 32px rgba(255,0,127,.16)' },
  secondaryButton: { border: '1px solid #d9dfeb', borderRadius: 14, padding: '16px 24px', color: '#182033', background: '#fff', fontWeight: 800, textDecoration: 'none' },
  note: { color: '#98a2b3', fontSize: 12, marginTop: 14 },
  error: { color: '#b42318', marginTop: 16, fontWeight: 700 },
  section: { maxWidth: 1080, margin: '0 auto', padding: '70px 0' },
  h2: { fontSize: 38, letterSpacing: '-.04em', marginBottom: 28 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))', gap: 16 },
  card: { background: 'rgba(255,255,255,.72)', border: '1px solid #e4e9f2', borderRadius: 22, padding: 28, boxShadow: '0 18px 50px rgba(31,38,135,.05)' },
  cardTitle: { fontSize: 20, margin: '0 0 10px' },
  cardText: { color: '#667085', lineHeight: 1.65, margin: 0 },
  offer: { maxWidth: 1080, margin: '30px auto 80px', padding: 36, borderRadius: 28, background: '#101522', color: '#fff', display: 'flex', justifyContent: 'space-between', gap: 28, alignItems: 'center', flexWrap: 'wrap' },
  offerLabel: { fontSize: 11, letterSpacing: '.16em', color: '#80deea', fontWeight: 800 },
  offerTitle: { fontSize: 32, letterSpacing: '-.04em', margin: '10px 0' },
  offerText: { color: '#c8ced9', maxWidth: 650, lineHeight: 1.6 },
  footer: { maxWidth: 1080, margin: '0 auto', padding: '30px 0 50px', borderTop: '1px solid #e4e9f2', color: '#98a2b3', fontSize: 12, textAlign: 'center' },
};
