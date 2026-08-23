import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useInspections } from '../context/InspectionContext';
import { useAuth } from '../context/AuthContext';
import { 
  mockDashboardMetrics, 
  mockComplianceOverTime, 
  mockRepeatOffenderBrands, 
  mockRuleViolationTrends, 
  mockDistrictIntelligence 
} from '../data/mockData';
import { MetricCard } from '../components/ui/MetricCard';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Search } from '../components/ui/Search';
import { Badge } from '../components/ui/Badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { InspectionStatus } from '../types';
import { 
  ClipboardCheck, 
  Clock, 
  AlertOctagon, 
  HelpCircle, 
  Percent, 
  Plus, 
  ShieldAlert, 
  ArrowUpRight, 
  Building, 
  Filter, 
  Sparkles, 
  FileText,
  AlertTriangle,
  Scale,
  MapPin,
  TrendingUp,
  BarChart2,
  ChevronRight,
  Layers,
  Camera
} from 'lucide-react';
import { cn } from '../utils/cn';

export const Dashboard: React.FC = () => {
  const { inspections, batchSessions, selectedDistrict } = useInspections();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [selectedStatusFilter, setSelectedStatusFilter] = useState<string>('ALL');
  const [tableSearch, setTableSearch] = useState<string>('');

  const statusFilters: { label: string; value: string; count?: number }[] = [
    { label: 'All Cases', value: 'ALL', count: inspections.length },
    { label: 'Verified', value: 'Verified', count: inspections.filter(i => i.status === 'Verified').length },
    { label: 'Violations', value: 'Violation', count: inspections.filter(i => i.status === 'Violation').length },
    { label: 'Review Required', value: 'Review Required', count: inspections.filter(i => i.status === 'Review Required').length },
    { label: 'Provisional', value: 'Provisional', count: inspections.filter(i => i.status === 'Provisional').length },
    { label: 'Not Evaluable', value: 'Not Evaluable', count: inspections.filter(i => i.status === 'Not Evaluable').length },
  ];

  const filteredInspections = inspections.filter(insp => {
    const matchesStatus = selectedStatusFilter === 'ALL' || insp.status === selectedStatusFilter;
    const matchesSearch = tableSearch.trim() === '' || 
      insp.productName.toLowerCase().includes(tableSearch.toLowerCase()) ||
      insp.brand.toLowerCase().includes(tableSearch.toLowerCase()) ||
      insp.id.toLowerCase().includes(tableSearch.toLowerCase()) ||
      insp.category.toLowerCase().includes(tableSearch.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Top Header & Action Bar */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-subtle">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Officer Command Center
            </h1>
            <Badge variant="blue" className="bg-blue-50 text-blue-800 border-blue-200">
              Active Session
            </Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Evidence-led inspection intelligence under Legal Metrology Act 2009 & Packaged Commodities Rules 2011 • <span className="font-semibold text-slate-700">{selectedDistrict}</span>
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Layers className="w-3.5 h-3.5" />}
            onClick={() => navigate('/inspection/session/LS-2026-1042')}
          >
            Batch Inspection
          </Button>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<FileText className="w-3.5 h-3.5" />}
            onClick={() => navigate('/reports')}
          >
            Notices & Reports
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => navigate('/inspection/new')}
            className="bg-blue-700 hover:bg-blue-800"
          >
            Launch Inspection
          </Button>
        </div>
      </div>

      {/* 6 Primary Metric Cards — Updated for Batch Intelligence & Legal Metrology Enforcement */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          title="Inspection Sessions"
          value={mockDashboardMetrics.inspectionSessions.toLocaleString()}
          subtitle="Batch Shelf Audits"
          change={{ value: "+18.5%", trend: "up", label: "multi-product" }}
          icon={<Layers className="w-4 h-4 text-indigo-700" />}
          iconBg="bg-indigo-50"
          variant="info"
        />

        <MetricCard
          title="Products Screened"
          value={mockDashboardMetrics.productsScreened.toLocaleString()}
          subtitle="Single & Batch Units"
          change={{ value: "+14.2%", trend: "up", label: "surveillance" }}
          icon={<ClipboardCheck className="w-4 h-4 text-blue-700" />}
          iconBg="bg-blue-50"
          variant="info"
        />

        <MetricCard
          title="High Priority"
          value={mockDashboardMetrics.highPriority}
          subtitle="Flagged by Rules"
          change={{ value: "42 items", trend: "neutral", label: "priority queue" }}
          icon={<AlertOctagon className="w-4 h-4 text-red-700" />}
          iconBg="bg-red-50"
          variant="violation"
        />

        <MetricCard
          title="Review Required"
          value={mockDashboardMetrics.reviewRequired}
          subtitle="Specular Glare / OCR"
          change={{ value: "86 pending", trend: "neutral", label: "human review" }}
          icon={<HelpCircle className="w-4 h-4 text-amber-600" />}
          iconBg="bg-amber-50"
          variant="warning"
        />

        <MetricCard
          title="Needs Recapture"
          value={mockDashboardMetrics.needsRecapture}
          subtitle="Occluded PDP Margin"
          change={{ value: "17 items", trend: "neutral", label: "recapture queue" }}
          icon={<Camera className="w-4 h-4 text-orange-600" />}
          iconBg="bg-orange-50"
          variant="warning"
        />

        <MetricCard
          title="Confirmed Violations"
          value={mockDashboardMetrics.confirmedViolations}
          subtitle="Officer Adjudicated"
          change={{ value: "31 Notices", trend: "neutral", label: "Sec 36 action" }}
          icon={<ShieldAlert className="w-4 h-4 text-red-800" />}
          iconBg="bg-red-50"
          variant="violation"
        />
      </div>

      {/* Grid: Compliance Score Trend + Rule Violations Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Section 1: Compliance Trend Over Time */}
        <Card className="lg:col-span-7">
          <CardHeader>
            <div>
              <CardTitle>Compliance Score Over Time</CardTitle>
              <CardDescription>Monthly pass rates & violation volumes across packaging categories</CardDescription>
            </div>
            <Badge variant="green" className="font-mono text-emerald-700">
              <TrendingUp className="w-3 h-3 inline mr-1" />
              +11% YoY Improvement
            </Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-6 gap-2 pt-2">
              {mockComplianceOverTime.map((item, idx) => (
                <div key={idx} className="flex flex-col items-center">
                  <div className="w-full bg-slate-100 rounded-t h-32 flex flex-col justify-end p-1 relative group">
                    {/* Pass Bar */}
                    <div 
                      className="w-full bg-blue-600 rounded-t transition-all group-hover:bg-blue-700 relative"
                      style={{ height: `${item.passRate}%` }}
                    >
                      <span className="opacity-0 group-hover:opacity-100 absolute -top-6 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[10px] font-mono px-1.5 py-0.5 rounded shadow whitespace-nowrap z-10 transition-opacity">
                        {item.passRate}% Pass ({item.violations} Vio)
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] font-semibold text-slate-600 mt-2 text-center truncate w-full">
                    {item.month.split(' ')[0]}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    {item.passRate}%
                  </span>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs text-slate-500">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-xs bg-blue-600 inline-block" />
                  <span>Statutory Pass Rate (%)</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-xs bg-slate-200 inline-block" />
                  <span>Total Inspected Batches</span>
                </span>
              </div>
              <span className="font-mono text-slate-700 font-medium">348 Samples / Aug 2026</span>
            </div>
          </CardContent>
        </Card>

        {/* Section 2: Rule Violation Trends */}
        <Card className="lg:col-span-5">
          <CardHeader>
            <div>
              <CardTitle>Rule Violation Trends</CardTitle>
              <CardDescription>Top statutory non-compliance clauses detected</CardDescription>
            </div>
            <Link to="/analytics" className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-0.5">
              <span>Deep Matrix</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </CardHeader>
          <CardContent className="space-y-3">
            {mockRuleViolationTrends.map((rule, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="font-mono font-bold text-slate-700 bg-slate-100 px-1 rounded text-[10px]">
                      {rule.rule}
                    </span>
                    <span className="text-slate-600 truncate max-w-[170px]">{rule.description}</span>
                  </div>
                  <span className="font-mono font-bold text-slate-900">{rule.count} ({rule.percentage}%)</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div 
                    className={cn(
                      "h-full rounded-full transition-all",
                      rule.severity === 'High' ? "bg-red-500" : "bg-amber-500"
                    )}
                    style={{ width: `${rule.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Grid: Repeat Offender Brands + District Zonal Intelligence */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Section 3: Repeat Brands Intelligence */}
        <Card className="lg:col-span-7">
          <CardHeader>
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-red-600" />
              <div>
                <CardTitle>Repeat Violator Brands Intelligence</CardTitle>
                <CardDescription>Section 36 compounding & enhanced prosecution risk tracking</CardDescription>
              </div>
            </div>
            <Badge variant="red">Sec 36 Enforcement</Badge>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-4">Brand / Entity</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Violations / Total</th>
                    <th className="py-2.5 px-3">Frequent Defect</th>
                    <th className="py-2.5 px-4 text-right">Statutory Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {mockRepeatOffenderBrands.map((b, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/80">
                      <td className="py-3 px-4 font-bold text-slate-900">
                        {b.brand}
                      </td>
                      <td className="py-3 px-3 text-slate-600">{b.category}</td>
                      <td className="py-3 px-3 font-mono">
                        <span className="text-red-600 font-bold">{b.violations}</span>
                        <span className="text-slate-400"> / {b.inspections} ({b.repeatOffenseRate}%)</span>
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

        {/* Section 4: District Intelligence & Zonal Heat */}
        <Card className="lg:col-span-5">
          <CardHeader>
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-blue-600" />
              <div>
                <CardTitle>District Zonal Intelligence</CardTitle>
                <CardDescription>Jurisdiction inspection coverage & officer deployment</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {mockDistrictIntelligence.map((dist, idx) => (
              <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 hover:bg-slate-100/70 transition-colors text-xs">
                <div>
                  <h4 className="font-bold text-slate-900">{dist.district}</h4>
                  <p className="text-slate-500 text-[11px] mt-0.5">
                    {dist.inspections} Inspections • {dist.activeOfficers} Field Officers
                  </p>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 justify-end">
                    <span className="font-mono font-bold text-slate-800">{dist.complianceRate}%</span>
                    <span className="text-[10px] text-slate-500">pass</span>
                  </div>
                  <span className="text-[10px] font-mono text-red-600">
                    {dist.violations} Violations
                  </span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Section 5 & 6: Recent Inspections Table with Live Filter & Seeded Cases */}
      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <CardTitle>Recent Legal Metrology Inspections</CardTitle>
              <Badge variant="slate" className="font-mono">{filteredInspections.length} Records</Badge>
            </div>
            <CardDescription>
              Evidence logs, millimeter measurements, and human-in-the-loop determination statuses
            </CardDescription>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="w-full sm:w-64">
              <Search
                value={tableSearch}
                onChange={(e) => setTableSearch(e.target.value)}
                onClear={() => setTableSearch('')}
                placeholder="Filter by product, brand, ID..."
              />
            </div>
          </div>
        </CardHeader>

        {/* Filter Pills */}
        <div className="px-5 py-2.5 bg-slate-50/70 border-b border-slate-100 flex items-center gap-2 overflow-x-auto">
          <span className="text-xs font-semibold text-slate-500 flex items-center gap-1 shrink-0">
            <Filter className="w-3.5 h-3.5" /> Status:
          </span>
          {statusFilters.map((f) => (
            <button
              key={f.value}
              onClick={() => setSelectedStatusFilter(f.value)}
              className={cn(
                "px-2.5 py-1 rounded-full text-xs font-medium transition-all shrink-0 flex items-center gap-1.5",
                selectedStatusFilter === f.value
                  ? "bg-slate-900 text-white shadow-xs"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
              )}
            >
              <span>{f.label}</span>
              {typeof f.count !== 'undefined' && (
                <span className={cn(
                  "text-[10px] font-mono px-1.5 rounded-full",
                  selectedStatusFilter === f.value ? "bg-slate-700 text-white" : "bg-slate-100 text-slate-600"
                )}>
                  {f.count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Inspection ID</TableHead>
                <TableHead>Product & Packaging</TableHead>
                <TableHead>Brand / Manufacturer</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Stated Qty / MRP</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Inspection Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredInspections.map((insp) => (
                <TableRow key={insp.id}>
                  <TableCell>
                    <Link
                      to={`/inspection/${insp.id}`}
                      className="font-mono font-bold text-blue-700 hover:text-blue-900 hover:underline flex items-center gap-1"
                    >
                      <span>{insp.id}</span>
                      <ArrowUpRight className="w-3 h-3 opacity-60" />
                    </Link>
                  </TableCell>

                  <TableCell className="max-w-[220px]">
                    <div className="truncate font-semibold text-slate-900" title={insp.productName}>
                      {insp.productName}
                    </div>
                    <div className="text-[11px] text-slate-500 font-medium flex items-center gap-1.5">
                      <span>{insp.packagingType}</span>
                      {insp.quietZoneViolation && (
                        <span className="text-[9px] font-mono text-red-600 bg-red-50 px-1 rounded border border-red-200">
                          Quiet-Zone Overlap
                        </span>
                      )}
                      {!insp.minFontHeightCompliant && (
                        <span className="text-[9px] font-mono text-red-600 bg-red-50 px-1 rounded border border-red-200">
                          Font Height Fail
                        </span>
                      )}
                    </div>
                  </TableCell>

                  <TableCell>
                    <div className="font-medium text-slate-900">{insp.brand}</div>
                    <div className="text-[11px] text-slate-400 truncate max-w-[180px]">{insp.manufacturerName}</div>
                  </TableCell>

                  <TableCell>
                    <span className="text-xs text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                      {insp.category}
                    </span>
                  </TableCell>

                  <TableCell className="font-mono text-xs">
                    <div className="font-semibold text-slate-900">{insp.netQuantity}</div>
                    <div className="text-slate-500">₹ {insp.mrp.toFixed(2)}</div>
                  </TableCell>

                  <TableCell>
                    <div className="flex items-center gap-1.5">
                      <span className={cn(
                        "font-mono font-bold text-xs",
                        insp.score >= 85 ? "text-emerald-700" : insp.score >= 60 ? "text-amber-700" : "text-red-700"
                      )}>
                        {insp.score}/100
                      </span>
                    </div>
                  </TableCell>

                  <TableCell>
                    <StatusBadge status={insp.status} size="sm" />
                  </TableCell>

                  <TableCell className="text-xs text-slate-500 font-mono whitespace-nowrap">
                    {insp.inspectionDate}
                  </TableCell>

                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/inspection/${insp.id}`)}
                        className="text-xs h-7 px-2.5"
                      >
                        Inspect
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/evidence/${insp.id}`)}
                        className="text-xs h-7 px-2 text-slate-500"
                        title="View Millimeter Forensic Evidence"
                      >
                        Forensics
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>
    </div>
  );
};
