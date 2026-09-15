// "use client";

// import {
//   createContext,
//   useCallback,
//   useContext,
//   useEffect,
//   useMemo,
//   useState,
//   type ReactNode,
// } from "react";

// import { requestInference } from "@/lib/api";
// import type { InferenceResponse } from "@/lib/dashboard-types";

// interface DashboardContextValue {
//   selectedDate: string;
//   setSelectedDate: (date: string) => void;
//   inference: InferenceResponse | null;
//   loading: boolean;
//   error: string | null;
//   retry: () => void;
// }

// const DashboardContext = createContext<DashboardContextValue | null>(null);

// function todayAsInputDate(): string {
//   const now = new Date();
//   const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
//   return localDate.toISOString().slice(0, 10);
// }

// export function DashboardProvider({ children }: { children: ReactNode }) {
//   const [selectedDate, setSelectedDate] = useState(todayAsInputDate);
//   const [inference, setInference] = useState<InferenceResponse | null>(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);
//   const [retryNumber, setRetryNumber] = useState(0);

//   const selectDate = useCallback((date: string) => {
//     setSelectedDate(date);
//     setLoading(true);
//     setError(null);
//   }, []);

//   const retry = useCallback(() => {
//     setLoading(true);
//     setError(null);
//     setRetryNumber((current) => current + 1);
//   }, []);

//   useEffect(() => {
//     if (!selectedDate) return;

//     const controller = new AbortController();

//     requestInference(selectedDate, controller.signal)
//       .then(setInference)
//       .catch((requestError: unknown) => {
//         if (requestError instanceof DOMException && requestError.name === "AbortError") {
//           return;
//         }
//         setError(
//           requestError instanceof Error
//             ? requestError.message
//             : "The inference request failed.",
//         );
//       })
//       .finally(() => {
//         if (!controller.signal.aborted) setLoading(false);
//       });

//     return () => controller.abort();
//   }, [selectedDate, retryNumber]);

//   const value = useMemo(
//     () => ({ selectedDate, setSelectedDate: selectDate, inference, loading, error, retry }),
//     [selectedDate, selectDate, inference, loading, error, retry],
//   );

//   return (
//     <DashboardContext.Provider value={value}>
//       {children}
//     </DashboardContext.Provider>
//   );
// }

// export function useDashboard() {
//   const context = useContext(DashboardContext);
//   if (!context) {
//     throw new Error("useDashboard must be used inside DashboardProvider.");
//   }
//   return context;
// }





"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

type DashboardContextValue = {
  selectedDate: string;
  setSelectedDate: (date: string) => void;
};

const DashboardContext = createContext<DashboardContextValue | null>(null);

function todayAsInputDate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [selectedDate, setSelectedDate] = useState(todayAsInputDate);

  const value = useMemo(
    () => ({
      selectedDate,
      setSelectedDate,
    }),
    [selectedDate],
  );

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export function useDashboard() {
  const context = useContext(DashboardContext);

  if (!context) {
    throw new Error("useDashboard must be used inside DashboardProvider.");
  }

  return context;
}