"use client";

import type { ComponentProps } from "react";
import { MapContainer, Rectangle, TileLayer, Tooltip } from "react-leaflet";

import type { RasterCell } from "@/lib/dashboard-types";

interface MapProps {
  cells: RasterCell[];
}

function cellColor(value: number): string {
  if (value >= 0.75) return "#166534";
  if (value >= 0.55) return "#65a30d";
  if (value >= 0.35) return "#eab308";
  return "#dc2626";
}

export function Map({ cells }: MapProps) {
  // react-leaflet relies on the optional @types/leaflet package for these
  // options. The unknown cast keeps the prototype type-safe without using any.
  const mapOptions = {
    center: [45.02, 28.017],
    zoom: 14,
    scrollWheelZoom: true,
    className: "h-full w-full",
  } as unknown as ComponentProps<typeof MapContainer>;

  const tileOptions = {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  } as unknown as ComponentProps<typeof TileLayer>;

  return (
    <div className="h-[460px] w-full overflow-hidden rounded-lg">
      <MapContainer {...mapOptions}>
        <TileLayer {...tileOptions} />
        {cells.map((cell, index) => (
          <Rectangle
            key={`${cell.south}-${cell.west}-${index}`}
            bounds={[
              [cell.south, cell.west],
              [cell.north, cell.east],
            ]}
            pathOptions={{
              color: cellColor(cell.value),
              fillColor: cellColor(cell.value),
              fillOpacity: 0.62,
              opacity: 0.25,
              weight: 1,
            }}
          >
            <Tooltip>Placeholder raster value: {cell.value.toFixed(3)}</Tooltip>
          </Rectangle>
        ))}
      </MapContainer>
    </div>
  );
}
