import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useInspections } from '../../context/InspectionContext';
import { UserRole } from '../../types';
import { 
  Search, 
  MapPin, 
  Bell, 
  User, 
  ChevronDown, 
  Menu, 
  Shield, 
  Wifi, 
  WifiOff, 
  Check, 
  AlertTriangle,
  FileSpreadsheet,
  Layers,
  Sparkles,
  Play
} from 'lucide-react';
import { Drawer } from '../ui/Drawer';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { cn } from '../../utils/cn';

interface HeaderProps {
  onOpenMobileSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenMobileSidebar }) => {
  const { user, setUserRole, availableUsers, switchUser } = useAuth();
  const { selectedDistrict, setSelectedDistrict } = useInspections();
  const navigate = useNavigate();

  const [searchQuery, setSearchQuery] = useState('');
  const [isRoleMenuOpen, setIsRoleMenuOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(true);

  const districts = [
    'Bengaluru Urban',
    'Bengaluru Rural',
    'Mysuru',
    'Dakshina Kannada (Mangaluru)',
    'Belagavi',
    'Kalaburagi',
    'New Delhi Central',
    'Mumbai Suburban'
  ];

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/history?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const notifications = [
    {
      id: 'n1',
      title: 'Repeat Violation Alert Flagged',
      desc: 'Patanjali Ayurved 500ml batch flagged for second Rule 9 font height non-compliance.',
      time: '12m ago',
      type: 'violation',
    },
    {
      id: 'n2',
      title: 'E-commerce Rule 6(10) Crawler Finished',
      desc: 'Amazon India scan detected 2 listings with missing Country of Origin declarations.',
      time: '45m ago',
      type: 'ecom',
    },
    {
      id: 'n3',
      title: 'Tenth Schedule Amendment Sync',
      desc: 'Legal Metrology Rules 2024.2 database rules updated and synced for field officers.',
      time: '2h ago',
      type: 'info',
    }
  ];

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between gap-4 sticky top-0 z-20 shadow-xs">
      {/* Mobile Toggle & Brand / District */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="lg:hidden p-2 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          aria-label="Open Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Location & District Badge */}
        <div className="hidden sm:flex items-center gap-2 bg-slate-100/80 hover:bg-slate-100 px-3 py-1.5 rounded-md border border-slate-200 text-xs text-slate-700 transition-colors">
          <MapPin className="w-3.5 h-3.5 text-blue-600 shrink-0" />
          <span className="text-slate-500 font-medium">Jurisdiction:</span>
          <select
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            className="bg-transparent font-semibold text-slate-900 focus:outline-none cursor-pointer text-xs"
          >
            {districts.map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
          <span className="text-slate-400">| Zone 4</span>
        </div>
      </div>

      {/* Center Search Bar */}
      <form onSubmit={handleSearchSubmit} className="flex-1 max-w-md hidden md:block">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search inspections, brands, batch numbers, clauses..."
            className="w-full h-9 pl-9 pr-4 text-xs rounded-md bg-slate-50 border border-slate-300 text-slate-900 placeholder:text-slate-400 focus:bg-white focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600 transition-colors"
          />
        </div>
      </form>

      {/* Right Controls: Connectivity, Notifications, Role Switcher */}
      <div className="flex items-center gap-2.5">
        {/* Golden SIH Demo Quick Launcher */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate('/inspection/INS-2026-0518-1123')}
          leftIcon={<Sparkles className="w-3.5 h-3.5 text-blue-600" />}
          className="hidden xl:flex text-xs h-8 bg-blue-50/70 border-blue-200 text-blue-950 font-bold hover:bg-blue-100"
        >
          SIH Live Demo
        </Button>

        {/* Connectivity Mode Simulator */}
        <button
          onClick={() => setIsOnline(!isOnline)}
          title={isOnline ? "Network: Online (Click to test Offline Mode)" : "Network: Offline Field Mode"}
          className={cn(
            "hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-mono font-medium border transition-colors",
            isOnline 
              ? "bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100" 
              : "bg-amber-50 text-amber-900 border-amber-300 animate-pulse"
          )}
        >
          {isOnline ? <Wifi className="w-3.5 h-3.5 text-emerald-600" /> : <WifiOff className="w-3.5 h-3.5 text-amber-600" />}
          <span>{isOnline ? "Live Network" : "Offline Mode"}</span>
        </button>

        {/* Notifications Button */}
        <button
          onClick={() => setIsNotificationsOpen(true)}
          className="relative p-2 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-600 rounded-full ring-2 ring-white" />
        </button>

        {/* Role Switcher Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsRoleMenuOpen(!isRoleMenuOpen)}
            className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-md bg-slate-100 hover:bg-slate-200/80 border border-slate-200 text-xs transition-colors"
          >
            <div className="w-6 h-6 rounded-full bg-blue-700 text-white flex items-center justify-center font-bold text-[10px]">
              {user.name.charAt(0)}
            </div>
            <div className="text-left hidden sm:block">
              <span className="font-semibold text-slate-900 block leading-none">{user.name.split(' ')[0]}</span>
              <span className="text-[10px] text-blue-700 capitalize font-medium">{user.role}</span>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
          </button>

          {isRoleMenuOpen && (
            <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-modal border border-slate-200 p-2 z-50 animate-in fade-in zoom-in-95 duration-100">
              <div className="px-2 py-1.5 border-b border-slate-100 mb-1">
                <p className="text-xs font-bold text-slate-900">Switch Ecosystem Role</p>
                <p className="text-[10px] text-slate-500">Instantaneous persona simulation</p>
              </div>

              <div className="space-y-1">
                {availableUsers.map((u) => {
                  const isSelected = user.id === u.id;
                  return (
                    <button
                      key={u.id}
                      onClick={() => {
                        switchUser(u.id);
                        setIsRoleMenuOpen(false);
                      }}
                      className={cn(
                        "w-full text-left p-2 rounded-md text-xs flex items-center justify-between transition-colors",
                        isSelected 
                          ? "bg-blue-50 text-blue-900 font-semibold" 
                          : "hover:bg-slate-100 text-slate-700"
                      )}
                    >
                      <div className="min-w-0">
                        <p className="truncate text-xs font-bold">{u.name}</p>
                        <p className="text-[10px] text-slate-500 capitalize">{u.role} • {u.district}</p>
                      </div>
                      {isSelected && <Check className="w-3.5 h-3.5 text-blue-600 shrink-0" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Notifications Drawer */}
      <Drawer
        isOpen={isNotificationsOpen}
        onClose={() => setIsNotificationsOpen(false)}
        title="Regulatory Alerts & Updates"
        description="Real-time statutory notifications & violation flags"
      >
        <div className="space-y-3">
          {notifications.map((n) => (
            <div key={n.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
              <div className="flex items-center justify-between">
                <span className={cn(
                  "text-[10px] font-bold uppercase font-mono px-1.5 py-0.5 rounded",
                  n.type === 'violation' && "bg-red-100 text-red-800",
                  n.type === 'ecom' && "bg-blue-100 text-blue-800",
                  n.type === 'info' && "bg-slate-200 text-slate-800"
                )}>
                  {n.type}
                </span>
                <span className="text-[10px] text-slate-400">{n.time}</span>
              </div>
              <h5 className="text-xs font-bold text-slate-900 mt-1">{n.title}</h5>
              <p className="text-xs text-slate-600 leading-relaxed">{n.desc}</p>
            </div>
          ))}
        </div>
      </Drawer>
    </header>
  );
};
