// import "./globals.css";
// import { DashboardProvider } from "@/components/DashboardContext";
// import { Sidebar } from "@/components/ui/Sidebar";

// export const metadata = {
//   title: "Climate & Pollination Dashboard",
//   description: "Date-driven climate, raster, and pollination inference prototype",
// };

// export default function RootLayout({ children }: { children: React.ReactNode }) {
//   return (
//     <html lang="en">
//       <body className="min-h-screen bg-gray-50">
//         <DashboardProvider>
//           <div className="flex min-h-screen flex-col lg:flex-row">
//             <Sidebar />
//             <main className="min-w-0 flex-1 p-4 sm:p-6 lg:p-8">{children}</main>
//           </div>
//         </DashboardProvider>
//       </body>
//     </html>
//   );
// }

import "./globals.css";

import { DashboardProvider } from "@/components/DashboardContext";
import { Sidebar } from "@/components/ui/Sidebar";

export const metadata = {
  title: "Biomass Dashboard",
  description: "Geospatial biomass dashboard prototype",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-100 text-slate-900">
        <DashboardProvider>
          <div className="flex min-h-screen flex-col lg:flex-row">
            <Sidebar />
            <main className="min-w-0 flex-1 p-4 sm:p-6 lg:p-8">{children}</main>
          </div>
        </DashboardProvider>
      </body>
    </html>
  );
}