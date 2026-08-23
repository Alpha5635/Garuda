import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { 
  Sparkles, 
  Binary, 
  UserCheck, 
  ArrowRight, 
  ShieldCheck, 
  Scale, 
  FileCheck2,
  BookOpen
} from 'lucide-react';
import { cn } from '../../utils/cn';

export const RuleTraceabilityCard: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <Card className={cn("border-t-4 border-t-blue-700 bg-white", className)}>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Scale className="w-5 h-5 text-blue-700" />
          <div>
            <CardTitle>Three-Tier Statutory Compliance Engine</CardTitle>
            <CardDescription>
              Why LabelSetu is evidence-native and zero-hallucination
            </CardDescription>
          </div>
        </div>
        <Badge variant="blue">Statutory Traceability</Badge>
      </CardHeader>
      <CardContent className="space-y-4 text-xs">
        {/* 3 Pillars */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          
          {/* Pillar 1 */}
          <div className="p-3.5 rounded-lg bg-blue-50/70 border border-blue-200 space-y-1.5">
            <div className="flex items-center gap-2 font-bold text-blue-900">
              <span className="w-5 h-5 rounded-full bg-blue-700 text-white flex items-center justify-center text-[10px]">1</span>
              <span>AI Vision & OCR</span>
            </div>
            <p className="text-[11px] text-blue-950 leading-relaxed">
              Extracts text patches, spatial bounding boxes, and detects reference calibration scale with confidence scoring.
            </p>
            <span className="text-[10px] font-mono text-blue-700 block font-semibold">Probabilistic Extraction</span>
          </div>

          {/* Pillar 2 */}
          <div className="p-3.5 rounded-lg bg-indigo-50/70 border border-indigo-200 space-y-1.5">
            <div className="flex items-center gap-2 font-bold text-indigo-900">
              <span className="w-5 h-5 rounded-full bg-indigo-700 text-white flex items-center justify-center text-[10px]">2</span>
              <span>Deterministic Rule Engine</span>
            </div>
            <p className="text-[11px] text-indigo-950 leading-relaxed">
              Strictly evaluates measured millimeters against versioned PCR tables (Tenth Schedule) with zero LLM hallucination.
            </p>
            <span className="text-[10px] font-mono text-indigo-700 block font-semibold">100% Deterministic Code</span>
          </div>

          {/* Pillar 3 */}
          <div className="p-3.5 rounded-lg bg-emerald-50/70 border border-emerald-200 space-y-1.5">
            <div className="flex items-center gap-2 font-bold text-emerald-900">
              <span className="w-5 h-5 rounded-full bg-emerald-700 text-white flex items-center justify-center text-[10px]">3</span>
              <span>Human Officer Decision</span>
            </div>
            <p className="text-[11px] text-emerald-950 leading-relaxed">
              Legal Metrology Officer reviews high-res evidence crop, overrides if needed, and digitally signs the Section 36 notice.
            </p>
            <span className="text-[10px] font-mono text-emerald-700 block font-semibold">Legal Accountability</span>
          </div>
        </div>

        {/* Evidence Chain Visual Ribbon */}
        <div className="pt-2">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-2">
            The LabelSetu Traceable Evidence Chain
          </span>
          <div className="p-3 bg-slate-900 text-white rounded-lg flex flex-wrap items-center justify-between gap-2 font-mono text-[10px]">
            <span className="bg-slate-800 px-2 py-1 rounded text-slate-300">Packaging Image</span>
            <ArrowRight className="w-3 h-3 text-blue-400 shrink-0" />
            <span className="bg-slate-800 px-2 py-1 rounded text-slate-300">Bounding Box</span>
            <ArrowRight className="w-3 h-3 text-blue-400 shrink-0" />
            <span className="bg-slate-800 px-2 py-1 rounded text-slate-300">Extracted Field</span>
            <ArrowRight className="w-3 h-3 text-blue-400 shrink-0" />
            <span className="bg-blue-900 text-blue-200 px-2 py-1 rounded font-bold">Measured (3.1mm)</span>
            <ArrowRight className="w-3 h-3 text-blue-400 shrink-0" />
            <span className="bg-indigo-900 text-indigo-200 px-2 py-1 rounded">Rule 7(2)(i)</span>
            <ArrowRight className="w-3 h-3 text-blue-400 shrink-0" />
            <span className="bg-red-900 text-red-200 px-2 py-1 rounded font-bold">FAILED</span>
            <ArrowRight className="w-3 h-3 text-blue-400 shrink-0" />
            <span className="bg-emerald-900 text-emerald-200 px-2 py-1 rounded font-bold">Officer Sign-Off</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
