import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  Inspection, 
  InspectionStatus, 
  OfflineQueueItem, 
  NoticeOfViolation,
  BatchInspectionSession,
  BatchSessionStatus 
} from '../types';
import { mockInspections, mockOfflineQueue, mockNotices, mockBatchSessions } from '../data/mockData';

interface InspectionContextType {
  inspections: Inspection[];
  batchSessions: BatchInspectionSession[];
  offlineQueue: OfflineQueueItem[];
  notices: NoticeOfViolation[];
  getInspectionById: (id: string) => Inspection | undefined;
  getBatchSessionById: (id: string) => BatchInspectionSession | undefined;
  addInspection: (newInspection: Inspection) => void;
  addBatchSession: (newSession: BatchInspectionSession) => void;
  updateInspectionStatus: (id: string, status: InspectionStatus, reason?: string, officerName?: string) => void;
  updateBatchSessionStatus: (id: string, status: BatchSessionStatus) => void;
  recaptureBatchProduct: (sessionId: string, productId: string, newCropUrl: string, notes?: string) => void;
  retryFailedBatchProducts: (sessionId: string) => void;
  syncOfflineItem: (id: string) => void;
  syncAllOffline: () => void;
  generateNotice: (inspectionId: string, ruleBreaches: string[], penaltyInr: number) => NoticeOfViolation;
  selectedDistrict: string;
  setSelectedDistrict: (district: string) => void;
}

const InspectionContext = createContext<InspectionContextType | undefined>(undefined);

export const InspectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [inspections, setInspections] = useState<Inspection[]>(() => {
    const saved = localStorage.getItem('labelsetu_inspections');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        // Ensure new mock cases are also accessible
        const missing = mockInspections.filter(m => !parsed.some((p: Inspection) => p.id === m.id));
        return [...parsed, ...missing];
      } catch (e) {
        return mockInspections;
      }
    }
    return mockInspections;
  });

  const [batchSessions, setBatchSessions] = useState<BatchInspectionSession[]>(() => {
    const saved = localStorage.getItem('labelsetu_batch_sessions');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        const missing = mockBatchSessions.filter(m => !parsed.some((p: BatchInspectionSession) => p.id === m.id));
        return [...parsed, ...missing];
      } catch (e) {
        return mockBatchSessions;
      }
    }
    return mockBatchSessions;
  });

  const [offlineQueue, setOfflineQueue] = useState<OfflineQueueItem[]>(() => {
    const saved = localStorage.getItem('labelsetu_offline_queue');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return mockOfflineQueue;
      }
    }
    return mockOfflineQueue;
  });

  const [notices, setNotices] = useState<NoticeOfViolation[]>(() => {
    const saved = localStorage.getItem('labelsetu_notices');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return mockNotices;
      }
    }
    return mockNotices;
  });

  const [selectedDistrict, setSelectedDistrict] = useState<string>('Bengaluru Urban');

  useEffect(() => {
    localStorage.setItem('labelsetu_inspections', JSON.stringify(inspections));
  }, [inspections]);

  useEffect(() => {
    localStorage.setItem('labelsetu_batch_sessions', JSON.stringify(batchSessions));
  }, [batchSessions]);

  useEffect(() => {
    localStorage.setItem('labelsetu_offline_queue', JSON.stringify(offlineQueue));
  }, [offlineQueue]);

  useEffect(() => {
    localStorage.setItem('labelsetu_notices', JSON.stringify(notices));
  }, [notices]);

  const getInspectionById = (id: string) => {
    if (!id) return inspections[0];
    const exact = inspections.find(i => i.id.toLowerCase() === id.toLowerCase());
    if (exact) return exact;
    const index = parseInt(id, 10);
    if (!isNaN(index) && index >= 0 && index < inspections.length) {
      return inspections[index];
    }
    if (id === '1') return inspections[0];
    return inspections[0];
  };

  const getBatchSessionById = (id: string) => {
    if (!id) return batchSessions[0];
    const exact = batchSessions.find(s => s.id.toLowerCase() === id.toLowerCase());
    if (exact) return exact;
    return batchSessions[0];
  };

  const addInspection = (newInspection: Inspection) => {
    setInspections(prev => [newInspection, ...prev]);
  };

  const addBatchSession = (newSession: BatchInspectionSession) => {
    setBatchSessions(prev => [newSession, ...prev.filter(s => s.id !== newSession.id)]);
  };

  const updateBatchSessionStatus = (id: string, status: BatchSessionStatus) => {
    setBatchSessions(prev => prev.map(s => {
      if (s.id.toLowerCase() === id.toLowerCase()) {
        return { ...s, status, updatedAt: new Date().toISOString() };
      }
      return s;
    }));
  };

  const updateInspectionStatus = (
    id: string, 
    status: InspectionStatus, 
    reason: string = 'Manual override by reviewing authority',
    officerName: string = 'Insp. Rajeshwar Rao'
  ) => {
    setInspections(prev => prev.map(insp => {
      if (insp.id.toLowerCase() === id.toLowerCase()) {
        return {
          ...insp,
          status,
          humanOverride: {
            overriddenBy: officerName,
            overrideDate: new Date().toLocaleString(),
            originalStatus: insp.status,
            newStatus: status,
            officerReason: reason,
          }
        };
      }
      return insp;
    }));
  };

  const syncOfflineItem = (id: string) => {
    setOfflineQueue(prev => prev.map(item => {
      if (item.id === id) {
        return { ...item, syncStatus: 'Synced' as const };
      }
      return item;
    }));
  };

  const syncAllOffline = () => {
    setOfflineQueue(prev => prev.map(item => ({ ...item, syncStatus: 'Synced' as const })));
  };

  const generateNotice = (inspectionId: string, ruleBreaches: string[], penaltyInr: number = 25000): NoticeOfViolation => {
    const insp = getInspectionById(inspectionId);
    const noticeId = `LM/KA/BLR/SEC36/${new Date().getFullYear()}/${Math.floor(1000 + Math.random() * 9000)}`;
    const newNotice: NoticeOfViolation = {
      noticeId,
      inspectionId,
      issuedToBrand: insp?.brand || 'Manufacturer / Packer',
      manufacturerAddress: insp?.manufacturerName || 'Registered Address',
      section: 'Section 36(1) of Legal Metrology Act, 2009',
      ruleBreaches: ruleBreaches.length > 0 ? ruleBreaches : ['Violation of Packaged Commodities Rules, 2011'],
      compoundingFeeInr: penaltyInr,
      issueDate: new Date().toISOString().split('T')[0],
      responseDeadline: '15 Days from Receipt',
      officerName: insp?.inspectorName || 'Insp. Rajeshwar Rao',
      officerDesignation: 'Legal Metrology Officer, Bengaluru Division',
      status: 'Issued'
    };

    setNotices(prev => [newNotice, ...prev]);

    // update inspection to note notice generated
    if (insp) {
      setInspections(prev => prev.map(i => i.id === inspectionId ? {
        ...i,
        legalNoticeGenerated: true,
        noticeNumber: noticeId,
      } : i));
    }

    return newNotice;
  };

  const recaptureBatchProduct = (
    sessionId: string,
    productId: string,
    newCropUrl: string,
    notes?: string
  ) => {
    setBatchSessions(prev => prev.map(s => {
      if (s.id.toLowerCase() === sessionId.toLowerCase()) {
        const updatedProducts = s.products.map(p => {
          if (p.id === productId) {
            return {
              ...p,
              cropImageUrl: newCropUrl,
              reviewStatus: 'Verified' as const,
              processingStatus: 'Complete' as const,
              priority: 'Low Priority' as const,
              priorityReason: 'Recapture verified: statutory declarations compliant and clear',
              notes: `Recaptured on ${new Date().toLocaleTimeString()} by officer. ${notes || 'Clean frontal evidence verified.'}`,
              recaptureEvidence: {
                originalCropUrl: p.cropImageUrl,
                newCropUrl: newCropUrl,
                reason: p.recaptureReason || 'glare',
                reasonDescription: 'Perspective-rectified clean product evidence captured by officer',
                recapturedAt: new Date().toLocaleTimeString(),
                officerNotes: notes,
                statusAfterRecapture: 'Verified' as const,
              }
            };
          }
          return p;
        });

        const newNeedsRecaptureCount = Math.max(0, s.needsRecaptureCount - 1);
        const newCompletedCount = s.completedCount + 1;
        const newLowPriorityCount = s.lowPriorityCount + 1;
        const newMediumPriorityCount = Math.max(0, s.mediumPriorityCount - 1);

        return {
          ...s,
          needsRecaptureCount: newNeedsRecaptureCount,
          completedCount: newCompletedCount,
          lowPriorityCount: newLowPriorityCount,
          mediumPriorityCount: newMediumPriorityCount,
          products: updatedProducts,
          updatedAt: new Date().toISOString(),
        };
      }
      return s;
    }));
  };

  const retryFailedBatchProducts = (sessionId: string) => {
    setBatchSessions(prev => prev.map(s => {
      if (s.id.toLowerCase() === sessionId.toLowerCase()) {
        return {
          ...s,
          status: 'Complete' as const,
          isPartialFailure: false,
          failedCount: 0,
          completedCount: s.totalProducts - s.reviewRequiredCount - s.needsRecaptureCount,
          processedCount: s.totalProducts,
          products: s.products.map(p => p.processingStatus === 'Failed' ? {
            ...p,
            processingStatus: 'Complete' as const,
            reviewStatus: 'Verified' as const,
            priority: 'Low Priority' as const,
            notes: 'Reprocessed successfully on retry.',
          } : p)
        };
      }
      return s;
    }));
  };

  return (
    <InspectionContext.Provider value={{
      inspections,
      batchSessions,
      offlineQueue,
      notices,
      getInspectionById,
      getBatchSessionById,
      addInspection,
      addBatchSession,
      updateInspectionStatus,
      updateBatchSessionStatus,
      recaptureBatchProduct,
      retryFailedBatchProducts,
      syncOfflineItem,
      syncAllOffline,
      generateNotice,
      selectedDistrict,
      setSelectedDistrict,
    }}>
      {children}
    </InspectionContext.Provider>
  );
};

export const useInspections = () => {
  const context = useContext(InspectionContext);
  if (!context) {
    throw new Error('useInspections must be used within an InspectionProvider');
  }
  return context;
};

