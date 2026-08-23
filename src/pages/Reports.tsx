import React, { useState } from 'react';
import { useInspections } from '../context/InspectionContext';
import { useAuth } from '../context/AuthContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { Modal } from '../components/ui/Modal';
import { 
  FileText, 
  Download, 
  Printer, 
  Scale, 
  Building2, 
  AlertOctagon, 
  CheckCircle2, 
  Calendar, 
  DollarSign,
  ShieldCheck,
  Eye,
  FileSpreadsheet,
  FileCode,
  MapPin,
  Clock,
  Crop,
  Ruler,
  Hash,
  Layers,
  Camera,
  HelpCircle,
  Sparkles
} from 'lucide-react';
import { cn } from '../utils/cn';
import { NoticeOfViolation, Inspection, BatchInspectionSession } from '../types';

export const Reports: React.FC = () => {
  const { notices, inspections, batchSessions } = useInspections();
  const { user } = useAuth();

  const [activeReportTab, setActiveReportTab] = useState<'SINGLE' | 'BATCH' | 'NOTICES'>('BATCH');
  const [selectedInspectionForReport, setSelectedInspectionForReport] = useState<Inspection>(inspections[0]);
  const [selectedBatchSessionForReport, setSelectedBatchSessionForReport] = useState<BatchInspectionSession>(batchSessions[0]);
  const [selectedNotice, setSelectedNotice] = useState<NoticeOfViolation | null>(null);
  
  const [isSingleReportModalOpen, setIsSingleReportModalOpen] = useState(false);
  const [isBatchReportModalOpen, setIsBatchReportModalOpen] = useState(false);
  const [isApproved, setIsApproved] = useState(false);
  const [exportNotification, setExportNotification] = useState<string | null>(null);

  const triggerExport = (format: string, docName: string) => {
    setExportNotification(`Generating ${format} Dossier for ${docName}...`);
    setTimeout(() => {
      setExportNotification(null);
      if (format === 'PDF') {
        window.print();
      } else {
        alert(`${format} Inspection Evidence Dossier downloaded successfully!`);
      }
    }, 600);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Officer Inspection Reports & Judicial Dossiers
            </h1>
            <Badge variant="blue">Statutory Section 36 Dossiers</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Official inspection summaries, batch shelf dockets, Form LM-N1 compounding notices, and judicial evidence dossiers for Legal Metrology Courts
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<FileSpreadsheet className="w-4 h-4 text-emerald-600" />}
            onClick={() => triggerExport('CSV', activeReportTab === 'BATCH' ? selectedBatchSessionForReport.id : selectedInspectionForReport.id)}
          >
            Export CSV
          </Button>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<FileCode className="w-4 h-4 text-blue-600" />}
            onClick={() => triggerExport('DOCX', activeReportTab === 'BATCH' ? selectedBatchSessionForReport.id : selectedInspectionForReport.id)}
          >
            Export DOCX
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Printer className="w-4 h-4" />}
            onClick={() => {
              if (activeReportTab === 'BATCH') {
                setIsBatchReportModalOpen(true);
              } else {
                setIsSingleReportModalOpen(true);
              }
            }}
            className="bg-blue-700 hover:bg-blue-800"
          >
            Open Report Preview
          </Button>
        </div>
      </div>

      {/* Export Toast if active */}
      {exportNotification && (
        <div className="p-3 bg-blue-50 border border-blue-300 rounded-lg text-xs font-mono text-blue-900 flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-blue-600 animate-spin" />
          <span>{exportNotification}</span>
        </div>
      )}

      {/* Dossier Category Selector Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto text-xs">
        <button
          onClick={() => setActiveReportTab('BATCH')}
          className={cn(
            "px-4 py-2 rounded-lg font-bold transition flex items-center gap-2",
            activeReportTab === 'BATCH'
              ? "bg-slate-900 text-white shadow-xs"
              : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
          )}
        >
          <Layers className="w-3.5 h-3.5 text-indigo-400" />
          <span>Batch / Shelf Session Reports ({batchSessions.length})</span>
        </button>

        <button
          onClick={() => setActiveReportTab('SINGLE')}
          className={cn(
            "px-4 py-2 rounded-lg font-bold transition flex items-center gap-2",
            activeReportTab === 'SINGLE'
              ? "bg-slate-900 text-white shadow-xs"
              : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
          )}
        >
          <FileText className="w-3.5 h-3.5 text-blue-400" />
          <span>Single Product Dossiers ({inspections.length})</span>
        </button>

        <button
          onClick={() => setActiveReportTab('NOTICES')}
          className={cn(
            "px-4 py-2 rounded-lg font-bold transition flex items-center gap-2",
            activeReportTab === 'NOTICES'
              ? "bg-slate-900 text-white shadow-xs"
              : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
          )}
        >
          <AlertOctagon className="w-3.5 h-3.5 text-red-400" />
          <span>Registered Form LM-N1 Notices ({notices.length})</span>
        </button>
      </div>

      {/* VIEW 1: BATCH SESSION REPORTS */}
      {activeReportTab === 'BATCH' && (
        <Card className="border-t-4 border-t-indigo-700">
          <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <div>
              <CardTitle>Multi-Product Batch Shelf Inspection Dockets</CardTitle>
              <CardDescription>Comprehensive audit dossiers encompassing all detected shelf units</CardDescription>
            </div>
            <Badge variant="purple" className="font-mono">
              Active: {selectedBatchSessionForReport.id}
            </Badge>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
                  <tr>
                    <th className="py-2.5 px-4">Session ID</th>
                    <th className="py-2.5 px-3">Premises / Location</th>
                    <th className="py-2.5 px-3">Products</th>
                    <th className="py-2.5 px-3">Priority Breakdown</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {batchSessions.map((session) => {
                    const highCount = session.products.filter(p => p.priority === 'High Priority' || p.reviewStatus === 'Violation').length;
                    const reqCount = session.products.filter(p => p.reviewStatus === 'Review Required' || p.reviewStatus === 'Needs Recapture').length;
                    
                    return (
                      <tr 
                        key={session.id} 
                        className={cn(
                          "hover:bg-slate-50 transition-colors",
                          selectedBatchSessionForReport.id === session.id && "bg-indigo-50/40"
                        )}
                      >
                        <td className="py-3 px-4 font-mono font-bold text-indigo-700">
                          {session.id}
                          {session.isSeededDemo && (
                            <span className="block text-[10px] text-slate-400 font-sans font-normal">Seeded Demo</span>
                          )}
                        </td>
                        <td className="py-3 px-3 font-semibold text-slate-900">
                          <div>{session.locationName}</div>
                          <span className="text-[11px] text-slate-500 font-normal">{session.district}, {session.state}</span>
                        </td>
                        <td className="py-3 px-3 font-mono font-bold text-slate-900">
                          {session.totalProducts} Units
                        </td>
                        <td className="py-3 px-3 font-mono text-[11px]">
                          <div className="flex items-center gap-1.5">
                            {highCount > 0 && (
                              <span className="text-red-700 bg-red-50 px-1.5 py-0.5 rounded border border-red-200 font-bold">
                                {highCount} High
                              </span>
                            )}
                            {reqCount > 0 && (
                              <span className="text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200 font-bold">
                                {reqCount} Review
                              </span>
                            )}
                            <span className="text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                              {session.completedCount} Compliant
                            </span>
                          </div>
                        </td>
                        <td className="py-3 px-3">
                          <Badge variant={session.status === 'Complete' ? 'green' : 'blue'}>
                            {session.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedBatchSessionForReport(session);
                              setIsBatchReportModalOpen(true);
                            }}
                            className="h-7 text-xs px-2.5 text-indigo-700 border-indigo-200 hover:bg-indigo-50"
                          >
                            View Batch Report
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* VIEW 2: SINGLE PRODUCT INSPECTION REPORTS */}
      {activeReportTab === 'SINGLE' && (
        <Card className="border-t-4 border-t-blue-700">
          <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <div>
              <CardTitle>Single Product Statutory Compliance Dossiers</CardTitle>
              <CardDescription>Forensic font height, PDP calibration & Quiet-Zone determination reports</CardDescription>
            </div>
            <Badge variant="slate" className="font-mono">
              Active: {selectedInspectionForReport.id}
            </Badge>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
                  <tr>
                    <th className="py-2.5 px-4">Inspection ID</th>
                    <th className="py-2.5 px-3">Product / Commodity</th>
                    <th className="py-2.5 px-3">Brand</th>
                    <th className="py-2.5 px-3">Score</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-4 text-right">Report Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {inspections.map((insp) => (
                    <tr 
                      key={insp.id} 
                      className={cn(
                        "hover:bg-slate-50 transition-colors",
                        selectedInspectionForReport.id === insp.id && "bg-blue-50/40"
                      )}
                    >
                      <td className="py-3 px-4 font-mono font-bold text-blue-700">{insp.id}</td>
                      <td className="py-3 px-3 font-semibold text-slate-900">{insp.productName}</td>
                      <td className="py-3 px-3 text-slate-600">{insp.brand}</td>
                      <td className="py-3 px-3 font-mono font-bold">{insp.score}/100</td>
                      <td className="py-3 px-3"><StatusBadge status={insp.status} size="sm" /></td>
                      <td className="py-3 px-4 text-right">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedInspectionForReport(insp);
                            setIsSingleReportModalOpen(true);
                          }}
                          className="h-7 text-xs px-2.5"
                        >
                          View Dossier
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* VIEW 3: NOTICES & SUMMONS */}
      {activeReportTab === 'NOTICES' && (
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Registered Form LM-N1 Summons & Notices</CardTitle>
              <CardDescription>
                Offenses compounded or forwarded for court prosecution under Legal Metrology Act, 2009
              </CardDescription>
            </div>
          </CardHeader>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Notice ID</TableHead>
                <TableHead>Target Entity / Brand</TableHead>
                <TableHead>Governing Section</TableHead>
                <TableHead>Compounding Fee</TableHead>
                <TableHead>Issued Date</TableHead>
                <TableHead>Response Window</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {notices.map((n) => (
                <TableRow key={n.noticeId}>
                  <TableCell className="font-mono font-bold text-xs text-blue-700">
                    {n.noticeId}
                  </TableCell>
                  <TableCell>
                    <div className="font-bold text-slate-900 text-xs">{n.issuedToBrand}</div>
                    <div className="text-[11px] text-slate-500 truncate max-w-xs">{n.manufacturerAddress}</div>
                  </TableCell>
                  <TableCell className="text-xs max-w-xs truncate font-mono text-slate-700">
                    {n.section}
                  </TableCell>
                  <TableCell className="font-mono text-xs font-bold text-red-700">
                    ₹ {n.compoundingFeeInr.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-xs text-slate-500 font-mono">
                    {n.issueDate}
                  </TableCell>
                  <TableCell className="text-xs font-semibold text-amber-800">
                    {n.responseDeadline}
                  </TableCell>
                  <TableCell>
                    <Badge variant={n.status === 'Issued' ? 'red' : 'amber'}>
                      {n.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      leftIcon={<Eye className="w-3.5 h-3.5" />}
                      onClick={() => setSelectedNotice(n)}
                      className="text-xs h-7 px-2.5"
                    >
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      {/* =========================================================================
          BATCH INSPECTION SESSION REPORT MODAL PREVIEW
          ========================================================================= */}
      <Modal
        isOpen={isBatchReportModalOpen}
        onClose={() => setIsBatchReportModalOpen(false)}
        title="Multi-Product Batch Shelf Inspection Report"
        description="Comprehensive Statutory Audit Dossier • Legal Metrology Act, 2009"
        maxWidth="4xl"
        footer={
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-500">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>SHA-256 Multi-Product Certified Evidence</span>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => triggerExport('DOCX', selectedBatchSessionForReport.id)}>
                DOCX
              </Button>
              <Button variant="outline" size="sm" onClick={() => triggerExport('CSV', selectedBatchSessionForReport.id)}>
                CSV
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => triggerExport('PDF', selectedBatchSessionForReport.id)}
                leftIcon={<Printer className="w-4 h-4" />}
              >
                Generate PDF
              </Button>
              <Button
                variant={isApproved ? "success" : "primary"}
                size="sm"
                onClick={() => setIsApproved(true)}
                leftIcon={<CheckCircle2 className="w-4 h-4" />}
              >
                {isApproved ? 'Report Approved & Signed' : 'Approve & Sign Batch Report'}
              </Button>
            </div>
          </div>
        }
      >
        <div className="space-y-6 text-xs text-slate-800 font-sans p-2">
          {/* Government Official Header */}
          <div className="text-center space-y-1.5 border-b-2 border-slate-900 pb-4">
            <Scale className="w-10 h-10 mx-auto text-indigo-950" />
            <h2 className="text-base font-extrabold uppercase tracking-wide text-slate-950">
              Department of Legal Metrology • Government of Karnataka
            </h2>
            <p className="text-xs text-slate-700 font-semibold">
              OFFICIAL BATCH / SHELF SURVEILLANCE & PACKAGED COMMODITIES AUDIT REPORT
            </p>
            <p className="text-[10px] font-mono text-slate-500">
              Issued under Sections 15, 29 & 36 of Legal Metrology Act, 2009 read with PCR 2011
            </p>
          </div>

          {/* Session Overview Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-4 rounded-lg border border-slate-300 font-mono text-xs">
            <div>
              <span className="text-slate-500 text-[10px] uppercase block font-semibold font-sans">Session ID</span>
              <strong className="text-indigo-900 font-bold">{selectedBatchSessionForReport.id}</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase block font-semibold font-sans">Inspection Timestamp</span>
              <strong className="text-slate-900">{selectedBatchSessionForReport.createdAt}</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase block font-semibold font-sans">Surveillance Premises</span>
              <strong className="text-slate-900">{selectedBatchSessionForReport.locationName}</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase block font-semibold font-sans">Inspecting Authority</span>
              <strong className="text-slate-900">{selectedBatchSessionForReport.inspectorName}</strong>
            </div>
          </div>

          {/* Batch Metrics Summary Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 bg-indigo-50/50 p-3 rounded-lg border border-indigo-200 font-mono text-center">
            <div>
              <span className="text-[9px] uppercase font-bold text-slate-500 font-sans block">Total Products</span>
              <span className="text-base font-bold text-slate-900">{selectedBatchSessionForReport.totalProducts}</span>
            </div>
            <div>
              <span className="text-[9px] uppercase font-bold text-emerald-700 font-sans block">Compliant Units</span>
              <span className="text-base font-bold text-emerald-700">{selectedBatchSessionForReport.completedCount}</span>
            </div>
            <div>
              <span className="text-[9px] uppercase font-bold text-red-700 font-sans block">High Priority / Breaches</span>
              <span className="text-base font-bold text-red-700">
                {selectedBatchSessionForReport.products.filter(p => p.priority === 'High Priority' || p.reviewStatus === 'Violation').length}
              </span>
            </div>
            <div>
              <span className="text-[9px] uppercase font-bold text-amber-700 font-sans block">Review Required</span>
              <span className="text-base font-bold text-amber-700">{selectedBatchSessionForReport.reviewRequiredCount}</span>
            </div>
            <div>
              <span className="text-[9px] uppercase font-bold text-orange-700 font-sans block">Needs Recapture</span>
              <span className="text-base font-bold text-orange-700">{selectedBatchSessionForReport.needsRecaptureCount}</span>
            </div>
            <div>
              <span className="text-[9px] uppercase font-bold text-slate-500 font-sans block">Failed Units</span>
              <span className="text-base font-bold text-slate-900">{selectedBatchSessionForReport.failedCount}</span>
            </div>
          </div>

          {/* Master Shelf Visual Evidence */}
          <div className="border border-slate-200 rounded-lg p-3 bg-white space-y-2">
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-900 flex items-center justify-between">
              <span>Primary Master Shelf Photographic Evidence</span>
              <span className="font-mono text-[10px] text-slate-500 font-normal">
                Resolution: 1600 x 1067 px • SHA-256 Verified
              </span>
            </h4>
            <div className="relative rounded-lg overflow-hidden border border-slate-300 aspect-21/9 bg-slate-950 flex items-center justify-center">
              <img
                src={selectedBatchSessionForReport.originalImageUrl}
                alt="Master Shelf Capture"
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          {/* Itemized Detected Products Table */}
          <div className="space-y-2">
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-900">
              Itemized Product Determinations & Statutory Evaluation
            </h4>
            <div className="border border-slate-200 rounded-lg overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200">
                  <tr>
                    <th className="p-2.5">Item</th>
                    <th className="p-2.5">Product & Brand</th>
                    <th className="p-2.5">Category</th>
                    <th className="p-2.5">Confidence</th>
                    <th className="p-2.5">Priority & Status</th>
                    <th className="p-2.5">Officer / Rule Determination</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-[11px]">
                  {selectedBatchSessionForReport.products.map((prod) => (
                    <tr key={prod.id} className={cn(prod.priority === 'High Priority' && "bg-red-50/40")}>
                      <td className="p-2.5 font-mono font-bold text-blue-700">{prod.productNumber}</td>
                      <td className="p-2.5">
                        <div className="font-bold text-slate-900">{prod.productName}</div>
                        <div className="text-[10px] text-slate-500">Brand: {prod.brand}</div>
                      </td>
                      <td className="p-2.5 text-slate-600">{prod.category}</td>
                      <td className="p-2.5 font-mono font-bold">{prod.detectionConfidence.toFixed(1)}%</td>
                      <td className="p-2.5">
                        <span className={cn(
                          "px-2 py-0.5 rounded text-[10px] font-bold uppercase",
                          prod.priority === 'High Priority' || prod.reviewStatus === 'Violation'
                            ? "bg-red-100 text-red-800"
                            : prod.reviewStatus === 'Needs Recapture'
                            ? "bg-orange-100 text-orange-800"
                            : prod.reviewStatus === 'Review Required'
                            ? "bg-amber-100 text-amber-800"
                            : "bg-emerald-100 text-emerald-800"
                        )}>
                          {prod.priority}
                        </span>
                      </td>
                      <td className="p-2.5 text-slate-700 italic">
                        {prod.priorityReason || prod.notes || 'Compliant with Rule 6 & 7 requirements.'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Officer Digital Signature Block */}
          <div className="pt-4 border-t-2 border-slate-300 flex justify-between items-end">
            <div className="space-y-1">
              <span className="text-[10px] text-emerald-700 font-mono font-bold flex items-center gap-1">
                <ShieldCheck className="w-4 h-4" />
                Digitally Authenticated by LabelSetu National Metrology Engine
              </span>
              <p className="text-[10px] text-slate-500">
                Timestamp: {selectedBatchSessionForReport.createdAt} • Session ID: {selectedBatchSessionForReport.id}
              </p>
            </div>
            <div className="text-right space-y-0.5">
              <p className="font-bold text-slate-900 text-xs">{selectedBatchSessionForReport.inspectorName}</p>
              <p className="text-[11px] text-slate-600">Senior Inspector of Legal Metrology</p>
              <p className="text-[10px] font-mono text-slate-500">Badge ID: {selectedBatchSessionForReport.inspectorBadge}</p>
            </div>
          </div>
        </div>
      </Modal>

      {/* =========================================================================
          SINGLE PRODUCT INSPECTION REPORT MODAL PREVIEW
          ========================================================================= */}
      <Modal
        isOpen={isSingleReportModalOpen}
        onClose={() => setIsSingleReportModalOpen(false)}
        title="Official Legal Metrology Inspection Report"
        description="Statutory Compliance Dossier under Legal Metrology Act, 2009"
        maxWidth="4xl"
        footer={
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-500">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>SHA-256 Certified Evidence</span>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => triggerExport('DOCX', selectedInspectionForReport.id)}>
                DOCX
              </Button>
              <Button variant="outline" size="sm" onClick={() => triggerExport('CSV', selectedInspectionForReport.id)}>
                CSV
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => triggerExport('PDF', selectedInspectionForReport.id)}
                leftIcon={<Printer className="w-4 h-4" />}
              >
                Generate PDF
              </Button>
              <Button
                variant={isApproved ? "success" : "primary"}
                size="sm"
                onClick={() => setIsApproved(true)}
                leftIcon={<CheckCircle2 className="w-4 h-4" />}
              >
                {isApproved ? 'Report Approved & Signed' : 'Approve Report'}
              </Button>
            </div>
          </div>
        }
      >
        <div className="space-y-6 text-xs text-slate-800 font-sans p-2">
          {/* Government Official Header */}
          <div className="text-center space-y-1.5 border-b-2 border-slate-900 pb-4">
            <Scale className="w-10 h-10 mx-auto text-blue-950" />
            <h2 className="text-base font-extrabold uppercase tracking-wide text-slate-950">
              Department of Legal Metrology • Government of Karnataka
            </h2>
            <p className="text-xs text-slate-700 font-semibold">
              OFFICIAL STATUTORY INSPECTION & PACKAGING COMPLIANCE REPORT
            </p>
            <p className="text-[10px] font-mono text-slate-500">
              Under Legal Metrology (Packaged Commodities) Rules, 2011 • Standard: LM-PCR-2011-v2024.2
            </p>
          </div>

          {/* Inspection Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-4 rounded-lg border border-slate-300 font-mono text-xs">
            <div>
              <span className="text-slate-500 text-[10px] uppercase block font-semibold">Inspection ID</span>
              <strong className="text-slate-900 font-bold">{selectedInspectionForReport.id}</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase block font-semibold">Inspection Date</span>
              <strong className="text-slate-900">{selectedInspectionForReport.inspectionDate}</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase block font-semibold">Jurisdiction</span>
              <strong className="text-slate-900">{selectedInspectionForReport.district}</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase block font-semibold">Statutory Status</span>
              <StatusBadge status={selectedInspectionForReport.status} size="sm" />
            </div>
          </div>

          {/* Product & Entity Information */}
          <div className="border border-slate-200 rounded-lg p-4 space-y-2 bg-white">
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-900 border-b border-slate-100 pb-1">
              Package & Manufacturer Specifications
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <p><strong>Product Name:</strong> {selectedInspectionForReport.productName}</p>
                <p><strong>Brand Name:</strong> {selectedInspectionForReport.brand}</p>
                <p><strong>Category:</strong> {selectedInspectionForReport.category}</p>
                <p><strong>Packaging Type:</strong> {selectedInspectionForReport.packagingType}</p>
              </div>
              <div>
                <p><strong>Stated Net Quantity:</strong> {selectedInspectionForReport.netQuantity}</p>
                <p><strong>Maximum Retail Price:</strong> ₹ {selectedInspectionForReport.mrp.toFixed(2)}</p>
                <p><strong>Unit Sale Price:</strong> {selectedInspectionForReport.unitSalePrice || 'N/A'}</p>
                <p><strong>Manufacturer:</strong> {selectedInspectionForReport.manufacturerName}</p>
              </div>
            </div>
          </div>

          {/* Evidence Image & Calibration Proof */}
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-4">
            <div className="sm:col-span-5 bg-slate-950 rounded-lg overflow-hidden border border-slate-700 aspect-16/10 flex items-center justify-center p-2 relative">
              <img
                src={selectedInspectionForReport.sampleImage}
                alt="Evidence"
                className="max-h-full max-w-full object-contain rounded"
              />
              <div className="absolute top-2 left-2 bg-slate-900/90 text-white font-mono text-[9px] px-1.5 py-0.5 rounded border border-slate-700">
                Scale: {selectedInspectionForReport.calibration.pixelsPerMm.toFixed(1)} px/mm
              </div>
            </div>

            <div className="sm:col-span-7 space-y-2 bg-slate-50 p-4 rounded-lg border border-slate-200 font-mono text-xs">
              <h4 className="font-bold text-slate-900 font-sans uppercase tracking-wider text-[11px]">
                Optical Calibration & Judicial Integrity
              </h4>
              <div className="space-y-1 text-[11px]">
                <div>• Calibration Method: <strong>{selectedInspectionForReport.calibration.method}</strong></div>
                <div>• Reference Standard: <strong>ISO/IEC 7810 ID-1 Card (85.60 mm)</strong></div>
                <div>• Optical Precision: <strong>{selectedInspectionForReport.calibration.pixelsPerMm.toFixed(2)} px/mm</strong></div>
                <div>• Master Image SHA-256: <span className="text-slate-600 break-all">{selectedInspectionForReport.imageSha256}</span></div>
                <div>• GPS Location: <strong>{selectedInspectionForReport.gpsCoordinates?.locationName || 'Bengaluru APMC Zone'}</strong></div>
              </div>
            </div>
          </div>

          {/* Statutory Findings Matrix */}
          <div className="space-y-2">
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-900">
              Mandatory Clause-by-Clause Evaluation Matrix
            </h4>
            <div className="border border-slate-200 rounded-lg overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200">
                  <tr>
                    <th className="p-2.5">Clause</th>
                    <th className="p-2.5">Declaration Field</th>
                    <th className="p-2.5">Extracted Text</th>
                    <th className="p-2.5">Measured (mm)</th>
                    <th className="p-2.5">Required (mm)</th>
                    <th className="p-2.5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                  {selectedInspectionForReport.findings.map((f) => (
                    <tr key={f.id} className={cn(f.status === 'Fail' && "bg-red-50/50")}>
                      <td className="p-2.5 font-bold text-slate-800">{f.clause}</td>
                      <td className="p-2.5 font-sans">{f.field}</td>
                      <td className="p-2.5 text-slate-600">{f.extractedText}</td>
                      <td className="p-2.5 font-bold">{f.measuredHeightMm ? `${f.measuredHeightMm.toFixed(1)} mm` : 'N/A'}</td>
                      <td className="p-2.5 text-slate-500">{f.requiredHeightMm ? `${f.requiredHeightMm.toFixed(1)} mm` : 'N/A'}</td>
                      <td className="p-2.5">
                        <span className={cn(
                          "px-2 py-0.5 rounded text-[10px] font-bold uppercase",
                          f.status === 'Pass' ? "bg-emerald-100 text-emerald-800" : f.status === 'Fail' ? "bg-red-100 text-red-800" : "bg-amber-100 text-amber-800"
                        )}>
                          {f.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Officer Digital Signature Block */}
          <div className="pt-4 border-t-2 border-slate-300 flex justify-between items-end">
            <div className="space-y-1">
              <span className="text-[10px] text-emerald-700 font-mono font-bold flex items-center gap-1">
                <ShieldCheck className="w-4 h-4" />
                Digitally Authenticated by LabelSetu National Metrology Engine
              </span>
              <p className="text-[10px] text-slate-500">
                Timestamp: {selectedInspectionForReport.inspectionDate} • Session ID: {user.badgeNumber}
              </p>
            </div>
            <div className="text-right space-y-0.5">
              <p className="font-bold text-slate-900 text-xs">{selectedInspectionForReport.inspectorName}</p>
              <p className="text-[11px] text-slate-600">Senior Inspector of Legal Metrology</p>
              <p className="text-[10px] font-mono text-slate-500">Badge ID: {selectedInspectionForReport.inspectorBadge}</p>
            </div>
          </div>
        </div>
      </Modal>

      {/* =========================================================================
          NOTICE LM-N1 MODAL
          ========================================================================= */}
      {selectedNotice && (
        <Modal
          isOpen={!!selectedNotice}
          onClose={() => setSelectedNotice(null)}
          title="Form LM-N1 Statutory Notice"
          description="Legal Metrology Act, 2009 • Section 36(1) Compounding Summons"
          maxWidth="2xl"
          footer={
            <>
              <Button variant="outline" onClick={() => setSelectedNotice(null)}>
                Close
              </Button>
              <Button
                variant="primary"
                leftIcon={<Printer className="w-4 h-4" />}
                onClick={() => window.print()}
              >
                Print Notice
              </Button>
            </>
          }
        >
          <div className="border border-slate-300 rounded-lg p-6 bg-white space-y-5 text-xs text-slate-800 font-sans shadow-xs">
            <div className="text-center space-y-1 border-b border-slate-200 pb-4">
              <Scale className="w-8 h-8 mx-auto text-blue-950" />
              <h3 className="text-sm font-extrabold uppercase tracking-wide text-slate-950">
                Department of Legal Metrology • Government of Karnataka
              </h3>
              <p className="text-[10px] font-mono font-bold text-slate-500">
                FORM LM-N1 (SECTION 36 / RULE 32)
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between font-mono text-[11px]">
                <span>Notice Ref: <strong>{selectedNotice.noticeId}</strong></span>
                <span>Date: <strong>{selectedNotice.issueDate}</strong></span>
              </div>

              <div className="bg-slate-50 p-3 rounded border border-slate-200">
                <span className="text-slate-500 font-bold block text-[10px]">TO:</span>
                <p className="font-bold text-slate-900 text-xs">{selectedNotice.issuedToBrand}</p>
                <p className="text-slate-600 text-[11px]">{selectedNotice.manufacturerAddress}</p>
              </div>

              <div className="p-3 bg-red-50 rounded border border-red-200 text-red-900 space-y-1">
                <strong className="block font-bold">Detected Statutory Contraventions:</strong>
                <ul className="list-disc pl-4 space-y-1">
                  {selectedNotice.ruleBreaches.map((b, idx) => (
                    <li key={idx} className="font-medium">{b}</li>
                  ))}
                </ul>
              </div>

              <p className="leading-relaxed">
                Compounding fee assessed under Section 49: <strong>₹ {selectedNotice.compoundingFeeInr.toLocaleString()} INR</strong> within <strong>{selectedNotice.responseDeadline}</strong>.
              </p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
