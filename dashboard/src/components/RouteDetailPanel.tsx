import type { RouteRecord } from "../lib/types";
import { ScoreBreakdown } from "./ScoreBreakdown";

type Props = {
  route: RouteRecord | null;
};

function formatHours(hours: number) {
  const wholeHours = Math.floor(hours);
  const minutes = Math.round((hours - wholeHours) * 60);
  return `${wholeHours}h ${minutes}m`;
}

function routeTypeLabel(routeType: RouteRecord["route_type"]) {
  if (routeType === "overwater") {
    return "Overwater";
  }
  if (routeType === "hybrid") {
    return "Hybrid";
  }
  return "Overland";
}

export function RouteDetailPanel({ route }: Props) {
  if (!route) {
    return (
      <section className="detail-placeholder">
        <h2>Route Detail Panel</h2>
        <p>Select a route from the map or table to inspect the score breakdown and economics.</p>
      </section>
    );
  }

  const economics = [
    ["Revenue / Flight", `$${route.revenue_per_flight.toLocaleString()}`],
    ["Cost / Flight", `$${route.cost_per_flight.toLocaleString()}`],
    ["Profit / Flight", `$${route.profit_per_flight.toLocaleString()}`],
    ["Annual Revenue", `$${route.annual_revenue_M.toFixed(0)}M`],
    ["Annual Profit", `$${route.annual_profit_M.toFixed(0)}M`],
    ["Payback", `${route.payback_years.toFixed(1)} years`],
    ["Breakeven LF", `${(route.breakeven_load_factor * 100).toFixed(0)}%`],
    ["Flights / Day", route.flights_per_day.toFixed(1)],
    ["Fuel / Flight", `${route.total_fuel_kg.toLocaleString()} kg`],
    ["Fuel Burn / Hr", `${route.fuel_per_hr.toFixed(0)} kg/hr`],
  ];
  const speedProfile = [
    ["Route Type", routeTypeLabel(route.route_type)],
    ["Overwater cruise (M1.7)", `${route.overwater_cruise_hr.toFixed(1)} hrs`],
    ["Boomless Cruise (M1.15)", `${route.boomless_cruise_hr.toFixed(1)} hrs`],
    ["Subsonic phases", `${route.subsonic_phase_hr.toFixed(1)} hrs`],
    ["Boomless savings", `${route.boomless_savings_min.toFixed(0)} min vs subsonic overland`],
  ];

  return (
    <section className="detail-layout">
      <div className="detail-header">
        <div>
          <span className={`tier-pill ${route.tier.toLowerCase().replace(" ", "-")}`}>{route.tier_label}</span>
          <h2>
            {route.origin_iata} → {route.dest_iata}
          </h2>
          <p>
            {route.origin_city}, {route.origin_country} to {route.dest_city}, {route.dest_country}
          </p>
        </div>
        <div className="detail-header-badges">
          <span className="tier-pill">{routeTypeLabel(route.route_type)}</span>
          {route.range_limited ? <span className="range-badge">Range-limited</span> : null}
        </div>
      </div>

      <div className="detail-grid">
        <ScoreBreakdown route={route} />

        <section className="detail-card">
          <div className="card-title-group">
            <h3>Economics</h3>
            <span>{route.tier}</span>
          </div>
          <div className="economics-grid">
            {economics.map(([label, value]) => (
              <div key={label} className="metric-row">
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="detail-card">
        <div className="card-title-group">
          <h3>Speed Profile</h3>
          <span>{route.effective_speed_kts.toFixed(0)} kts effective</span>
        </div>
        <div className="economics-grid">
          {speedProfile.map(([label, value]) => (
            <div key={label} className="metric-row">
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="detail-card">
        <div className="card-title-group">
          <h3>Time Comparison</h3>
          <span>{(route.time_saved_pct * 100).toFixed(0)}% faster</span>
        </div>
        <div className="time-comparison">
          <div>
            <span>Overture</span>
            <div className="time-bar">
              <div
                className="time-bar-fill supersonic"
                style={{ width: `${(route.supersonic_block_hr / route.subsonic_block_hr) * 100}%` }}
              />
            </div>
            <strong>{formatHours(route.supersonic_block_hr)}</strong>
          </div>
          <div>
            <span>Overture (without Boomless)</span>
            <div className="time-bar">
              <div
                className="time-bar-fill hybrid"
                style={{ width: `${(route.overture_without_boomless_block_hr / route.subsonic_block_hr) * 100}%` }}
              />
            </div>
            <strong>{formatHours(route.overture_without_boomless_block_hr)}</strong>
          </div>
          <div>
            <span>787-9</span>
            <div className="time-bar">
              <div className="time-bar-fill subsonic" style={{ width: "100%" }} />
            </div>
            <strong>{formatHours(route.subsonic_block_hr)}</strong>
          </div>
          <p className="detail-note">
            Boomless Cruise saves {route.boomless_savings_min.toFixed(0)} minutes over subsonic overland operations.
            Total savings vs a 787-9 are {formatHours(route.time_saved_hr)} with {Math.round(route.overwater_pct * 100)}%
            overwater routing and BTI {route.bti_origin.toFixed(0)}/{route.bti_dest.toFixed(0)} endpoints.
          </p>
        </div>
      </section>

      <section className="detail-card">
        <div className="card-title-group">
          <h3>Why This Route?</h3>
          <span>{route.distance_nm.toFixed(0)} nm</span>
        </div>
        <p className="why-route">{route.why_this_route}</p>
      </section>
    </section>
  );
}
