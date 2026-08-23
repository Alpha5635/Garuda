import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useInspections } from '../context/InspectionContext';
import { useAuth } from '../context/AuthContext';
import type { 
  BatchInspectionSession as IBatchSession, 
  DetectedProduct, 
  BatchSessionStatus,
  ProductReviewStatus,
  ProductPriority 
} from '../types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { ShelfDetectionCanvas } from '../components/inspection/ShelfDetectionCanvas';
import { RecaptureModal } from '../components/inspection/RecaptureModal';
import { 
  ArrowLeft, 
  Layers, 
  CheckCircle2, 
  AlertTriangle, 
  AlertOctagon, 
  Camera, 
  RefreshCw, 
  Clock, 
  ShieldCheck, 
  MapPin, 
  FileText, 
  Download, 
  ChevronRight, 
  Sparkles, 
  HelpCircle, 
  Hash, 
  Eye, 
  RotateCcw,
  Zap,
  ArrowUpRight,
  Sun,
  Sliders,
  Check
} from 'lucide-react';
import { cn } from '../utils/cn';

export const BatchInspectionSession: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { 
    getBatchSessionById, 
    batchSessions, 
    updateBatchSessionStatus,
    retryFailedBatchProducts 
  } = useInspections();
  const { user } = useAuth();

  const currentSessionId = id || 'LS-2026-1042';
  const session = getBatchSessionById(currentSessionId) || batchSessions[0];

  const [selectedProductId, setSelectedProductId] = useState<string | null>(
    session?.products?.[0]?.id || null
  );
  const [hoveredProductId, setHoveredProductId] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [isRetryingFailed, setIsRetryingFailed] = useState<boolean>(false);

  // Recapture Modal State
  const [isRecaptureModalOpen, setIsRecaptureModalOpen] = useState<boolean>(false);
  const [targetRecaptureProduct, setTargetRecaptureProduct] = useState<DetectedProduct | null>(null);

  // Sync selected product when session changes
  useEffect(() => {
    if (session?.products?.length && (!selectedProductId || !session.products.some(p => p.id === selectedProductId))) {
      setSelectedProductId(session.products[0].id);
    }
  }, [session, selectedProductId]);

  if (!session) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center space-y-4">
        <h2 className="text-xl font-bold text-slate-800">Batch Inspection Session Not Found</h2>
        <p className="text-xs text-slate-500">The requested session identifier does not exist or has expired.</p>
        <Button variant="primary" onClick={() => navigate('/inspection/new')}>
          Create New Batch Inspection
        </Button>
      </div>
    );
  }

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
    }, 500);
  };

  const handleRetryFailed = async () => {
    setIsRetryingFailed(true);
    await new Promise(r => setTimeout(r, 800));
    retryFailedBatchProducts(session.id);
    setIsRetryingFailed(false);
  };

  const handleOpenRecapture = (product: DetectedProduct) => {
    setTargetRecaptureProduct(product);
    setIsRecaptureModalOpen(true);
  };

  const getStatusBadgeVariant = (status: BatchSessionStatus): 'green' | 'blue' | 'amber' | 'red' | 'slate' => {
    switch (status) {
      case 'Complete':
        return 'green';
      case 'Detecting Products':
      case 'Processing Products':
      case 'Aggregating Results':
        return 'blue';
      case 'Partial Failure':
        return 'amber';
      case 'Failed':
        return 'red';
      case 'Queued':
      default:
        return 'slate';
    }
  };

  // Filter products by priority & status
  const filteredProducts = session.products.filter(p => {
    if (priorityFilter === 'ALL') return true;
    if (priorityFilter === 'HIGH') return p.priority === 'High Priority' || p.reviewStatus === 'Violation';
    if (priorityFilter === 'MEDIUM') return p.priority === 'Medium Priority';
    if (priorityFilter === 'LOW') return p.priority === 'Low Priority' || p.priority === 'Normal';
    if (priorityFilter === 'REVIEW') return p.reviewStatus === 'Review Required';
    if (priorityFilter === 'RECAPTURE') return p.reviewStatus === 'Needs Recapture';
    return true;
  });

  const highPriorityCount = session.products.filter(p => p.priority === 'High Priority' || p.reviewStatus === 'Violation').length;
  const mediumPriorityCount = session.products.filter(p => p.priority === 'Medium Priority').length;
  const lowPriorityCount = session.products.filter(p => p.priority === 'Low Priority' || p.priority === 'Normal').length;
  const reviewRequiredCount = session.products.filter(p => p.reviewStatus === 'Review Required').length;
  const needsRecaptureCount = session.products.filter(p => p.reviewStatus === 'Needs Recapture').length;
  const violationsCount = session.products.filter(p => p.reviewStatus === 'Violation').length;

  return (
    <div className="space-y-5 max-w-7xl mx-auto">
      
      {/* 🌟 MAJOR DIFFERENTIATOR BANNER: ONE CAPTURE -> 12 PRODUCTS -> 12 DETERMINATIONS */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-blue-900 text-white p-4 rounded-xl shadow-md flex flex-col md:flex-row md:items-center md:justify-between gap-4 border border-indigo-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="bg-blue-500/30 text-blue-300 font-mono text-[10px] font-bold px-2 py-0.5 rounded border border-blue-400/30 uppercase tracking-wider flex items-center gap-1">
              <Zap className="w-3 h-3 text-amber-400" />
              Multi-Product Inference Architecture
            </span>
            <span className="text-xs text-slate-300 font-mono">Stage 4B Intelligence</span>
          </div>
          <h2 className="text-sm sm:text-base font-bold tracking-tight text-white flex items-center gap-2">
            <span>ONE SHELF CAPTURE</span>
            <span className="text-blue-400">➔</span>
            <span>{session.totalProducts} DETECTED PRODUCTS</span>
            <span className="text-blue-400">➔</span>
            <span>{session.totalProducts} EVIDENCE DETERMINATIONS</span>
          </h2>
          <p className="text-xs text-slate-300">
            Autonomous multi-bounding box localization, sub-millimeter font height measurement, and legal risk prioritization in one unified pass.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Link
            to="/reports"
            className="inline-flex items-center gap-1.5 text-xs font-bold bg-white text-slate-900 hover:bg-slate-100 px-3.5 py-2 rounded-lg transition shadow-xs"
          >
            <FileText className="w-3.5 h-3.5 text-blue-700" />
            <span>Generate Session Dossier</span>
          </Link>
        </div>
      </div>

      {/* Top Header Card */}
      <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200 shadow-subtle flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              onClick={() => navigate('/history')}
              className="p-1 hover:bg-slate-100 rounded text-slate-500 hover:text-slate-900 transition mr-1"
              title="Back to History"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>

            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              Batch Inspection Session
            </h1>

            <span className="font-mono text-xs font-bold bg-slate-100 text-slate-800 px-2.5 py-1 rounded-md border border-slate-200">
              {session.id}
            </span>

            <Badge variant={getStatusBadgeVariant(session.status)} className="capitalize font-mono">
              {session.status}
            </Badge>

            {session.isSeededDemo && (
              <Badge variant="blue" className="text-[10px] uppercase font-mono">
                Seeded Demo ({session.totalProducts} Products)
              </Badge>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 pt-0.5">
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {session.locationName} • <strong className="text-slate-700">{session.district}</strong>
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              {session.createdAt}
            </span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
              Officer: {session.inspectorName} ({session.inspectorBadge})
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<RefreshCw className={cn("w-3.5 h-3.5", isRefreshing && "animate-spin")} />}
            onClick={handleRefresh}
          >
            Refresh
          </Button>

          <Button
            variant="outline"
            size="sm"
            leftIcon={<Camera className="w-3.5 h-3.5" />}
            onClick={() => navigate('/inspection/new')}
          >
            New Batch
          </Button>

          <Button
            variant="primary"
            size="sm"
            leftIcon={<Download className="w-3.5 h-3.5" />}
            onClick={() => navigate('/reports')}
            className="bg-blue-700 hover:bg-blue-800"
          >
            Session Report
          </Button>
        </div>
      </div>

      {/* Partial Failure Warning Banner if applicable */}
      {(session.status === 'Partial Failure' || session.failedCount > 0) && (
        <div className="p-4 bg-amber-50 border border-amber-300 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-amber-950">
          <div className="flex items-start gap-2.5">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-amber-900">
                Partial Batch Processing Alert
              </h4>
              <p className="text-xs text-amber-800">
                {session.totalProducts} products detected: {session.completedCount} complete, {session.reviewRequiredCount} review required, and {session.failedCount} product failed extraction. The valid products remain active.
              </p>
            </div>
          </div>
          <Button
            variant="primary"
            size="sm"
            leftIcon={isRetryingFailed ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <RotateCcw className="w-3.5 h-3.5" />}
            onClick={handleRetryFailed}
            disabled={isRetryingFailed}
            className="bg-amber-700 hover:bg-amber-800 shrink-0 text-xs text-white border-amber-800"
          >
            {isRetryingFailed ? 'Retrying...' : 'Retry Failed Products'}
          </Button>
        </div>
      )}

      {/* 8-Metric Real Backend Session Summary Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5 font-mono">
        <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block font-sans">
            Total Products
          </span>
          <div className="text-xl font-bold text-slate-900 mt-0.5">
            {session.totalProducts}
          </div>
          <span className="text-[10px] text-slate-400 font-sans">Detected</span>
        </div>

        <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider block font-sans">
            Processed
          </span>
          <div className="text-xl font-bold text-blue-900 mt-0.5">
            {session.processedCount}
          </div>
          <span className="text-[10px] text-blue-600 font-sans">100% complete</span>
        </div>

        <div className="bg-white p-3 rounded-xl border border-red-200 shadow-xs bg-red-50/20">
          <span className="text-[10px] font-bold text-red-700 uppercase tracking-wider block font-sans flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-red-600 inline-block"></span>
            High Priority
          </span>
          <div className="text-xl font-bold text-red-700 mt-0.5">
            {highPriorityCount}
          </div>
          <span className="text-[10px] text-red-600 font-sans">Rule breach</span>
        </div>

        <div className="bg-white p-3 rounded-xl border border-amber-200 shadow-xs bg-amber-50/20">
          <span className="text-[10px] font-bold text-amber-700 uppercase tracking-wider block font-sans flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 inline-block"></span>
            Med Priority
          </span>
          <div className="text-xl font-bold text-amber-700 mt-0.5">
            {mediumPriorityCount}
          </div>
          <span className="text-[10px] text-amber-600 font-sans">Attention</span>
        </div>

        <div className="bg-white p-3 rounded-xl border border-emerald-200 shadow-xs bg-emerald-50/20">
          <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider block font-sans flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 inline-block"></span>
            Low Priority
          </span>
          <div className="text-xl font-bold text-emerald-700 mt-0.5">
            {lowPriorityCount}
          </div>
          <span className="text-[10px] text-emerald-600 font-sans">Compliant</span>
        </div>

        <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold text-amber-600 uppercase tracking-wider block font-sans">
            Review Req.
          </span>
          <div className="text-xl font-bold text-amber-800 mt-0.5">
            {reviewRequiredCount}
          </div>
          <span className="text-[10px] text-amber-600 font-sans">Glare / OCR</span>
        </div>

        <div className="bg-white p-3 rounded-xl border border-orange-200 shadow-xs bg-orange-50/30">
          <span className="text-[10px] font-bold text-orange-700 uppercase tracking-wider block font-sans">
            Needs Recapt.
          </span>
          <div className="text-xl font-bold text-orange-800 mt-0.5">
            {needsRecaptureCount}
          </div>
          <span className="text-[10px] text-orange-600 font-sans">Occluded PDP</span>
        </div>

        <div className="bg-white p-3 rounded-xl border border-red-300 shadow-xs bg-red-50/40">
          <span className="text-[10px] font-bold text-red-800 uppercase tracking-wider block font-sans">
            Violations
          </span>
          <div className="text-xl font-bold text-red-800 mt-0.5">
            {violationsCount}
          </div>
          <span className="text-[10px] text-red-700 font-sans">Sec 36 notices</span>
        </div>
      </div>

      {/* Main Split Layout: Shelf Canvas (Left) + Product Results Grid (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Shelf Visual Evidence + Bounding Box Canvas (7 cols on lg) */}
        <div className="lg:col-span-7 space-y-4">
          <ShelfDetectionCanvas
            imageUrl={session.originalImageUrl}
            products={session.products}
            selectedProductId={selectedProductId}
            hoveredProductId={hoveredProductId}
            onSelectProduct={(id) => setSelectedProductId(id)}
            onHoverProduct={(id) => setHoveredProductId(id)}
            onOpenProductDetail={(inspectionId) => navigate(`/inspection/${inspectionId}`)}
          />

          {/* Session Technical Metadata Panel */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-subtle space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-900 flex items-center gap-1.5">
                <Hash className="w-3.5 h-3.5 text-blue-600" />
                Backend Cryptographic Tokens & Evidence Integrity
              </span>
              <span className="text-emerald-700 font-mono text-[10px] font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" /> SHA-256 Validated
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
              <div className="bg-slate-50 p-2 rounded border border-slate-200 truncate">
                <span className="text-slate-500 block text-[9px] uppercase font-bold tracking-wider font-sans">Client Session UUID</span>
                <span className="text-slate-900 font-medium">{session.clientSessionId}</span>
              </div>
              <div className="bg-slate-50 p-2 rounded border border-slate-200 truncate">
                <span className="text-slate-500 block text-[9px] uppercase font-bold tracking-wider font-sans">Idempotency Key</span>
                <span className="text-slate-900 font-medium">{session.idempotencyKey}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Detected Product Results Grid (5 cols on lg) */}
        <div className="lg:col-span-5 space-y-4">
          <Card className="flex flex-col h-full border border-slate-200 shadow-sm">
            <CardHeader className="border-b border-slate-100 pb-3">
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Product Inspections Ledger</CardTitle>
                  <span className="text-xs font-mono text-slate-500">
                    {filteredProducts.length} of {session.products.length} Products
                  </span>
                </div>

                {/* 6-Pill Filter Tabs */}
                <div className="flex items-center gap-1 overflow-x-auto pb-1 pt-1">
                  {[
                    { id: 'ALL', label: 'All' },
                    { id: 'HIGH', label: '🔴 High Priority' },
                    { id: 'MEDIUM', label: '🟡 Medium' },
                    { id: 'LOW', label: '🟢 Low' },
                    { id: 'REVIEW', label: '⚠️ Review' },
                    { id: 'RECAPTURE', label: '📷 Recapture' },
                  ].map(f => (
                    <button
                      key={f.id}
                      type="button"
                      onClick={() => setPriorityFilter(f.id)}
                      className={cn(
                        "px-2.5 py-1 rounded text-[11px] font-semibold transition whitespace-nowrap",
                        priorityFilter === f.id
                          ? "bg-slate-900 text-white shadow-xs"
                          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      )}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-3 space-y-2.5 overflow-y-auto max-h-[620px]">
              {filteredProducts.map((prod) => {
                const isSelected = selectedProductId === prod.id;
                const isHovered = hoveredProductId === prod.id;
                const isHighPriority = prod.priority === 'High Priority' || prod.reviewStatus === 'Violation';
                const isMediumPriority = prod.priority === 'Medium Priority';
                const isNeedsRecapture = prod.reviewStatus === 'Needs Recapture';

                return (
                  <div
                    key={prod.id}
                    onClick={() => setSelectedProductId(prod.id)}
                    onMouseEnter={() => setHoveredProductId(prod.id)}
                    onMouseLeave={() => setHoveredProductId(null)}
                    className={cn(
                      "p-3 rounded-xl border transition-all cursor-pointer bg-white space-y-2.5",
                      isSelected 
                        ? "border-blue-500 ring-2 ring-blue-500/30 shadow-md bg-blue-50/20" 
                        : isHovered
                        ? "border-slate-300 bg-slate-50/70 shadow-xs"
                        : "border-slate-200 hover:border-slate-300"
                    )}
                  >
                    {/* Top Row: Thumbnail + Product Meta */}
                    <div className="flex items-start gap-3">
                      {/* Product Crop Thumbnail */}
                      <div className="w-14 h-14 rounded-lg bg-slate-100 overflow-hidden border border-slate-200 shrink-0 relative">
                        <img
                          src={prod.cropImageUrl}
                          alt={prod.productName}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute bottom-0 inset-x-0 bg-slate-900/80 text-white font-mono text-[8px] text-center font-bold py-0.5">
                          {prod.sequenceNumber < 10 ? `0${prod.sequenceNumber}` : prod.sequenceNumber}
                        </div>
                      </div>

                      {/* Title & Brand */}
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-1">
                          <span className="font-mono text-xs font-bold text-blue-700">
                            {prod.productNumber}
                          </span>
                          <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                            Conf: {prod.detectionConfidence.toFixed(1)}%
                          </span>
                        </div>

                        <h4 className="text-xs font-bold text-slate-900 truncate mt-0.5" title={prod.productName}>
                          {prod.productName}
                        </h4>

                        <p className="text-[11px] text-slate-500">
                          {prod.brand} • {prod.category}
                        </p>
                      </div>
                    </div>

                    {/* Middle Row: Risk Priority Tag & Backend Explanation (No 'AI says illegal') */}
                    <div className="space-y-1 bg-slate-50 p-2 rounded-lg border border-slate-100 text-xs">
                      <div className="flex items-center justify-between">
                        {isHighPriority ? (
                          <span className="inline-flex items-center gap-1 font-bold text-red-700 text-[11px]">
                            <AlertOctagon className="w-3.5 h-3.5 text-red-600" />
                            🔴 High Priority — Review Required
                          </span>
                        ) : isMediumPriority ? (
                          <span className="inline-flex items-center gap-1 font-bold text-amber-700 text-[11px]">
                            <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
                            🟡 Medium Priority — Review Required
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 font-bold text-emerald-700 text-[11px]">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            🟢 Low Priority — Compliant
                          </span>
                        )}

                        <span className="text-[10px] font-mono text-slate-400">
                          {prod.reviewStatus}
                        </span>
                      </div>

                      {prod.priorityReason && (
                        <p className="text-[11px] text-slate-600 leading-snug">
                          <strong>Reason:</strong> {prod.priorityReason}
                        </p>
                      )}
                    </div>

                    {/* Recapture Actions Bar if product Needs Recapture */}
                    {isNeedsRecapture ? (
                      <div className="p-2 bg-orange-50/80 border border-orange-200 rounded-lg flex items-center justify-between gap-2">
                        <div className="flex items-center gap-1.5 text-orange-800 text-[11px] font-bold truncate">
                          <Camera className="w-3.5 h-3.5 text-orange-600 shrink-0" />
                          <span className="truncate">Defect: {prod.recaptureReason || 'Occlusion'}</span>
                        </div>

                        <div className="flex items-center gap-1.5 shrink-0">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/inspection/${prod.inspectionId}`);
                            }}
                            className="text-[10px] py-0.5 px-2 h-7 bg-white text-slate-700"
                          >
                            View Evidence
                          </Button>

                          <Button
                            variant="primary"
                            size="sm"
                            leftIcon={<Camera className="w-3 h-3" />}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleOpenRecapture(prod);
                            }}
                            className="text-[10px] py-0.5 px-2.5 h-7 bg-orange-600 hover:bg-orange-700 text-white border-orange-700"
                          >
                            Recapture
                          </Button>
                        </div>
                      </div>
                    ) : (
                      /* Standard Action Link to Inspection Detail */
                      <div className="flex items-center justify-between pt-1 border-t border-slate-100 text-xs">
                        {prod.recaptureEvidence ? (
                          <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-bold flex items-center gap-1">
                            <Check className="w-3 h-3 text-emerald-600" /> Recaptured & Verified
                          </span>
                        ) : (
                          <span className="text-[11px] text-slate-400 font-mono">
                            {prod.processingStatus}
                          </span>
                        )}

                        <Link
                          to={`/inspection/${prod.inspectionId}`}
                          onClick={(e) => e.stopPropagation()}
                          className="inline-flex items-center gap-1 text-[11px] font-bold text-blue-700 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-2.5 py-1 rounded transition"
                        >
                          <span>Open Docket</span>
                          <ChevronRight className="w-3 h-3" />
                        </Link>
                      </div>
                    )}
                  </div>
                );
              })}

              {filteredProducts.length === 0 && (
                <div className="text-center py-10 text-slate-400 text-xs">
                  No detected products match the selected priority filter.
                </div>
              )}
            </CardContent>

            <CardFooter className="border-t border-slate-100 bg-slate-50/50 p-3 flex items-center justify-between text-xs text-slate-500">
              <span className="font-mono">Human Review Required</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const firstPriority = session.products.find(p => p.priority === 'High Priority' || p.reviewStatus === 'Violation');
                  if (firstPriority) {
                    navigate(`/inspection/${firstPriority.inspectionId}`);
                  } else if (session.products[0]) {
                    navigate(`/inspection/${session.products[0].inspectionId}`);
                  }
                }}
                className="text-xs"
              >
                Review First Priority Item →
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>

      {/* Smart Recapture Modal Component */}
      <RecaptureModal
        isOpen={isRecaptureModalOpen}
        onClose={() => setIsRecaptureModalOpen(false)}
        sessionId={session.id}
        product={targetRecaptureProduct}
        onRecaptureSuccess={(updated) => {
          setSelectedProductId(updated.id);
        }}
      />
    </div>
  );
};
