import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { DeclarationFinding, FindingActionType } from '../../types';
import { CheckCircle2, XCircle, AlertTriangle, Edit3, Camera, ShieldCheck } from 'lucide-react';
import { cn } from '../../utils/cn';

interface FindingActionModalProps {
  isOpen: boolean;
  onClose: () => void;
  finding: DeclarationFinding | null;
  actionType: FindingActionType;
  onConfirm: (findingId: string, action: FindingActionType, note: string, correctedMm?: number) => void;
}

export const FindingActionModal: React.FC<FindingActionModalProps> = ({
  isOpen,
  onClose,
  finding,
  actionType,
  onConfirm,
}) => {
  if (!finding) return null;

  const [officerNote, setOfficerNote] = useState<string>('');
  const [correctedMm, setCorrectedMm] = useState<number>(finding.measuredHeightMm || 4.0);

  const getActionConfig = () => {
    switch (actionType) {
      case 'Approve':
        return {
          title: finding.status === 'Fail' ? 'Confirm Statutory Violation' : 'Approve Statutory Compliance',
          description: `Formal signing of ${finding.field} evaluation under Legal Metrology Act`,
          buttonVariant: finding.status === 'Fail' ? ('danger' as const) : ('success' as const),
          buttonText: finding.status === 'Fail' ? 'Sign Violation Notice' : 'Approve Declaration',
          icon: <CheckCircle2 className="w-5 h-5 text-emerald-600" />,
          defaultNote: `Verified compliant with ${finding.clause} standards.`,
        };
      case 'Correct':
        return {
          title: 'Manual Measurement Correction',
          description: 'Override optical caliper measurement with verified physical steel rule reading',
          buttonVariant: 'primary' as const,
          buttonText: 'Save Corrected Measurement',
          icon: <Edit3 className="w-5 h-5 text-blue-600" />,
          defaultNote: 'Physical measurement with calibrated 0.1mm steel rule verified.',
        };
      case 'Reject':
        return {
          title: 'Reject Finding (False Detection)',
          description: 'Dismiss AI finding as image artifact or non-statutory element',
          buttonVariant: 'danger' as const,
          buttonText: 'Reject Finding',
          icon: <XCircle className="w-5 h-5 text-red-600" />,
          defaultNote: 'Dismissed: Background decorative artwork misidentified as text.',
        };
      case 'ReviewRequired':
        return {
          title: 'Flag for Physical Review',
          description: 'Escalate to reviewing authority for physical sample inspection',
          buttonVariant: 'outline' as const,
          buttonText: 'Escalate for Review',
          icon: <AlertTriangle className="w-5 h-5 text-amber-600" />,
          defaultNote: 'Low optical confidence / specular reflection requires physical verification.',
        };
      case 'Recapture':
        return {
          title: 'Request Evidence Recapture',
          description: 'Instruct field officer to re-photograph package with ISO calibration card',
          buttonVariant: 'primary' as const,
          buttonText: 'Dispatch Recapture Ticket',
          icon: <Camera className="w-5 h-5 text-blue-600" />,
          defaultNote: 'Recapture requested: Diffuse lighting and ISO 7810 calibration target required.',
        };
    }
  };

  const config = getActionConfig();

  const handleConfirm = (e: React.FormEvent) => {
    e.preventDefault();
    onConfirm(finding.id, actionType, officerNote || config.defaultNote, actionType === 'Correct' ? correctedMm : undefined);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div className="flex items-center gap-2">
          {config.icon}
          <span>{config.title}</span>
        </div>
      }
      description={config.description}
      footer={
        <>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant={config.buttonVariant} onClick={handleConfirm}>
            {config.buttonText}
          </Button>
        </>
      }
    >
      <form onSubmit={handleConfirm} className="space-y-4 text-xs">
        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 space-y-1 font-mono">
          <div className="flex justify-between">
            <span className="text-slate-500">Field:</span>
            <span className="font-bold text-slate-900">{finding.field}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Statutory Clause:</span>
            <span className="font-bold text-blue-700">{finding.clause}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Extracted Text:</span>
            <span className="text-slate-900">{finding.extractedText}</span>
          </div>
        </div>

        {actionType === 'Correct' && (
          <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-lg space-y-3">
            <label className="text-xs font-bold uppercase tracking-wider text-blue-900 block">
              Physical Numeral Font Height (in Millimeters)
            </label>
            <Input
              type="number"
              step="0.1"
              value={correctedMm}
              onChange={(e) => setCorrectedMm(Number(e.target.value))}
              helperText={`Statutory requirement: ${finding.requiredHeightMm || 4.0} mm`}
            />
          </div>
        )}

        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
            Officer Statutory Note & Audit Justification
          </label>
          <textarea
            rows={3}
            value={officerNote}
            onChange={(e) => setOfficerNote(e.target.value)}
            placeholder={config.defaultNote}
            className="w-full text-xs p-3 rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none"
          />
        </div>

        <div className="p-2.5 bg-slate-100 rounded border border-slate-200 text-[11px] text-slate-600 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Action recorded with officer digital signature in the tamper-proof audit log.</span>
        </div>
      </form>
    </Modal>
  );
};
