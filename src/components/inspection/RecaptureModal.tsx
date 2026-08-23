import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { DetectedProduct, RecaptureReason } from '../../types';
import { batchInspectionApi } from '../../services/batchInspectionApi';
import { useInspections } from '../../context/InspectionContext';
import { 
  Camera, 
  Upload, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  Eye, 
  Sparkles, 
  ShieldCheck, 
  Image as ImageIcon,
  Sliders,
  FileCheck2,
  ArrowRight,
  Sun,
  Layers
} from 'lucide-react';
import { cn } from '../../utils/cn';

interface RecaptureModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
  product: DetectedProduct | null;
  onRecaptureSuccess?: (updatedProduct: DetectedProduct) => void;
}

export const RecaptureModal: React.FC<RecaptureModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  product,
  onRecaptureSuccess,
}) => {
  const { recaptureBatchProduct } = useInspections();
  
  // Clean replacement image candidates for smooth demo
  const sampleCleanPresets: Record<string, { title: string; url: string; note: string }> = {
    'Aashirvaad': {
      title: 'Clean Frontal Pack (Unobstructed PDP)',
      url: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop&q=90',
      note: 'Captured with shelf barrier moved; bottom declaration zone 100% visible.',
    },
    'Haldiram': {
      title: 'Polarized Glare-Free Exposure',
      url: 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=600&auto=format&fit=crop&q=90',
      note: 'Diffused lighting applied; MRP and Net Wt numeral contrast restored.',
    },
    'Everest': {
      title: 'High-Contrast Isolated Crop',
      url: 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600&auto=format&fit=crop&q=90',
      note: '90° direct angle; Consumer Care email text extracted at 98% confidence.',
    },
    'Default': {
      title: 'Optimal Rectified Single Product Crop',
      url: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=90',
      note: 'Isolated capture with statutory reference card.',
    }
  };

  const currentPreset = product?.brand && sampleCleanPresets[product.brand] 
    ? sampleCleanPresets[product.brand] 
    : sampleCleanPresets['Default'];

  const [selectedImageUrl, setSelectedImageUrl] = useState<string>(currentPreset.url);
  const [officerNotes, setOfficerNotes] = useState<string>(currentPreset.note);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [processingStage, setProcessingStage] = useState<string>('');
  const [isSuccess, setIsSuccess] = useState<boolean>(false);

  if (!product) return null;

  const getReasonBadge = (reason?: string) => {
    switch (reason?.toLowerCase()) {
      case 'shelf_divider_occlusion':
      case 'occlusion':
        return { label: 'Shelf Divider Occlusion', variant: 'amber' as const, icon: Layers };
      case 'glare':
        return { label: 'Specular Glare Defect', variant: 'amber' as const, icon: Sun };
      case 'blur':
        return { label: 'Motion / Optical Blur', variant: 'amber' as const, icon: Eye };
      case 'low_resolution':
        return { label: 'Low Pixel Density (<150 DPI)', variant: 'amber' as const, icon: AlertTriangle };
      case 'low_ocr_confidence':
        return { label: 'Ambiguous OCR Extraction', variant: 'amber' as const, icon: Sliders };
      default:
        return { label: 'Optical Quality Defect', variant: 'amber' as const, icon: AlertTriangle };
    }
  };

  const reasonInfo = getReasonBadge(product.recaptureReason || 'shelf_divider_occlusion');

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const localUrl = URL.createObjectURL(file);
      setSelectedImageUrl(localUrl);
      setOfficerNotes(`Officer uploaded photo (${file.name}) directly from surveillance unit.`);
    }
  };

  const handleExecuteRecapture = async () => {
    setIsProcessing(true);
    setProcessingStage('Uploading isolated product evidence...');
    
    await new Promise(r => setTimeout(r, 600));
    setProcessingStage('Performing high-density Neural OCR & Font Caliper extraction...');
    
    await new Promise(r => setTimeout(r, 700));
    setProcessingStage('Cross-verifying Rule 6 & 7 Packaged Commodities declarations...');
    
    await new Promise(r => setTimeout(r, 500));

    try {
      const updatedProduct = await batchInspectionApi.recaptureProduct(
        sessionId,
        product.id,
        {
          new_image_url: selectedImageUrl,
          reason: product.recaptureReason || 'glare',
          officer_notes: officerNotes,
        }
      );

      recaptureBatchProduct(sessionId, product.id, selectedImageUrl, officerNotes);
      setIsProcessing(false);
      setIsSuccess(true);

      if (onRecaptureSuccess) {
        onRecaptureSuccess(updatedProduct);
      }
    } catch (err) {
      setIsProcessing(false);
      alert('Recapture failed to reprocess. Please try again.');
    }
  };

  const handleClose = () => {
    setIsSuccess(false);
    setIsProcessing(false);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={`Smart Recapture Workstation — ${product.productNumber}`}
      maxWidth="4xl"
    >
      <div className="space-y-5 text-slate-800">
        {/* Top Statutory Guidance & Original Integrity Notice */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-3 text-xs text-blue-950">
          <ShieldCheck className="w-5 h-5 text-blue-700 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-bold flex items-center gap-2">
              <span>Statutory Evidence Preservation Protocol</span>
              <span className="bg-blue-200 text-blue-900 text-[10px] px-1.5 py-0.2 rounded font-mono">Sec 15 / Rule 7</span>
            </div>
            <p className="text-[11px] text-blue-800 leading-relaxed">
              The original shelf context image will <strong>never be deleted</strong>. It is preserved in the judicial dossier. The newly captured image is linked as secondary forensic evidence to resolve optical ambiguity.
            </p>
          </div>
        </div>

        {/* Product & Backend Defect Reason Overview */}
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider">
              Target Item: {product.productNumber}
            </div>
            <h3 className="text-base font-bold text-slate-900 mt-0.5">
              {product.productName}
            </h3>
            <p className="text-xs text-slate-500">
              Brand: <span className="font-semibold text-slate-700">{product.brand}</span> • Category: <span className="font-semibold text-slate-700">{product.category}</span>
            </p>
          </div>

          <div className="flex flex-col sm:items-end gap-1.5 shrink-0">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Backend Flag
            </div>
            <Badge variant="amber" className="flex items-center gap-1 text-xs py-1 px-2.5 font-bold">
              <reasonInfo.icon className="w-3.5 h-3.5" />
              <span>{reasonInfo.label}</span>
            </Badge>
            <span className="text-[10px] text-slate-500 font-mono">
              Conf: {product.detectionConfidence.toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Side-by-Side: Original Evidence vs New Evidence */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          {/* Column 1: Original Evidence (Defective) */}
          <div className="border border-slate-200 rounded-xl p-3.5 bg-white space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
                <ImageIcon className="w-4 h-4 text-slate-500" />
                <span>Original Shelf Evidence</span>
              </div>
              <Badge variant="amber" className="text-[10px]">
                Defective
              </Badge>
            </div>

            <div className="relative rounded-lg overflow-hidden bg-slate-950 border border-slate-300 aspect-video flex items-center justify-center">
              <img
                src={product.cropImageUrl}
                alt="Original Evidence"
                className="w-full h-full object-cover opacity-85"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex flex-col justify-end p-2.5">
                <div className="text-[11px] font-mono text-amber-300 font-bold flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>{product.recaptureDescription || product.notes || 'Optical defect detected'}</span>
                </div>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 italic">
              Original bounding box crop from master shelf capture.
            </p>
          </div>

          {/* Column 2: New Evidence (Preview & Clean Replacement) */}
          <div className="border border-blue-300 ring-2 ring-blue-100 rounded-xl p-3.5 bg-blue-50/40 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs font-bold text-blue-900">
                <Sparkles className="w-4 h-4 text-blue-600" />
                <span>New Replacement Evidence</span>
              </div>
              <Badge variant="green" className="text-[10px]">
                Clean Capture
              </Badge>
            </div>

            <div className="relative rounded-lg overflow-hidden bg-slate-950 border border-blue-400 aspect-video flex items-center justify-center">
              <img
                src={selectedImageUrl}
                alt="New Evidence Preview"
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-2 right-2 bg-slate-900/80 backdrop-blur-xs text-white text-[10px] font-mono px-2 py-0.5 rounded">
                Preview Ready
              </div>
            </div>

            {/* Quick Acquisition Controls */}
            <div className="flex items-center gap-2 pt-1">
              <label className="flex-1">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  leftIcon={<Upload className="w-3.5 h-3.5 text-slate-600" />}
                  className="w-full bg-white text-xs"
                  onClick={(e) => {
                    // Let the label trigger file picker
                  }}
                >
                  Upload Photo
                </Button>
              </label>

              <Button
                type="button"
                variant="outline"
                size="sm"
                leftIcon={<Camera className="w-3.5 h-3.5 text-blue-700" />}
                className="flex-1 bg-white text-xs text-blue-700 border-blue-200"
                onClick={() => {
                  setSelectedImageUrl(currentPreset.url);
                  setOfficerNotes(currentPreset.note);
                }}
              >
                Use Clean Preset
              </Button>
            </div>
          </div>
        </div>

        {/* Officer Recapture Log Notes */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 block">
            Officer Verification Notes & Rectification Log:
          </label>
          <input
            type="text"
            value={officerNotes}
            onChange={(e) => setOfficerNotes(e.target.value)}
            className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-hidden bg-white"
            placeholder="e.g. Cleared physical obstruction, captured high-contrast frontal angle."
          />
        </div>

        {/* Processing State Feedback */}
        {isProcessing && (
          <div className="p-4 bg-slate-900 text-white rounded-xl space-y-2 animate-pulse">
            <div className="flex items-center gap-2 text-xs font-bold text-blue-400">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Reprocessing Product Pipeline...</span>
            </div>
            <p className="text-xs text-slate-300 font-mono">
              {processingStage}
            </p>
          </div>
        )}

        {/* Success Confirmation Banner */}
        {isSuccess && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 rounded-xl flex items-center justify-between gap-3 text-emerald-950">
            <div className="flex items-center gap-2.5">
              <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0" />
              <div>
                <h4 className="text-sm font-bold text-emerald-900">
                  Product Successfully Reprocessed & Verified!
                </h4>
                <p className="text-xs text-emerald-700">
                  Status updated to <strong>Verified (Compliant)</strong>. Primary shelf and secondary recapture evidence have been synchronized into the docket.
                </p>
              </div>
            </div>
            <Button
              variant="primary"
              size="sm"
              onClick={handleClose}
              className="bg-emerald-700 hover:bg-emerald-800 shrink-0 text-xs"
            >
              Done & Return
            </Button>
          </div>
        )}

        {/* Modal Action Footer */}
        {!isSuccess && (
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-200">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              disabled={isProcessing}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              leftIcon={isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <FileCheck2 className="w-4 h-4" />}
              onClick={handleExecuteRecapture}
              disabled={isProcessing}
              className="bg-blue-700 hover:bg-blue-800 text-xs px-5"
            >
              {isProcessing ? 'Processing...' : 'Reprocess Product Evidence'}
            </Button>
          </div>
        )}
      </div>
    </Modal>
  );
};
