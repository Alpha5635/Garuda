import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { 
  Factory, 
  Upload, 
  CheckCircle2, 
  FileCheck2, 
  Ruler, 
  Download, 
  Sparkles, 
  AlertTriangle, 
  Building, 
  Printer,
  FileWarning,
  HelpCircle,
  Ban,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import { cn } from '../utils/cn';

type PreCheckStatus = 'Verified' | 'Potential issue' | 'Review required' | 'Not evaluable';

export const ManufacturerPortal: React.FC = () => {
  const [skuName, setSkuName] = useState('Tata Tea Gold Care 500g Pouch');
  const [packWeight, setPackWeight] = useState(500);
  const [packagingType, setPackagingType] = useState('Flexible Laminate Pouch');
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditComplete, setAuditComplete] = useState(false);

  const [preCheckResults, setPreCheckResults] = useState<{
    status: PreCheckStatus;
    score: number;
    certificateId: string;
    detectedDeclarations: { field: string; clause: string; status: PreCheckStatus; measured?: string; req?: string; note: string }[];
    recommendations: string[];
  }>({
    status: 'Verified',
    score: 96,
    certificateId: 'LM-PMC-2026-88192',
    detectedDeclarations: [
      { field: 'Net Quantity Font Height', clause: 'Tenth Schedule, Table I', status: 'Verified', measured: '4.4 mm', req: '4.0 mm', note: 'Exceeds 4.0mm requirement for >200g up to 500g category.' },
      { field: 'Quiet-Zone Graphic Clearance', clause: 'Rule 9(3)', status: 'Verified', measured: '6.2 mm', req: '8.0 mm (safe buffer)', note: 'Clear of brand logo and decorative illustrations.' },
      { field: 'Unit Sale Price Declaration', clause: 'Rule 6(1)(s)', status: 'Potential issue', note: 'Ensure font size matches MRP numeral height per 2022 amendment.' },
      { field: 'Consumer Care Redressal', clause: 'Rule 6(1)(e)', status: 'Verified', note: 'Includes email and toll-free telephone number.' },
      { field: 'Manufacturer Postal Address', clause: 'Rule 6(1)(a)', status: 'Verified', note: 'Complete address with PIN code detected.' },
    ],
    recommendations: [
      'Increase Unit Sale Price font weight to bold to prevent optical OCR ambiguity on glossy poly-film.',
      'Maintain 8.0 mm minimum quiet zone clearance on final gravure cylinder engraving.',
      'Ensure MRP text contrast ratio is above 4.5:1 on golden background areas.'
    ]
  });

  const handleRunAudit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsAuditing(true);
    setTimeout(() => {
      setIsAuditing(false);
      setAuditComplete(true);
    }, 600);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Manufacturer Pre-Market Self-Audit Portal
            </h1>
            <Badge variant="green">Pre-Print QA Certification</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Validate packaging artwork against Tenth Schedule millimeter font heights and quiet-zone standards before cylinder engraving and mass printing
          </p>
        </div>

        <Badge variant="blue" className="font-mono">
          ISO/IEC 7810 Direct PDF Vector Ingestion
        </Badge>
      </div>

      {/* 4-Step Pre-check Workflow Ribbon */}
      <div className="p-3 bg-slate-900 text-white rounded-xl flex flex-wrap items-center justify-between gap-2 font-mono text-xs shadow-sm">
        <span className="bg-slate-800 px-3 py-1 rounded text-slate-300">1. Upload Label Master</span>
        <ArrowRight className="w-4 h-4 text-blue-400 shrink-0" />
        <span className="bg-slate-800 px-3 py-1 rounded text-slate-300">2. Vector Optical Analysis</span>
        <ArrowRight className="w-4 h-4 text-blue-400 shrink-0" />
        <span className="bg-blue-900 text-blue-200 px-3 py-1 rounded font-bold">3. Compliance Pre-Check</span>
        <ArrowRight className="w-4 h-4 text-blue-400 shrink-0" />
        <span className="bg-emerald-900 text-emerald-200 px-3 py-1 rounded font-bold">4. Actionable Recommendations</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Upload & Parameters */}
        <Card className="lg:col-span-5">
          <CardHeader>
            <CardTitle>Artwork Vector & Packaging Specs</CardTitle>
            <CardDescription>Upload packaging PDF, AI or high-res TIFF artwork</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleRunAudit} className="space-y-4 text-xs">
              <Input
                label="Product / SKU Title"
                value={skuName}
                onChange={(e) => setSkuName(e.target.value)}
              />

              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Target Net Qty (g/ml)"
                  type="number"
                  value={packWeight}
                  onChange={(e) => setPackWeight(Number(e.target.value))}
                  helperText="Tenth Schedule: 4.0 mm required"
                />
                <Select
                  label="Substrate Format"
                  value={packagingType}
                  onChange={(e) => setPackagingType(e.target.value)}
                  options={[
                    { value: 'Flexible Laminate Pouch', label: 'Flexible Laminate Pouch' },
                    { value: 'Duplex Board Carton', label: 'Duplex Board Carton' },
                    { value: 'PET Bottle Label', label: 'PET Bottle Label' },
                    { value: 'Printed Metal Can', label: 'Printed Metal Can' },
                  ]}
                />
              </div>

              {/* Upload Dropzone */}
              <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors bg-slate-50/50 cursor-pointer">
                <Upload className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <p className="text-xs font-bold text-slate-800">Drag & Drop Packaging Artwork Master</p>
                <p className="text-[11px] text-slate-500 mt-0.5">Supports PDF vector master with exact cut margins</p>
              </div>

              <Button
                type="submit"
                variant="primary"
                isLoading={isAuditing}
                leftIcon={<Sparkles className="w-4 h-4" />}
                className="w-full bg-blue-700 hover:bg-blue-800"
              >
                Run Pre-Market Compliance Check
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Audit Certification Result & Actionable Recommendations */}
        <div className="lg:col-span-7 space-y-4">
          <Card className="border-t-4 border-t-emerald-600 bg-white">
            <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <FileCheck2 className="w-5 h-5 text-emerald-600" />
                  <CardTitle>Pre-Market Compliance Pre-Check Report</CardTitle>
                </div>
                <CardDescription>Verified against Legal Metrology (Packaged Commodities) Rules, 2011</CardDescription>
              </div>

              <span className="font-mono text-xs bg-emerald-100 text-emerald-900 font-bold px-2.5 py-1 rounded">
                Score: {preCheckResults.score}/100
              </span>
            </CardHeader>

            <CardContent className="space-y-4 text-xs">
              {/* Certificate Banner */}
              <div className="bg-emerald-50 p-3.5 rounded-lg border border-emerald-200 text-emerald-950 flex items-center justify-between font-mono text-xs">
                <div>
                  <span className="text-[10px] text-emerald-700 uppercase font-bold block">Pre-Print Certificate ID</span>
                  <strong className="text-sm text-emerald-900">{preCheckResults.certificateId}</strong>
                </div>
                <Badge variant="green">Verified Compliant</Badge>
              </div>

              {/* Detected Declarations & Measurement Check */}
              <div className="space-y-2">
                <h4 className="font-bold text-xs uppercase tracking-wider text-slate-700">
                  Detected Packaging Declarations & Rule Evaluation
                </h4>
                <div className="space-y-2">
                  {preCheckResults.detectedDeclarations.map((d, idx) => (
                    <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-start justify-between gap-2 text-xs">
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-1.5">
                          <span className="font-bold text-slate-900">{d.field}</span>
                          <span className="text-[10px] font-mono text-slate-500 bg-white px-1.5 py-0.2 rounded border border-slate-200">
                            {d.clause}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-600">{d.note}</p>
                        {d.measured && (
                          <p className="text-[11px] font-mono text-emerald-700 font-bold">
                            Measured: {d.measured} (Req: {d.req})
                          </p>
                        )}
                      </div>

                      <Badge variant={d.status === 'Verified' ? 'green' : d.status === 'Potential issue' ? 'amber' : 'slate'}>
                        {d.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actionable Recommendations for Print Shop */}
              <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-lg space-y-1.5 text-blue-950">
                <strong className="font-bold block text-blue-900">Actionable Print Shop Recommendations:</strong>
                <ul className="list-disc pl-4 space-y-1 text-[11px]">
                  {preCheckResults.recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            </CardContent>

            <CardFooter className="flex items-center justify-between bg-slate-50 p-4">
              <Button
                variant="outline"
                size="sm"
                leftIcon={<Download className="w-4 h-4" />}
                onClick={() => alert("Downloading PDF Pre-Print Compliance Certificate...")}
              >
                Download PDF Certificate
              </Button>
              <Button
                variant="primary"
                size="sm"
                leftIcon={<Printer className="w-4 h-4" />}
                onClick={() => window.print()}
                className="bg-blue-700 hover:bg-blue-800"
              >
                Print QA Sign-Off
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  );
};
