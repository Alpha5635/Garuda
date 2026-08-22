import React from 'react';
import { Card, CardContent } from './Card';
import { Badge } from './Badge';
import { cn } from '../../utils/cn';
import { CheckCircle, XCircle, AlertTriangle, BookOpen } from 'lucide-react';

export interface RuleCardProps {
  clause: string;
  ruleTitle: string;
  statutoryStandard: string;
  evaluatedValue: string;
  status: 'Pass' | 'Fail' | 'Warning' | 'Not Applicable' | 'Review Required';
  measuredMm?: number;
  requiredMm?: number;
  notes?: string;
  className?: string;
}

export const RuleCard: React.FC<RuleCardProps> = ({
  clause,
  ruleTitle,
  statutoryStandard,
  evaluatedValue,
  status,
  measuredMm,
  requiredMm,
  notes,
  className,
}) => {
  const getStatusDisplay = () => {
    switch (status) {
      case 'Pass':
        return {
          badge: <Badge variant="green">Verified Pass</Badge>,
          border: 'border-l-4 border-l-emerald-600',
          icon: <CheckCircle className="w-4 h-4 text-emerald-600" />
        };
      case 'Fail':
        return {
          badge: <Badge variant="red">Statutory Violation</Badge>,
          border: 'border-l-4 border-l-red-600',
          icon: <XCircle className="w-4 h-4 text-red-600" />
        };
      case 'Warning':
      case 'Review Required':
        return {
          badge: <Badge variant="amber">Review Required</Badge>,
          border: 'border-l-4 border-l-amber-500',
          icon: <AlertTriangle className="w-4 h-4 text-amber-600" />
        };
      default:
        return {
          badge: <Badge variant="slate">Exempt / N.A.</Badge>,
          border: 'border-l-4 border-l-slate-400',
          icon: <BookOpen className="w-4 h-4 text-slate-500" />
        };
    }
  };

  const statusConfig = getStatusDisplay();

  return (
    <Card className={cn(statusConfig.border, "transition-all", className)}>
      <CardContent className="p-4 space-y-2.5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                {clause}
              </span>
              <h4 className="text-sm font-bold text-slate-900">{ruleTitle}</h4>
            </div>
            <p className="text-xs text-slate-500 mt-1 flex items-center gap-1.5">
              <BookOpen className="w-3 h-3 text-slate-400" />
              <span>Standard: {statutoryStandard}</span>
            </p>
          </div>
          {statusConfig.badge}
        </div>

        <div className="bg-slate-50 p-2.5 rounded-md border border-slate-200/80 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">Detected / Readout</span>
            <span className="font-medium text-slate-800 break-words">{evaluatedValue}</span>
          </div>
          {typeof measuredMm !== 'undefined' && typeof requiredMm !== 'undefined' && (
            <div>
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Millimeter Calibration</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className={cn(
                  "font-mono font-bold",
                  measuredMm >= requiredMm ? "text-emerald-700" : "text-red-700"
                )}>
                  {measuredMm.toFixed(1)} mm
                </span>
                <span className="text-slate-400 text-[10px]">vs Req. {requiredMm.toFixed(1)} mm</span>
              </div>
            </div>
          )}
        </div>

        {notes && (
          <p className="text-xs text-slate-600 bg-amber-50/60 text-amber-900 border border-amber-200/60 p-2 rounded">
            <strong>Finding Note:</strong> {notes}
          </p>
        )}
      </CardContent>
    </Card>
  );
};
