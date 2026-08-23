import React from 'react';
import { Card, CardContent } from './Card';
import { cn } from '../../utils/cn';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: {
    value: string | number;
    trend: 'up' | 'down' | 'neutral';
    label?: string;
  };
  icon?: React.ReactNode;
  iconBg?: string;
  variant?: 'default' | 'pass' | 'warning' | 'violation' | 'info';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  change,
  icon,
  iconBg = 'bg-slate-100 text-slate-700',
  variant = 'default',
  className,
}) => {
  const borderVariants = {
    default: 'border-slate-200/80',
    pass: 'border-l-4 border-l-emerald-600 border-slate-200/80',
    warning: 'border-l-4 border-l-amber-500 border-slate-200/80',
    violation: 'border-l-4 border-l-red-600 border-slate-200/80',
    info: 'border-l-4 border-l-blue-600 border-slate-200/80',
  };

  return (
    <Card className={cn(borderVariants[variant], "hover:shadow-elevated transition-shadow", className)}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</p>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 font-mono">
                {value}
              </span>
              {subtitle && <span className="text-xs text-slate-500">{subtitle}</span>}
            </div>
          </div>
          {icon && (
            <div className={cn("p-2.5 rounded-lg shrink-0 flex items-center justify-center shadow-xs", iconBg)}>
              {icon}
            </div>
          )}
        </div>

        {change && (
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center gap-1.5 text-xs">
            {change.trend === 'up' && <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />}
            {change.trend === 'down' && <TrendingDown className="w-3.5 h-3.5 text-red-600" />}
            {change.trend === 'neutral' && <Minus className="w-3.5 h-3.5 text-slate-400" />}
            
            <span className={cn(
              "font-semibold font-mono",
              change.trend === 'up' && "text-emerald-700",
              change.trend === 'down' && "text-red-700",
              change.trend === 'neutral' && "text-slate-600"
            )}>
              {change.value}
            </span>
            {change.label && <span className="text-slate-500">{change.label}</span>}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
