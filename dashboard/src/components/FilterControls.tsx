import type { Filters, RouteType, Tier } from "../lib/types";

type Props = {
  filters: Filters;
  onChange: (filters: Filters) => void;
};

const tiers: Tier[] = ["Tier 1", "Tier 2", "Tier 3", "Tier 4"];
const routeTypes: RouteType[] = ["overwater", "hybrid", "overland"];

export function FilterControls({ filters, onChange }: Props) {
  const toggleTier = (tier: Tier) => {
    const active = filters.tiers.includes(tier);
    onChange({
      ...filters,
      tiers: active ? filters.tiers.filter((value) => value !== tier) : [...filters.tiers, tier],
    });
  };

  const toggleRouteType = (routeType: RouteType) => {
    const active = filters.routeTypes.includes(routeType);
    onChange({
      ...filters,
      routeTypes: active
        ? filters.routeTypes.filter((value) => value !== routeType)
        : [...filters.routeTypes, routeType],
    });
  };

  return (
    <section className="filter-panel">
      <div className="filter-block">
        <label htmlFor="region">Region</label>
        <select
          id="region"
          value={filters.region}
          onChange={(event) => onChange({ ...filters, region: event.target.value })}
        >
          <option value="all">All</option>
          <option value="transatlantic">Transatlantic</option>
          <option value="transpacific">Transpacific</option>
          <option value="europe_asia">Europe-Asia</option>
          <option value="americas">Americas</option>
          <option value="middle_east">Middle East</option>
          <option value="intercontinental">Intercontinental</option>
        </select>
      </div>

      <div className="filter-block">
        <label htmlFor="scoreRange">Minimum Score</label>
        <input
          id="scoreRange"
          type="range"
          min={0}
          max={100}
          step={1}
          value={filters.minScore}
          onChange={(event) => onChange({ ...filters, minScore: Number(event.target.value) })}
        />
        <span>{filters.minScore}</span>
      </div>

      <div className="filter-block">
        <label htmlFor="minDistance">Distance Band</label>
        <div className="distance-inputs">
          <input
            id="minDistance"
            type="number"
            min={1500}
            max={5500}
            value={filters.minDistance}
            onChange={(event) =>
              onChange({ ...filters, minDistance: Number(event.target.value) || 1500 })
            }
          />
          <span>to</span>
          <input
            type="number"
            min={1500}
            max={5500}
            value={filters.maxDistance}
            onChange={(event) =>
              onChange({ ...filters, maxDistance: Number(event.target.value) || 5500 })
            }
          />
        </div>
      </div>

      <div className="filter-block">
        <label>Tiers</label>
        <div className="tier-toggle-group">
          {tiers.map((tier) => (
            <button
              key={tier}
              type="button"
              className={filters.tiers.includes(tier) ? "tier-chip active" : "tier-chip"}
              onClick={() => toggleTier(tier)}
            >
              {tier.replace("Tier ", "★")}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-block">
        <label>Route Type</label>
        <div className="tier-toggle-group">
          {routeTypes.map((routeType) => (
            <button
              key={routeType}
              type="button"
              className={filters.routeTypes.includes(routeType) ? "tier-chip active" : "tier-chip"}
              onClick={() => toggleRouteType(routeType)}
            >
              {routeType === "overwater"
                ? "Overwater"
                : routeType === "hybrid"
                  ? "Hybrid"
                  : "Overland"}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
