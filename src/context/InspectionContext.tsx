import React, { createContext, useContext, useState, useEffect } from 'react';
import { Inspection, InspectionStatus, OfflineQueueItem, NoticeOfViolation } from '../types';
import { mockInspections, mockOfflineQueue, mockNotices } from '../data/mockData';

interface InspectionContextType {
  inspections: Inspection[];
  offlineQueue: OfflineQueueItem[];
  notices: NoticeOfViolation[];
  getInspectionById: (id: string) => Inspection | undefined;
  addInspection: (newInspection: Inspection) => void;
  updateInspectionStatus: (id: string, status: InspectionStatus, reason?: string, officerName?: string) => void;
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
        return JSON.parse(saved);
      } catch (e) {
        return mockInspections;
      }
    }
    return mockInspections;
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

  const addInspection = (newInspection: Inspection) => {
    setInspections(prev => [newInspection, ...prev]);
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

  return (
    <InspectionContext.Provider value={{
      inspections,
      offlineQueue,
      notices,
      getInspectionById,
      addInspection,
      updateInspectionStatus,
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
