import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { useInspections } from '../context/InspectionContext';
import { InspectionStatus } from '../types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Search } from '../components/ui/Search';
import { Badge } from '../components/ui/Badge';
import { 
  History, 
  Filter, 
  ArrowUpRight, 
  Download, 
  Sparkles,
  Calendar,
  Layers,
  SlidersHorizontal,
  RotateCcw,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { cn } from '../utils/cn';

export const InspectionHistory: React.FC = () => {
  const { inspections } = useInspections();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const queryParam = searchParams.get('q') || '';
  const [searchQuery, setSearchQuery] = useState(queryParam);
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedDateFilter, setSelectedDateFilter] = useState<string>('ALL');
  const [minScore, setMinScore] = useState<number>(0);

  useEffect(() => {
    if (queryParam) {
      setSearchQuery(queryParam);
    }
  }, [queryParam]);

  const categories = [
    'ALL', 
    'Food & Grains', 
    'Edible Oils & Fats', 
    'Packaged Snacks', 
    'Dairy & Beverages', 
    'Electronics & Wearables', 
    'Spices & Condiments'
  ];

  const resetFilters = () => {
    setSearchQuery('');
    setSelectedStatus('ALL');
    setSelectedCategory('ALL');
    setSelectedDateFilter('ALL');
    setMinScore(0);
  };

  const filtered = inspections.filter(i => {
    const matchesSearch = searchQuery.trim() === '' ||
      i.productName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      i.brand.toLowerCase().includes(searchQuery.toLowerCase()) ||
      i.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      i.manufacturerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      i.inspectorName.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = selectedStatus === 'ALL' || i.status === selectedStatus;
    const matchesCategory = selectedCategory === 'ALL' || i.category === selectedCategory;
    const matchesScore = i.score >= minScore;

    return matchesSearch && matchesStatus && matchesCategory && matchesScore;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Statutory Inspections Ledger
            </h1>
            <Badge variant="blue">{filtered.length} of {inspections.length} Records</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Tamper-proof audit ledger of calibrated millimeter inspections, OCR readouts, and officer determinations
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
            onClick={resetFilters}
          >
            Reset Filters
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Download className="w-4 h-4" />}
            onClick={() => alert("Exporting filtered inspection ledger to CSV...")}
            className="bg-blue-700 hover:bg-blue-800"
          >
            Export Ledger CSV
          </Button>
        </div>
      </div>

      {/* Advanced Filter Matrix */}
      <Card>
        <CardContent className="p-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {/* Search Input */}
            <div className="lg:col-span-1">
              <Search
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onClear={() => setSearchQuery('')}
                placeholder="Search ID, brand, product, officer..."
              />
            </div>

            {/* Status Filter */}
            <div>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full h-9 rounded-md border border-slate-300 bg-white px-3 text-xs text-slate-800 font-medium focus:border-blue-600 focus:outline-none"
              >
                <option value="ALL">All Statuses</option>
                <option value="Verified">Verified (Compliant)</option>
                <option value="Violation">Statutory Violation</option>
                <option value="Review Required">Review Required (Uncertain)</option>
                <option value="Provisional">Provisional</option>
                <option value="Not Evaluable">Not Evaluable</option>
              </select>
            </div>

            {/* Category Filter */}
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full h-9 rounded-md border border-slate-300 bg-white px-3 text-xs text-slate-800 font-medium focus:border-blue-600 focus:outline-none"
              >
                {categories.map(c => (
                  <option key={c} value={c}>{c === 'ALL' ? 'All Categories' : c}</option>
                ))}
              </select>
            </div>

            {/* Date Filter */}
            <div>
              <select
                value={selectedDateFilter}
                onChange={(e) => setSelectedDateFilter(e.target.value)}
                className="w-full h-9 rounded-md border border-slate-300 bg-white px-3 text-xs text-slate-800 font-medium focus:border-blue-600 focus:outline-none"
              >
                <option value="ALL">All Inspection Dates</option>
                <option value="TODAY">Today (22 Aug 2026)</option>
                <option value="WEEK">Past 7 Days</option>
                <option value="MONTH">August 2026 MTD</option>
              </select>
            </div>
          </div>

          {/* Score Slider Filter */}
          <div className="pt-2 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-3 flex-1 max-w-md">
              <span className="font-semibold text-slate-600 whitespace-nowrap">
                Min Compliance Score: <strong className="font-mono text-slate-900">{minScore}/100</strong>
              </span>
              <input
                type="range"
                min="0"
                max="100"
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
            </div>
            <span className="text-slate-500 font-mono text-[11px]">
              Showing {filtered.length} matching inspection dockets
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Complete Table with 10 Columns */}
      <Card>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Inspection ID</TableHead>
                <TableHead>Product</TableHead>
                <TableHead>Brand</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Inspection Date</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Officer</TableHead>
                <TableHead>Violations</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((insp) => {
                const violationCount = insp.findings.filter(f => f.status === 'Fail').length;
                return (
                  <TableRow
                    key={insp.id}
                    onClick={() => navigate(`/inspection/${insp.id}`)}
                    className="cursor-pointer hover:bg-blue-50/40"
                  >
                    <TableCell>
                      <Link
                        to={`/inspection/${insp.id}`}
                        onClick={(e) => e.stopPropagation()}
                        className="font-mono font-bold text-blue-700 hover:underline flex items-center gap-1 text-xs"
                      >
                        <span>{insp.id}</span>
                        <ArrowUpRight className="w-3 h-3 opacity-60" />
                      </Link>
                    </TableCell>

                    <TableCell className="max-w-[190px]">
                      <div className="font-semibold text-slate-900 truncate text-xs" title={insp.productName}>
                        {insp.productName}
                      </div>
                      <div className="text-[11px] text-slate-400 font-medium">{insp.packagingType} • {insp.netQuantity}</div>
                    </TableCell>

                    <TableCell>
                      <span className="font-bold text-slate-900 text-xs">{insp.brand}</span>
                    </TableCell>

                    <TableCell className="text-xs text-slate-600">
                      {insp.category}
                    </TableCell>

                    <TableCell className="text-xs text-slate-500 font-mono whitespace-nowrap">
                      {insp.inspectionDate}
                    </TableCell>

                    <TableCell className="text-xs text-slate-600 max-w-[130px] truncate" title={insp.gpsCoordinates?.locationName || insp.district}>
                      {insp.gpsCoordinates?.locationName || insp.district}
                    </TableCell>

                    <TableCell>
                      <span className={cn(
                        "font-mono font-bold text-xs",
                        insp.score >= 85 ? "text-emerald-700" : insp.score >= 60 ? "text-amber-700" : "text-red-700"
                      )}>
                        {insp.score}/100
                      </span>
                    </TableCell>

                    <TableCell>
                      <StatusBadge status={insp.status} size="sm" />
                    </TableCell>

                    <TableCell className="text-xs text-slate-700 whitespace-nowrap">
                      {insp.inspectorName.split(' ')[1] || insp.inspectorName} ({insp.inspectorBadge.split('-')[3] || 'KA'})
                    </TableCell>

                    <TableCell>
                      {violationCount > 0 ? (
                        <span className="font-mono text-xs font-bold text-red-700 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                          {violationCount} Defect{violationCount > 1 ? 's' : ''}
                        </span>
                      ) : (
                        <span className="font-mono text-[11px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          Zero Breaches
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </Card>
    </div>
  );
};
