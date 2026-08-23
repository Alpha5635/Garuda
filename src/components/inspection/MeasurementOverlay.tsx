import React, { useState } from 'react';
import { DeclarationFinding, CalibrationTarget } from '../../types';
import { cn } from '../../utils/cn';
import { Ruler, ShieldAlert, CheckCircle2, AlertTriangle } from 'lucide-react';

interface MeasurementOverlayProps {
  imageUrl: string;
  findings: DeclarationFinding[];
  calibration: CalibrationTarget;
  pdpAreaCm2: number;
  selectedFindingId: string | null;
  onSelectFinding: (findingId: string) => void;
  showPdpBoundary?: boolean;
  showQuietZone?: boolean;
  showCalipers?: boolean;
  showBBoxes?: boolean;
  contrastFilter?: boolean;
  zoom?: number;
}

export const MeasurementOverlay: React.FC<MeasurementOverlayProps> = ({
  imageUrl,
  findings,
  calibration,
  pdpAreaCm2,
  selectedFindingId,
  onSelectFinding,
  showPdpBoundary = true,
  showQuietZone = true,
  showCalipers = true,
  showBBoxes = true,
  contrastFilter = false,
  zoom = 100,
}) => {
  const [hoveredFindingId, setHoveredFindingId] = useState<string | null>(null);

  // Focus finding for calipers
  const netQtyFinding = findings.find(f => f.field.toLowerCase().includes('net quantity'));
  const activeFinding = findings.find(f => f.id === (hoveredFindingId || selectedFindingId)) || netQtyFinding;

  return (
    <div className="relative w-full h-full min-h-[500px] bg-slate-950 flex items-center justify-center overflow-hidden select-none">
      <div 
        className="relative transition-transform duration-200 w-full h-full flex items-center justify-center p-4"
        style={{ transform: `scale(${zoom / 100})` }}
      >
        <div className="relative inline-block max-w-full max-h-[580px] shadow-2xl rounded-lg overflow-hidden border border-slate-800">
          {/* Base Product Image */}
          <img
            src={imageUrl}
            alt="Packaging Evidence"
            className={cn(
              "block max-h-[560px] w-auto object-contain transition-all",
              contrastFilter && "contrast-125 brightness-95 saturate-150"
            )}
          />

          {/* Calibrated Millimeter Grid Background */}
          <div className="absolute inset-0 bg-mm-grid pointer-events-none opacity-30" />

          {/* SVG Geometric Overlay Layer */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-10">
            <defs>
              {/* Pattern for Quiet-Zone Collision Hatching */}
              <pattern id="hazardHatch" width="12" height="12" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
                <line x1="0" y1="0" x2="0" y2="12" stroke="#EF4444" strokeWidth="4" opacity="0.45" />
              </pattern>
              <pattern id="safeHatch" width="12" height="12" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
                <line x1="0" y1="0" x2="0" y2="12" stroke="#10B981" strokeWidth="2" opacity="0.25" />
              </pattern>
            </defs>

            {/* Principal Display Panel (PDP) 40% Area Rectangle */}
            {showPdpBoundary && (
              <g>
                <rect
                  x="8%"
                  y="6%"
                  width="84%"
                  height="88%"
                  fill="rgba(59, 130, 246, 0.04)"
                  stroke="#38BDF8"
                  strokeWidth="2"
                  strokeDasharray="6 4"
                  rx="6"
                />
                <rect
                  x="10%"
                  y="7%"
                  width="180"
                  height="22"
                  fill="#0F172A"
                  rx="3"
                  opacity="0.9"
                />
                <text
                  x="11%"
                  y="9.8%"
                  fill="#38BDF8"
                  fontSize="10"
                  fontFamily="JetBrains Mono, monospace"
                  fontWeight="bold"
                >
                  PDP AREA: {pdpAreaCm2} cm² (40% RULE)
                </text>
              </g>
            )}

            {/* Quiet Zone Hazard Boundary */}
            {showQuietZone && netQtyFinding && netQtyFinding.bbox && (
              <g>
                <rect
                  x={`${netQtyFinding.bbox.x - 4}%`}
                  y={`${netQtyFinding.bbox.y - 4}%`}
                  width={`${netQtyFinding.bbox.width + 8}%`}
                  height={`${netQtyFinding.bbox.height + 8}%`}
                  fill={netQtyFinding.quietZoneCleared ? "url(#safeHatch)" : "url(#hazardHatch)"}
                  stroke={netQtyFinding.quietZoneCleared ? "#10B981" : "#EF4444"}
                  strokeWidth="1.5"
                  strokeDasharray="4 2"
                  rx="4"
                />
              </g>
            )}
          </svg>

          {/* Interactive Bounding Boxes Layer */}
          {showBBoxes && findings.map((finding) => {
            if (!finding.bbox) return null;
            const isSelected = selectedFindingId === finding.id;
            const isHovered = hoveredFindingId === finding.id;
            const isViolation = finding.status === 'Fail';
            const isReview = finding.status === 'Review Required' || finding.status === 'Warning';
            const isPass = finding.status === 'Pass';

            return (
              <div
                key={finding.id}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectFinding(finding.id);
                }}
                onMouseEnter={() => setHoveredFindingId(finding.id)}
                onMouseLeave={() => setHoveredFindingId(null)}
                style={{
                  left: `${finding.bbox.x}%`,
                  top: `${finding.bbox.y}%`,
                  width: `${finding.bbox.width}%`,
                  height: `${finding.bbox.height}%`,
                }}
                className={cn(
                  "absolute z-20 cursor-pointer transition-all rounded-md group flex items-start justify-between p-1",
                  isViolation && "border-2 border-red-500 bg-red-500/15 shadow-lg",
                  isReview && "border-2 border-amber-500 bg-amber-500/15 shadow-lg",
                  isPass && "border-2 border-emerald-500 bg-emerald-500/10 hover:bg-emerald-500/20",
                  (isSelected || isHovered) && "ring-4 ring-white/60 scale-[1.02] z-30"
                )}
              >
                {/* Micro Tag on Box */}
                <div className={cn(
                  "text-[9px] font-mono font-bold px-1.5 py-0.5 rounded shadow-sm whitespace-nowrap -mt-3.5 -ml-1 flex items-center gap-1",
                  isViolation && "bg-red-600 text-white",
                  isReview && "bg-amber-600 text-white",
                  isPass && "bg-emerald-700 text-white"
                )}>
                  <span>{finding.clause.split(' ')[0]}</span>
                  {finding.measuredHeightMm && (
                    <span className="font-mono">({finding.measuredHeightMm.toFixed(1)}mm)</span>
                  )}
                </div>

                {/* Hover Tooltip */}
                {(isHovered || isSelected) && (
                  <div className="absolute left-0 bottom-full mb-2 bg-slate-900 text-white text-xs p-2.5 rounded-md shadow-2xl border border-slate-700 w-64 pointer-events-none z-40 animate-in fade-in zoom-in-95 duration-100">
                    <div className="flex items-center justify-between gap-1 border-b border-slate-700 pb-1 mb-1 font-bold">
                      <span className="truncate">{finding.field}</span>
                      <span className={cn(
                        "text-[10px] font-mono px-1 rounded",
                        isViolation ? "bg-red-900 text-red-200" : "bg-emerald-900 text-emerald-200"
                      )}>
                        {finding.status}
                      </span>
                    </div>
                    <div className="space-y-0.5 text-[11px] font-mono">
                      <div>Extracted: <span className="text-slate-300 font-semibold">{finding.extractedText}</span></div>
                      {finding.measuredHeightMm && (
                        <div>
                          Measured: <span className={cn(isViolation ? "text-red-400 font-bold" : "text-emerald-400 font-bold")}>
                            {finding.measuredHeightMm.toFixed(1)} mm
                          </span> (Req: {finding.requiredHeightMm?.toFixed(1)} mm)
                        </div>
                      )}
                      <div>Confidence: <span className="text-blue-300">{finding.ocrConfidence}%</span></div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          {/* Visual Caliper & Measurement Geometry Card Overlay */}
          {showCalipers && activeFinding && activeFinding.measuredHeightMm && (
            <div className={cn(
              "absolute bottom-3 right-3 p-3 rounded-lg border-2 shadow-2xl backdrop-blur-md font-mono text-xs z-30 flex flex-col gap-1 max-w-xs animate-in slide-in-from-bottom duration-150",
              activeFinding.status === 'Fail'
                ? "bg-slate-950/90 border-red-500 text-white"
                : "bg-slate-950/90 border-emerald-500 text-white"
            )}>
              <div className="flex items-center justify-between border-b border-slate-800 pb-1">
                <div className="flex items-center gap-1.5 font-bold">
                  <Ruler className={cn("w-4 h-4", activeFinding.status === 'Fail' ? "text-red-400" : "text-emerald-400")} />
                  <span>Calibrated Numeral Measurement</span>
                </div>
                <span className={cn(
                  "text-[10px] font-bold px-1.5 py-0.2 rounded uppercase",
                  activeFinding.status === 'Fail' ? "bg-red-600 text-white" : "bg-emerald-600 text-white"
                )}>
                  {activeFinding.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">Measured Numeral</span>
                  <span className={cn(
                    "text-sm font-extrabold",
                    activeFinding.status === 'Fail' ? "text-red-400 font-bold" : "text-emerald-400 font-bold"
                  )}>
                    {activeFinding.measuredHeightMm.toFixed(1)} mm
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">Statutory Minimum</span>
                  <span className="text-sm font-bold text-slate-200">
                    {activeFinding.requiredHeightMm?.toFixed(1)} mm
                  </span>
                </div>
              </div>

              {activeFinding.quietZoneCleared === false && (
                <div className="mt-1 p-1.5 bg-red-950/80 border border-red-500/60 rounded text-[10px] text-red-200 flex items-start gap-1">
                  <ShieldAlert className="w-3.5 h-3.5 text-red-400 shrink-0 mt-0.5" />
                  <span>Quiet-zone collision: Clearance 1.2mm &lt; 8.0mm required buffer.</span>
                </div>
              )}

              <div className="text-[9px] text-slate-400 pt-0.5 border-t border-slate-800 flex justify-between">
                <span>Scale: {calibration.pixelsPerMm.toFixed(1)} px/mm</span>
                <span>Rule 7(2)(i) Table I</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
