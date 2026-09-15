// "use client";

// import Link from "next/link";
// import { BarChart, CalendarDays, Leaf, LoaderCircle, Map, Settings } from "lucide-react";

// import { useDashboard } from "@/components/DashboardContext";

// export function Sidebar() {
//   const { selectedDate, setSelectedDate, loading } = useDashboard();

//   return (
//     <aside className="w-full shrink-0 border-b bg-white p-4 shadow-sm lg:min-h-screen lg:w-64 lg:border-b-0 lg:border-r">
//       <div className="mb-6 flex items-center gap-2">
//         <Leaf className="h-6 w-6 text-green-600" />
//         <div>
//           <h1 className="text-lg font-semibold">Pollination</h1>
//           <p className="text-xs text-muted-foreground">Inference prototype</p>
//         </div>
//       </div>

//       <nav className="flex gap-4 lg:flex-col">
//         <Link href="/" className="flex items-center gap-2 text-gray-700 hover:text-green-600">
//           <BarChart className="h-5 w-5" /> Dashboard
//         </Link>

//         <Link href="/map" className="flex items-center gap-2 text-gray-700 hover:text-green-600">
//           <Map className="h-5 w-5" /> Map
//         </Link>

//         <Link href="/settings" className="flex items-center gap-2 text-gray-700 hover:text-green-600">
//           <Settings className="h-5 w-5" /> Settings
//         </Link>
//       </nav>

//       <div className="mt-6 border-t pt-5">
//         <label htmlFor="inference-date" className="mb-2 flex items-center gap-2 text-sm font-medium">
//           <CalendarDays className="h-4 w-4 text-green-600" aria-hidden="true" />
//           Prediction date
//         </label>
//         <input
//           id="inference-date"
//           type="date"
//           value={selectedDate}
//           onChange={(event) => setSelectedDate(event.target.value)}
//           className="w-full rounded-md border bg-white px-3 py-2 text-sm shadow-sm outline-none focus:border-green-600 focus:ring-2 focus:ring-green-600/20"
//         />
//         <p className="mt-2 flex items-center gap-1.5 text-xs text-muted-foreground">
//           {loading && <LoaderCircle className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />}
//           {loading ? "Running placeholder inference…" : "Change the date to run again."}
//         </p>
//       </div>
//     </aside>
//   );
// }

"use client";

import Link from "next/link";
import { BarChart, CalendarDays, Leaf, Map, Settings } from "lucide-react";

import { useDashboard } from "@/components/DashboardContext";

export function Sidebar() {
  const { selectedDate, setSelectedDate } = useDashboard();

  return (
    <aside className="w-full shrink-0 border-b bg-white p-4 shadow-sm lg:min-h-screen lg:w-72 lg:border-b-0 lg:border-r">
      <div className="mb-6 flex items-center gap-2">
        <Leaf className="h-7 w-7 text-green-600" />
        <div>
          <h1 className="text-lg font-semibold text-slate-900">Biomass</h1>
          <p className="text-xs text-slate-500">Spatial monitoring</p>
        </div>
      </div>

      <nav className="flex gap-4 lg:flex-col">
        <Link href="/" className="flex items-center gap-2 rounded-md px-2 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-green-700">
          <BarChart className="h-4 w-4" />
          Dashboard
        </Link>

        <Link href="/map" className="flex items-center gap-2 rounded-md px-2 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-green-700">
          <Map className="h-4 w-4" />
          Map
        </Link>

        <Link href="/settings" className="flex items-center gap-2 rounded-md px-2 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-green-700">
          <Settings className="h-4 w-4" />
          Settings
        </Link>
      </nav>

      <div className="mt-6 border-t border-slate-200 pt-5">
        <label htmlFor="raster-date" className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-700">
          <CalendarDays className="h-4 w-4 text-green-600" aria-hidden="true" />
          Observation date
        </label>

        <input
          id="raster-date"
          type="date"
          value={selectedDate}
          onChange={(event) => setSelectedDate(event.target.value)}
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-500/20"
        />
      </div>
    </aside>
  );
}