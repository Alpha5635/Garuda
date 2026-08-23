import React from 'react';
import { Card, CardContent } from './Card';
import { Badge } from './Badge';
import { cn } from '../../utils/cn';
import { ShieldCheck, Ruler, Hash, ZoomIn, Camera } from 'lucide-react';
import { CalibrationTarget } from '../../types';

export interface EvidenceCardProps {
  imageUrl: string;
  imageSha256: string;
  calibration?: CalibrationTarget;
  pdpAreaCm2?: number;
  productName: string;
  brand: string;
  onInspectFullscreen?: () => void;
  className?: string;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({
  imageUrl,
  imageSha256,
  calibration,
  pdpAreaCm2,
  productName,
  brand,
  onInspectFullscreen,
  className,
}) => {
  return (
    <Card className={cn("overflow-hidden border-slate-200", className)}>
      <div className="relative bg-slate-900 aspect-4/3 flex items-center justify-center overflow-hidden group">
        <img
          src={imageUrl}
          alt={productName}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />

        {/* Reticle / Measurement Grid Overlay */}
        <div className="absolute inset-0 bg-mm-grid pointer-events-none opacity-40" />

        {/* Status Overlays */}
        <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
          <Badge variant="slate" className="bg-slate-900/80 text-white backdrop-blur-xs border-slate-700">
            <Camera className="w-3 h-3 text-blue-400" />
            <span>Forensic Evidence</span>
          </Badge>
          {calibration && (
            <Badge variant="blue" className="bg-blue-950/80 text-blue-200 backdrop-blur-xs border-blue-800">
              <Ruler className="w-3 h-3 text-blue-400" />
              <span>{calibration.pixelsPerMm.toFixed(1)} px/mm ({calibration.confidence.toFixed(0)}% cal)</span>
            </Badge>
          )}
        </div>

        {onInspectFullscreen && (
          <button
            onClick={onInspectFullscreen}
            className="absolute bottom-3 right-3 bg-slate-900/90 text-white text-xs px-3 py-1.5 rounded-md backdrop-blur-xs hover:bg-blue-600 transition-colors flex items-center gap-1.5 shadow-md"
          >
            <ZoomIn className="w-3.5 h-3.5" />
            <span>Inspect Calibrated Millimeters</span>
          </button>
        )}
      </div>

      <CardContent className="p-4 bg-slate-50 border-t border-slate-200 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h4 className="text-sm font-bold text-slate-900 leading-tight">{productName}</h4>
            <p className="text-xs text-slate-500 font-medium">{brand}</p>
          </div>
          {pdpAreaCm2 && (
            <div className="text-right">
              <span className="text-[10px] uppercase font-semibold text-slate-500 block">PDP Area</span>
              <span className="text-xs font-mono font-bold text-slate-800">{pdpAreaCm2} cm²</span>
            </div>
          )}
        </div>

        {/* SHA-256 Cryptographic Audit Proof */}
        <div className="bg-white p-2.5 rounded border border-slate-200 text-slate-600 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">SHA-256 Chain-of-Custody</span>
              <span className="text-[10px] text-emerald-600 font-semibold font-mono">Immutable Stamp</span>
            </div>
            <p className="text-[10px] font-mono text-slate-600 truncate mt-0.5" title={imageSha256}>
              <Hash className="w-2.5 h-2.5 inline mr-0.5 text-slate-400" />
              {imageSha256}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
