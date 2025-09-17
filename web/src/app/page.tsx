import DataTable, { type FundRow } from "@/components/DataTable";

type BrapiFund = {
  stock: string;
  name?: string | null;
  close?: number | null;
  change?: number | null;
  volume?: number | null;
  market_cap?: number | null;
  logo?: string | null;
  sector?: string | null;
  type?: string | null;
};

type BrapiQuoteListResponse = {
  stocks: BrapiFund[];
};

export const revalidate = 300; // revalida a cada 5 minutos

async function fetchFunds(): Promise<FundRow[]> {
  const res = await fetch("https://brapi.dev/api/quote/list?type=fund", {
    // cache incremental
    next: { revalidate },
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Falha ao buscar dados (${res.status})`);
  }
  const json = (await res.json()) as BrapiQuoteListResponse;
  const rows: FundRow[] = (json?.stocks ?? []).map((s) => ({
    stock: s.stock,
    name: s.name ?? null,
    close: typeof s.close === "number" ? s.close : null,
    change: typeof s.change === "number" ? s.change : null,
    volume: typeof s.volume === "number" ? s.volume : null,
    market_cap: typeof s.market_cap === "number" ? s.market_cap : null,
    logo: s.logo ?? null,
    sector: s.sector ?? null,
    type: s.type ?? null,
  }));
  return rows;
}

export default async function Home() {
  let data: FundRow[] = [];
  let error: string | null = null;
  try {
    data = await fetchFunds();
  } catch (e) {
    error = e instanceof Error ? e.message : "Erro inesperado";
  }

  return (
    <div className="min-h-screen p-6 sm:p-8 font-sans">
      <div className="max-w-[1200px] mx-auto w-full flex flex-col gap-4">
        <header className="flex items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">Fundos Imobiliários (FIIs)</h1>
            <p className="text-sm opacity-70">
              Fonte: brapi — <a className="underline" href="https://brapi.dev/api/quote/list?type=fund" target="_blank" rel="noreferrer">documentação da consulta</a>
            </p>
          </div>
        </header>

        {error ? (
          <div className="rounded-md border border-red-500/30 bg-red-500/10 p-4 text-sm">
            {error}
          </div>
        ) : (
          <DataTable data={data} />
        )}
      </div>
    </div>
  );
}
