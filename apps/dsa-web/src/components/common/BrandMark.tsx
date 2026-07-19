import React from 'react';
import { cn } from '../../utils/cn';

type BrandMarkProps = {
  variant?: 'icon' | 'full' | 'wordmark';
  theme?: 'light' | 'dark' | 'auto';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
};

const SIZE_MAP = {
  sm: { icon: 20, wordmark: 'text-xs', gap: 1.5 },
  md: { icon: 28, wordmark: 'text-sm', gap: 2 },
  lg: { icon: 36, wordmark: 'text-lg', gap: 2.5 },
  xl: { icon: 48, wordmark: 'text-2xl', gap: 3 },
};

export const BrandMark: React.FC<BrandMarkProps> = ({
  variant = 'full',
  theme = 'auto',
  size = 'md',
  className,
}) => {
  const s = SIZE_MAP[size];
  const logoSize = variant === 'icon' ? s.icon : Math.round(s.icon * 1.2);

  const iconImg = (
    <img
      src="/logo.png"
      width={logoSize}
      height={logoSize}
      className="shrink-0 object-contain"
      style={{ borderRadius: '0.375rem' }}
      alt="如意金股"
    />
  );

  if (variant === 'icon') {
    return <div className={cn('inline-flex items-center justify-center', className)}>{iconImg}</div>;
  }

  const textColor = theme === 'light' ? 'text-gray-900' : theme === 'dark' ? 'text-gray-100' : 'text-foreground';
  const mutedColor = theme === 'light' ? 'text-gray-500' : theme === 'dark' ? 'text-gray-400' : 'text-secondary-text';

  return (
    <div className={cn('inline-flex items-center gap-2', className)}>
      {iconImg}
      <div className="flex flex-col">
        <span className={cn('font-bold tracking-tight leading-none', s.wordmark, textColor)}>
          如意金股
        </span>
        {variant === 'full' && (
          <span className={cn('text-[10px] font-medium tracking-wider leading-tight', mutedColor)}>
            RuyiDailyStockAnalysis
          </span>
        )}
      </div>
    </div>
  );
};