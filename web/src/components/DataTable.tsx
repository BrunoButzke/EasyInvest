"use client";

import { useMemo, useState } from "react";
import Image from "next/image";

export type FundRow = {
  stock: string;
  name: string | null;
  close: number | null;
  change: number | null;
  volume: number | null;
  market_cap: number | null;
  logo: string | null;
  sector: string | null;
  type: string | null;
};

type SortDirection = "asc" | "desc";
type SortState = { key: keyof FundRow | null; direction: SortDirection };

const numberFormat = new Intl.NumberFormat("pt-BR", {
  maximumFractionDigits: 2,
});

const percentFormat = new Intl.NumberFormat("pt-BR", {
  maximumFractionDigits: 2,
  minimumFractionDigits: 2,
});

const columns: Array<{
  key: keyof FundRow;
  label: string;
  numeric?: boolean;
  sortable?: boolean;
}> = [
  { key: "logo", label: "Logo", sortable: false },
  { key: "stock", label: "Ticker", sortable: true },
  { key: "name", label: "Nome", sortable: true },
  { key: "sector", label: "Setor", sortable: true },
  { key: "type", label: "Tipo", sortable: true },
  { key: "close", label: "Preço (R$)", numeric: true, sortable: true },
  { key: "change", label: "Variação (%)", numeric: true, sortable: true },
  { key: "volume", label: "Volume", numeric: true, sortable: true },
  { key: "market_cap", label: "Market Cap", numeric: true, sortable: true },
];

function compareValues(
  a: unknown,
  b: unknown,
  direction: SortDirection,
  numeric: boolean
) {
  // Handle null/undefined consistently
  const aIsNil = a === null || a === undefined || (a as any) === "";
  const bIsNil = b === null || b === undefined || (b as any) === "";
  if (aIsNil && bIsNil) return 0;
  if (aIsNil) return direction === "asc" ? 1 : -1; // nils last in asc, first in desc
  if (bIsNil) return direction === "asc" ? -1 : 1;

  if (numeric) {
    const an = Number(a);
    const bn = Number(b);
    if (an === bn) return 0;
    return direction === "asc" ? an - bn : bn - an;
  }
  const as = String(a).toLocaleLowerCase();
  const bs = String(b).toLocaleLowerCase();
  if (as === bs) return 0;
  return direction === "asc" ? (as < bs ? -1 : 1) : (as > bs ? -1 : 1);
}

export default function DataTable({ data }: { data: FundRow[] }) {
  const [sort, setSort] = useState<SortState>({ key: null, direction: "desc" });

  const sorted = useMemo(() => {
    if (!sort.key) return data;
    const col = columns.find((c) => c.key === sort.key);
    const numeric = Boolean(col?.numeric);
    const clone = [...data];
    clone.sort((r1, r2) =>
      compareValues(r1[sort.key!], r2[sort.key!], sort.direction, numeric)
    );
    return clone;
  }, [data, sort]);

  function onSortClick(key: keyof FundRow, sortable?: boolean) {
    if (!sortable) return;
    setSort((prev) => {
      if (prev.key === key) {
        return {
          key,
          direction: prev.direction === "desc" ? "asc" : "desc",
        };
      }
      // default to DESC to atender "maior para menor"
      return { key, direction: "desc" };
    });
  }

  return (
    <div className="w-full overflow-auto rounded-lg border border-black/10 dark:border-white/10">
      <table className="min-w-full border-collapse">
        <thead className="sticky top-0 bg-background text-foreground z-10">
          <tr>
            {columns.map((c) => {
              const isActive = sort.key === c.key;
              const isSortable = c.sortable !== false;
              return (
                <th
                  key={c.key as string}
                  className={
                    "px-3 py-2 text-left text-sm font-semibold border-b border-black/10 dark:border-white/10 whitespace-nowrap " +
                    (isSortable ? "cursor-pointer select-none" : "")
                  }
                  onClick={() => onSortClick(c.key, isSortable)}
                >
                  <span className="inline-flex items-center gap-1">
                    {c.label}
                    {isSortable && (
                      <span className="text-xs opacity-70">
                        {isActive ? (sort.direction === "desc" ? "▼" : "▲") : "⇅"}
                      </span>
                    )}
                  </span>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr
              key={row.stock}
              className="odd:bg-black/[.03] dark:odd:bg-white/[.03] hover:bg-black/[.06] dark:hover:bg-white/[.06] transition-colors"
            >
              {/* Logo */}
              <td className="px-3 py-2 align-middle border-b border-black/10 dark:border-white/10">
                {row.logo ? (
                  <Image
                    src={row.logo}
                    alt={row.stock}
                    width={24}
                    height={24}
                    className="rounded"
                  />)
                : (
                  <div className="w-6 h-6 rounded bg-black/10 dark:bg-white/10" />
                )}
              </td>
              {/* Ticker */}
              <td className="px-3 py-2 align-middle font-mono text-xs border-b border-black/10 dark:border-white/10">
                {row.stock}
              </td>
              {/* Nome */}
              <td className="px-3 py-2 align-middle border-b border-black/10 dark:border-white/10">
                {row.name ?? "—"}
              </td>
              {/* Setor */}
              <td className="px-3 py-2 align-middle border-b border-black/10 dark:border-white/10">
                {row.sector ?? "—"}
              </td>
              {/* Tipo */}
              <td className="px-3 py-2 align-middle border-b border-black/10 dark:border-white/10">
                {row.type ?? "—"}
              </td>
              {/* Preço */}
              <td className="px-3 py-2 align-middle text-right tabular-nums border-b border-black/10 dark:border-white/10">
                {typeof row.close === "number" ? numberFormat.format(row.close) : "—"}
              </td>
              {/* Variação */}
              <td className="px-3 py-2 align-middle text-right tabular-nums border-b border-black/10 dark:border-white/10">
                {typeof row.change === "number" ? (
                  <span className={row.change > 0 ? "text-green-600" : row.change < 0 ? "text-red-600" : undefined}>
                    {percentFormat.format(row.change)}%
                  </span>
                ) : (
                  "—"
                )}
              </td>
              {/* Volume */}
              <td className="px-3 py-2 align-middle text-right tabular-nums border-b border-black/10 dark:border-white/10">
                {typeof row.volume === "number" ? numberFormat.format(row.volume) : "—"}
              </td>
              {/* Market Cap */}
              <td className="px-3 py-2 align-middle text-right tabular-nums border-b border-black/10 dark:border-white/10">
                {typeof row.market_cap === "number" ? numberFormat.format(row.market_cap) : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


