import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useState } from "react";

import type { RouteRecord } from "../lib/types";

type Props = {
  routes: RouteRecord[];
  selectedRoute: RouteRecord | null;
  onSelect: (route: RouteRecord) => void;
};

const columnHelper = createColumnHelper<RouteRecord>();

const columns = [
  columnHelper.accessor("rank", { header: "Rank" }),
  columnHelper.display({
    id: "route",
    header: "Route",
    cell: ({ row }) => `${row.original.origin_iata} → ${row.original.dest_iata}`,
  }),
  columnHelper.accessor("total_score", {
    header: "Score",
    cell: (info) => info.getValue().toFixed(1),
  }),
  columnHelper.accessor("tier", { header: "Tier" }),
  columnHelper.accessor("distance_nm", {
    header: "Distance",
    cell: (info) => `${info.getValue().toFixed(0)} nm`,
  }),
  columnHelper.accessor("time_saved_hr", {
    header: "Time Saved",
    cell: (info) => `${info.getValue().toFixed(1)}h`,
  }),
  columnHelper.accessor("overwater_pct", {
    header: "Overwater",
    cell: (info) => `${(info.getValue() * 100).toFixed(0)}%`,
  }),
  columnHelper.accessor("annual_pax", {
    header: "Annual Pax",
    cell: (info) => info.getValue().toLocaleString(),
  }),
  columnHelper.accessor("estimated_supersonic_revenue_M", {
    header: "Revenue",
    cell: (info) => `$${info.getValue().toFixed(0)}M`,
  }),
];

export function RankingTable({ routes, selectedRoute, onSelect }: Props) {
  const [sorting, setSorting] = useState([{ id: "total_score", desc: true }]);

  const table = useReactTable({
    columns,
    data: routes,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <section className="table-card">
      <div className="panel-header">
        <div>
          <h2>Ranking Table</h2>
          <p>Sortable top-50 output with unified map selection.</p>
        </div>
      </div>
      <div className="table-shell">
        <table>
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id} onClick={header.column.getToggleSortingHandler()}>
                    {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => {
              const route = row.original;
              const isSelected =
                selectedRoute?.origin_iata === route.origin_iata &&
                selectedRoute?.dest_iata === route.dest_iata;

              return (
                <tr
                  key={row.id}
                  className={isSelected ? "selected-row" : undefined}
                  onClick={() => onSelect(route)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

