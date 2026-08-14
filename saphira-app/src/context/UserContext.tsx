/**
 * Saphira AI™ User Session Provider
 * Holds the currently logged-in user's profile details so Saphira
 * always knows who it is interacting with.
 */

import React, { createContext, useContext, useMemo, useState, ReactNode } from 'react';

export interface SaphiraUser {
  id: string | null;
  name: string;
  email?: string;
  avatarUrl?: string;
}

interface UserContextValue {
  user: SaphiraUser;
  setUser: (user: SaphiraUser) => void;
  setUserName: (name: string) => void;
  clearUser: () => void;
}

const defaultUser: SaphiraUser = {
  id: null,
  name: 'Guest',
};

const UserContext = createContext<UserContextValue | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SaphiraUser>(defaultUser);

  const value = useMemo(
    () => ({
      user,
      setUser,
      setUserName: (name: string) => setUser((prev) => ({ ...prev, name })),
      clearUser: () => setUser(defaultUser),
    }),
    [user]
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export function useUser(): UserContextValue {
  const ctx = useContext(UserContext);
  if (!ctx) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return ctx;
}
