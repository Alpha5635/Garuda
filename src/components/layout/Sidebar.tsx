import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useInspections } from '../../context/InspectionContext';
import { 
  LayoutDashboard, 
  PlusCircle, 
  History, 
  ShoppingBag, 
  FileText, 
  BarChart3, 
  Factory, 
  Users, 
  WifiOff, 
  Settings, 
  Shield, 
  Scale,
  LogOut,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { cn } from '../../utils/cn';

interface SidebarProps {
  isOpenMobile?: boolean;
  onCloseMobile?: () => void;
}

interface NavSubItem {
  label: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  badgeCount?: number;
}

interface NavGroup {
  group: string;
  items: NavSubItem[];
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpenMobile, onCloseMobile }) => {
  const { user, logout } = useAuth();
  const { offlineQueue } = useInspections();
  const navigate = useNavigate();

  const pendingOfflineCount = offlineQueue.filter(i => i.syncStatus === 'Pending').length;

  const navItems: NavGroup[] = [
    {
      group: 'Core Inspections',
      items: [
        { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
        { label: 'New Inspection', path: '/inspection/new', icon: PlusCircle, badge: 'Studio' },
        { label: 'Inspections', path: '/history', icon: History },
      ]
    },
    {
      group: 'Intelligence & Modules',
      items: [
        { label: 'E-commerce Inspector', path: '/ecommerce', icon: ShoppingBag, badge: 'Rule 6(10)' },
        { label: 'Reports & Notices', path: '/reports', icon: FileText },
        { label: 'Analytics & Trends', path: '/analytics', icon: BarChart3 },
      ]
    },
    {
      group: 'Ecosystem Portals',
      items: [
        { label: 'Manufacturers', path: '/manufacturer', icon: Factory },
        { label: 'Consumers Grievance', path: '/consumer', icon: Users },
        { 
          label: 'Offline Sync', 
          path: '/offline', 
          icon: WifiOff, 
          badgeCount: pendingOfflineCount > 0 ? pendingOfflineCount : undefined 
        },
      ]
    }
  ];

  return (
    <aside className={cn(
      "w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 border-r border-slate-800 transition-all duration-200 z-30",
      "fixed inset-y-0 left-0 lg:static lg:translate-x-0",
      isOpenMobile ? "translate-x-0" : "-translate-x-full"
    )}>
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800/80 bg-slate-950 flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white shadow-md ring-1 ring-white/10 shrink-0">
          <Scale className="w-5 h-5 text-white" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <h1 className="text-base font-bold text-white tracking-tight leading-none">LabelSetu</h1>
            <span className="text-[10px] uppercase font-mono font-bold bg-blue-500/20 text-blue-300 px-1.5 py-0.5 rounded border border-blue-500/30">
              v1.0
            </span>
          </div>
          <p className="text-[11px] text-slate-400 truncate mt-0.5">
            Legal Metrology AI Intel
          </p>
        </div>
      </div>

      {/* Statutory Authority Badge */}
      <div className="mx-3 mt-3 p-2.5 rounded-md bg-slate-800/60 border border-slate-700/60 flex items-center gap-2">
        <Shield className="w-4 h-4 text-emerald-400 shrink-0" />
        <div className="text-[11px] leading-tight">
          <span className="text-slate-300 font-semibold block">Act 2009 & PCR 2011</span>
          <span className="text-slate-400 text-[10px]">Statutory Verification Ready</span>
        </div>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
        {navItems.map((group, groupIdx) => (
          <div key={groupIdx} className="space-y-1">
            <h3 className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              {group.group}
            </h3>
            <div className="space-y-0.5 mt-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={onCloseMobile}
                    className={({ isActive }) => cn(
                      "flex items-center justify-between px-3 py-2 rounded-md text-xs font-semibold transition-colors group",
                      isActive
                        ? "bg-blue-600 text-white shadow-sm"
                        : "text-slate-300 hover:bg-slate-800 hover:text-white"
                    )}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <Icon className="w-4 h-4 shrink-0 text-slate-400 group-hover:text-white" />
                      <span className="truncate">{item.label}</span>
                    </div>

                    {item.badge && (
                      <span className="text-[9px] font-mono font-bold bg-slate-800 text-blue-300 px-1.5 py-0.5 rounded border border-slate-700">
                        {item.badge}
                      </span>
                    )}

                    {typeof item.badgeCount !== 'undefined' && item.badgeCount > 0 && (
                      <span className="text-[10px] font-mono font-bold bg-amber-500 text-slate-950 px-1.5 py-0.2 rounded-full">
                        {item.badgeCount}
                      </span>
                    )}
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* User / Officer Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/60">
        <div className="flex items-center justify-between p-2 rounded-md bg-slate-900 border border-slate-800">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-blue-900/80 text-blue-200 flex items-center justify-center font-bold text-xs border border-blue-700/60 shrink-0">
              {user.name.charAt(0)}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-white truncate leading-tight">{user.name}</p>
              <p className="text-[10px] text-slate-400 truncate capitalize">Role: {user.role}</p>
            </div>
          </div>
          <button
            onClick={() => {
              logout();
              navigate('/login');
            }}
            title="Sign out / Switch role"
            className="text-slate-400 hover:text-red-400 p-1.5 rounded transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
