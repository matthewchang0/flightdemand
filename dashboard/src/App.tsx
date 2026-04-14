import { startTransition, useDeferredValue, useEffect, useState } from "react";

import { FilterControls } from "./components/FilterControls";
import { GlobalMap } from "./components/GlobalMap";
import { RankingTable } from "./components/RankingTable";
import { RouteDetailPanel } from "./components/RouteDetailPanel";
import { SummaryStats } from "./components/SummaryStats";
import { loadRoutes, loadSummary } from "./lib/data";
import type { Filters, RouteRecord, SummaryStats as SummaryStatsType } from "./lib/types";

const initialFilters: Filters = {
  region: "all",
  minScore: 0,
  minDistance: 1500,
  maxDistance: 5500,
  tiers: ["Tier 1", "Tier 2", "Tier 3", "Tier 4"],
  routeTypes: ["overwater", "hybrid", "overland"],
};

export default function App() {
  const [routes, setRoutes] = useState<RouteRecord[]>([]);
  const [summary, setSummary] = useState<SummaryStatsType | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<RouteRecord | null>(null);
  const [filters, setFilters] = useState<Filters>(initialFilters);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function hydrate() {
      try {
        const [nextRoutes, nextSummary] = await Promise.all([loadRoutes(), loadSummary()]);
        if (cancelled) {
          return;
        }
        setRoutes(nextRoutes);
        setSummary(nextSummary);
        setSelectedRoute(nextRoutes[0] ?? null);
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Unable to load dashboard data.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    hydrate();
    return () => {
      cancelled = true;
    };
  }, []);

  const deferredFilters = useDeferredValue(filters);
  const filteredRoutes = routes.filter((route) => {
    const regionMatch = deferredFilters.region === "all" || route.region === deferredFilters.region;
    const scoreMatch = route.total_score >= deferredFilters.minScore;
    const distanceMatch =
      route.distance_nm >= deferredFilters.minDistance && route.distance_nm <= deferredFilters.maxDistance;
    const tierMatch = deferredFilters.tiers.includes(route.tier);
    const routeTypeMatch = deferredFilters.routeTypes.includes(route.route_type);
    return regionMatch && scoreMatch && distanceMatch && tierMatch && routeTypeMatch;
  });

  useEffect(() => {
    if (!filteredRoutes.length) {
      setSelectedRoute(null);
      return;
    }
    if (
      selectedRoute &&
      filteredRoutes.some(
        (route) =>
          route.origin_iata === selectedRoute.origin_iata && route.dest_iata === selectedRoute.dest_iata,
      )
    ) {
      return;
    }
    setSelectedRoute(filteredRoutes[0]);
  }, [filteredRoutes, selectedRoute]);

  const handleFilterChange = (nextFilters: Filters) => {
    startTransition(() => setFilters(nextFilters));
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <h1>Most Economically Viable Flights for Supersonic</h1>
        <p>
          Ranking the top 50 routes where Mach 1.7 over water and Boomless Cruise over land make the strongest economic case.
        </p>
      </header>

      {loading ? <div className="loading-panel">Loading ranked route outputs...</div> : null}
      {error ? <div className="error-panel">{error}</div> : null}

      {!loading && !error ? (
        <>
          <SummaryStats summary={summary} routes={filteredRoutes} />
          <FilterControls filters={filters} onChange={handleFilterChange} />

          <section className="top-grid">
            <GlobalMap routes={filteredRoutes} selectedRoute={selectedRoute} onSelect={setSelectedRoute} />
            <RankingTable routes={filteredRoutes} selectedRoute={selectedRoute} onSelect={setSelectedRoute} />
          </section>

          <RouteDetailPanel route={selectedRoute} />
        </>
      ) : null}
    </main>
  );
}
