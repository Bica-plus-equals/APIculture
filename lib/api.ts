// import type { InferenceResponse } from "@/lib/dashboard-types";

// const API_BASE_URL =
//   process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// export async function requestInference(
//   selectedDate: string,
//   signal?: AbortSignal,
// ): Promise<InferenceResponse> {
//   const response = await fetch(`${API_BASE_URL}/api/v1/inference`, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({ date: selectedDate }),
//     signal,
//   });

//   if (!response.ok) {
//     const detail = await response.text();
//     throw new Error(
//       `Inference request failed (${response.status}). ${detail}`.trim(),
//     );
//   }

//   return (await response.json()) as InferenceResponse;
// }


export async function requestRaster(selectedDate: string) {
    const response = await fetch(
        `http://localhost:8000/api/raster?date=${selectedDate}`
    );

    return await response.blob();
}