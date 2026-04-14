import type { RouteRecord, SummaryStats } from "./types";

export async function loadRoutes(): Promise<RouteRecord[]> {
  const response = await fetch("/routes.json");
  if (!response.ok) {
    throw new Error("Unable to load routes.json");
  }
  return response.json();
}

export async function loadSummary(): Promise<SummaryStats> {
  const response = await fetch("/summary.json");
  if (!response.ok) {
    throw new Error("Unable to load summary.json");
  }
  return response.json();
}

