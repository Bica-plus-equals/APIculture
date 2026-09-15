// "use client";

// import dynamic from "next/dynamic";
// import { CloudRain, RefreshCw, Thermometer, Wind } from "lucide-react";

// import { useDashboard } from "@/components/DashboardContext";
// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// import { KPI } from "@/components/ui/KPI";

// const Map = dynamic(
//   () => import("@/components/ui/MapView").then((module) => module.Map),
//   {
//     ssr: false,
//     loading: () => <div className="h-[460px] animate-pulse rounded-lg bg-muted" />,
//   },
// );

// function formatDate(date: string): string {
//   return new Intl.DateTimeFormat("en", {
//     day: "numeric",
//     month: "short",
//     year: "numeric",
//     timeZone: "UTC",
//   }).format(new Date(`${date}T00:00:00Z`));
// }

// export default function Home() {
//   const { selectedDate, inference, loading, error, retry } = useDashboard();
//   const climate = inference?.climate;
//   const statistics = inference?.statistics;

//   return (
//     <div className="mx-auto max-w-7xl">
//       <header className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
//         <div>
//           <p className="text-sm font-medium text-green-700">Climate inference</p>
//           <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">
//             Pollination forecast
//           </h2>
//           <p className="mt-1 text-sm text-muted-foreground">
//             Prediction date: {formatDate(selectedDate)}
//           </p>
//         </div>
//         {inference?.is_placeholder && (
//           <span className="w-fit rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
//             Placeholder model data
//           </span>
//         )}
//       </header>

//       {error && (
//         <div role="alert" className="mb-6 flex flex-col gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-900 sm:flex-row sm:items-center sm:justify-between">
//           <div>
//             <p className="font-semibold">The Python API could not be reached.</p>
//             <p className="mt-1 break-words text-xs">{error}</p>
//           </div>
//           <button type="button" onClick={retry} className="flex w-fit items-center gap-2 rounded-md border border-red-300 px-3 py-2 font-medium hover:bg-red-100">
//             <RefreshCw className="h-4 w-4" aria-hidden="true" /> Retry
//           </button>
//         </div>
//       )}

//       <section aria-label="Climate forecast" className="grid gap-4 md:grid-cols-3">
//         <KPI
//           label="Temperature"
//           value={climate?.temperature_c.toFixed(1) ?? "—"}
//           unit="°C"
//           detail="Placeholder daily mean"
//           icon={Thermometer}
//           loading={loading && !inference}
//         />
//         <KPI
//           label="Precipitation"
//           value={climate?.precipitation_mm.toFixed(1) ?? "—"}
//           unit="mm"
//           detail="Placeholder accumulated estimate"
//           icon={CloudRain}
//           loading={loading && !inference}
//         />
//         <KPI
//           label="Wind"
//           value={climate?.wind_kph.toFixed(1) ?? "—"}
//           unit="km/h"
//           detail="Placeholder mean wind speed"
//           icon={Wind}
//           loading={loading && !inference}
//         />
//       </section>

//       <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
//         <Card className="overflow-hidden">
//           <CardHeader className="flex-row items-center justify-between">
//             <div>
//               <CardTitle>Predicted raster preview</CardTitle>
//               <p className="mt-1 text-sm text-muted-foreground">
//                 JSON grid placeholder; replace with the CNN GeoTIFF or tile layer later.
//               </p>
//             </div>
//             {loading && <RefreshCw className="h-4 w-4 animate-spin text-green-600" aria-label="Loading inference" />}
//           </CardHeader>
//           <CardContent>
//             <Map cells={inference?.raster_cells ?? []} />
//           </CardContent>
//         </Card>

//         <Card>
//           <CardHeader>
//             <CardTitle>Pollination statistics</CardTitle>
//             <p className="text-sm text-muted-foreground">
//               Output reserved for spatial calculations and clustering.
//             </p>
//           </CardHeader>
//           <CardContent>
//             <dl className="divide-y">
//               <Statistic label="Area" value={statistics ? `${statistics.area_hectares.toFixed(1)} ha` : "—"} />
//               <Statistic label="Pollinizable area" value={statistics ? `${statistics.pollinizable_area_hectares.toFixed(1)} ha` : "—"} />
//               <Statistic label="Average pollination period" value={statistics ? `${statistics.average_pollination_period_days.toFixed(1)} days` : "—"} />
//               <Statistic label="Clusters" value={statistics ? statistics.clusters.toString() : "—"} />
//             </dl>
//             <div className="mt-5 rounded-md bg-muted p-3 text-xs text-muted-foreground">
//               Model: {inference?.model_name ?? "Waiting for API"}
//             </div>
//           </CardContent>
//         </Card>
//       </div>
//     </div>
//   );
// }

// function Statistic({ label, value }: { label: string; value: string }) {
//   return (
//     <div className="flex items-center justify-between gap-4 py-3">
//       <dt className="text-sm text-muted-foreground">{label}</dt>
//       <dd className="text-right text-sm font-semibold tabular-nums">{value}</dd>
//     </div>
//   );
// }

///VERSION 2

// "use client";

// import dynamic from "next/dynamic";

// import { useDashboard } from "@/components/DashboardContext";
// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// const Map = dynamic(
//   () => import("@/components/ui/MapView").then((module) => module.Map),
//   {
//     ssr: false,
//     loading: () => <div className="h-[460px] animate-pulse rounded-lg bg-muted" />,
//   },
// );

// export default function Home() {
//   const dashboard = useDashboard();

//   if (!dashboard) return null;

//   const { selectedDate } = dashboard;

//   return (
//     <div className="mx-auto max-w-7xl">
//       <header className="mb-6">
//         <h2 className="text-2xl font-bold tracking-tight">
//           Biomass Dashboard
//         </h2>

//         <p className="mt-1 text-sm text-muted-foreground">
//           Selected date: {selectedDate || "No date selected"}
//         </p>
//       </header>

//       <Card>
//         <CardHeader>
//           <CardTitle>Satellite raster</CardTitle>
//         </CardHeader>

//         <CardContent>
//           <Map />
//         </CardContent>
//       </Card>
//     </div>
//   );
// }

"use client";

import dynamic from "next/dynamic";
import { CloudRain, Thermometer, Wind } from "lucide-react";
import { useMemo } from "react";

import { useDashboard } from "@/components/DashboardContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { KPI } from "@/components/ui/KPI";
import type { RasterCell } from "@/lib/dashboard-types";

const Map = dynamic(() => import("@/components/ui/MapView").then((module) => module.Map), {
  ssr: false,
  loading: () => <div className="h-[460px] animate-pulse rounded-lg bg-slate-100" />,
});

const FARM_SOUTH = 45.01;
const FARM_WEST = 28.0;
const FARM_NORTH = 45.03;
const FARM_EAST = 28.035;

function formatDate(date: string): string {
  if (!date) {
    return "Today";
  }

  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${date}T00:00:00Z`));
}

function generateCells(selectedDate: string): RasterCell[] {
  const day = selectedDate ? new Date(`${selectedDate}T00:00:00Z`).getUTCDate() : 1;
  const rows = 5;
  const columns = 6;
  const latitudeStep = (FARM_NORTH - FARM_SOUTH) / rows;
  const longitudeStep = (FARM_EAST - FARM_WEST) / columns;
  const cells: RasterCell[] = [];

  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      const value =
        0.18 +
        0.17 * Math.sin((row + 1) * 1.7) +
        0.12 * Math.cos((column + 2) * 1.25) +
        0.12 * Math.sin((day / 5) + row - column * 0.5);

      cells.push({
        south: Number((FARM_SOUTH + row * latitudeStep).toFixed(6)),
        west: Number((FARM_WEST + column * longitudeStep).toFixed(6)),
        north: Number((FARM_SOUTH + (row + 1) * latitudeStep).toFixed(6)),
        east: Number((FARM_WEST + (column + 1) * longitudeStep).toFixed(6)),
        value: Number(Math.min(0.96, Math.max(0.12, value)).toFixed(3)),
      });
    }
  }

  return cells;
}

export default function Home() {
  const { selectedDate } = useDashboard();

  const weather = useMemo(() => {
    const base = selectedDate ? new Date(`${selectedDate}T00:00:00Z`).getTime() : Date.now();
    const seed = base / 86400000;

    return {
      temperature: 22 + Math.sin(seed * 0.8) * 5.5,
      precipitation: 18 + Math.cos(seed * 0.6) * 7,
      wind: 14 + Math.sin(seed * 0.9 + 1.2) * 4.5,
    };
  }, [selectedDate]);

  const statistics = useMemo(
    () => ({
      area: 1248.7,
      pollinizableArea: 893.2,
      averagePollinationPeriod: 14.8,
      clusters: 9,
    }),
    [selectedDate],
  );

  const rasterCells = useMemo(() => generateCells(selectedDate), [selectedDate]);

  return (
    <div className="mx-auto max-w-7xl">
      <header className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-emerald-700">Field overview</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Biomass Dashboard</h2>
          <p className="mt-1 text-sm text-slate-500">Observation date: {formatDate(selectedDate)}</p>
        </div>
      </header>

      <section aria-label="Weather KPIs" className="grid gap-4 md:grid-cols-3">
        <KPI
          label="Temperature"
          value={weather.temperature.toFixed(1)}
          unit="°C"
          detail="Surface thermal status"
          icon={Thermometer}
        />
        <KPI
          label="Precipitation"
          value={weather.precipitation.toFixed(1)}
          unit="mm"
          detail="Rainfall estimate"
          icon={CloudRain}
        />
        <KPI
          label="Wind"
          value={weather.wind.toFixed(1)}
          unit="km/h"
          detail="Average wind speed"
          icon={Wind}
        />
      </section>

      <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(300px,1fr)]">
        <Card className="overflow-hidden border-slate-200 bg-white">
          <CardHeader className="flex-row items-center justify-between gap-3">
            <div>
              <CardTitle className="text-xl text-slate-900">Raster coverage</CardTitle>
              <p className="mt-1 text-sm text-slate-500">Estimated biomass index across the monitored field.</p>
            </div>
          </CardHeader>
          <CardContent>
            <Map cells={rasterCells} />
          </CardContent>
        </Card>

        <Card className="border-slate-200 bg-white">
          <CardHeader>
            <CardTitle className="text-xl text-slate-900">Statistics</CardTitle>
            <p className="mt-1 text-sm text-slate-500">Survey summary for the selected observation window.</p>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3">
              <StatisticRow label="Area" value={`${statistics.area.toFixed(1)} ha`} />
              <StatisticRow label="Pollinizable area" value={`${statistics.pollinizableArea.toFixed(1)} ha`} />
              <StatisticRow label="Avg. pollination period" value={`${statistics.averagePollinationPeriod.toFixed(1)} days`} />
              <StatisticRow label="Clusters" value={statistics.clusters.toString()} />
            </dl>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatisticRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-200 pb-3 last:border-b-0 last:pb-0">
      <dt className="text-sm text-slate-500">{label}</dt>
      <dd className="text-right text-sm font-semibold text-slate-900">{value}</dd>
    </div>
  );
}