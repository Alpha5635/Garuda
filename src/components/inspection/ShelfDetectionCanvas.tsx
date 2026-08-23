import React, { useState } from 'react';
import { DetectedProduct } from '../../types';
import { cn } from '../../utils/cn';
import { 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Sliders, 
  Layers, 
  Maximize2, 
  Minimize2, 
  CheckCircle2, 
  AlertTriangle, 
  AlertOctagon, 
  Camera, 
  HelpCircle,
  Eye
} from 'lucide-react';

interface ShelfDetectionCanvasProps {
  imageUrl: string;
  products: DetectedProduct[];
  selectedProductId: string | null;
  hoveredProductId: string | null;
  onSelectProduct: (productId: string) => void;
  onHoverProduct: (productId: string | null) => void;
  onOpenProductDetail?: (inspectionId: string) => void;
}

export const ShelfDetectionCanvas: React.FC<ShelfDetectionCanvasProps> = ({
  imageUrl,
  products,
  selectedProductId,
  hoveredProductId,
  onSelectProduct,
  onHoverProduct,
  onOpenProductDetail,
}) => {
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [showBoxes, setShowBoxes] = useState<boolean>(true);
  const [showConfidence, setShowConfidence] = useState<boolean>(true);
  const [contrastEnhance, setContrastEnhance] = useState<boolean>(false);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 25, 200));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 25, 75));
  const handleResetZoom = () => setZoomLevel(100);

  const getStatusTheme = (status: string, priority?: string) => {
    if (priority === 'High Priority' || status === 'Violation') {
      return {
        border: 'border-red-500',
        bg: 'bg-red-500/20',
        activeBorder: 'border-red-400 ring-2 ring-red-400 shadow-red-500/50',
        badge: 'bg-red-600 text-white',
        text: 'text-red-300',
        dot: 'bg-red-500',
      };
    }
    if (status === 'Review Required') {
      return {
        border: 'border-amber-400',
        bg: 'bg-amber-400/20',
        activeBorder: 'border-amber-300 ring-2 ring-amber-300 shadow-amber-400/50',
        badge: 'bg-amber-500 text-slate-900 font-bold',
        text: 'text-amber-300',
        dot: 'bg-amber-400',
      };
    }
    if (status === 'Needs Recapture') {
      return {
        border: 'border-orange-500',
        bg: 'bg-orange-500/20',
        activeBorder: 'border-orange-400 ring-2 ring-orange-400 shadow-orange-500/50',
        badge: 'bg-orange-600 text-white',
        text: 'text-orange-300',
        dot: 'bg-orange-500',
      };
    }
    if (status === 'Verified' || status === 'Complete') {
      return {
        border: 'border-emerald-500',
        bg: 'bg-emerald-500/15',
        activeBorder: 'border-emerald-400 ring-2 ring-emerald-400 shadow-emerald-500/50',
        badge: 'bg-emerald-600 text-white',
        text: 'text-emerald-300',
        dot: 'bg-emerald-500',
      };
    }
    return {
      border: 'border-blue-500',
      bg: 'bg-blue-500/15',
      activeBorder: 'border-blue-400 ring-2 ring-blue-400 shadow-blue-500/50',
      badge: 'bg-blue-600 text-white',
      text: 'text-blue-300',
      dot: 'bg-blue-500',
    };
  };

  return (
    <div className={cn(
      "bg-slate-950 rounded-xl border border-slate-800 flex flex-col overflow-hidden shadow-card transition-all",
      isFullscreen && "fixed inset-4 z-50 rounded-2xl shadow-2xl"
    )}>
      {/* Top Toolbar */}
      <div className="bg-slate-900/90 backdrop-blur-md px-4 py-2.5 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-300">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-white flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Original Shelf Visual Evidence
          </span>
          <span className="bg-slate-800 text-slate-400 font-mono text-[11px] px-2 py-0.5 rounded border border-slate-700">
            {products.length} Products Detected
          </span>
        </div>

        {/* Toolbar Controls */}
        <div className="flex items-center gap-1.5">
          {/* Zoom Controls */}
          <div className="flex items-center bg-slate-800/80 rounded-lg p-0.5 border border-slate-700/60">
            <button
              type="button"
              onClick={handleZoomOut}
              disabled={zoomLevel <= 75}
              className="p-1.5 text-slate-400 hover:text-white disabled:opacity-40 rounded hover:bg-slate-700 transition"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="px-2 font-mono text-[11px] text-slate-300 min-w-[42px] text-center font-bold">
              {zoomLevel}%
            </span>
            <button
              type="button"
              onClick={handleZoomIn}
              disabled={zoomLevel >= 200}
              className="p-1.5 text-slate-400 hover:text-white disabled:opacity-40 rounded hover:bg-slate-700 transition"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={handleResetZoom}
              className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-700 transition border-l border-slate-700/80"
              title="Reset View"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Toggle Bounding Boxes */}
          <button
            type="button"
            onClick={() => setShowBoxes(!showBoxes)}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs transition font-medium",
              showBoxes 
                ? "bg-blue-600/30 text-blue-300 border-blue-500/50" 
                : "bg-slate-800 text-slate-400 border-slate-700 hover:text-white"
            )}
            title="Toggle Bounding Boxes"
          >
            <Layers className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Boxes</span>
          </button>

          {/* Toggle Confidence */}
          <button
            type="button"
            onClick={() => setShowConfidence(!showConfidence)}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs transition font-medium",
              showConfidence 
                ? "bg-indigo-600/30 text-indigo-300 border-indigo-500/50" 
                : "bg-slate-800 text-slate-400 border-slate-700 hover:text-white"
            )}
            title="Toggle Confidence Tag"
          >
            <Eye className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Confidence</span>
          </button>

          {/* Glare/Contrast Filter */}
          <button
            type="button"
            onClick={() => setContrastEnhance(!contrastEnhance)}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs transition font-medium",
              contrastEnhance 
                ? "bg-amber-600/30 text-amber-300 border-amber-500/50" 
                : "bg-slate-800 text-slate-400 border-slate-700 hover:text-white"
            )}
            title="High Contrast Glare Filter"
          >
            <Sliders className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Contrast</span>
          </button>

          {/* Fullscreen toggle */}
          <button
            type="button"
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 bg-slate-800 text-slate-400 hover:text-white rounded-lg border border-slate-700 hover:bg-slate-700 transition"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen View"}
          >
            {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Main Interactive Canvas Area */}
      <div className="relative w-full flex-1 min-h-[420px] max-h-[640px] flex items-center justify-center p-3 sm:p-6 overflow-auto select-none bg-radial-gradient">
        <div 
          className="relative transition-transform duration-200 ease-out inline-block max-w-full"
          style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'center center' }}
        >
          {/* Base Shelf Image */}
          <img
            src={imageUrl}
            alt="Batch Shelf Visual Evidence"
            className={cn(
              "block max-h-[540px] w-auto rounded-lg shadow-2xl border border-slate-800/80 transition-all object-contain",
              contrastEnhance && "contrast-150 brightness-95 saturate-150"
            )}
          />

          {/* Calibrated Millimeter Grid Background */}
          <div className="absolute inset-0 bg-mm-grid pointer-events-none opacity-25 rounded-lg" />

          {/* Interactive Bounding Boxes Overlay */}
          {showBoxes && products.map((prod) => {
            const isSelected = selectedProductId === prod.id;
            const isHovered = hoveredProductId === prod.id;
            const theme = getStatusTheme(prod.reviewStatus, prod.priority);

            return (
              <div
                key={prod.id}
                style={{
                  left: `${prod.bbox.x}%`,
                  top: `${prod.bbox.y}%`,
                  width: `${prod.bbox.width}%`,
                  height: `${prod.bbox.height}%`,
                }}
                onMouseEnter={() => onHoverProduct(prod.id)}
                onMouseLeave={() => onHoverProduct(null)}
                onClick={() => {
                  onSelectProduct(prod.id);
                  if (onOpenProductDetail) {
                    onOpenProductDetail(prod.inspectionId);
                  }
                }}
                className={cn(
                  "absolute border-2 rounded transition-all duration-150 cursor-pointer group z-20 flex flex-col justify-between p-1",
                  theme.border,
                  theme.bg,
                  (isSelected || isHovered) && cn("z-30 shadow-lg scale-[1.02]", theme.activeBorder),
                  !isSelected && !isHovered && "opacity-90 hover:opacity-100"
                )}
              >
                {/* Header Tag: Product Number & Confidence */}
                <div className="flex items-center justify-between gap-1 overflow-hidden pointer-events-none">
                  <div className={cn(
                    "px-1.5 py-0.5 rounded text-[10px] font-bold font-mono tracking-tight whitespace-nowrap shadow-xs",
                    theme.badge
                  )}>
                    {prod.productNumber}
                  </div>

                  {showConfidence && (
                    <div className="bg-slate-950/85 backdrop-blur-xs text-white font-mono text-[9px] px-1.5 py-0.5 rounded border border-white/20 whitespace-nowrap">
                      {prod.detectionConfidence.toFixed(1)}%
                    </div>
                  )}
                </div>

                {/* Bottom Tag: Brand / Status Mini Pill */}
                <div className="flex items-center justify-between gap-1 mt-auto pointer-events-none">
                  <span className="bg-slate-900/90 backdrop-blur-xs text-[9px] font-bold text-white px-1.5 py-0.5 rounded truncate max-w-[85%] border border-slate-700">
                    {prod.brand}
                  </span>

                  <span className={cn("w-2 h-2 rounded-full shrink-0 shadow-xs", theme.dot)} />
                </div>

                {/* Hover Quick Insight Overlay Tooltip */}
                {isHovered && (
                  <div className="absolute -bottom-14 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[11px] py-1 px-2.5 rounded-lg border border-slate-700 shadow-xl whitespace-nowrap z-40 pointer-events-none flex items-center gap-1.5 animate-in fade-in zoom-in-95">
                    <span className={cn("w-2 h-2 rounded-full", theme.dot)} />
                    <span className="font-bold">{prod.productName}</span>
                    <span className="text-slate-400 font-mono text-[10px]">({prod.reviewStatus})</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Canvas Footer Status Legend */}
      <div className="bg-slate-900/80 px-4 py-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-4 text-[11px] text-slate-400 font-medium">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 border border-emerald-300" />
            Verified Complete
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-amber-400 border border-amber-200" />
            Review Required
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-red-500 border border-red-300" />
            High Priority / Violation
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-orange-500 border border-orange-300" />
            Needs Recapture
          </span>
        </div>

        <div className="text-[11px] text-slate-400 font-mono">
          Click any bounding box to open individual product inspection docket
        </div>
      </div>
    </div>
  );
};
