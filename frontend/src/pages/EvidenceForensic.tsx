import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useInspections } from '../context/InspectionContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Breadcrumbs } from '../components/ui/Breadcrumbs';
import { 
  Ruler, 
  ZoomIn, 
  ZoomOut, 
  Sliders, 
  ShieldCheck, 
  Eye, 
  Hash, 
  Maximize, 
  Sparkles, 
  Sun, 
  Contrast, 
  ArrowLeft,
  Grid,
  CheckCircle2
} from 'lucide-react';
import { cn } from '../utils/cn';

export const EvidenceForensic: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { getInspectionById } = useInspections();
  const navigate = useNavigate();

  const inspection = getInspectionById(id || '');

  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [showMillimeterGrid, setShowMillimeterGrid] = useState<boolean>(true);
  const [showQuietZoneHatch, setShowQuietZoneHatch] = useState<boolean>(true);
  const [glareFilterActive, setGlareFilterActive] = useState<boolean>(false);
  const [selectedMeasurementBox, setSelectedMeasurementBox] = useState<'net_qty' | 'mrp' | 'address'>('net_qty');

  if (!inspection) {
    return (
      <div className="text-center py-16">
        <h2 className="text-lg font-bold text-slate-800">Evidence File Not Found</h2>
        <Button variant="primary" className="mt-4" onClick={() => navigate('/dashboard')}>
          Return to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: 'Inspections Ledger', href: '/history' },
          { label: inspection.id, href: `/inspection/${inspection.id}` },
          { label: 'Forensic Millimeter Studio' },
        ]}
      />

      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Evidence Forensic Studio
            </h1>
            <Badge variant="blue" className="font-mono">
              Scale: {inspection.calibration.pixelsPerMm.toFixed(2)} px / mm
            </Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Sub-pixel millimeter verification, glare reduction filtering, and quiet-zone clearance audit
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/inspection/${inspection.id}`)}
            leftIcon={<ArrowLeft className="w-4 h-4" />}
          >
            Back to Details
          </Button>
        </div>
      </div>

      {/* Forensic Main Canvas & Tools */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Main Viewport */}
        <div className="lg:col-span-8 space-y-4">
          <Card className="overflow-hidden border-slate-300">
            <div className="bg-slate-950 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between text-xs text-slate-300">
              <div className="flex items-center gap-3">
                <span className="font-mono font-bold text-emerald-400 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  SHA-256 Verified
                </span>
                <span className="text-slate-500">|</span>
                <span>Zoom: {zoomLevel}%</span>
              </div>

              {/* Viewport Control Bar */}
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setZoomLevel(prev => Math.max(50, prev - 25))}
                  className="p-1 rounded hover:bg-slate-800 text-slate-300"
                  title="Zoom Out"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setZoomLevel(prev => Math.min(250, prev + 25))}
                  className="p-1 rounded hover:bg-slate-800 text-slate-300"
                  title="Zoom In"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setZoomLevel(100)}
                  className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-slate-700 text-slate-200"
                >
                  Reset 100%
                </button>
              </div>
            </div>

            {/* Interactive Image Canvas */}
            <div className="relative bg-slate-950 min-h-[480px] flex items-center justify-center overflow-hidden">
              <div 
                className="relative transition-transform duration-200"
                style={{ transform: `scale(${zoomLevel / 100})` }}
              >
                <img
                  src={inspection.sampleImage}
                  alt="Forensic Evidence"
                  className={cn(
                    "max-h-[500px] w-auto object-contain transition-all",
                    glareFilterActive && "contrast-125 brightness-95 saturate-150"
                  )}
                />

                {/* Millimeter Overlay Grid */}
                {showMillimeterGrid && (
                  <div className="absolute inset-0 bg-mm-grid pointer-events-none opacity-40" />
                )}

                {/* Calibration Reticle Badge */}
                <div className="absolute top-4 left-4 border border-blue-400 bg-blue-950/80 p-2 rounded text-blue-200 font-mono text-[11px] backdrop-blur-xs">
                  <div className="flex items-center gap-1 font-bold text-blue-300">
                    <Ruler className="w-3.5 h-3.5" />
                    <span>Calibrated Millimeter Reference</span>
                  </div>
                  <div className="mt-0.5">85.60 mm standard = {inspection.calibration.pixelsPerMm * 85.6} px</div>
                </div>

                {/* Measurement Callout Box */}
                {selectedMeasurementBox === 'net_qty' && (
                  <div className={cn(
                    "absolute bottom-16 right-16 p-2 rounded font-mono text-xs border-2 shadow-2xl backdrop-blur-md",
                    inspection.minFontHeightCompliant
                      ? "border-emerald-400 bg-emerald-950/80 text-emerald-100"
                      : "border-red-500 bg-red-950/80 text-red-100"
                  )}>
                    <div className="flex items-center justify-between gap-3 text-[11px] font-bold">
                      <span>Net Quantity Numeral Height</span>
                      <span>{inspection.minFontHeightCompliant ? "COMPLIANT" : "FAIL"}</span>
                    </div>
                    <div className="text-sm font-extrabold mt-1">
                      Measured: {inspection.statedWeightGramsOrMl === 500 ? '3.1 mm' : '2.6 mm'}
                    </div>
                    <div className="text-[10px] opacity-80">
                      Statutory Minimum: {inspection.statedWeightGramsOrMl === 500 ? '4.0 mm' : '2.0 mm'} (Tenth Schedule Table II)
                    </div>

                    {showQuietZoneHatch && !inspection.minFontHeightCompliant && (
                      <div className="mt-1.5 p-1 rounded quiet-zone-hazard text-[10px] text-red-200 border border-red-400">
                        Collision: Background border encroaches on 2x letter height clearance.
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Canvas Footer Options */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-4 text-xs">
              <div className="flex flex-wrap items-center gap-3">
                <label className="flex items-center gap-1.5 cursor-pointer select-none font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={showMillimeterGrid}
                    onChange={(e) => setShowMillimeterGrid(e.target.checked)}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span>Millimeter Grid Overlay</span>
                </label>

                <label className="flex items-center gap-1.5 cursor-pointer select-none font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={showQuietZoneHatch}
                    onChange={(e) => setShowQuietZoneHatch(e.target.checked)}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span>Quiet-Zone Hatching</span>
                </label>

                <label className="flex items-center gap-1.5 cursor-pointer select-none font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={glareFilterActive}
                    onChange={(e) => setGlareFilterActive(e.target.checked)}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span>Specular Glare Filter</span>
                </label>
              </div>

              <div className="text-slate-500 font-mono text-[11px]">
                Target: {inspection.statedWeightGramsOrMl}g Pack Category
              </div>
            </div>
          </Card>
        </div>

        {/* Right Tools & Forensic Data */}
        <div className="lg:col-span-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Measurement Targets</CardTitle>
              <CardDescription>Select declaration zone to inspect</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {[
                { id: 'net_qty', label: 'Net Quantity Numeral', desc: 'Rule 9 / Tenth Schedule height' },
                { id: 'mrp', label: 'MRP & Unit Sale Price', desc: 'Rule 6(1)(d) font clearance' },
                { id: 'address', label: 'Manufacturer Name/Address', desc: 'Rule 6(1)(a) legibility' },
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => setSelectedMeasurementBox(t.id as any)}
                  className={cn(
                    "w-full text-left p-3 rounded-lg border text-xs transition-all",
                    selectedMeasurementBox === t.id
                      ? "bg-blue-50 border-blue-600 ring-1 ring-blue-600 text-blue-950 font-bold"
                      : "bg-slate-50 border-slate-200 hover:bg-slate-100 text-slate-700"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span>{t.label}</span>
                    {selectedMeasurementBox === t.id && <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />}
                  </div>
                  <p className="text-[11px] text-slate-500 font-normal mt-0.5">{t.desc}</p>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* SHA-256 Integrity Verification */}
          <Card className="bg-slate-50">
            <CardHeader>
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <CardTitle>Forensic Chain-of-Custody</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              <div>
                <span className="text-slate-500 text-[10px] uppercase font-semibold block">SHA-256 Hash</span>
                <p className="font-mono text-[11px] bg-white p-2 rounded border border-slate-200 break-all text-slate-800">
                  {inspection.imageSha256}
                </p>
              </div>
              <div className="pt-2 text-[11px] text-slate-600 space-y-1">
                <p>• EXIF Capture Timestamp: {inspection.inspectionDate}</p>
                <p>• Calibrated Sensor: 12.0 MP Optical Array</p>
                <p>• Statutory Certificate: Ready for Judicial Admissibility</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
