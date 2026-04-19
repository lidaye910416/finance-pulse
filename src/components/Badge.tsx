interface BadgeProps {
  text: string;
  variant?: 'green' | 'red' | 'yellow' | 'blue' | 'purple' | 'gray';
}

export function Badge({ text, variant = 'gray' }: BadgeProps) {
  const variantStyles: Record<string, { bg: string; text: string; dot: string }> = {
    green: { bg: 'bg-accent-green/10 text-accent-green border-accent-green/20', text: 'text-accent-green', dot: 'bg-accent-green' },
    red: { bg: 'bg-accent-red/10 text-accent-red border-accent-red/20', text: 'text-accent-red', dot: 'bg-accent-red' },
    yellow: { bg: 'bg-accent-yellow/10 text-accent-yellow border-accent-yellow/20', text: 'text-accent-yellow', dot: 'bg-accent-yellow' },
    blue: { bg: 'bg-accent-blue/10 text-accent-blue border-accent-blue/20', text: 'text-accent-blue', dot: 'bg-accent-blue' },
    purple: { bg: 'bg-accent-purple/10 text-accent-purple border-accent-purple/20', text: 'text-accent-purple', dot: 'bg-accent-purple' },
    gray: { bg: 'bg-white/5 text-gray-400 border-white/10', text: 'text-gray-400', dot: 'bg-gray-500' },
  };

  const styles = variantStyles[variant];

  return (
    <span className={`
      inline-flex items-center gap-1.5
      px-2.5 py-1
      rounded-full text-xs font-medium font-display
      border
      ${styles.bg}
    `}>
      <span className={`w-1.5 h-1.5 rounded-full ${styles.dot} animate-pulse-slow`} />
      {text}
    </span>
  );
}
