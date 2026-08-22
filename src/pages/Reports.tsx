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
  Hash
} from 'lucide-react';
import { cn } from '../utils/cn';
import { NoticeOfViolation, Inspection } from '../types';

export const Reports: React.FC = () => {
  const { notices, inspections } = useInspections();
  const { user } = useAuth();

  const [selectedInspectionForReport, setSelectedInspectionForReport] = useState<Inspection>(inspections[0]);
  const [selectedNotice, setSelectedNotice] = useState<NoticeOfViolation | null>(null);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [isApproved, setIsApproved] = useState(false);
  const [exportNotification, setExportNotification] = useState<string | null>(null);

  const triggerExport = (format: string) => {
    setExportNotification(`Generating ${format} Dossier for ${selectedInspectionForReport.id}...`);
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
            Official inspection summaries, Form LM-N1 compounding notices, and judicial evidence dossiers for Legal Metrology Courts
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<FileSpreadsheet className="w-4 h-4 text-emerald-600" />}
            onClick={() => triggerExport('CSV')}
          >
            Export CSV
          </Button>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<FileCode className="w-4 h-4 text-blue-600" />}
            onClick={() => triggerExport('DOCX')}
          >
            Export DOCX
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Printer className="w-4 h-4" />}
            onClick={() => {
              setIsReportModalOpen(true);
            }}
            className="bg-blue-700 hover:bg-blue-800"
          >
            Open Officer Report Preview
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

      {/* Select Target Inspection for Report Preview */}
      <Card className="border-t-4 border-t-blue-700">
        <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <CardTitle>Select Inspection Record for Official Report Dossier</CardTitle>
            <CardDescription>Generated under Legal Metrology Act, 2009 & PCR 2011</CardDescription>
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
                      <div className="flex items-center justify-end gap-1.5">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedInspectionForReport(insp);
                            setIsReportModalOpen(true);
                          }}
                          className="h-7 text-xs px-2.5"
                        >
                          View Dossier
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Issued Notices Table */}
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

      {/* Complete Officer Report Preview Modal */}
      <Modal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
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
              <Button variant="outline" size="sm" onClick={() => triggerExport('DOCX')}>
                DOCX
              </Button>
              <Button variant="outline" size="sm" onClick={() => triggerExport('CSV')}>
                CSV
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => triggerExport('PDF')}
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

      {/* Notice LM-N1 Modal */}
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
