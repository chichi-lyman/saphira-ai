import React from 'react';
import { useUser } from '../../context/UserContext';

/**
 * Top Bar / App Navigation for Saphira AI™
 */
const Header: React.FC = () => {
  const { user } = useUser();

  return (
    <header className="saphira-header">
      <h1>Saphira AI™</h1>
      <div style={{ fontSize: '0.9rem', color: 'var(--saphira-muted)' }}>
        {user.name}
      </div>
    </header>
  );
};

export default Header;
