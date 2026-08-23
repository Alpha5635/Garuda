import React from 'react';
import { Card, CardContent } from './Card';
import { Badge } from './Badge';
import { DeclarationFinding } from '../../types';
import { cn } from '../../utils/cn';
import { AlertCircle, CheckCircle2, AlertTriangle, Languages, ShieldAlert, Sparkles } from 'lucide-react';

export interface FindingCardProps {
  finding: DeclarationFinding;
  onEdit?: (finding: DeclarationFinding) => void;
  className?: string;
}

export const FindingCard: React.FC<FindingCardProps> = ({
  finding,
  onEdit,
  className,
}) => {
  const isViolation = finding.status === 'Fail';
  const isReview = finding.status === 'Review Required' || finding.status === 'Warning';
  const isPass = finding.status === 'Pass';

  return (
    <Card className={cn(
      "border-l-4 transition-all",
      isViolation && "border-l-red-600 border-red-200 bg-red-50/20",
      isReview && "border-l-amber-500 border-amber-200 bg-amber-50/20",
      isPass && "border-l-emerald-600 border-slate-200",
      className
    )}>
      <CardContent className="p-4 space-y-2.5">
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono font-bold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                {finding.clause}
              </span>
              <h4 className="text-sm font-bold text-slate-900">{finding.field}</h4>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-mono text-slate-500">
              OCR: <strong className={cn(finding.ocrConfidence < 70 ? "text-amber-600 font-bold" : "text-slate-700")}>{finding.ocrConfidence}%</strong>
            </span>
            {isViolation && <Badge variant="red">Violation</Badge>}
            {isReview && <Badge variant="amber">Review</Badge>}
            {isPass && <Badge variant="green">Verified</Badge>}
          </div>
        </div>

        {/* Extracted Raw & Multilingual Text */}
        <div className="p-2.5 bg-white rounded border border-slate-200 space-y-1.5">
          <div className="flex items-baseline justify-between text-xs">
            <span className="text-slate-500 text-[10px] uppercase font-semibold">Extracted Text:</span>
            {finding.measuredHeightMm && (
              <span className="font-mono text-xs">
                Height: <strong className={cn(
                  finding.requiredHeightMm && finding.measuredHeightMm < finding.requiredHeightMm ? "text-red-600 font-bold" : "text-emerald-700 font-bold"
                )}>{finding.measuredHeightMm.toFixed(1)} mm</strong>
                {finding.requiredHeightMm && <span className="text-slate-400"> (Min: {finding.requiredHeightMm.toFixed(1)} mm)</span>}
              </span>
            )}
          </div>
          <p className="text-xs font-mono font-semibold text-slate-800 bg-slate-50 p-1.5 rounded border border-slate-100">
            {finding.extractedText}
          </p>

          {finding.hindiTranslation && (
            <div className="flex items-center gap-1.5 text-xs text-blue-800 bg-blue-50/70 px-2 py-1 rounded">
              <Languages className="w-3.5 h-3.5 text-blue-600 shrink-0" />
              <span className="font-hindi text-xs">{finding.hindiTranslation}</span>
            </div>
          )}
        </div>

        {/* Quiet Zone & Geometry Issues */}
        {!finding.quietZoneCleared && finding.quietZoneOverlapReason && (
          <div className="p-2.5 bg-red-100/60 border border-red-300 rounded text-xs text-red-900 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-red-800">
              <ShieldAlert className="w-3.5 h-3.5 text-red-600" />
              <span>Quiet-Zone Collision Detected</span>
            </div>
            <p className="text-xs text-red-800 leading-relaxed">{finding.quietZoneOverlapReason}</p>
          </div>
        )}

        {/* Finding Notes / Retake Recommendations */}
        {finding.notes && (
          <p className="text-xs text-slate-600 bg-slate-50 p-2 rounded border border-slate-200">
            <strong className="text-slate-700">Audit Protocol:</strong> {finding.notes}
          </p>
        )}
      </CardContent>
    </Card>
  );
};
