import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { 
  mockRepeatOffenderBrands, 
  mockRuleViolationTrends, 
  mockDistrictIntelligence,
  mockComplianceOverTime,
  mockCategoryBreakdown,
  mockDashboardMetrics
} from '../data/mockData';
import { 
  BarChart3, 
  TrendingUp, 
  ShieldAlert, 
  ShieldCheck,
  AlertTriangle, 
  MapPin, 
  Scale, 
  Layers, 
  Clock, 
  CheckCircle2, 
  HelpCircle,
  PieChart,
  LineChart,
  ArrowUpRight,
  Filter
} from 'lucide-react';
import { cn } from '../utils/cn';

export const Analytics: React.FC = () => {
  const [dataViewMode, setDataViewMode] = useState<'CONFIRMED_ONLY' | 'ALL_WITH_AI_ALERTS'>('CONFIRMED_ONLY');

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header with Confirmed vs AI Alert Mode Toggle */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Enforcement Intelligence & Trend Analytics
            </h1>
            <Badge variant="blue">National Metrology Intelligence</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Predictive habitual offender risk index, seasonal commodity violations, and font-height defect clustering
          </p>
        </div>

        {/* Essential Data Trust Filter Toggle */}
        <div className="flex items-center gap-2 p-1 bg-slate-100 rounded-lg border border-slate-200 text-xs">
          <button
            onClick={() => setDataViewMode('CONFIRMED_ONLY')}
            className={cn(
              "px-3 py-1.5 rounded-md font-bold transition-all flex items-center gap-1.5",
              dataViewMode === 'CONFIRMED_ONLY'
                ? "bg-slate-900 text-white shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            )}
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Confirmed Findings Only</span>
          </button>

          <button
            onClick={() => setDataViewMode('ALL_WITH_AI_ALERTS')}
            className={cn(
              "px-3 py-1.5 rounded-md font-bold transition-all flex items-center gap-1.5",
              dataViewMode === 'ALL_WITH_AI_ALERTS'
                ? "bg-slate-900 text-white shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            )}
          >
            <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
            <span>Include Provisional AI Alerts</span>
          </button>
        </div>
      </div>

      {/* Critical Trust & Safety Banner */}
      {dataViewMode === 'ALL_WITH_AI_ALERTS' && (
        <div className="p-3 bg-amber-50 border border-amber-300 rounded-lg flex items-start gap-2.5 text-xs text-amber-950">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <strong>Legal Metrology Enforcement Protocol:</strong>
            <span>
              {' '}Provisional AI alerts represent unverified optical extractions (e.g. glare-obscured packages). Under Legal Metrology inspection guidelines, they are not admissible as statutory violation records until physically confirmed by a reviewing officer.
            </span>
          </div>
        </div>
      )}

      {/* 4 Top KPI Cards — Updated for Batch Surveillance & Smart Recapture */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
        <Card className="border-l-4 border-l-blue-700">
          <CardContent className="p-4">
            <span className="text-[10px] uppercase font-bold text-slate-500 font-sans block">Products Screened</span>
            <div className="text-2xl font-extrabold text-slate-900 mt-0.5">1,284</div>
            <p className="text-[11px] text-slate-500 font-sans mt-0.5">+18.5% Multi-Product Acceleration</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-indigo-600">
          <CardContent className="p-4">
            <span className="text-[10px] uppercase font-bold text-slate-500 font-sans block">Batch Shelf Sessions</span>
            <div className="text-2xl font-extrabold text-indigo-700 mt-0.5">124 Sessions</div>
            <p className="text-[11px] text-indigo-700 font-sans mt-0.5">Avg 10.4 Products / Master Capture</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-red-600">
          <CardContent className="p-4">
            <span className="text-[10px] uppercase font-bold text-slate-500 font-sans block">Confirmed Violations</span>
            <div className="text-2xl font-extrabold text-red-700 mt-0.5">
              {dataViewMode === 'CONFIRMED_ONLY' ? '152 Confirmed' : '152 (+67 Provisional)'}
            </div>
            <p className="text-[11px] text-slate-500 font-sans mt-0.5">138 Section 36 Notices Issued</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-600">
          <CardContent className="p-4">
            <span className="text-[10px] uppercase font-bold text-slate-500 font-sans block">Recapture Resolution Rate</span>
            <div className="text-2xl font-extrabold text-emerald-700 mt-0.5">94.2%</div>
            <p className="text-[11px] text-slate-500 font-sans mt-0.5">16 of 17 Occlusions Rectified</p>
          </CardContent>
        </Card>
      </div>

      {/* Grid: Line Chart (Volume & Pass Rate) + Donut/Category Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Line / Monthly Trend Chart */}
        <Card className="lg:col-span-7">
          <CardHeader>
            <div>
              <CardTitle>Inspection Volume & Pass Rate Over Time</CardTitle>
              <CardDescription>Monthly inspection volume vs statutory compliance curve</CardDescription>
            </div>
            <Badge variant="green" className="font-mono">+11% YoY Improvement</Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* SVG Visual Line Chart */}
            <div className="h-48 w-full relative flex items-end justify-between gap-2 pt-6">
              <svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="none">
                <polyline
                  fill="none"
                  stroke="#2563EB"
                  strokeWidth="3"
                  points="20,130 90,118 160,105 230,85 300,70 370,55"
                />
                <polyline
                  fill="none"
                  stroke="#DC2626"
                  strokeWidth="2"
                  strokeDasharray="4 2"
                  points="20,90 90,85 160,80 230,95 300,100 370,110"
                />
              </svg>

              {mockComplianceOverTime.map((item, idx) => (
                <div key={idx} className="flex-1 flex flex-col items-center justify-end z-10">
                  <div className="w-8 bg-blue-100 hover:bg-blue-200 rounded-t transition-all flex flex-col justify-end p-0.5 text-center relative group" style={{ height: `${item.total / 3.5}px` }}>
                    <span className="opacity-0 group-hover:opacity-100 absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-900 text-white font-mono text-[10px] p-1 rounded shadow whitespace-nowrap z-20">
                      {item.total} Total ({item.passRate}% Pass)
                    </span>
                  </div>
                  <span className="text-[10px] font-semibold text-slate-600 mt-2 font-mono">{item.month.split(' ')[0]}</span>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs text-slate-500">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-0.5 bg-blue-600 inline-block" />
                  <span>Compliance Pass Curve (%)</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-0.5 bg-red-600 border border-red-600 inline-block" />
                  <span>Violations Count</span>
                </span>
              </div>
              <span className="font-mono text-slate-700 font-semibold">348 Batches / Aug 2026</span>
            </div>
          </CardContent>
        </Card>

        {/* Category Breakdown (Donut Style Bar Visualization) */}
        <Card className="lg:col-span-5">
          <CardHeader>
            <div>
              <CardTitle>Commodity Category Breakdown</CardTitle>
              <CardDescription>Inspection volume and compliance rate by industry sector</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-3.5">
            {mockCategoryBreakdown.map((cat, idx) => (
              <div key={idx} className="space-y-1 text-xs">
                <div className="flex justify-between font-semibold">
                  <span className="text-slate-900">{cat.category}</span>
                  <span className="font-mono text-slate-600">{cat.compliance}% Pass ({cat.violations} Vio)</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all"
                    style={{ width: `${cat.compliance}%`, backgroundColor: cat.color }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Repeat Brand Risk Matrix & District Heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Habitual Violator Risk Matrix */}
        <Card className="lg:col-span-7 border-t-4 border-t-red-600">
          <CardHeader>
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-red-600" />
              <div>
                <CardTitle>Habitual Offender Risk Matrix</CardTitle>
                <CardDescription>Section 36 compounding & enhanced prosecution risk tracking</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-4">Brand / Packer</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Confirmed Vio</th>
                    <th className="py-2.5 px-3">Frequent Defect</th>
                    <th className="py-2.5 px-4 text-right">Statutory Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {mockRepeatOffenderBrands.map((b, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-bold text-slate-900">{b.brand}</td>
                      <td className="py-3 px-3 text-slate-600">{b.category}</td>
                      <td className="py-3 px-3 font-mono text-red-700 font-bold">
                        {b.confirmedCount} ({b.repeatOffenseRate}%)
                      </td>
                      <td className="py-3 px-3 text-slate-600 max-w-xs truncate" title={b.mostFrequentDefect}>
                        {b.mostFrequentDefect}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <span className="font-mono text-[11px] font-semibold bg-red-50 text-red-700 px-2 py-0.5 rounded border border-red-200">
                          {b.section36Applies}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* District Zonal Intelligence Cards */}
        <Card className="lg:col-span-5 border-t-4 border-t-blue-700">
          <CardHeader>
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-blue-600" />
              <div>
                <CardTitle>District Zonal Intelligence</CardTitle>
                <CardDescription>Enforcement pass rate and officer deployment</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {mockDistrictIntelligence.map((d, idx) => (
              <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between text-xs">
                <div>
                  <h4 className="font-bold text-slate-900">{d.district}</h4>
                  <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                    {d.inspections} Inspections • {d.activeOfficers} Active Officers
                  </p>
                </div>
                <div className="text-right font-mono">
                  <div className="font-bold text-emerald-700 text-xs">{d.complianceRate}% Pass</div>
                  <span className="text-[10px] text-red-600">{d.confirmed} Confirmed Vio</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
