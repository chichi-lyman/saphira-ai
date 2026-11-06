/**
 * Centralized Supabase Auth session context for Saphira AI.
 * Supabase owns credentials, refresh, expiry, recovery, and session revocation.
 */
import {
  createContext, useContext, useEffect, useMemo, useState,
  type ReactNode, type Dispatch, type SetStateAction,
} from 'react';
import type { Session } from '@supabase/supabase-js';
import { supabase, isSupabaseConfigured } from '../lib/supabase';

export interface SaphiraUser { id: string; name?: string; email?: string; }
interface UserContextValue {
  user: SaphiraUser | null;
  session: Session | null;
  loading: boolean;
  authEnabled: boolean;
  passwordRecovery: boolean;
  setUser: Dispatch<SetStateAction<SaphiraUser | null>>;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  updatePassword: (password: string) => Promise<void>;
}
const UserContext = createContext<UserContextValue | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SaphiraUser | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [passwordRecovery, setPasswordRecovery] = useState(false);

  useEffect(() => {
    if (!supabase) { setLoading(false); return; }
    let active = true;
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, next) => {
      if (!active) return;
      setSession(next);
      setUser(next?.user ? {
        id: next.user.id,
        email: next.user.email,
        name: next.user.user_metadata?.full_name || next.user.user_metadata?.name,
      } : null);
      if (event === 'PASSWORD_RECOVERY') setPasswordRecovery(true);
      if (event === 'SIGNED_OUT') setPasswordRecovery(false);
      setLoading(false);
    });
    supabase.auth.getSession().then(({ data, error }) => {
      if (!active) return;
      if (error) console.error('Could not restore Saphira session:', error.message);
      const next = data.session;
      setSession(next);
      setUser(next?.user ? {
        id: next.user.id,
        email: next.user.email,
        name: next.user.user_metadata?.full_name || next.user.user_metadata?.name,
      } : null);
      setLoading(false);
    }).catch(() => { if (active) setLoading(false); });
    return () => { active = false; subscription.unsubscribe(); };
  }, []);

  const signIn = async (email: string, password: string) => {
    if (!supabase) throw new Error('Supabase Auth is not configured.');
    const { error } = await supabase.auth.signInWithPassword({ email: email.trim(), password });
    if (error) throw error;
  };
  const signUp = async (email: string, password: string) => {
    if (!supabase) throw new Error('Supabase Auth is not configured.');
    const { error } = await supabase.auth.signUp({
      email: email.trim(), password,
      options: { emailRedirectTo: window.location.origin },
    });
    if (error) throw error;
  };
  const signInWithGoogle = async () => {
    if (!supabase) throw new Error('Supabase Auth is not configured.');
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google', options: { redirectTo: window.location.origin },
    });
    if (error) throw error;
  };
  const signOut = async () => {
    if (!supabase) return;
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  };
  const resetPassword = async (email: string) => {
    if (!supabase) throw new Error('Supabase Auth is not configured.');
    const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), {
      redirectTo: window.location.origin,
    });
    if (error) throw error;
  };
  const updatePassword = async (password: string) => {
    if (!supabase) throw new Error('Supabase Auth is not configured.');
    const { error } = await supabase.auth.updateUser({ password });
    if (error) throw error;
    setPasswordRecovery(false);
    window.history.replaceState({}, document.title, window.location.pathname);
  };

  const value = useMemo(() => ({
    user, session, loading, authEnabled: isSupabaseConfigured, passwordRecovery,
    setUser, signIn, signUp, signInWithGoogle, signOut, resetPassword, updatePassword,
  }), [user, session, loading, passwordRecovery]);
  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}
export function useUser(): UserContextValue {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error('useUser must be used within a UserProvider');
  return ctx;
}
