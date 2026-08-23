import React from 'react';
import { cn } from '../../utils/cn';
import { Check } from 'lucide-react';

export interface StepItem {
  id: string;
  label: string;
  description?: string;
}

export interface ProgressIndicatorProps {
  steps: StepItem[];
  currentStepIndex: number;
  onStepClick?: (index: number) => void;
  className?: string;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  steps,
  currentStepIndex,
  onStepClick,
  className,
}) => {
  return (
    <div className={cn("w-full py-2", className)}>
      <div className="flex items-center justify-between relative">
        {/* Background Connecting Line */}
        <div className="absolute left-0 top-1/2 -translate-y-1/2 h-0.5 bg-slate-200 w-full z-0" />
        
        {/* Active Progress Fill */}
        <div 
          className="absolute left-0 top-1/2 -translate-y-1/2 h-0.5 bg-blue-600 transition-all duration-300 z-0"
          style={{
            width: `${(currentStepIndex / (steps.length - 1)) * 100}%`
          }}
        />

        {steps.map((step, index) => {
          const isCompleted = index < currentStepIndex;
          const isCurrent = index === currentStepIndex;
          const isPending = index > currentStepIndex;

          return (
            <div
              key={step.id}
              className={cn(
                "relative z-10 flex flex-col items-center group",
                onStepClick && !isPending && "cursor-pointer"
              )}
              onClick={() => onStepClick && !isPending && onStepClick(index)}
            >
              <div className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all border-2",
                isCompleted && "bg-blue-600 border-blue-600 text-white shadow-xs",
                isCurrent && "bg-white border-blue-600 text-blue-700 ring-4 ring-blue-100 shadow-sm",
                isPending && "bg-white border-slate-300 text-slate-400"
              )}>
                {isCompleted ? <Check className="w-4 h-4" /> : index + 1}
              </div>
              <span className={cn(
                "text-[11px] font-semibold mt-1.5 whitespace-nowrap tracking-tight transition-colors",
                isCurrent && "text-blue-900 font-bold",
                isCompleted && "text-slate-800",
                isPending && "text-slate-400"
              )}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
