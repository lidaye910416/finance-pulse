import { ReactNode, MouseEventHandler } from 'react';

interface CardProps {
  title?: string;
  children: ReactNode;
  className?: string;
  onClick?: MouseEventHandler<HTMLDivElement>;
  variant?: 'default' | 'highlighted' | 'metric';
  animationDelay?: number;
}

export function Card({
  title,
  children,
  className = '',
  onClick,
  variant = 'default',
  animationDelay = 0
}: CardProps) {
  const baseStyles = `
    relative rounded-2xl p-4
    transition-all duration-200
    animate-fade-in-up
    ${onClick ? 'cursor-pointer btn-press' : ''}
  `;

  const variantStyles = {
    default: `
      glass-card
      hover:bg-surface-200
      hover:border-white/10
    `,
    highlighted: `
      bg-gradient-to-br from-surface-100 to-surface
      border border-accent-blue/20
      shadow-glow-blue
    `,
    metric: `
      bg-surface-100/80
      border border-white/5
      hover:border-white/10
    `,
  };

  return (
    <div
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      style={{ animationDelay: `${animationDelay}ms` }}
      onClick={onClick}
    >
      {title && (
        <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider mb-3">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}
