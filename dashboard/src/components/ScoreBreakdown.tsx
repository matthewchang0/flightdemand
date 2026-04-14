import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";

import type { RouteRecord } from "../lib/types";

type Props = {
  route: RouteRecord;
};

function tierColor(tier: RouteRecord["tier"]) {
  switch (tier) {
    case "Tier 1":
      return "var(--tier-1)";
    case "Tier 2":
      return "var(--tier-2)";
    case "Tier 3":
      return "var(--tier-3)";
    default:
      return "var(--tier-4)";
  }
}

export function ScoreBreakdown({ route }: Props) {
  const data = [
    { metric: "Traffic", score: (route.traffic_score / 25) * 100 },
    { metric: "Premium", score: (route.premium_demand_score / 20) * 100 },
    { metric: "Time", score: (route.time_savings_score / 25) * 100 },
    { metric: "Viability", score: (route.viability_score / 15) * 100 },
    { metric: "Revenue", score: (route.revenue_score / 15) * 100 },
  ];

  return (
    <section className="detail-card">
      <div className="card-title-group">
        <h3>Score Breakdown</h3>
        <span>{route.total_score.toFixed(1)} / 100</span>
      </div>
      <div className="radar-shell">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data}>
            <PolarGrid stroke="rgba(139,149,173,0.18)" />
            <PolarAngleAxis dataKey="metric" tick={{ fill: "#cbd5e1", fontSize: 12 }} />
            <Radar
              dataKey="score"
              stroke={tierColor(route.tier)}
              fill={tierColor(route.tier)}
              fillOpacity={0.35}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

