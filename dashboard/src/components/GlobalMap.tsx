import type { RouteRecord } from "../lib/types";

type Props = {
  routes: RouteRecord[];
  selectedRoute: RouteRecord | null;
  onSelect: (route: RouteRecord) => void;
};

function project(lat: number, lon: number, width: number, height: number) {
  const x = ((lon + 180) / 360) * width;
  const y = ((90 - lat) / 180) * height;
  return { x, y };
}

function buildArc(route: RouteRecord, width: number, height: number) {
  const start = project(route.origin_lat, route.origin_lon, width, height);
  const end = project(route.dest_lat, route.dest_lon, width, height);
  const midX = (start.x + end.x) / 2;
  const midY = (start.y + end.y) / 2;
  const curvature = Math.max(30, Math.min(140, route.distance_nm / 40));
  const controlY = midY - curvature;
  return `M ${start.x} ${start.y} Q ${midX} ${controlY} ${end.x} ${end.y}`;
}

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

export function GlobalMap({ routes, selectedRoute, onSelect }: Props) {
  const width = 820;
  const height = 440;

  return (
    <section className="map-card">
      <div className="panel-header">
        <div>
          <h2>Global Opportunity Map</h2>
          <p>Top-ranked routes rendered as great-circle-inspired arcs.</p>
        </div>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="global-map" role="img" aria-label="Global route map">
        <defs>
          <radialGradient id="mapGlow" cx="50%" cy="50%" r="60%">
            <stop offset="0%" stopColor="rgba(59,130,246,0.16)" />
            <stop offset="100%" stopColor="rgba(12,15,26,0)" />
          </radialGradient>
        </defs>
        <rect width={width} height={height} rx="24" fill="url(#mapGlow)" />
        {[0.2, 0.4, 0.6, 0.8].map((line) => (
          <line
            key={line}
            x1={0}
            x2={width}
            y1={height * line}
            y2={height * line}
            className="map-graticule"
          />
        ))}
        {routes.map((route) => {
          const isSelected = selectedRoute?.origin_iata === route.origin_iata && selectedRoute?.dest_iata === route.dest_iata;
          return (
            <path
              key={`${route.origin_iata}-${route.dest_iata}`}
              d={buildArc(route, width, height)}
              stroke={tierColor(route.tier)}
              strokeWidth={isSelected ? 3.6 : Math.max(1.3, route.total_score / 30)}
              opacity={isSelected ? 1 : 0.62}
              className="map-arc"
              onClick={() => onSelect(route)}
            >
              <title>{`${route.origin_iata}-${route.dest_iata} • ${route.total_score.toFixed(1)}`}</title>
            </path>
          );
        })}
      </svg>
    </section>
  );
}

