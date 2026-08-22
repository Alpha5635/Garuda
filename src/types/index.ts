export type InspectionStatus = 
  | 'Verified' 
  | 'Provisional' 
  | 'Violation' 
  | 'Review Required' 
  | 'Not Evaluable';

export type UserRole = 
  | 'officer' 
  | 'reviewer' 
  | 'manufacturer' 
  | 'analyst' 
  | 'consumer';

export interface UserProfile {
  id: string;
  name: string;
  role: UserRole;
  badgeNumber?: string;
  district: string;
  state: string;
  email: string;
  avatarUrl?: string;
}

export type PackagingType = 
  | 'Pouch' 
  | 'Rigid Box' 
  | 'Bottle / Can' 
  | 'Tin' 
  | 'Carton' 
  | 'E-commerce Listing';

export type CalibrationMethod = 
  | 'Calibration Card (ISO/IEC 7810)' 
  | 'Enter Panel Dimensions' 
  | 'ArUco Marker' 
  | 'Physical Steel Rule'
  | 'Uncalibrated';

export interface CalibrationTarget {
  method: CalibrationMethod;
  type: string;
  detectedWidthPx: number;
  knownWidthMm: number; // e.g. 85.60 mm for ISO card
  pixelsPerMm: number;
  confidence: number;
  panelDimensionsMm?: {
    height: number;
    width: number;
  };
}

export interface BoundingBox {
  x: number; // percentage (0-100) from left
  y: number; // percentage (0-100) from top
  width: number; // percentage width
  height: number; // percentage height
  label?: string;
  rawCoordsPx?: {
    ymin: number;
    xmin: number;
    ymax: number;
    xmax: number;
  };
}

export interface EvidenceCropInfo {
  cropUrl: string;
  cropSha256: string;
  aspectRatio: string;
  pixelWidth: number;
  pixelHeight: number;
  magnification: string;
}

export type FindingSeverity = 'Critical' | 'Major' | 'Minor' | 'Advisory';

export type FindingActionType = 
  | 'Approve' 
  | 'Correct' 
  | 'Reject' 
  | 'ReviewRequired' 
  | 'Recapture';

export interface DeclarationFinding {
  id: string;
  field: string;
  clause: string; // e.g., "Rule 7(2)(i), Table I" or "Rule 6(1)(b)"
  ruleTitle?: string;
  ruleVersion?: string; // e.g. "LM-PCR-2011-v2024.2"
  extractedText: string;
  hindiTranslation?: string;
  status: 'Pass' | 'Fail' | 'Warning' | 'Not Applicable' | 'Review Required';
  severity?: FindingSeverity;
  ocrConfidence: number; // 0 - 100
  measuredHeightMm?: number;
  requiredHeightMm?: number;
  pdpAreaCm2?: number;
  quietZoneCleared?: boolean;
  quietZoneOverlapReason?: string;
  quietZoneClearanceMm?: number;
  quietZoneRequiredBufferMm?: number;
  bbox?: BoundingBox;
  evidenceCrop?: EvidenceCropInfo;
  notes?: string;
  logicResult?: 'PASSED' | 'FAILED' | 'AMBIGUOUS' | 'EXEMPT';
  statutorySource?: string;
  officerDecision?: {
    action: FindingActionType;
    officer: string;
    timestamp: string;
    overrideNote?: string;
    correctedHeightMm?: number;
  };
}

export interface ScoreBreakdown {
  criticalViolations: number;
  majorViolations: number;
  minorWarnings: number;
  reviewRequired: number;
  verifiedCount: number;
}

export type InspectionSourceType = 
  | 'Package / Label' 
  | 'Take Photo' 
  | 'E-commerce Listing';

export type InspectionCategoryType = 
  | 'Routine Market Surveillance' 
  | 'Consumer Complaint Investigation' 
  | 'Pre-Market Certification Audit' 
  | 'E-Commerce Marketplace Crawl';

export interface Inspection {
  id: string;
  productName: string;
  brand: string;
  manufacturerName: string;
  category: string;
  netQuantity: string;
  statedWeightGramsOrMl: number;
  mrp: number;
  unitSalePrice?: string;
  batchNumber?: string;
  mfgDate?: string;
  expiryDate?: string;
  consumerCareDetails?: string;
  countryOfOrigin?: string;
  packagingType: PackagingType;
  pdpAreaCm2: number;
  score: number; // 0 - 100
  scoreBreakdown?: ScoreBreakdown;
  status: InspectionStatus;
  inspectionDate: string;
  inspectionType?: InspectionCategoryType;
  district: string;
  state: string;
  gpsCoordinates?: {
    latitude: number;
    longitude: number;
    locationName: string;
  };
  capturedDevice?: string;
  inspectorName: string;
  inspectorBadge: string;
  sampleImage: string;
  imageSha256: string;
  calibration: CalibrationTarget;
  findings: DeclarationFinding[];
  quietZoneViolation: boolean;
  minFontHeightCompliant: boolean;
  multilingualDetected: boolean;
  ecommerceRule6_10?: {
    isEcommerce: boolean;
    marketplace?: string;
    listingUrl?: string;
    missingDigitalDeclarations: string[];
    exemptionsApplied: string[];
  };
  humanOverride?: {
    overriddenBy: string;
    overrideDate: string;
    originalStatus: InspectionStatus;
    newStatus: InspectionStatus;
    officerReason: string;
  };
  legalNoticeGenerated?: boolean;
  noticeNumber?: string;
}

export interface EcommerceScanItem {
  id: string;
  marketplace: 'Amazon India' | 'Flipkart' | 'Blinkit' | 'Zepto' | 'Instamart' | 'JioMart';
  productTitle: string;
  brand: string;
  sellerName: string;
  pdpUrl: string;
  thumbnailUrl: string;
  mrp: number;
  listedPrice: number;
  declaredNetQuantity: string;
  unitSalePricePresent: boolean;
  countryOfOriginPresent: boolean;
  manufacturerAddressPresent: boolean;
  expiryOrBestBeforePresent: boolean;
  consumerCareEmailPhonePresent: boolean;
  monthYearPackingPresent: boolean;
  overallStatus: InspectionStatus;
  violationCount: number;
  lastScannedAt: string;
  noticeEligible: boolean;
}

export interface OfflineQueueItem {
  id: string;
  localId: string;
  productName: string;
  brand: string;
  capturedAt: string;
  syncStatus: 'Pending' | 'Syncing' | 'Synced' | 'Conflict';
  fileSizeKb: number;
  latitude?: number;
  longitude?: number;
  district: string;
  imageThumbnail: string;
}

export interface NoticeOfViolation {
  noticeId: string;
  inspectionId: string;
  issuedToBrand: string;
  manufacturerAddress: string;
  section: string;
  ruleBreaches: string[];
  compoundingFeeInr: number;
  issueDate: string;
  responseDeadline: string;
  officerName: string;
  officerDesignation: string;
  status: 'Draft' | 'Issued' | 'Acknowledged' | 'Compounded' | 'Forwarded for Prosecution';
}
