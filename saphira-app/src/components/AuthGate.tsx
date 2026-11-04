import { useState, type FormEvent, type ReactNode } from 'react';
import { useUser } from '../context/UserContext';

export function AuthGate({ children }: { children: ReactNode }) {
  const { user, loading, authEnabled, signIn, signUp, resetPassword } = useUser();
  const [mode, setMode] = useState<'signin' | 'signup' | 'reset'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setMessage('');
    setBusy(true);
    try {
      if (mode === 'signup') {
        await signUp(email, password);
        setMessage('Account created. Check your email to verify your address before signing in.');
      } else if (mode === 'reset') {
        await resetPassword(email);
        setMessage('If that account exists, a password-reset email has been sent.');
      } else {
        await signIn(email, password);
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Authentication could not be completed.');
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <main style={shell}><section style={panel}><p>Checking your secure session…</p></section></main>;
  if (!authEnabled) return <main style={shell}><section style={panel}>
    <div style={mark}>✦</div><h1 style={heading}>Saphira</h1>
    <p style={copy}>Cloud sign-in is not configured yet.</p>
    <p style={small}>Set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY in the web deployment, then rebuild. No shared API key belongs in the browser.</p>
  </section></main>;
  if (user) return <>{children}</>;

  return <main style={shell}><section style={panel}>
    <div style={mark}>✦</div><h1 style={heading}>Saphira</h1>
    <p style={copy}>Your AI assistant. Sign in to continue.</p>
    <form onSubmit={submit} style={{ display: 'grid', gap: 12, marginTop: 24 }}>
      <label style={label}>Email<input style={field} type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" /></label>
      {mode !== 'reset' && <label style={label}>Password<input style={field} type="password" minLength={8} autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" /></label>}
      <button type="submit" disabled={busy} style={primary}>{busy ? 'Please wait…' : mode === 'signup' ? 'Create account' : mode === 'reset' ? 'Send reset link' : 'Sign in'}</button>
    </form>
    {message && <p role="status" style={notice}>{message}</p>}
    <div style={links}>
      {mode !== 'signin' && <button style={link} onClick={() => { setMode('signin'); setMessage(''); }}>Back to sign in</button>}
      {mode === 'signin' && <>
        <button style={link} onClick={() => { setMode('signup'); setMessage(''); }}>Create an account</button>
        <button style={link} onClick={() => { setMode('reset'); setMessage(''); }}>Forgot password?</button>
      </>}
    </div>
    <p style={small}>Account security and sessions are managed by the identity provider.</p>
  </section></main>;
}

const shell: React.CSSProperties = { minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24, background: '#0B0813', color: '#fff', fontFamily: 'Inter, system-ui, sans-serif' };
const panel: React.CSSProperties = { width: 'min(100%, 420px)', padding: 32, border: '1px solid rgba(255,255,255,.12)', borderRadius: 24, background: 'rgba(25,18,37,.92)', boxShadow: '0 24px 80px rgba(0,0,0,.4)' };
const mark: React.CSSProperties = { color: '#FF00A0', fontSize: 30 };
const heading: React.CSSProperties = { margin: '8px 0', fontSize: 34, letterSpacing: '-.04em' };
const copy: React.CSSProperties = { color: '#c9bfd3', margin: 0 };
const small: React.CSSProperties = { color: '#93899e', fontSize: 12, lineHeight: 1.5, marginTop: 22 };
const label: React.CSSProperties = { display: 'grid', gap: 7, color: '#e9e2ef', fontSize: 13 };
const field: React.CSSProperties = { width: '100%', boxSizing: 'border-box', borderRadius: 12, border: '1px solid rgba(255,255,255,.16)', padding: '13px 14px', background: '#100b19', color: '#fff', fontSize: 15 };
const primary: React.CSSProperties = { border: 0, borderRadius: 12, padding: 14, background: 'linear-gradient(100deg,#8B00FF,#FF00A0)', color: '#fff', fontWeight: 700, cursor: 'pointer' };
const notice: React.CSSProperties = { color: '#e9d8ff', fontSize: 13, lineHeight: 1.5 };
const links: React.CSSProperties = { display: 'flex', justifyContent: 'space-between', gap: 12, marginTop: 16 };
const link: React.CSSProperties = { border: 0, background: 'transparent', color: '#d9a9ff', cursor: 'pointer', padding: 0, fontSize: 13 };
