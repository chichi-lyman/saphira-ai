import React from 'react';
import { useUser } from '../../context/UserContext';

/**
 * Top Bar / App Navigation for Saphira AI™
 */
const Header: React.FC = () => {
  const { user } = useUser();
  const displayName = user?.name ?? 'Guest';

  return (
    <header className="saphira-header">
      <h1>Saphira AI™</h1>
      <div style={{ fontSize: '0.9rem', color: 'var(--saphira-muted)' }}>
        {displayName}
        {user?.name ?? 'Guest'}
      </div>
    </header>
  );
};

export default Header;
