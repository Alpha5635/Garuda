import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInspections } from '../context/InspectionContext';
import { useAuth } from '../context/AuthContext';
import { 
  Inspection, 
  InspectionStatus, 
  PackagingType, 
  CalibrationMethod,
  InspectionSourceType,
  InspectionCategoryType,
  DeclarationFinding 
} from '../types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Badge } from '../components/ui/Badge';
import { StatusBadge } from '../components/ui/StatusBadge';
import { ProgressIndicator } from '../components/ui/ProgressIndicator';
import { FindingCard } from '../components/ui/FindingCard';
import { 
  Camera, 
  Upload, 
  Ruler, 
  CheckCircle2, 
  Sparkles, 
  ShieldCheck, 
  AlertTriangle, 
  Languages, 
  FileText,
  HelpCircle,
  Hash,
  ArrowRight,
  ArrowLeft,
  ShoppingBag,
  MapPin,
  Clock,
  Layers,
  Check,
  Loader2,
  Scan,
  Maximize2,
  Minimize2,
  Sun,
  Eye
} from 'lucide-react';
import { cn } from '../utils/cn';

export const NewInspection: React.FC = () => {
  const { addInspection, selectedDistrict } = useInspections();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState<number>(0);

  // Source Type
  const [sourceType, setSourceType] = useState<InspectionSourceType>('Package / Label');
  const [inspectionType, setInspectionType] = useState<InspectionCategoryType>('Routine Market Surveillance');

  // Product Details
  const [productName, setProductName] = useState('Fortune Sunlite Refined Sunflower Oil 500g Pouch');
  const [brand, setBrand] = useState('Fortune');
  const [manufacturerName, setManufacturerName] = useState('Adani Wilmar Limited, Ahmedabad 380009');
  const [category, setCategory] = useState('Edible Oils & Fats');
  const [statedWeight, setStatedWeight] = useState(500);
  const [packagingType, setPackagingType] = useState<PackagingType>('Pouch');
  const [locationName, setLocationName] = useState('APMC Yard, Yeshwanthpur Wholesale Hub');
  const [gpsCoords, setGpsCoords] = useState({ lat: 12.9716, lng: 77.5946 });
  const [timestamp, setTimestamp] = useState('2026-08-22 11:23 AM');

  // Calibration State
  const [calibrationMethod, setCalibrationMethod] = useState<CalibrationMethod>('Calibration Card (ISO/IEC 7810)');
  const [panelHeightMm, setPanelHeightMm] = useState<number>(190);
  const [panelWidthMm, setPanelWidthMm] = useState<number>(140);
  const [isCalibrated, setIsCalibrated] = useState<boolean>(true);
  const [pixelsPerMm, setPixelsPerMm] = useState<number>(10.0);

  // Image & Preset
  const [selectedPreset, setSelectedPreset] = useState<string>('preset_violation_500g');
  const [imageUrl, setImageUrl] = useState('https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=1000&auto=format&fit=crop&q=85');

  // Animated Pipeline State
  const [pipelineIndex, setPipelineIndex] = useState<number>(0);
  const [pipelineRunning, setPipelineRunning] = useState<boolean>(false);

  // Results
  const [findings, setFindings] = useState<DeclarationFinding[]>([]);
  const [evaluatedScore, setEvaluatedScore] = useState<number>(62);
  const [evaluatedStatus, setEvaluatedStatus] = useState<InspectionStatus>('Violation');

  const steps = [
    { id: 'step-1', label: '1. Capture', description: 'Intake source & guidance' },
    { id: 'step-2', label: '2. Product Details', description: 'GPS, category, params' },
    { id: 'step-3', label: '3. Calibration', description: 'Card vs Panel scale' },
    { id: 'step-4', label: '4. Analysis Pipeline', description: '8-stage deterministic audit' },
    { id: 'step-5', label: '5. Review & Sign', description: 'Final determination' },
  ];

  const pipelineStages = [
    { id: 'p1', title: 'Quality Check', desc: 'Analyzing resolution, contrast, and specular glare factors...' },
    { id: 'p2', title: 'Perspective Correction', desc: 'Homography warping and packaging boundary planar rectification...' },
    { id: 'p3', title: 'Package / PDP Detection', desc: 'Geometric boundary segmentation & 40% area calculation...' },
    { id: 'p4', title: 'OCR Extraction', desc: 'Bilingual neural text extraction (English & Devanagari Hindi)...' },
    { id: 'p5', title: 'Field Parsing & Entity Mapping', desc: 'Classifying declarations: Net Qty, MRP, USP, Date, Manufacturer...' },
    { id: 'p6', title: 'Physical Calibration Alignment', desc: 'Applying 10.00 px/mm scale ratio to measured numeral bounding boxes...' },
    { id: 'p7', title: 'Rule 6(1) & Tenth Schedule Evaluation', desc: 'Checking 3.1mm measured font height against 4.0mm requirement...' },
    { id: 'p8', title: 'Human Review Staging', desc: 'Generating traceable evidence docket and Section 36 advisory notice...' },
  ];

  const handlePresetSelect = (presetKey: string) => {
    setSelectedPreset(presetKey);
    if (presetKey === 'preset_violation_500g') {
      setProductName('Fortune Sunlite Refined Sunflower Oil 500g Pouch');
      setBrand('Fortune');
      setManufacturerName('Adani Wilmar Limited, Ahmedabad 380009');
      setCategory('Edible Oils & Fats');
      setStatedWeight(500);
      setPackagingType('Pouch');
      setImageUrl('https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=1000&auto=format&fit=crop&q=85');
      setCalibrationMethod('Calibration Card (ISO/IEC 7810)');
      setIsCalibrated(true);
    } else if (presetKey === 'preset_good_100g') {
      setProductName('Tata Sampann Unpolished Yellow Moong Dal 100g');
      setBrand('Tata Sampann');
      setManufacturerName('Tata Consumer Products Ltd., Kolkata 700020');
      setCategory('Food & Grains');
      setStatedWeight(100);
      setPackagingType('Pouch');
      setImageUrl('https://images.unsplash.com/photo-1586201375761-83865001e31c?w=1000&auto=format&fit=crop&q=85');
      setCalibrationMethod('Calibration Card (ISO/IEC 7810)');
      setIsCalibrated(true);
    } else if (presetKey === 'preset_uncertain_glare') {
      setProductName("Haldiram's Nagpur Bhujia Sev 200g Pouch");
      setBrand("Haldiram's");
      setManufacturerName('Haldiram Snacks Pvt. Ltd., New Delhi 110044');
      setCategory('Packaged Snacks');
      setStatedWeight(200);
      setPackagingType('Pouch');
      setImageUrl('https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=1000&auto=format&fit=crop&q=85');
      setCalibrationMethod('Uncalibrated');
      setIsCalibrated(false);
    } else if (presetKey === 'preset_ecommerce') {
      setProductName('Noise Pulse 2 Max 1.85" Bluetooth Smart Watch (Jet Black)');
      setBrand('Noise');
      setManufacturerName('Nexxbase Marketing Pvt. Ltd., Gurugram 122016');
      setCategory('Electronics & Wearables');
      setStatedWeight(1);
      setPackagingType('E-commerce Listing');
      setSourceType('E-commerce Listing');
      setImageUrl('https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1000&auto=format&fit=crop&q=85');
      setCalibrationMethod('Physical Steel Rule');
      setIsCalibrated(true);
    }
  };

  const startAnalysisPipeline = () => {
    setCurrentStep(3);
    setPipelineRunning(true);
    setPipelineIndex(0);

    let stage = 0;
    const interval = setInterval(() => {
      stage += 1;
      setPipelineIndex(stage);
      if (stage >= pipelineStages.length) {
        clearInterval(interval);
        setPipelineRunning(false);

        // Load Findings
        if (selectedPreset === 'preset_violation_500g') {
          setFindings([
            {
              id: 'f-201',
              field: 'Net Quantity Numeral Height',
              clause: 'Rule 7(2)(i), Table I',
              extractedText: 'Net Qty: 500 g',
              status: 'Fail',
              severity: 'Critical',
              ocrConfidence: 96,
              measuredHeightMm: 3.1,
              requiredHeightMm: 4.0,
              quietZoneCleared: false,
              quietZoneClearanceMm: 1.2,
              quietZoneRequiredBufferMm: 8.0,
              quietZoneOverlapReason: 'Numeral 3.1mm printed below statutory 4.0mm requirement for weight >200g up to 500g.',
              notes: 'Critical defect under Rule 7(2)(i). Section 36 compounding notice recommended.',
            },
            {
              id: 'f-202',
              field: 'Quiet-Zone & Graphic Clearance',
              clause: 'Rule 9(3) - Separation of Declarations',
              extractedText: 'Clearance: 1.2 mm (Required: 8.0 mm)',
              status: 'Fail',
              severity: 'Major',
              ocrConfidence: 94,
              measuredHeightMm: 3.1,
              requiredHeightMm: 4.0,
              quietZoneCleared: false,
              quietZoneClearanceMm: 1.2,
              quietZoneRequiredBufferMm: 8.0,
              quietZoneOverlapReason: 'Hatching collision: Background artwork encroaches on 2x letter height clearance.',
            },
            {
              id: 'f-203',
              field: 'Maximum Retail Price (MRP) Declaration',
              clause: 'Rule 6(1)(d) & Rule 6(1)(s)',
              extractedText: 'MRP ₹ 95.00 (Incl. of all taxes) | USP ₹ 0.19/g',
              status: 'Pass',
              ocrConfidence: 97,
              measuredHeightMm: 2.8,
              requiredHeightMm: 2.0,
              quietZoneCleared: true,
            },
            {
              id: 'f-204',
              field: 'Name and Address of Manufacturer',
              clause: 'Rule 6(1)(a)',
              extractedText: 'Mfd & Pkd by Adani Wilmar Limited, Ahmedabad 380009',
              status: 'Pass',
              ocrConfidence: 98,
              measuredHeightMm: 2.2,
              requiredHeightMm: 1.5,
              quietZoneCleared: true,
            }
          ]);
          setEvaluatedScore(62);
          setEvaluatedStatus('Violation');
        } else if (selectedPreset === 'preset_uncertain_glare') {
          setFindings([
            {
              id: 'f-301',
              field: 'Maximum Retail Price (MRP)',
              clause: 'Rule 6(1)(d)',
              extractedText: 'MRP ₹ 5[?].00 (Specular Glare)',
              status: 'Review Required',
              ocrConfidence: 51,
              measuredHeightMm: undefined,
              requiredHeightMm: 2.0,
              notes: 'Glare obscured MRP patch. Retake with calibration card or manually verify.',
            }
          ]);
          setEvaluatedScore(58);
          setEvaluatedStatus('Review Required');
        } else {
          setFindings([
            {
              id: 'f-101',
              field: 'Net Quantity',
              clause: 'Rule 7(2)(i), Table I',
              extractedText: 'NET QUANTITY: 100 g',
              status: 'Pass',
              ocrConfidence: 99,
              measuredHeightMm: 2.6,
              requiredHeightMm: 2.0,
              quietZoneCleared: true,
            },
            {
              id: 'f-102',
              field: 'MRP & Unit Sale Price',
              clause: 'Rule 6(1)(d)',
              extractedText: 'MRP ₹ 42.00 | USP ₹ 0.42/g',
              status: 'Pass',
              ocrConfidence: 97,
              measuredHeightMm: 2.3,
              requiredHeightMm: 1.5,
              quietZoneCleared: true,
            }
          ]);
          setEvaluatedScore(96);
          setEvaluatedStatus('Verified');
        }
        setCurrentStep(4); // jump to Review
      }
    }, 450);
  };

  const handleFinalizeAndInspect = () => {
    const newId = selectedPreset === 'preset_violation_500g' ? 'INS-2026-0518-1123' : `INS-2026-${Math.floor(1000 + Math.random() * 9000)}`;
    const newInspection: Inspection = {
      id: newId,
      productName,
      brand,
      manufacturerName,
      category,
      netQuantity: `${statedWeight} ${packagingType === 'Bottle / Can' ? 'ml' : 'g'}`,
      statedWeightGramsOrMl: statedWeight,
      mrp: statedWeight === 500 ? 95 : statedWeight === 200 ? 55 : 42,
      unitSalePrice: `₹ ${(statedWeight === 500 ? 95/500 : 42/100).toFixed(2)} / g`,
      packagingType,
      pdpAreaCm2: 380,
      score: evaluatedScore,
      scoreBreakdown: {
        criticalViolations: evaluatedStatus === 'Violation' ? 1 : 0,
        majorViolations: evaluatedStatus === 'Violation' ? 1 : 0,
        minorWarnings: 0,
        reviewRequired: evaluatedStatus === 'Review Required' ? 1 : 0,
        verifiedCount: evaluatedStatus === 'Verified' ? 6 : 4,
      },
      status: evaluatedStatus,
      inspectionDate: timestamp,
      inspectionType,
      district: selectedDistrict,
      state: 'Karnataka',
      gpsCoordinates: {
        latitude: gpsCoords.lat,
        longitude: gpsCoords.lng,
        locationName,
      },
      capturedDevice: 'Samsung Galaxy Tab Active4 Pro (Officer Unit KA-04)',
      inspectorName: user.name,
      inspectorBadge: user.badgeNumber || 'LM-KA-BLR-0482',
      sampleImage: imageUrl,
      imageSha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      calibration: {
        method: calibrationMethod,
        type: calibrationMethod === 'Calibration Card (ISO/IEC 7810)' ? 'ISO/IEC 7810 ID-1 Standard' : 'Manual Dimensions',
        detectedWidthPx: 856,
        knownWidthMm: 85.60,
        pixelsPerMm,
        confidence: isCalibrated ? 98.7 : 0,
      },
      findings,
      quietZoneViolation: evaluatedStatus === 'Violation',
      minFontHeightCompliant: evaluatedStatus !== 'Violation',
      multilingualDetected: true,
      legalNoticeGenerated: evaluatedStatus === 'Violation',
      noticeNumber: evaluatedStatus === 'Violation' ? 'LM/KA/BLR/SEC36/2026/0192' : undefined,
    };

    addInspection(newInspection);
    navigate(`/inspection/${newId}`);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header & Step Tracker */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Legal Metrology Officer Inspection Intake
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              5-stage statutory intake: Capture guidance, GPS tag, physical calibration & deterministic analysis
            </p>
          </div>
          <Badge variant="blue" className="w-fit font-mono">
            LM-PCR-2011-v2024.2
          </Badge>
        </div>

        <ProgressIndicator
          steps={steps}
          currentStepIndex={currentStep}
          onStepClick={(idx) => !pipelineRunning && setCurrentStep(idx)}
        />
      </div>

      {/* STEP 0: Capture & Intake Source */}
      {currentStep === 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <Card className="lg:col-span-7">
            <CardHeader>
              <div>
                <CardTitle>1. Inspection Source & Evidence Intake</CardTitle>
                <CardDescription>Select inspection input method and sample asset</CardDescription>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Source Type Selector */}
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-600 block mb-2">
                  Select Evidence Intake Source
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'Package / Label', label: 'Package / Label', icon: Upload, desc: 'High-res file intake' },
                    { id: 'Take Photo', label: 'Take Photo', icon: Camera, desc: 'Field tablet camera' },
                    { id: 'E-commerce Listing', label: 'E-commerce Listing', icon: ShoppingBag, desc: 'Online PDP crawler' },
                  ].map((src) => {
                    const isSelected = sourceType === src.id;
                    const Icon = src.icon;
                    return (
                      <button
                        key={src.id}
                        type="button"
                        onClick={() => setSourceType(src.id as any)}
                        className={cn(
                          "p-3 rounded-lg border text-center transition-all flex flex-col items-center justify-center gap-1.5",
                          isSelected
                            ? "bg-blue-50 border-blue-600 ring-2 ring-blue-600 text-blue-900 font-bold shadow-xs"
                            : "bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100"
                        )}
                      >
                        <Icon className="w-5 h-5" />
                        <span className="text-xs">{src.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Seeded Cases Quick Selector */}
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-600 block mb-2">
                  Select Demo Inspection Case
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {[
                    { id: 'preset_violation_500g', title: 'Case 2 — Fortune 500g', badge: 'Violation (3.1mm)', color: 'border-red-400 bg-red-50/50' },
                    { id: 'preset_good_100g', title: 'Case 1 — Tata Moong 100g', badge: 'Verified (2.6mm)', color: 'border-emerald-400 bg-emerald-50/50' },
                    { id: 'preset_uncertain_glare', title: 'Case 3 — Haldiram Glare', badge: 'Review Req. (51%)', color: 'border-amber-400 bg-amber-50/50' },
                    { id: 'preset_ecommerce', title: 'Case 4 — E-Commerce PDP', badge: 'Rule 6(10) Violation', color: 'border-blue-400 bg-blue-50/50' },
                  ].map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => handlePresetSelect(p.id)}
                      className={cn(
                        "p-3 rounded-lg border text-left transition-all",
                        selectedPreset === p.id 
                          ? cn("ring-2 ring-blue-600 shadow-xs", p.color)
                          : "bg-slate-50 border-slate-200 hover:bg-slate-100"
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900">{p.title}</span>
                        <span className="text-[10px] font-mono font-bold">{p.badge}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Image Preview with Reticle */}
              <div className="relative aspect-16/9 bg-slate-950 rounded-lg overflow-hidden border border-slate-700">
                <img
                  src={imageUrl}
                  alt="Inspection Sample"
                  className="w-full h-full object-cover opacity-85"
                />
                <div className="absolute inset-0 bg-mm-grid opacity-30 pointer-events-none" />
                <div className="absolute bottom-3 left-3 bg-slate-900/90 text-white font-mono text-[10px] px-2 py-1 rounded border border-slate-700">
                  SHA-256: e3b0c44298fc...855
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <span className="text-xs text-slate-500 font-mono">Source: {sourceType}</span>
              <Button
                variant="primary"
                onClick={() => setCurrentStep(1)}
                rightIcon={<ArrowRight className="w-4 h-4" />}
                className="bg-blue-700 hover:bg-blue-800"
              >
                Proceed to Product Details
              </Button>
            </CardFooter>
          </Card>

          {/* Image Quality Guidance Panel */}
          <div className="lg:col-span-5 space-y-4">
            <Card className="border-t-4 border-t-amber-500 bg-white">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Eye className="w-5 h-5 text-amber-600" />
                  <CardTitle>Image Quality Guidance</CardTitle>
                </div>
                <CardDescription>Legal Metrology capture protocol for statutory validity</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-xs">
                {[
                  { title: '1. Fill the Frame', desc: 'Package should cover at least 70% of optical sensor viewport with straight alignment.' },
                  { title: '2. Reduce Specular Glare', desc: 'Avoid direct overhead flash on glossy plastic or metallic foil pouches.' },
                  { title: '3. Improve Focus & Edge Acuity', desc: 'Ensure sub-millimeter letter stroke edges are sharp and free from motion blur.' },
                  { title: '4. Include ISO Calibration Card', desc: 'Place standard ID-1 card (85.60 mm) flat in the same focal plane as the Principal Display Panel.' },
                ].map((g, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 space-y-0.5">
                    <strong className="text-slate-900 font-bold block">{g.title}</strong>
                    <p className="text-slate-600 text-[11px] leading-relaxed">{g.desc}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* STEP 1: Product Details & GPS */}
      {currentStep === 1 && (
        <Card>
          <CardHeader>
            <div>
              <CardTitle>2. Product Parameters & Geotagging</CardTitle>
              <CardDescription>Stated package net weight, manufacturer, and inspection location</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Product Name / Description"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
              />
              <Input
                label="Brand Name"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Select
                label="Commodity Category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                options={[
                  { value: 'Edible Oils & Fats', label: 'Edible Oils & Fats' },
                  { value: 'Food & Grains', label: 'Food & Grains' },
                  { value: 'Packaged Snacks', label: 'Packaged Snacks' },
                  { value: 'Dairy & Beverages', label: 'Dairy & Beverages' },
                  { value: 'Electronics & Wearables', label: 'Electronics & Wearables' },
                  { value: 'Cosmetics', label: 'Cosmetics & Soap' },
                ]}
              />

              <Input
                label="Stated Net Quantity (g / ml)"
                type="number"
                value={statedWeight}
                onChange={(e) => setStatedWeight(Number(e.target.value))}
                helperText={
                  statedWeight <= 50 ? 'Table I Min Font: 1.5 mm' :
                  statedWeight <= 200 ? 'Table I Min Font: 2.0 mm' :
                  statedWeight <= 500 ? 'Table I Min Font: 4.0 mm' : 'Table I Min Font: 6.0 mm'
                }
              />

              <Select
                label="Packaging Type"
                value={packagingType}
                onChange={(e) => setPackagingType(e.target.value as any)}
                options={[
                  { value: 'Pouch', label: 'Flexible Poly Pouch' },
                  { value: 'Rigid Box', label: 'Rigid Box / Carton' },
                  { value: 'Bottle / Can', label: 'Bottle / Can' },
                  { value: 'E-commerce Listing', label: 'E-commerce Listing' },
                ]}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-slate-100">
              <Input
                label="Inspection Location"
                value={locationName}
                onChange={(e) => setLocationName(e.target.value)}
                leftIcon={<MapPin className="w-4 h-4 text-blue-600" />}
              />
              <div className="grid grid-cols-2 gap-2">
                <Input
                  label="GPS Latitude"
                  value={gpsCoords.lat.toString()}
                  onChange={(e) => setGpsCoords({ ...gpsCoords, lat: Number(e.target.value) })}
                />
                <Input
                  label="GPS Longitude"
                  value={gpsCoords.lng.toString()}
                  onChange={(e) => setGpsCoords({ ...gpsCoords, lng: Number(e.target.value) })}
                />
              </div>
            </div>

            <Input
              label="Manufacturer / Packer Address"
              value={manufacturerName}
              onChange={(e) => setManufacturerName(e.target.value)}
            />
          </CardContent>
          <CardFooter>
            <Button variant="outline" onClick={() => setCurrentStep(0)} leftIcon={<ArrowLeft className="w-4 h-4" />}>
              Back
            </Button>
            <Button variant="primary" onClick={() => setCurrentStep(2)} rightIcon={<ArrowRight className="w-4 h-4" />}>
              Proceed to Calibration
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* STEP 2: Physical Calibration (Card vs Dimensions) */}
      {currentStep === 2 && (
        <Card>
          <CardHeader>
            <div>
              <CardTitle>3. Physical Scale Calibration</CardTitle>
              <CardDescription>
                Establish physical millimeters to sensor pixels conversion ratio
              </CardDescription>
            </div>
            {isCalibrated ? (
              <Badge variant="green" className="font-mono">
                <CheckCircle2 className="w-3.5 h-3.5 inline mr-1" />
                Scale Locked: 10.00 px / mm
              </Badge>
            ) : (
              <Badge variant="amber" className="font-mono">
                <AlertTriangle className="w-3.5 h-3.5 inline mr-1" />
                Uncalibrated
              </Badge>
            )}
          </CardHeader>
          <CardContent className="space-y-5">
            {/* Calibration Method Choice */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => {
                  setCalibrationMethod('Calibration Card (ISO/IEC 7810)');
                  setIsCalibrated(true);
                  setPixelsPerMm(10.0);
                }}
                className={cn(
                  "p-4 rounded-xl border text-left transition-all space-y-1",
                  calibrationMethod === 'Calibration Card (ISO/IEC 7810)'
                    ? "bg-blue-50 border-blue-600 ring-2 ring-blue-600"
                    : "bg-slate-50 border-slate-200 hover:bg-slate-100"
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-900">Calibration Card (ISO/IEC 7810)</span>
                  <span className="text-[10px] font-mono bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded font-bold">Recommended</span>
                </div>
                <p className="text-[11px] text-slate-500">
                  Sub-pixel optical detection of standard 85.60 mm reference smart card.
                </p>
              </button>

              <button
                type="button"
                onClick={() => {
                  setCalibrationMethod('Enter Panel Dimensions');
                  setIsCalibrated(true);
                  setPixelsPerMm(10.0);
                }}
                className={cn(
                  "p-4 rounded-xl border text-left transition-all space-y-1",
                  calibrationMethod === 'Enter Panel Dimensions'
                    ? "bg-blue-50 border-blue-600 ring-2 ring-blue-600"
                    : "bg-slate-50 border-slate-200 hover:bg-slate-100"
                )}
              >
                <span className="font-bold text-xs text-slate-900 block">Enter Panel Dimensions</span>
                <p className="text-[11px] text-slate-500">
                  Enter physical height and width of Principal Display Panel in millimeters.
                </p>
              </button>
            </div>

            {/* If Panel Dimensions Selected */}
            {calibrationMethod === 'Enter Panel Dimensions' && (
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 grid grid-cols-2 gap-4">
                <Input
                  label="Panel Height (mm)"
                  type="number"
                  value={panelHeightMm}
                  onChange={(e) => setPanelHeightMm(Number(e.target.value))}
                />
                <Input
                  label="Panel Width (mm)"
                  type="number"
                  value={panelWidthMm}
                  onChange={(e) => setPanelWidthMm(Number(e.target.value))}
                />
              </div>
            )}

            {/* Fallback Warning if Uncalibrated */}
            {!isCalibrated && (
              <div className="p-4 bg-amber-50 border border-amber-300 rounded-lg flex items-start gap-2.5 text-xs text-amber-950">
                <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <strong className="block font-bold">Calibration Warning:</strong>
                  <span>Measurement unavailable — recapture with calibration card or enter panel dimensions.</span>
                </div>
              </div>
            )}
          </CardContent>
          <CardFooter>
            <Button variant="outline" onClick={() => setCurrentStep(1)} leftIcon={<ArrowLeft className="w-4 h-4" />}>
              Back
            </Button>
            <Button
              variant="primary"
              onClick={startAnalysisPipeline}
              rightIcon={<Sparkles className="w-4 h-4" />}
              className="bg-blue-700 hover:bg-blue-800"
            >
              Launch 8-Stage Analysis Pipeline
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* STEP 3: Animated 8-Stage Analysis Pipeline */}
      {currentStep === 3 && (
        <Card className="border-t-4 border-t-blue-700">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-600 animate-spin" />
              <div>
                <CardTitle>4. Deterministic Analysis Engine Running</CardTitle>
                <CardDescription>Simulated deterministic evaluation pipeline (Zero hallucination)</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2.5">
              {pipelineStages.map((stage, idx) => {
                const isPassed = idx < pipelineIndex;
                const isCurrent = idx === pipelineIndex;
                const isPending = idx > pipelineIndex;

                return (
                  <div
                    key={stage.id}
                    className={cn(
                      "p-3 rounded-lg border flex items-center justify-between gap-3 text-xs transition-all",
                      isPassed && "bg-emerald-50/60 border-emerald-200 text-emerald-950",
                      isCurrent && "bg-blue-50 border-blue-500 ring-1 ring-blue-500 text-blue-950 shadow-sm",
                      isPending && "bg-slate-50 border-slate-200 text-slate-400 opacity-60"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "w-6 h-6 rounded-full flex items-center justify-center font-mono font-bold text-[10px]",
                        isPassed && "bg-emerald-600 text-white",
                        isCurrent && "bg-blue-600 text-white animate-pulse",
                        isPending && "bg-slate-200 text-slate-500"
                      )}>
                        {isPassed ? <Check className="w-3.5 h-3.5" /> : isCurrent ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : idx + 1}
                      </div>
                      <div>
                        <span className="font-bold block">{stage.title}</span>
                        <span className="text-[11px] opacity-85">{stage.desc}</span>
                      </div>
                    </div>

                    <div className="font-mono text-[10px] font-bold uppercase shrink-0">
                      {isPassed && <span className="text-emerald-700">Done</span>}
                      {isCurrent && <span className="text-blue-700 animate-pulse">Running...</span>}
                      {isPending && <span className="text-slate-400">Waiting</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* STEP 4: Review & Finalize */}
      {currentStep === 4 && (
        <Card className="border-t-4 border-t-blue-700">
          <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <CardTitle>5. Inspection Findings Summary</CardTitle>
                <StatusBadge status={evaluatedStatus} size="md" />
              </div>
              <CardDescription>
                Compliance Score: <strong className="font-mono text-slate-900">{evaluatedScore}/100</strong> • {findings.length} Declarations Evaluated
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2.5">
              {findings.map((f) => (
                <FindingCard key={f.id} finding={f} />
              ))}
            </div>
          </CardContent>
          <CardFooter>
            <Button variant="outline" onClick={() => setCurrentStep(2)} leftIcon={<ArrowLeft className="w-4 h-4" />}>
              Re-calibrate
            </Button>
            <Button
              variant="primary"
              size="lg"
              onClick={handleFinalizeAndInspect}
              leftIcon={<ShieldCheck className="w-5 h-5" />}
              className="bg-blue-700 hover:bg-blue-800 border-blue-700"
            >
              Open Officer Workstation
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  );
};
