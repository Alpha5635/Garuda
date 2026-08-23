import React from 'react';
import { InspectionStatus } from '../../types';
import { cn } from '../../utils/cn';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, Ban } from 'lucide-react';

export interface StatusBadgeProps {
  status: InspectionStatus;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  showIcon = true,
  className
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'Verified':
        return {
          label: 'Verified',
          icon: <CheckCircle2 className="shrink-0" />,
          styles: 'bg-emerald-50 text-emerald-800 border-emerald-300 ring-1 ring-emerald-500/20',
          dotColor: 'bg-emerald-600',
        };
      case 'Provisional':
        return {
          label: 'Provisional',
          icon: <HelpCircle className="shrink-0" />,
          styles: 'bg-blue-50 text-blue-800 border-blue-300 ring-1 ring-blue-500/20',
          dotColor: 'bg-blue-600',
        };
      case 'Violation':
        return {
          label: 'Violation',
          icon: <XCircle className="shrink-0" />,
          styles: 'bg-red-50 text-red-800 border-red-300 ring-1 ring-red-500/20',
          dotColor: 'bg-red-600',
        };
      case 'Review Required':
        return {
          label: 'Review Required',
          icon: <AlertTriangle className="shrink-0" />,
          styles: 'bg-amber-50 text-amber-900 border-amber-300 ring-1 ring-amber-500/20',
          dotColor: 'bg-amber-600',
        };
      case 'Not Evaluable':
        return {
          label: 'Not Evaluable',
          icon: <Ban className="shrink-0" />,
          styles: 'bg-slate-100 text-slate-700 border-slate-300 ring-1 ring-slate-400/20',
          dotColor: 'bg-slate-500',
        };
      default:
        return {
          label: status,
          icon: <HelpCircle className="shrink-0" />,
          styles: 'bg-slate-100 text-slate-700 border-slate-200',
          dotColor: 'bg-slate-500',
        };
    }
  };

  const config = getStatusConfig();

  const sizeStyles = {
    sm: 'text-[11px] px-2 py-0.5 gap-1 font-medium',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-semibold',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-semibold',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border shadow-sm tracking-tight',
        config.styles,
        sizeStyles[size],
        className
      )}
    >
      {showIcon && (
        <span className={iconSizes[size]}>
          {React.cloneElement(config.icon, { className: cn(iconSizes[size], 'text-current') })}
        </span>
      )}
      <span>{config.label}</span>
    </span>
  );
};
