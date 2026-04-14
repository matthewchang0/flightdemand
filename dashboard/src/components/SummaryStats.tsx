import type { RouteRecord, SummaryStats as SummaryStatsType } from "../lib/types";

type Props = {
  summary: SummaryStatsType | null;
  routes: RouteRecord[];
};

function formatCompactNumber(value: number, suffix = ""): string {
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(1)}B${suffix}`;
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M${suffix}`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K${suffix}`;
  }
  return `${value}${suffix}`;
}

export function SummaryStats({ summary, routes }: Props) {
  const tierOneRoutes = routes.filter((route) => route.tier === "Tier 1").length;
  const overlandUnlocked = routes.filter((route) => route.route_type === "overland" && route.rank <= 50).length;
  const cards = [
    {
      label: "Routes Analyzed",
      value: summary ? formatCompactNumber(summary.total_routes_analyzed) : "--",
      accent: "traffic",
    },
    {
      label: "Tier 1 Routes",
      value: formatCompactNumber(tierOneRoutes),
      accent: "tier1",
    },
    {
      label: "Avg Time Saved",
      value: summary ? `${summary.avg_time_saved_hr.toFixed(1)} hrs` : "--",
      accent: "time",
    },
    {
      label: "Premium Pax Pool",
      value: summary ? formatCompactNumber(summary.total_addressable_premium_pax) : "--",
      accent: "premium",
    },
    {
      label: "Revenue Opportunity",
      value: summary ? `$${summary.total_addressable_revenue_B.toFixed(1)}B` : "--",
      accent: "revenue",
    },
    {
      label: "Overland Routes Unlocked",
      value: summary ? String(summary.overland_routes_unlocked || overlandUnlocked) : "--",
      accent: "time",
    },
    {
      label: "Avg Score",
      value: summary ? summary.avg_score.toFixed(1) : "--",
      accent: "viability",
    },
  ];

  return (
    <section className="summary-grid">
      {cards.map((card) => (
        <article key={card.label} className={`summary-card accent-${card.accent}`}>
          <span className="summary-label">{card.label}</span>
          <strong className="summary-value">{card.value}</strong>
        </article>
      ))}
    </section>
  );
}
