export interface WeatherSnapshot {
  temperature: number;
  precipitation: number;
  wind: number;
}

export interface DashboardStatistics {
  area: number;
  pollinizableArea: number;
  averagePollinationPeriod: number;
  clusters: number;
}

export interface RasterCell {
  south: number;
  west: number;
  north: number;
  east: number;
  value: number;
}

export interface InferenceResponse {
  selectedDate: string;
  climate: WeatherSnapshot;
  statistics: DashboardStatistics;
  rasterCells: RasterCell[];
}
