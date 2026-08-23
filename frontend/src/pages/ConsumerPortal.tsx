import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { 
  Users, 
  Search, 
  Camera, 
  AlertTriangle, 
  CheckCircle2, 
  FileWarning, 
  Send, 
  PhoneCall, 
  ShieldCheck, 
  Building,
  Smartphone,
  ArrowRight,
  Sparkles,
  QrCode
} from 'lucide-react';
import { cn } from '../utils/cn';

export const ConsumerPortal: React.FC = () => {
  const [barcodeInput, setBarcodeInput] = useState('8901030889124');
  const [activeStep, setActiveStep] = useState<number>(0);
  const [isScanning, setIsScanning] = useState(false);

  const [scannedProduct, setScannedProduct] = useState<any>({
    product: 'Amul Pure Ghee 1 L Pouch',
    brand: 'Amul',
    declaredMrp: 610.00,
    chargedPrice: 650.00,
    unitSalePrice: '₹ 0.61 / ml',
    netQuantity: '1000 ml (1 L)',
    manufacturer: 'GCMMF Ltd., Anand 388001, Gujarat',
    customerCare: '1800-258-3333 | care@amul.coop',
    isOvercharged: true,
    suspiciousItem: 'Overcharging (+ ₹ 40 above printed MRP)',
  });

  const [grievanceText, setGrievanceText] = useState('Retailer at Indiranagar market charged ₹ 650 for ₹ 610 printed MRP pouch.');
  const [storeAddress, setStoreAddress] = useState('Sri Krishna Supermarket, 100ft Road, Indiranagar, Bengaluru');
  const [grievanceDocketId, setGrievanceDocketId] = useState<string | null>(null);

  const handleRunScan = (e: React.FormEvent) => {
    e.preventDefault();
    setIsScanning(true);
    setTimeout(() => {
      setIsScanning(false);
      setActiveStep(1); // Detected Info
    }, 450);
  };

  const handleSubmitLead = (e: React.FormEvent) => {
    e.preventDefault();
    const docket = `LM-NCH-2026-${Math.floor(10000 + Math.random() * 90000)}`;
    setGrievanceDocketId(docket);
    setActiveStep(3); // Confirmed Lead
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Citizen Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Citizen Package Verification & Consumer Grievance
            </h1>
            <Badge variant="blue">National Consumer Helpline</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Empowering consumers to verify printed MRP & Unit Sale Price, detect overcharging, and report deceptive packaging leads
          </p>
        </div>

        <div className="flex items-center gap-1.5 font-mono text-xs text-blue-700 bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-200 shrink-0">
          <PhoneCall className="w-4 h-4 text-blue-600" />
          <span>Toll-Free: 1915</span>
        </div>
      </div>

      {/* 5-Step Visual Flow for Citizen */}
      <div className="p-3 bg-slate-900 text-white rounded-xl flex flex-wrap items-center justify-between gap-2 font-mono text-[11px] shadow-sm">
        <span className={cn("px-2 py-0.5 rounded", activeStep === 0 ? "bg-blue-600 text-white font-bold" : "text-slate-300")}>1. Scan Package</span>
        <ArrowRight className="w-3.5 h-3.5 text-blue-400 shrink-0" />
        <span className={cn("px-2 py-0.5 rounded", activeStep === 1 ? "bg-blue-600 text-white font-bold" : "text-slate-300")}>2. Detected Info</span>
        <ArrowRight className="w-3.5 h-3.5 text-blue-400 shrink-0" />
        <span className={cn("px-2 py-0.5 rounded", activeStep === 2 ? "bg-blue-600 text-white font-bold" : "text-slate-300")}>3. Check & Report</span>
        <ArrowRight className="w-3.5 h-3.5 text-blue-400 shrink-0" />
        <span className={cn("px-2 py-0.5 rounded", activeStep === 3 ? "bg-emerald-600 text-white font-bold" : "text-slate-300")}>4. Submit Lead</span>
      </div>

      {/* STEP 1: Scan / Enter Barcode */}
      {activeStep === 0 && (
        <Card className="border-t-4 border-t-blue-700">
          <CardHeader>
            <div className="flex items-center gap-2">
              <QrCode className="w-5 h-5 text-blue-600" />
              <div>
                <CardTitle>Scan Barcode or Upload Label Photo</CardTitle>
                <CardDescription>Enter product EAN/barcode digits or snap package label</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleRunScan} className="space-y-3 text-xs">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Product Barcode / EAN-13
                </label>
                <div className="relative">
                  <Camera className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={barcodeInput}
                    onChange={(e) => setBarcodeInput(e.target.value)}
                    placeholder="e.g. 8901030889124"
                    className="w-full h-10 pl-9 pr-3 rounded-lg border border-slate-300 text-xs font-mono text-slate-900 focus:border-blue-600 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setBarcodeInput('8901030889124');
                    setActiveStep(1);
                  }}
                  className="text-xs text-slate-700"
                >
                  Demo: Amul Ghee 1L
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  isLoading={isScanning}
                  leftIcon={<Search className="w-4 h-4" />}
                  className="bg-blue-700 hover:bg-blue-800 text-xs"
                >
                  Scan Package Details
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* STEP 2: Detected Information & Price Verification */}
      {activeStep >= 1 && (
        <Card className={cn(
          "border-l-4",
          scannedProduct.isOvercharged ? "border-l-red-600" : "border-l-emerald-600"
        )}>
          <CardHeader>
            <div className="flex items-start justify-between w-full">
              <div>
                <CardTitle>{scannedProduct.product}</CardTitle>
                <CardDescription>{scannedProduct.brand} • {scannedProduct.manufacturer}</CardDescription>
              </div>
              <Badge variant={scannedProduct.isOvercharged ? 'red' : 'green'}>
                {scannedProduct.isOvercharged ? 'Overcharging Detected' : 'Verified MRP'}
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="space-y-4 text-xs">
            {/* Price Comparison Block */}
            <div className="grid grid-cols-3 gap-3 bg-slate-50 p-4 rounded-lg border border-slate-200 font-mono text-center">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-500 block">Printed Statutory MRP</span>
                <span className="text-lg font-extrabold text-slate-900">₹ {scannedProduct.declaredMrp.toFixed(2)}</span>
                <span className="text-[10px] text-slate-400 block font-sans">Incl. all taxes</span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-500 block">Unit Sale Price</span>
                <span className="text-lg font-extrabold text-blue-700">{scannedProduct.unitSalePrice}</span>
                <span className="text-[10px] text-slate-400 block font-sans">Rule 6(1)(s)</span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-500 block">Retail Price Charged</span>
                <span className="text-lg font-extrabold text-red-600">₹ {scannedProduct.chargedPrice.toFixed(2)}</span>
                <span className="text-[10px] text-red-700 font-bold block font-sans">+ ₹ 40 Overcharge</span>
              </div>
            </div>

            {/* Overcharging Legal Rights Alert */}
            {scannedProduct.isOvercharged && (
              <div className="p-3.5 bg-red-50 border border-red-200 rounded-lg space-y-1.5 text-red-950">
                <div className="flex items-center gap-1.5 font-bold text-red-800 text-xs">
                  <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
                  <span>Violation of Rule 18(2) of Legal Metrology (Packaged Commodities) Rules, 2011</span>
                </div>
                <p className="text-[11px] text-red-900 leading-relaxed">
                  No dealer or retailer may sell any packaged commodity at a price higher than the Maximum Retail Price printed on the package. You are legally entitled to report this store to Legal Metrology Enforcement.
                </p>
              </div>
            )}
          </CardContent>

          {activeStep === 1 && (
            <CardFooter className="flex justify-between bg-slate-50 p-3.5">
              <Button variant="outline" size="sm" onClick={() => setActiveStep(0)}>
                Scan Another Item
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => setActiveStep(2)}
                leftIcon={<FileWarning className="w-4 h-4" />}
              >
                Proceed to Report Overcharging Lead
              </Button>
            </CardFooter>
          )}
        </Card>
      )}

      {/* STEP 3: Report Grievance Lead to Department */}
      {activeStep === 2 && (
        <Card className="border-t-4 border-t-red-600">
          <CardHeader>
            <div className="flex items-center gap-2">
              <FileWarning className="w-5 h-5 text-red-600" />
              <div>
                <CardTitle>Submit Citizen Enforcement Lead</CardTitle>
                <CardDescription>Direct dispatch to Local Legal Metrology Inspector & National Consumer Helpline</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmitLead} className="space-y-3 text-xs">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Retailer Name & Store Address
                </label>
                <Input
                  value={storeAddress}
                  onChange={(e) => setStoreAddress(e.target.value)}
                />
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Complaint Description
                </label>
                <textarea
                  rows={3}
                  value={grievanceText}
                  onChange={(e) => setGrievanceText(e.target.value)}
                  className="w-full text-xs p-3 rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none font-sans"
                />
              </div>

              <div className="p-2.5 bg-blue-50 border border-blue-200 rounded text-[11px] text-blue-900 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0" />
                <span>Your identity is protected under the Consumer Protection Whistleblower Guidelines.</span>
              </div>

              <div className="flex justify-between pt-2">
                <Button type="button" variant="outline" size="sm" onClick={() => setActiveStep(1)}>
                  Back
                </Button>
                <Button type="submit" variant="danger" size="sm" leftIcon={<Send className="w-4 h-4" />}>
                  Submit Lead to Legal Metrology Inspector
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* STEP 4: Success Docket Registered */}
      {activeStep === 3 && (
        <Card className="border-t-4 border-t-emerald-600 bg-white">
          <CardContent className="p-8 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Enforcement Lead Registered Successfully</h3>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg max-w-sm mx-auto font-mono text-xs">
              <span className="text-slate-500 text-[10px] uppercase block">NCH / Metrology Docket ID</span>
              <strong className="text-blue-700 text-sm">{grievanceDocketId}</strong>
            </div>
            <p className="text-xs text-slate-600 max-w-md mx-auto leading-relaxed">
              Assigned to <strong>Insp. Rajeshwar Rao (Legal Metrology, Zone 4)</strong> for immediate field verification and Section 15 seizure inspection.
            </p>
            <Button variant="primary" size="sm" onClick={() => setActiveStep(0)}>
              Verify Another Product
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
