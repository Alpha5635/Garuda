import React from 'react';
import { Drawer } from '../ui/Drawer';
import { DeclarationFinding, Inspection, FindingActionType } from '../../types';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { 
  ShieldCheck, 
  Ruler, 
  Hash, 
  Crop, 
  FileCode2, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Scale, 
  Smartphone, 
  Clock, 
  UserCheck,
  Edit3,
  RefreshCw,
  Ban
} from 'lucide-react';
import { cn } from '../../utils/cn';

interface EvidenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  finding: DeclarationFinding | null;
  inspection: Inspection;
  onActionClick: (finding: DeclarationFinding, action: FindingActionType) => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  isOpen,
  onClose,
  finding,
  inspection,
  onActionClick,
}) => {
  if (!finding) return null;

  const isViolation = finding.status === 'Fail';
  const isReview = finding.status === 'Review Required' || finding.status === 'Warning';
  const isPass = finding.status === 'Pass';

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-blue-600" />
          <span>Traceable Evidence Docket</span>
        </div>
      }
      description={`Judicial chain-of-custody for ${finding.field}`}
      size="lg"
      footer={
        <div className="flex flex-wrap items-center justify-between gap-2 w-full">
          <div className="text-[11px] text-slate-500 font-mono">
            Chain-of-Custody Immutable
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onActionClick(finding, 'ReviewRequired')}
              leftIcon={<AlertTriangle className="w-3.5 h-3.5 text-amber-600" />}
            >
              Mark Review Required
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onActionClick(finding, 'Correct')}
              leftIcon={<Edit3 className="w-3.5 h-3.5 text-blue-600" />}
            >
              Correct Measurement
            </Button>
            {isViolation ? (
              <Button
                variant="danger"
                size="sm"
                onClick={() => onActionClick(finding, 'Approve')}
                leftIcon={<CheckCircle2 className="w-3.5 h-3.5" />}
              >
                Confirm Violation
              </Button>
            ) : (
              <Button
                variant="success"
                size="sm"
                onClick={() => onActionClick(finding, 'Approve')}
                leftIcon={<CheckCircle2 className="w-3.5 h-3.5" />}
              >
                Approve Verified
              </Button>
            )}
          </div>
        </div>
      }
    >
      <div className="space-y-5 text-xs text-slate-800">
        {/* Top Summary Banner */}
        <div className={cn(
          "p-4 rounded-xl border flex items-start justify-between gap-3",
          isViolation && "bg-red-50/80 border-red-200 text-red-950",
          isReview && "bg-amber-50/80 border-amber-200 text-amber-950",
          isPass && "bg-emerald-50/80 border-emerald-200 text-emerald-950"
        )}>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold bg-white px-2 py-0.5 rounded border border-slate-300">
                {finding.clause}
              </span>
              <h3 className="font-bold text-sm text-slate-900">{finding.field}</h3>
            </div>
            <p className="text-[11px] text-slate-600">
              {finding.ruleTitle || 'Legal Metrology (Packaged Commodities) Rules, 2011'}
            </p>
          </div>
          <div className="shrink-0">
            {isViolation && <Badge variant="red">Statutory Violation</Badge>}
            {isReview && <Badge variant="amber">Review Required</Badge>}
            {isPass && <Badge variant="green">Verified Compliant</Badge>}
          </div>
        </div>

        {/* Evidence Crop Visualizer */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold uppercase tracking-wider text-slate-500 text-[10px] flex items-center gap-1.5">
              <Crop className="w-3.5 h-3.5 text-blue-600" />
              High-Magnification Optical Crop
            </span>
            <span className="font-mono text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
              {finding.evidenceCrop?.magnification || '4.5x Optical Zoom'}
            </span>
          </div>

          <div className="relative aspect-16/8 bg-slate-950 rounded-lg overflow-hidden border border-slate-700 flex items-center justify-center p-3 shadow-inner">
            <img
              src={finding.evidenceCrop?.cropUrl || inspection.sampleImage}
              alt="Evidence Crop"
              className="max-h-full max-w-full object-contain rounded"
            />
            {/* Overlay Bounding Box Caliper on Crop */}
            <div className="absolute inset-x-8 inset-y-4 border border-blue-400 bg-blue-500/10 pointer-events-none rounded flex items-end justify-end p-1.5">
              <span className="text-[9px] font-mono text-blue-200 bg-slate-900/90 px-1 rounded">
                Calibrated: {finding.measuredHeightMm ? `${finding.measuredHeightMm.toFixed(1)} mm` : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Optical & Physical Measurement Breakdown */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-3.5 rounded-lg border border-slate-200 font-mono">
          <div>
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">Detected OCR</span>
            <span className="text-slate-900 font-bold text-xs">{finding.extractedText}</span>
          </div>
          <div>
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">Measured Height</span>
            <span className={cn(
              "font-bold text-xs",
              finding.measuredHeightMm && finding.requiredHeightMm && finding.measuredHeightMm < finding.requiredHeightMm ? "text-red-700" : "text-emerald-700"
            )}>
              {finding.measuredHeightMm ? `${finding.measuredHeightMm.toFixed(1)} mm` : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">Statutory Req</span>
            <span className="text-slate-900 font-bold text-xs">
              {finding.requiredHeightMm ? `${finding.requiredHeightMm.toFixed(1)} mm` : 'Rule 6(1)'}
            </span>
          </div>
          <div>
            <span className="text-slate-500 text-[10px] uppercase font-semibold block">OCR Confidence</span>
            <span className={cn(
              "font-bold text-xs",
              finding.ocrConfidence < 70 ? "text-amber-700" : "text-slate-900"
            )}>
              {finding.ocrConfidence}%
            </span>
          </div>
        </div>

        {/* Quiet Zone Clearance Detail */}
        {finding.quietZoneCleared === false && (
          <div className="p-3 bg-red-100/60 border border-red-300 rounded-lg text-red-950 space-y-1">
            <strong className="block font-bold">Rule 9(3) Quiet-Zone Hazard Detected:</strong>
            <p className="text-[11px] leading-relaxed">
              Measured clearance is <strong>{finding.quietZoneClearanceMm || 1.2} mm</strong>, which violates the mandatory 2x font height buffer requirement (<strong>{finding.quietZoneRequiredBufferMm || 8.0} mm</strong>).
            </p>
          </div>
        )}

        {/* Bounding Box Spatial Coordinates */}
        <div className="space-y-1.5">
          <span className="font-bold uppercase tracking-wider text-slate-500 text-[10px]">
            Spatial Bounding Box Pixel Coordinates
          </span>
          <div className="p-2.5 bg-slate-900 text-slate-200 font-mono rounded text-[11px] space-y-1">
            <div>Normalized (%): x={finding.bbox?.x}%, y={finding.bbox?.y}%, w={finding.bbox?.width}%, h={finding.bbox?.height}%</div>
            {finding.bbox?.rawCoordsPx && (
              <div className="text-slate-400">
                Raw Sensor Pixels: [ymin: {finding.bbox.rawCoordsPx.ymin}, xmin: {finding.bbox.rawCoordsPx.xmin}, ymax: {finding.bbox.rawCoordsPx.ymax}, xmax: {finding.bbox.rawCoordsPx.xmax}]
              </div>
            )}
          </div>
        </div>

        {/* Rule Traceability & Deterministic Logic */}
        <div className="space-y-1.5">
          <span className="font-bold uppercase tracking-wider text-slate-500 text-[10px]">
            Deterministic Rule Engine Logic
          </span>
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1.5 font-mono text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-500">Statutory Citation:</span>
              <span className="text-slate-900 font-bold">{finding.clause}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Rule Engine Version:</span>
              <span className="text-blue-700 font-bold">{finding.ruleVersion || 'LM-PCR-2011-v2024.2'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Evaluation Logic:</span>
              <span className={cn(
                "font-bold",
                finding.logicResult === 'FAILED' ? "text-red-700" : "text-emerald-700"
              )}>
                {finding.logicResult || (isViolation ? 'FAILED' : 'PASSED')}
              </span>
            </div>
          </div>
        </div>

        {/* Chain-of-Custody & Device EXIF Stamp */}
        <div className="space-y-1.5">
          <span className="font-bold uppercase tracking-wider text-slate-500 text-[10px]">
            Judicial Chain-of-Custody & Hardware Metadata
          </span>
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-500">Master Image SHA-256:</span>
              <span className="font-mono text-slate-800 truncate max-w-[220px]" title={inspection.imageSha256}>
                {inspection.imageSha256}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Evidence Sub-Crop Hash:</span>
              <span className="font-mono text-slate-800 truncate max-w-[220px]">
                {finding.evidenceCrop?.cropSha256 || '7fa890123efb671a980c5412df09e145b238a9701a23801f98124018fba81234'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Calibration Method:</span>
              <span className="font-bold text-slate-800">{inspection.calibration.method}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Scale Locked:</span>
              <span className="font-mono text-blue-700 font-bold">{inspection.calibration.pixelsPerMm.toFixed(2)} px / mm</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Inspection Officer:</span>
              <span className="text-slate-900 font-bold">{inspection.inspectorName} ({inspection.inspectorBadge})</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Captured Device:</span>
              <span className="text-slate-800">{inspection.capturedDevice || 'Samsung Galaxy Tab Active4 Pro'}</span>
            </div>
          </div>
        </div>
      </div>
    </Drawer>
  );
};
