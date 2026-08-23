import React, { useState } from 'react';
import { mockEcommerceScans } from '../data/mockData';
import { EcommerceScanItem } from '../types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Badge } from '../components/ui/Badge';
import { 
  ShoppingBag, 
  Search, 
  ExternalLink, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Globe, 
  ShieldAlert, 
  FileText,
  Sparkles,
  RefreshCw,
  Building2,
  Clock,
  Layers,
  ArrowRight,
  ShieldCheck,
  Check
} from 'lucide-react';
import { cn } from '../utils/cn';

export const EcommerceInspector: React.FC = () => {
  const [scans, setScans] = useState<EcommerceScanItem[]>(mockEcommerceScans);
  const [urlInput, setUrlInput] = useState('https://amazon.in/dp/B0B4PR287X');
  const [isScanning, setIsScanning] = useState(false);
  const [crawlStage, setCrawlStage] = useState<number>(0);
  const [selectedScan, setSelectedScan] = useState<EcommerceScanItem>(mockEcommerceScans[0]);

  const crawlerSteps = [
    'Connecting to Digital Marketplace Endpoint...',
    'Extracting Structured JSON-LD & DOM Attributes...',
    'Optical OCR Analysis on Product Image Carousel...',
    'Evaluating Mandatory Disclosures under Rule 6(10)...',
  ];

  const handleRunUrlScan = (e: React.FormEvent) => {
    e.preventDefault();
    setIsScanning(true);
    setCrawlStage(0);

    let stage = 0;
    const interval = setInterval(() => {
      stage += 1;
      setCrawlStage(stage);
      if (stage >= crawlerSteps.length) {
        clearInterval(interval);
        setIsScanning(false);
        setSelectedScan(mockEcommerceScans[0]);
      }
    }, 400);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              E-Commerce Rule 6(10) Marketplace Inspector
            </h1>
            <Badge variant="blue">Automated Digital PDP Surveillance</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            End-to-end digital compliance crawler for Amazon, Flipkart, Blinkit & Zepto under Legal Metrology (Packaged Commodities) Amendment Rules
          </p>
        </div>

        <Badge variant="green" className="font-mono">
          <Clock className="w-3.5 h-3.5 inline mr-1" />
          Rule 6(10) Engine Active
        </Badge>
      </div>

      {/* URL Scanner Simulator Input */}
      <Card className="border-2 border-blue-100 bg-gradient-to-r from-blue-50/50 via-white to-indigo-50/50 shadow-sm">
        <CardContent className="p-5 space-y-3">
          <form onSubmit={handleRunUrlScan} className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block">
                Paste E-Commerce Listing URL (Amazon / Flipkart / Blinkit / Zepto)
              </label>
              <span className="text-[11px] text-blue-700 font-mono font-semibold">
                Rule 6(10) Audit Protocol
              </span>
            </div>

            <div className="flex flex-col sm:flex-row gap-2">
              <div className="relative flex-1">
                <Globe className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="url"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://amazon.in/dp/... or https://blinkit.com/..."
                  className="w-full h-10 pl-9 pr-3 rounded-lg border border-slate-300 text-xs text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600 font-mono bg-white"
                />
              </div>
              <Button
                type="submit"
                variant="primary"
                isLoading={isScanning}
                leftIcon={<Search className="w-4 h-4" />}
                className="bg-blue-700 hover:bg-blue-800"
              >
                Analyze Listing Declarations
              </Button>
            </div>

            {/* Live Crawler Stages Animation */}
            {isScanning && (
              <div className="p-3 bg-blue-900 text-white rounded-lg text-xs font-mono flex items-center gap-2 animate-in fade-in">
                <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />
                <span>{crawlerSteps[crawlStage] || crawlerSteps[0]}</span>
              </div>
            )}

            {/* Statutory Online Exemption Note */}
            <div className="p-2.5 bg-blue-50/80 border border-blue-200 rounded text-[11px] text-blue-950 flex items-start gap-2">
              <Sparkles className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <strong>Statutory Exemption Rule 6(10) Proviso 2 (2022 Amendment):</strong>
                <span>
                  {' '}Month and Year of packing is <strong>NOT APPLICABLE ONLINE</strong> provided that expiry date, best before, or manufacturer warranty period is declared on the digital display page.
                </span>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Main Inspection Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Scanned Listings Feed */}
        <div className="lg:col-span-5 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 px-1">
            Marketplace Surveillance Ledger
          </h3>

          {scans.map((scan) => {
            const isSelected = selectedScan.id === scan.id;
            return (
              <div
                key={scan.id}
                onClick={() => setSelectedScan(scan)}
                className={cn(
                  "p-4 rounded-xl border transition-all cursor-pointer bg-white space-y-3",
                  isSelected
                    ? "border-blue-600 ring-2 ring-blue-500 shadow-elevated"
                    : "border-slate-200 hover:border-slate-300 hover:bg-slate-50/60"
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2.5">
                    <img
                      src={scan.thumbnailUrl}
                      alt={scan.productTitle}
                      className="w-12 h-12 rounded-lg object-cover border border-slate-200 shrink-0"
                    />
                    <div className="min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-bold font-mono bg-slate-100 px-1.5 py-0.2 rounded text-slate-700">
                          {scan.marketplace}
                        </span>
                        <span className="text-xs font-bold text-slate-900">{scan.brand}</span>
                      </div>
                      <h4 className="text-xs font-semibold text-slate-800 truncate max-w-[220px] mt-0.5" title={scan.productTitle}>
                        {scan.productTitle}
                      </h4>
                    </div>
                  </div>
                  <StatusBadge status={scan.overallStatus} size="sm" />
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-100 pt-2 font-mono">
                  <span>Seller: {scan.sellerName}</span>
                  <span className={cn(scan.violationCount > 0 ? "text-red-600 font-bold" : "text-emerald-700 font-semibold")}>
                    {scan.violationCount > 0 ? `${scan.violationCount} Violations` : '100% Compliant'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Deep Dive Rule 6(10) Disclosure Audit Details */}
        <div className="lg:col-span-7 space-y-6">
          <Card className="border-t-4 border-t-blue-700">
            <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <CardTitle>Rule 6(10) Mandatory Declarations Audit</CardTitle>
                  <StatusBadge status={selectedScan.overallStatus} size="sm" />
                </div>
                <CardDescription>
                  Digital PDP verification under Legal Metrology Act, 2009
                </CardDescription>
              </div>

              <a
                href={selectedScan.pdpUrl}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-semibold text-blue-700 hover:underline flex items-center gap-1"
              >
                <span>Open PDP Listing</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </CardHeader>

            <CardContent className="space-y-4">
              {/* Product Header Card */}
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Product Title:</span>
                  <span className="font-bold text-slate-900 text-right max-w-md">{selectedScan.productTitle}</span>
                </div>
                <div className="flex justify-between font-mono">
                  <span className="text-slate-500">Declared Net Quantity:</span>
                  <span className="font-bold text-slate-900">{selectedScan.declaredNetQuantity}</span>
                </div>
                <div className="flex justify-between font-mono">
                  <span className="text-slate-500">Listed Price / Stated MRP:</span>
                  <span className="font-bold text-slate-900">₹ {selectedScan.listedPrice} (MRP ₹ {selectedScan.mrp})</span>
                </div>
              </div>

              {/* 8 Mandatory Digital Declarations Checklist */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Statutory Rule 6(10) Digital Declarations Matrix
                </h4>

                {[
                  {
                    field: '1. Country of Origin on Digital Platform',
                    clause: 'Rule 6(10) read with Rule 6(1)(n)',
                    passed: selectedScan.countryOfOriginPresent,
                    notes: selectedScan.countryOfOriginPresent ? 'Declared in specifications table' : 'CRITICAL DEFECT: Country of Origin missing in listing attributes',
                  },
                  {
                    field: '2. Manufacturer / Importer Complete Address',
                    clause: 'Rule 6(10) read with Rule 6(1)(a)',
                    passed: selectedScan.manufacturerAddressPresent,
                    notes: selectedScan.manufacturerAddressPresent ? 'Complete address provided' : 'DEFECT: Missing / unreadable on product carousel',
                  },
                  {
                    field: '3. Unit Sale Price (USP)',
                    clause: 'Rule 6(10) read with Rule 6(1)(s)',
                    passed: selectedScan.unitSalePricePresent,
                    notes: selectedScan.unitSalePricePresent ? 'Declared per piece / gram format' : 'Omitted on digital price widget',
                  },
                  {
                    field: '4. Consumer Grievance / Redressal Email & Tel',
                    clause: 'Rule 6(10) read with Rule 6(1)(e)',
                    passed: selectedScan.consumerCareEmailPhonePresent,
                    notes: selectedScan.consumerCareEmailPhonePresent ? 'Customer support details listed' : 'Consumer care details missing',
                  },
                  {
                    field: '5. Expiry Date / Best Before / Warranty',
                    clause: 'Rule 6(10) read with Rule 6(1)(c)',
                    passed: selectedScan.expiryOrBestBeforePresent,
                    notes: 'Present in product specifications table',
                  },
                  {
                    field: '6. Month & Year of Packing Exemption',
                    clause: 'Rule 6(10) 2022 Amendment Proviso',
                    passed: true,
                    isExempt: true,
                    notes: 'NOT APPLICABLE ONLINE: Statutorily exempt on digital marketplaces provided expiry or warranty is declared.',
                  }
                ].map((item, idx) => (
                  <div
                    key={idx}
                    className={cn(
                      "p-3 rounded-lg border flex items-start justify-between gap-3 text-xs",
                      item.isExempt
                        ? "bg-slate-50 border-slate-200"
                        : item.passed
                        ? "bg-emerald-50/60 border-emerald-200"
                        : "bg-red-50/70 border-red-300"
                    )}
                  >
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900">{item.field}</span>
                        <span className="text-[10px] font-mono text-slate-500 bg-white px-1.5 py-0.2 rounded border border-slate-200">
                          {item.clause}
                        </span>
                      </div>
                      <p className={cn("text-[11px]", item.isExempt ? "text-slate-600" : item.passed ? "text-emerald-900 font-medium" : "text-red-800 font-bold")}>
                        {item.notes}
                      </p>
                    </div>

                    <div className="shrink-0">
                      {item.isExempt ? (
                        <Badge variant="blue" className="bg-blue-100 text-blue-900 border-blue-200">
                          Not Applicable Online
                        </Badge>
                      ) : item.passed ? (
                        <Badge variant="green">Verified Pass</Badge>
                      ) : (
                        <Badge variant="red">Violation</Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Notice generation if violation */}
              {selectedScan.overallStatus === 'Violation' && (
                <div className="p-4 bg-red-100/70 border border-red-300 rounded-lg flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs text-red-950">
                  <div className="flex items-center gap-2 font-bold">
                    <ShieldAlert className="w-5 h-5 text-red-600 shrink-0" />
                    <span>E-Commerce Notice Warranted under Section 36 of Legal Metrology Act</span>
                  </div>
                  <Button variant="danger" size="sm" onClick={() => alert("E-Commerce Form LM-N1 Notice dispatched to marketplace legal cell!")}>
                    Issue Notice
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
