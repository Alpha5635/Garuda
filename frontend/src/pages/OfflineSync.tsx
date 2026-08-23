import React, { useState } from 'react';
import { useInspections } from '../context/InspectionContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { 
  WifiOff, 
  Wifi, 
  RefreshCw, 
  Database, 
  HardDrive, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  UploadCloud, 
  FileCheck2, 
  Layers,
  Smartphone,
  Camera,
  Ruler,
  AlertTriangle,
  RotateCcw,
  Check
} from 'lucide-react';
import { cn } from '../utils/cn';

export const OfflineSync: React.FC = () => {
  const { offlineQueue, syncOfflineItem, syncAllOffline } = useInspections();
  const [isSyncingAll, setIsSyncingAll] = useState(false);
  const [isOfflineSimulated, setIsOfflineSimulated] = useState(true);
  const [isSimulatedCapturing, setIsSimulatedCapturing] = useState(false);
  const [lastSyncSuccessId, setLastSyncSuccessId] = useState<string | null>(null);

  const pendingItems = offlineQueue.filter(i => i.syncStatus === 'Pending');
  const syncedItems = offlineQueue.filter(i => i.syncStatus === 'Synced');

  const handleSyncAll = () => {
    setIsSyncingAll(true);
    setTimeout(() => {
      syncAllOffline();
      setIsSyncingAll(false);
      setLastSyncSuccessId('ALL');
    }, 700);
  };

  const handleSyncSingle = (id: string) => {
    syncOfflineItem(id);
    setLastSyncSuccessId(id);
    setTimeout(() => setLastSyncSuccessId(null), 2500);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Offline Field Inspection & IndexedDB Sync Manager
            </h1>
            <Badge variant="blue">Zero-Connectivity Field Architecture</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Enables full local OCR, millimeter calibration, and Rule 6(1) evaluation in APMC mandis, remote wholesale godowns, and rural inspection spots without internet connectivity
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant={isOfflineSimulated ? "danger" : "outline"}
            size="sm"
            onClick={() => setIsOfflineSimulated(!isOfflineSimulated)}
            leftIcon={isOfflineSimulated ? <WifiOff className="w-4 h-4" /> : <Wifi className="w-4 h-4" />}
          >
            {isOfflineSimulated ? "Network: Offline Field Mode" : "Network: Live Uplink Online"}
          </Button>

          <Button
            variant="primary"
            size="sm"
            isLoading={isSyncingAll}
            disabled={pendingItems.length === 0}
            onClick={handleSyncAll}
            leftIcon={<UploadCloud className="w-4 h-4" />}
            className="bg-blue-700 hover:bg-blue-800"
          >
            Sync All Pending ({pendingItems.length})
          </Button>
        </div>
      </div>

      {/* Sync Success Banner */}
      {lastSyncSuccessId && (
        <div className="p-3 bg-emerald-50 border border-emerald-300 rounded-lg flex items-center gap-2 text-xs text-emerald-950 font-mono animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Synced successfully to State Legal Metrology Central Ledger (SHA-256 Verified).</span>
        </div>
      )}

      {/* Storage & Queue Statistics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-amber-50 text-amber-700">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-500 font-mono">Waiting for Sync</span>
              <div className="text-xl font-extrabold font-mono text-slate-900">{pendingItems.length} Records</div>
              <p className="text-[11px] text-slate-500">Encrypted in browser IndexedDB</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-600">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-emerald-50 text-emerald-700">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-500 font-mono">Synced to State Cloud</span>
              <div className="text-xl font-extrabold font-mono text-slate-900">{syncedItems.length} Records</div>
              <p className="text-[11px] text-slate-500">Chain-of-Custody Dispatched</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-700">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-blue-50 text-blue-700">
              <HardDrive className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-500 font-mono">Local Sandbox Memory</span>
              <div className="text-xl font-extrabold font-mono text-slate-900">9.77 MB / 50 MB</div>
              <p className="text-[11px] text-slate-500">Offline SQLite / IndexedDB</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Field Mobile Inspection Preview Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Offline Queue Ledger */}
        <div className="lg:col-span-8 space-y-4">
          <Card>
            <CardHeader className="flex items-center justify-between">
              <div>
                <CardTitle>Field Offline Inspection Buffer</CardTitle>
                <CardDescription>Local inspections awaiting connection restore</CardDescription>
              </div>
              <Badge variant="slate" className="font-mono">{offlineQueue.length} Items</Badge>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-100">
                {offlineQueue.map((item) => (
                  <div key={item.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/80 transition-colors">
                    <div className="flex items-center gap-3">
                      <img
                        src={item.imageThumbnail}
                        alt={item.productName}
                        className="w-12 h-12 rounded-lg object-cover border border-slate-200 shrink-0"
                      />
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-xs text-blue-700">{item.localId}</span>
                          <h4 className="font-bold text-xs text-slate-900">{item.productName}</h4>
                        </div>
                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-500 mt-1 font-mono">
                          <span>Brand: {item.brand}</span>
                          <span>•</span>
                          <span>Size: {(item.fileSizeKb / 1024).toFixed(1)} MB</span>
                          <span>•</span>
                          <span className="flex items-center gap-0.5">
                            <MapPin className="w-3 h-3 text-slate-400" />
                            <span>{item.latitude?.toFixed(4)}, {item.longitude?.toFixed(4)}</span>
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2.5 self-end sm:self-center">
                      <span className={cn(
                        "text-[10px] font-mono font-bold uppercase px-2.5 py-1 rounded-full border",
                        item.syncStatus === 'Synced'
                          ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                          : "bg-amber-50 text-amber-800 border-amber-300 animate-pulse"
                      )}>
                        {item.syncStatus === 'Synced' ? 'Synced successfully' : 'Waiting for sync'}
                      </span>

                      {item.syncStatus === 'Pending' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleSyncSingle(item.id)}
                          leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
                          className="text-xs h-7 px-2"
                        >
                          Sync Now
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recapture Guidance & Hardware EXIF specs */}
        <div className="lg:col-span-4 space-y-4">
          <Card className="border-t-4 border-t-blue-700">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Smartphone className="w-5 h-5 text-blue-600" />
                <CardTitle>Field Mobile Protocol</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1">
                <strong className="block text-slate-900 font-bold">Local Edge Verification Engine:</strong>
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  Field officers run on-device optical perspective correction, ArUco/smart-card calibration, and rule evaluations locally even in basements and remote mandis.
                </p>
              </div>

              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg space-y-1">
                <strong className="block text-blue-950 font-bold">Automatic Sync on Network Restore:</strong>
                <p className="text-[11px] text-blue-900 leading-relaxed">
                  As soon as 4G/5G signal is detected, background service workers upload cryptographically signed records to the central registry.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
