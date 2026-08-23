import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useInspections } from '../context/InspectionContext';
import { useAuth } from '../context/AuthContext';
import { 
  Inspection, 
  InspectionStatus, 
  DeclarationFinding, 
  FindingActionType 
} from '../types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Breadcrumbs } from '../components/ui/Breadcrumbs';
import { MeasurementOverlay } from '../components/inspection/MeasurementOverlay';
import { EvidenceDrawer } from '../components/inspection/EvidenceDrawer';
import { FindingActionModal } from '../components/inspection/FindingActionModal';
import { RuleTraceabilityCard } from '../components/inspection/RuleTraceabilityCard';
import { 
  ShieldCheck, 
  Ruler, 
  FileText, 
  Edit3, 
  AlertOctagon, 
  CheckCircle2, 
  ExternalLink, 
  Download, 
  Building2, 
  Clock, 
  AlertTriangle,
  Scale,
  Sparkles,
  Layers,
  ZoomIn,
  ZoomOut,
  Sliders,
  Crop,
  ShieldAlert,
  Printer,
  ChevronRight,
  ArrowRight
} from 'lucide-react';
import { cn } from '../utils/cn';

export const InspectionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { inspections, batchSessions, updateInspectionStatus, generateNotice } = useInspections();
  const { user } = useAuth();
  const navigate = useNavigate();

  // Find target or default to Case 2 (Fortune Sunlite 500g)
  const currentId = id || 'INS-2026-0518-1123';
  const inspection = inspections.find(
    i => i.id.toLowerCase() === currentId.toLowerCase()
  ) || inspections[0];

  const parentSession = batchSessions?.find(
    s => s.products.some(p => p.inspectionId.toLowerCase() === inspection?.id?.toLowerCase())
  );

  // Workstation Interactive Controls
  const [selectedFindingId, setSelectedFindingId] = useState<string | null>(
    inspection?.findings[0]?.id || null
  );
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [showPdpBoundary, setShowPdpBoundary] = useState<boolean>(true);
  const [showQuietZone, setShowQuietZone] = useState<boolean>(true);
  const [showCalipers, setShowCalipers] = useState<boolean>(true);
  const [showBBoxes, setShowBBoxes] = useState<boolean>(true);
  const [contrastFilter, setContrastFilter] = useState<boolean>(false);

  // Evidence Drawer & Action Modals
  const [isEvidenceDrawerOpen, setIsEvidenceDrawerOpen] = useState<boolean>(false);
  const [activeFindingForDrawer, setActiveFindingForDrawer] = useState<DeclarationFinding | null>(null);

  const [isActionModalOpen, setIsActionModalOpen] = useState<boolean>(false);
  const [actionModalType, setActionModalType] = useState<FindingActionType>('Approve');
  const [actionModalFinding, setActionModalFinding] = useState<DeclarationFinding | null>(null);

  // Notice Generation
  const [noticeGeneratedMessage, setNoticeGeneratedMessage] = useState<string | null>(null);

  if (!inspection) {
    return (
      <div className="text-center py-16 space-y-4">
        <h2 className="text-xl font-bold text-slate-800">Inspection Record Not Found</h2>
        <Button variant="primary" onClick={() => navigate('/dashboard')}>
          Back to Command Center
        </Button>
      </div>
    );
  }

  const selectedFinding = inspection.findings.find(f => f.id === selectedFindingId) || inspection.findings[0];

  const handleSelectFindingFromCanvas = (findingId: string) => {
    setSelectedFindingId(findingId);
    const target = inspection.findings.find(f => f.id === findingId);
    if (target) {
      setActiveFindingForDrawer(target);
      setIsEvidenceDrawerOpen(true);
    }
  };

  const handleOpenEvidenceDrawer = (finding: DeclarationFinding) => {
    setSelectedFindingId(finding.id);
    setActiveFindingForDrawer(finding);
    setIsEvidenceDrawerOpen(true);
  };

  const handleOpenActionModal = (finding: DeclarationFinding, action: FindingActionType) => {
    setActionModalFinding(finding);
    setActionModalType(action);
    setIsActionModalOpen(true);
  };

  const handleConfirmFindingAction = (
    findingId: string, 
    action: FindingActionType, 
    note: string, 
    correctedMm?: number
  ) => {
    const updatedFindings = inspection.findings.map(f => {
      if (f.id === findingId) {
        return {
          ...f,
          measuredHeightMm: correctedMm || f.measuredHeightMm,
          officerDecision: {
            action,
            officer: user.name,
            timestamp: new Date().toLocaleTimeString(),
            overrideNote: note,
            correctedHeightMm: correctedMm,
          }
        };
      }
      return f;
    });

    inspection.findings = updatedFindings;
  };

  const handleIssueNotice = () => {
    const breaches = inspection.findings
      .filter(f => f.status === 'Fail')
      .map(f => `${f.field}: ${f.notes || f.quietZoneOverlapReason || 'Statutory Defect'}`);

    const notice = generateNotice(inspection.id, breaches, 25000);
    setNoticeGeneratedMessage(`Form LM-N1 Notice (${notice.noticeId}) successfully dispatched under Section 36(1)`);
  };

  return (
    <div className="space-y-5 max-w-[1600px] mx-auto">
      {/* Top Breadcrumb & Demo Case Switcher */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3 bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs">
        <div className="flex items-center gap-3">
          <Breadcrumbs
            items={parentSession ? [
              { label: 'Command Center', href: '/dashboard' },
              { label: `Batch Session ${parentSession.id}`, href: `/inspection/session/${parentSession.id}` },
              { label: inspection.id },
            ] : [
              { label: 'Officer Command', href: '/dashboard' },
              { label: 'Inspection Workstation' },
              { label: inspection.id },
            ]}
          />
          {parentSession && (
            <Link
              to={`/inspection/session/${parentSession.id}`}
              className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 px-2 py-0.5 rounded border border-indigo-200 transition"
            >
              <Layers className="w-3 h-3 text-indigo-600" />
              <span>← Back to Batch {parentSession.id}</span>
            </Link>
          )}
        </div>

        {/* Quick Demo Case Selector Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
          <span className="font-bold text-slate-500 text-[10px] uppercase tracking-wider shrink-0 mr-1">
            Demo Cases:
          </span>
          {[
            { id: 'INS-2026-0518-1123', label: 'Case 2: 500g Violation (Primary)', badge: '62/100', color: 'border-red-500 bg-red-50 text-red-900 font-bold' },
            { id: 'INSP-2026-0814', label: 'Case 1: 100g Verified', badge: '96/100', color: 'border-emerald-500 bg-emerald-50 text-emerald-900 font-bold' },
            { id: 'INSP-2026-0803', label: 'Case 3: Glare Uncertain', badge: '58/100', color: 'border-amber-500 bg-amber-50 text-amber-900 font-bold' },
            { id: 'INSP-2026-0798', label: 'Case 4: E-Commerce Rule 6(10)', badge: '51/100', color: 'border-blue-500 bg-blue-50 text-blue-900 font-bold' },
          ].map((c) => {
            const isMatch = inspection.id.toLowerCase() === c.id.toLowerCase();
            return (
              <button
                key={c.id}
                onClick={() => navigate(`/inspection/${c.id}`)}
                className={cn(
                  "px-2.5 py-1 rounded-md border text-xs whitespace-nowrap transition-all flex items-center gap-1.5",
                  isMatch
                    ? cn("ring-2 ring-blue-600 shadow-xs", c.color)
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                )}
              >
                <span>{c.label}</span>
                <span className="text-[10px] font-mono font-bold opacity-80">({c.badge})</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Split-Screen Workstation Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        
        {/* =========================================================================
            LEFT SIDE (LARGE INTERACTIVE PACKAGE IMAGE & MEASUREMENT GEOMETRY)
            ========================================================================= */}
        <div className="xl:col-span-7 space-y-4">
          <Card className="overflow-hidden border-2 border-slate-300 shadow-elevated">
            
            {/* Workstation Top Control Bar */}
            <div className="bg-slate-950 px-4 py-3 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-300">
              <div className="flex items-center gap-2.5">
                <span className="font-mono font-bold text-white bg-blue-900 px-2 py-0.5 rounded border border-blue-700">
                  {inspection.id}
                </span>
                <span className="text-slate-400 font-medium truncate max-w-[200px]">{inspection.productName}</span>
              </div>

              {/* Layer & Caliper View Controls */}
              <div className="flex items-center gap-2">
                <div className="flex items-center bg-slate-900 rounded p-0.5 border border-slate-800">
                  <button
                    onClick={() => setZoomLevel(prev => Math.max(50, prev - 20))}
                    className="p-1 rounded hover:bg-slate-800 text-slate-300"
                    title="Zoom Out"
                  >
                    <ZoomOut className="w-3.5 h-3.5" />
                  </button>
                  <span className="px-1.5 text-[10px] font-mono text-slate-400">{zoomLevel}%</span>
                  <button
                    onClick={() => setZoomLevel(prev => Math.min(200, prev + 20))}
                    className="p-1 rounded hover:bg-slate-800 text-slate-300"
                    title="Zoom In"
                  >
                    <ZoomIn className="w-3.5 h-3.5" />
                  </button>
                </div>

                <Button
                  variant={showPdpBoundary ? "secondary" : "outline"}
                  size="sm"
                  onClick={() => setShowPdpBoundary(!showPdpBoundary)}
                  className="text-[11px] h-7 px-2"
                >
                  PDP Box
                </Button>

                <Button
                  variant={showQuietZone ? "secondary" : "outline"}
                  size="sm"
                  onClick={() => setShowQuietZone(!showQuietZone)}
                  className="text-[11px] h-7 px-2"
                >
                  Quiet Zone
                </Button>

                <Button
                  variant={showCalipers ? "secondary" : "outline"}
                  size="sm"
                  onClick={() => setShowCalipers(!showCalipers)}
                  className="text-[11px] h-7 px-2"
                >
                  Calipers
                </Button>
              </div>
            </div>

            {/* Interactive Package Canvas */}
            <div className="min-h-[520px] bg-slate-950">
              <MeasurementOverlay
                imageUrl={inspection.sampleImage}
                findings={inspection.findings}
                calibration={inspection.calibration}
                pdpAreaCm2={inspection.pdpAreaCm2}
                selectedFindingId={selectedFindingId}
                onSelectFinding={handleSelectFindingFromCanvas}
                showPdpBoundary={showPdpBoundary}
                showQuietZone={showQuietZone}
                showCalipers={showCalipers}
                showBBoxes={showBBoxes}
                contrastFilter={contrastFilter}
                zoom={zoomLevel}
              />
            </div>

            {/* Workstation Canvas Footer Bar */}
            <div className="bg-slate-900 px-4 py-2.5 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
              <div className="flex items-center gap-3 font-mono text-[11px]">
                <span className="text-emerald-400 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Scale: {inspection.calibration.pixelsPerMm.toFixed(2)} px/mm
                </span>
                <span>•</span>
                <span>Target: {inspection.statedWeightGramsOrMl}g Category</span>
                <span>•</span>
                <span>Rule 7(2)(i) Table I</span>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/evidence/${inspection.id}`)}
                  leftIcon={<Ruler className="w-3.5 h-3.5 text-blue-400" />}
                  className="text-[11px] h-7 px-2.5 bg-slate-800 text-white border-slate-700 hover:bg-slate-700"
                >
                  Full Forensic Studio
                </Button>
              </div>
            </div>
          </Card>

          {/* Rule Traceability Engine Banner */}
          <RuleTraceabilityCard />
        </div>

        {/* =========================================================================
            RIGHT SIDE (INSPECTION FINDINGS, SCORE CARD & ACTION DOCKET)
            ========================================================================= */}
        <div className="xl:col-span-5 space-y-4">
          
          {/* Professional Compliance Score Card */}
          <Card className="border-t-4 border-t-blue-700 bg-white">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500">Inspection Review</h2>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="font-mono text-base font-extrabold text-slate-900">{inspection.id}</span>
                    <StatusBadge status={inspection.status} size="md" />
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Compliance Score</span>
                  <div className="flex items-baseline gap-1 justify-end">
                    <span className={cn(
                      "text-2xl font-extrabold font-mono",
                      inspection.score >= 85 ? "text-emerald-700" : inspection.score >= 60 ? "text-amber-600" : "text-red-700"
                    )}>
                      {inspection.score}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">/ 100</span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-semibold block">
                    {inspection.status === 'Verified' ? 'Fully Compliant' : 'Provisional Non-Compliance'}
                  </span>
                </div>
              </div>
            </CardHeader>

            {/* Score Breakdown Pill Counters */}
            <CardContent className="pt-0 pb-4">
              <div className="grid grid-cols-4 gap-2 pt-2 border-t border-slate-100 font-mono text-center">
                <div className="p-2 rounded-lg bg-red-50 border border-red-200">
                  <span className="text-[9px] uppercase font-bold text-red-700 block">Critical</span>
                  <span className="text-base font-bold text-red-800">
                    {inspection.scoreBreakdown?.criticalViolations || (inspection.status === 'Violation' ? 1 : 0)}
                  </span>
                </div>
                <div className="p-2 rounded-lg bg-amber-50 border border-amber-200">
                  <span className="text-[9px] uppercase font-bold text-amber-700 block">Major</span>
                  <span className="text-base font-bold text-amber-800">
                    {inspection.scoreBreakdown?.majorViolations || (inspection.status === 'Violation' ? 1 : 0)}
                  </span>
                </div>
                <div className="p-2 rounded-lg bg-blue-50 border border-blue-200">
                  <span className="text-[9px] uppercase font-bold text-blue-700 block">Minor</span>
                  <span className="text-base font-bold text-blue-800">
                    {inspection.scoreBreakdown?.minorWarnings || 0}
                  </span>
                </div>
                <div className="p-2 rounded-lg bg-emerald-50 border border-emerald-200">
                  <span className="text-[9px] uppercase font-bold text-emerald-700 block">Verified</span>
                  <span className="text-base font-bold text-emerald-800">
                    {inspection.scoreBreakdown?.verifiedCount || 4}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Notice Feedback Banner if Generated */}
          {noticeGeneratedMessage && (
            <div className="p-3 bg-emerald-50 border border-emerald-300 rounded-lg flex items-center justify-between gap-2 text-xs text-emerald-950 animate-in fade-in duration-200">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>{noticeGeneratedMessage}</span>
              </div>
              <Button size="sm" variant="outline" onClick={() => navigate('/reports')}>
                View Notice
              </Button>
            </div>
          )}

          {/* Interactive Findings List */}
          <Card>
            <CardHeader className="pb-3 flex items-center justify-between">
              <div>
                <CardTitle>Mandatory Statutory Declarations</CardTitle>
                <CardDescription>Click a finding to inspect traceable optical crop & rule logic</CardDescription>
              </div>
              <Badge variant="slate" className="font-mono">{inspection.findings.length} Declarations</Badge>
            </CardHeader>

            <CardContent className="space-y-3 p-4">
              {inspection.findings.map((finding) => {
                const isSelected = selectedFindingId === finding.id;
                const isViolation = finding.status === 'Fail';
                const isReview = finding.status === 'Review Required' || finding.status === 'Warning';
                const isPass = finding.status === 'Pass';

                return (
                  <div
                    key={finding.id}
                    onClick={() => {
                      setSelectedFindingId(finding.id);
                    }}
                    className={cn(
                      "p-3.5 rounded-xl border transition-all cursor-pointer space-y-2.5",
                      isSelected
                        ? "border-blue-600 ring-2 ring-blue-500 shadow-md bg-blue-50/30"
                        : "border-slate-200 hover:border-slate-300 hover:bg-slate-50/60 bg-white"
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono font-bold text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.2 rounded border border-slate-200">
                            {finding.clause}
                          </span>
                          <h4 className="font-bold text-xs text-slate-900">{finding.field}</h4>
                        </div>
                        <p className="text-[11px] font-mono text-slate-600">
                          {finding.extractedText}
                        </p>
                      </div>

                      <div className="flex items-center gap-1 shrink-0">
                        {isViolation && <Badge variant="red">Violation</Badge>}
                        {isReview && <Badge variant="amber">Review Req.</Badge>}
                        {isPass && <Badge variant="green">Verified</Badge>}
                      </div>
                    </div>

                    {/* Calibrated Metric Measurements */}
                    {finding.measuredHeightMm && (
                      <div className="p-2 bg-slate-50 rounded-md border border-slate-200/80 flex items-center justify-between text-xs font-mono">
                        <div>
                          <span className="text-slate-500 text-[10px] uppercase block">Measured</span>
                          <span className={cn(
                            "font-bold",
                            finding.requiredHeightMm && finding.measuredHeightMm < finding.requiredHeightMm ? "text-red-700 font-bold" : "text-emerald-700 font-bold"
                          )}>
                            {finding.measuredHeightMm.toFixed(1)} mm
                          </span>
                        </div>

                        <div>
                          <span className="text-slate-500 text-[10px] uppercase block">Required</span>
                          <span className="font-bold text-slate-800">
                            {finding.requiredHeightMm?.toFixed(1)} mm
                          </span>
                        </div>

                        <div>
                          <span className="text-slate-500 text-[10px] uppercase block">Confidence</span>
                          <span className="font-bold text-blue-700">{finding.ocrConfidence}%</span>
                        </div>
                      </div>
                    )}

                    {/* Quiet Zone Collision Note if present */}
                    {finding.quietZoneCleared === false && (
                      <div className="p-2 bg-red-100/60 border border-red-300 rounded text-[11px] text-red-950 flex items-start gap-1.5">
                        <ShieldAlert className="w-3.5 h-3.5 text-red-600 shrink-0 mt-0.5" />
                        <span>Collision: Background border encroaches on 2x letter height buffer.</span>
                      </div>
                    )}

                    {/* Officer Action Log if recorded */}
                    {finding.officerDecision && (
                      <div className="p-2 bg-purple-50 border border-purple-200 rounded text-[10px] text-purple-900 font-mono flex items-center justify-between">
                        <span>Action: <strong>{finding.officerDecision.action}</strong> by {finding.officerDecision.officer}</span>
                        <span className="text-purple-600">{finding.officerDecision.timestamp}</span>
                      </div>
                    )}

                    {/* Interactive Action Toolbar for this Finding */}
                    <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-100">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenEvidenceDrawer(finding);
                        }}
                        className="text-[11px] font-semibold text-blue-700 hover:text-blue-900 flex items-center gap-1"
                      >
                        <Crop className="w-3 h-3" />
                        <span>Inspect Evidence Crop</span>
                      </button>

                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenActionModal(finding, 'Correct');
                          }}
                          className="h-6 px-2 text-[10px]"
                          title="Correct manual millimeter measurement"
                        >
                          Correct
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenActionModal(finding, 'ReviewRequired');
                          }}
                          className="h-6 px-2 text-[10px] text-amber-700"
                        >
                          Review
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenActionModal(finding, 'Approve');
                          }}
                          className="h-6 px-2 text-[10px]"
                        >
                          Approve
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </CardContent>

            <CardFooter className="flex items-center justify-between bg-slate-50 p-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/history')}
              >
                Back to Ledger
              </Button>

              {inspection.status === 'Violation' && (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleIssueNotice}
                  leftIcon={<AlertOctagon className="w-4 h-4" />}
                >
                  Issue Form LM-N1 Notice
                </Button>
              )}
            </CardFooter>
          </Card>
        </div>
      </div>

      {/* Traceable Evidence Drawer */}
      <EvidenceDrawer
        isOpen={isEvidenceDrawerOpen}
        onClose={() => setIsEvidenceDrawerOpen(false)}
        finding={activeFindingForDrawer}
        inspection={inspection}
        onActionClick={(f, act) => {
          setIsEvidenceDrawerOpen(false);
          handleOpenActionModal(f, act);
        }}
      />

      {/* Interactive Finding Action Modal */}
      <FindingActionModal
        isOpen={isActionModalOpen}
        onClose={() => setIsActionModalOpen(false)}
        finding={actionModalFinding}
        actionType={actionModalType}
        onConfirm={handleConfirmFindingAction}
      />
    </div>
  );
};
