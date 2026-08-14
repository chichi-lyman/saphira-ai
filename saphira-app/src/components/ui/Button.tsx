import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost';
  children: React.ReactNode;
}

/**
 * Reusable UI Button for Saphira AI™
 */
const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  children,
  className = '',
  ...rest
}) => {
  const base = 'saphira-btn';
  const variantClass = variant === 'ghost' ? 'saphira-btn-ghost' : '';
  return (
    <button className={`${base} ${variantClass} ${className}`.trim()} {...rest}>
      {children}
    </button>
  );
};

export default Button;
