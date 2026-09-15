import type { LucideIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface KPIProps {
  label: string;
  value: string;
  unit: string;
  detail: string;
  icon: LucideIcon;
  loading?: boolean;
}

export function KPI({ label, value, unit, detail, icon: Icon, loading }: KPIProps) {
  return (
    <Card className="min-w-0">
      <CardHeader className="flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
        <Icon className="h-5 w-5 text-green-600" aria-hidden="true" />
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-1.5">
          <span className="text-3xl font-bold tabular-nums">
            {loading ? "—" : value}
          </span>
          <span className="text-sm text-muted-foreground">{unit}</span>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">{detail}</p>
      </CardContent>
    </Card>
  );
}
