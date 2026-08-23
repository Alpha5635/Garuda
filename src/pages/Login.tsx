import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';
import { 
  Scale, 
  ShieldCheck, 
  Lock, 
  User, 
  Building2, 
  CheckCircle2, 
  ArrowRight,
  Shield,
  FileCheck2,
  Sparkles
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { cn } from '../utils/cn';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [selectedRole, setSelectedRole] = useState<UserRole>('officer');
  const [email, setEmail] = useState('r.rao.lm@karnataka.gov.in');
  const [password, setPassword] = useState('••••••••••••');
  const [badgeId, setBadgeId] = useState('LM-KA-BLR-0482');
  const [isLoading, setIsLoading] = useState(false);

  const roleOptions: { role: UserRole; title: string; desc: string; defaultEmail: string; badge: string }[] = [
    {
      role: 'officer',
      title: 'Legal Metrology Officer',
      desc: 'Field inspection, millimeter verification, seizure notices',
      defaultEmail: 'r.rao.lm@karnataka.gov.in',
      badge: 'LM-KA-BLR-0482',
    },
    {
      role: 'reviewer',
      title: 'Reviewing Authority',
      desc: 'Second-level human-in-the-loop audit and appeals',
      defaultEmail: 'sunita.d.metrology@nic.in',
      badge: 'LM-HQ-REV-012',
    },
    {
      role: 'manufacturer',
      title: 'Manufacturer / Brand Owner',
      desc: 'Pre-market artwork compliance & self-certification',
      defaultEmail: 'anand.v@tataconsumer.com',
      badge: 'MFG-TATA-7701',
    },
    {
      role: 'analyst',
      title: 'Market Intelligence Analyst',
      desc: 'Enforcement trends, repeat offender brand matrices',
      defaultEmail: 'p.sen.analyst@gov.in',
      badge: 'MIA-NAT-889',
    },
    {
      role: 'consumer',
      title: 'Citizen / Consumer Portal',
      desc: 'Product verification, MRP checking & grievance filing',
      defaultEmail: 'aakash.v92@gmail.com',
      badge: 'CITIZEN-NCH',
    }
  ];

  const handleRoleSelect = (opt: typeof roleOptions[0]) => {
    setSelectedRole(opt.role);
    setEmail(opt.defaultEmail);
    setBadgeId(opt.badge);
  };

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      login(selectedRole);
      setIsLoading(false);
      navigate('/dashboard');
    }, 400);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col justify-between selection:bg-blue-600 selection:text-white">
      {/* Top Banner */}
      <div className="bg-slate-950/80 border-b border-slate-800 px-6 py-2 text-xs flex items-center justify-between text-slate-400">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-300">Government of India / State Legal Metrology Departments</span>
          <span className="text-slate-600">•</span>
          <span className="hidden sm:inline">Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011</span>
        </div>
        <div className="flex items-center gap-1 text-emerald-400 font-mono text-[11px]">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Secured National Enforcement Portal</span>
        </div>
      </div>

      {/* Main Login Body */}
      <div className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-12">
        <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-12 gap-8 bg-slate-950/70 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl backdrop-blur-md">
          
          {/* Left Column: Brand Context & Differentiators */}
          <div className="lg:col-span-5 flex flex-col justify-between space-y-6 border-b lg:border-b-0 lg:border-r border-slate-800 pb-6 lg:pb-0 lg:pr-8">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg ring-1 ring-blue-400/30">
                <Scale className="w-7 h-7" />
              </div>
              <div>
                <h1 className="text-2xl font-extrabold text-white tracking-tight">LabelSetu</h1>
                <p className="text-sm font-semibold text-blue-400 mt-0.5">
                  AI-assisted Legal Metrology Compliance Intelligence
                </p>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Evidence-led regulatory inspection intelligence platform automating Rule 6(1), Tenth Schedule font heights, quiet-zone geometry, and e-commerce digital compliance.
              </p>
            </div>

            {/* Key Pillars */}
            <div className="space-y-2.5 pt-4 border-t border-slate-800/80">
              <div className="flex items-start gap-2.5 text-xs text-slate-300">
                <FileCheck2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>Calibrated millimeter optical verification (ISO/IEC 7810 targets)</span>
              </div>
              <div className="flex items-start gap-2.5 text-xs text-slate-300">
                <Shield className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <span>Section 36 prosecution notices with SHA-256 chain-of-custody</span>
              </div>
              <div className="flex items-start gap-2.5 text-xs text-slate-300">
                <Building2 className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span>Rule 6(10) E-Commerce & marketplace automated compliance</span>
              </div>
            </div>

            <div className="text-[11px] text-slate-500 font-mono">
              LabelSetu SIH Edition • Built for Precision Enforcement
            </div>
          </div>

          {/* Right Column: Interactive Role Selector & Login Form */}
          <div className="lg:col-span-7 space-y-6">
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">Sign In to Inspection Command</h2>
              <p className="text-xs text-slate-400 mt-0.5">Select your ecosystem persona to access the authenticated portal</p>
            </div>

            {/* Role Switcher Grid */}
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 block">
                Select Persona Role
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {roleOptions.map((opt) => {
                  const isSelected = selectedRole === opt.role;
                  return (
                    <button
                      key={opt.role}
                      type="button"
                      onClick={() => handleRoleSelect(opt)}
                      className={cn(
                        "p-3 rounded-lg border text-left transition-all relative",
                        isSelected
                          ? "bg-blue-950/80 border-blue-500 ring-1 ring-blue-500 shadow-sm"
                          : "bg-slate-900/80 border-slate-800 hover:border-slate-700 text-slate-400"
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className={cn("text-xs font-bold", isSelected ? "text-white" : "text-slate-300")}>
                          {opt.title}
                        </span>
                        {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 shrink-0" />}
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">{opt.desc}</p>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Login Inputs */}
            <form onSubmit={handleSignIn} className="space-y-4 pt-2">
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-1">
                    Email / Government NIC ID
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="w-full h-10 pl-9 pr-3 rounded-lg bg-slate-900 border border-slate-700 text-white text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-1">
                      Badge / Officer ID
                    </label>
                    <input
                      type="text"
                      value={badgeId}
                      onChange={(e) => setBadgeId(e.target.value)}
                      className="w-full h-10 px-3 rounded-lg bg-slate-900 border border-slate-700 text-white text-sm font-mono focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-1">
                      Password / Security Token
                    </label>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className="w-full h-10 pl-9 pr-3 rounded-lg bg-slate-900 border border-slate-700 text-white text-sm font-mono focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={isLoading}
                rightIcon={<ArrowRight className="w-4 h-4" />}
                className="w-full bg-blue-600 hover:bg-blue-500 border-blue-500 text-white font-bold h-11"
              >
                Access {roleOptions.find(r => r.role === selectedRole)?.title || 'Portal'}
              </Button>
            </form>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-slate-950 border-t border-slate-800/80 px-6 py-3 text-center text-xs text-slate-500 flex items-center justify-between">
        <span>© 2026 LabelSetu — Legal Metrology Compliance Intelligence</span>
        <span>Version 1.0 (Amended PCR Standards)</span>
      </div>
    </div>
  );
};
