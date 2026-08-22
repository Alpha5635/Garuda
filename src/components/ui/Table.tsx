import React from 'react';
import { cn } from '../../utils/cn';

export interface TableProps extends React.TableHTMLAttributes<HTMLTableElement> {
  containerClassName?: string;
}

export const Table: React.FC<TableProps> = ({ className, containerClassName, children, ...props }) => (
  <div className={cn("w-full overflow-x-auto border border-slate-200 rounded-lg bg-white shadow-subtle", containerClassName)}>
    <table className={cn("w-full text-left text-sm text-slate-700 divide-y divide-slate-200", className)} {...props}>
      {children}
    </table>
  </div>
);

export const TableHeader: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({ className, children, ...props }) => (
  <thead className={cn("bg-slate-50 text-xs uppercase font-semibold text-slate-600 tracking-wider", className)} {...props}>
    {children}
  </thead>
);

export const TableBody: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({ className, children, ...props }) => (
  <tbody className={cn("divide-y divide-slate-100 bg-white", className)} {...props}>
    {children}
  </tbody>
);

export const TableRow: React.FC<React.HTMLAttributes<HTMLTableRowElement>> = ({ className, children, ...props }) => (
  <tr className={cn("hover:bg-slate-50/80 transition-colors group", className)} {...props}>
    {children}
  </tr>
);

export const TableHead: React.FC<React.ThHTMLAttributes<HTMLTableCellElement>> = ({ className, children, ...props }) => (
  <th className={cn("px-4 py-3 font-semibold text-slate-700 whitespace-nowrap text-xs", className)} {...props}>
    {children}
  </th>
);

export const TableCell: React.FC<React.TdHTMLAttributes<HTMLTableCellElement>> = ({ className, children, ...props }) => (
  <td className={cn("px-4 py-3.5 whitespace-nowrap text-sm", className)} {...props}>
    {children}
  </td>
);
