import React from 'react';
import { cn } from '../../utils/cn';
import { FileQuestion, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from './Button';

export interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionLabel,
  onAction,
  icon,
  className,
}) => (
  <div className={cn("text-center py-12 px-4 bg-white rounded-lg border border-dashed border-slate-300 flex flex-col items-center justify-center", className)}>
    <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mb-3">
      {icon || <FileQuestion className="w-6 h-6" />}
    </div>
    <h3 className="text-base font-semibold text-slate-900">{title}</h3>
    <p className="text-xs text-slate-500 max-w-sm mt-1 mb-4">{description}</p>
    {actionLabel && onAction && (
      <Button size="sm" onClick={onAction}>
        {actionLabel}
      </Button>
    )}
  </div>
);

export const LoadingState: React.FC<{ message?: string; className?: string }> = ({
  message = "Processing Legal Metrology Inspection Intelligence...",
  className,
}) => (
  <div className={cn("py-12 px-4 flex flex-col items-center justify-center text-center", className)}>
    <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
    <h4 className="text-sm font-semibold text-slate-800">{message}</h4>
    <p className="text-xs text-slate-500 mt-1">Calibrating millimeter optical grid & querying Rule 6(1) engine</p>
  </div>
);

export const ErrorState: React.FC<{
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}> = ({
  title = "Inspection Engine Notice",
  message,
  onRetry,
  className,
}) => (
  <div className={cn("py-8 px-6 bg-red-50/50 border border-red-200 rounded-lg text-center flex flex-col items-center", className)}>
    <div className="w-10 h-10 rounded-full bg-red-100 text-red-600 flex items-center justify-center mb-2">
      <AlertCircle className="w-5 h-5" />
    </div>
    <h4 className="text-sm font-bold text-red-900">{title}</h4>
    <p className="text-xs text-red-700 max-w-md mt-1 mb-4">{message}</p>
    {onRetry && (
      <Button variant="outline" size="sm" onClick={onRetry} className="border-red-300 text-red-800 hover:bg-red-50">
        Retry Inspection Scan
      </Button>
    )}
  </div>
);
