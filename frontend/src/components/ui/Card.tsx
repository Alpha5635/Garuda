import React from 'react';
import { cn } from '../../utils/cn';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'bordered' | 'subtle' | 'accent';
  hoverEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({
  className,
  variant = 'default',
  hoverEffect = false,
  children,
  ...props
}) => {
  const variantStyles = {
    default: "bg-white border border-slate-200/80 shadow-subtle",
    bordered: "bg-white border-2 border-slate-300 shadow-sm",
    subtle: "bg-slate-50 border border-slate-200/60",
    accent: "bg-gradient-to-b from-white to-slate-50 border border-slate-200 shadow-sm",
  };

  return (
    <div
      className={cn(
        "rounded-lg transition-all duration-150",
        variantStyles[variant],
        hoverEffect && "hover:shadow-elevated hover:border-slate-300",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={cn("px-5 py-4 border-b border-slate-100 flex items-center justify-between gap-3", className)} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className, children, ...props }) => (
  <h3 className={cn("text-base font-semibold text-slate-900", className)} {...props}>
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ className, children, ...props }) => (
  <p className={cn("text-xs text-slate-500 mt-0.5", className)} {...props}>
    {children}
  </p>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={cn("p-5", className)} {...props}>
    {children}
  </div>
);

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={cn("px-5 py-3.5 bg-slate-50/70 border-t border-slate-100 rounded-b-lg flex items-center justify-between gap-3", className)} {...props}>
    {children}
  </div>
);
