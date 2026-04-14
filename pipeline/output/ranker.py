from __future__ import annotations


def classify_tier(score: float) -> tuple[str, str]:
    if score >= 75:
        return "Tier 1", "Flagship"
    if score >= 60:
        return "Tier 2", "Strong"
    if score >= 45:
        return "Tier 3", "Viable"
    return "Tier 4", "Marginal"


def rank_routes(scored_routes: list[dict]) -> list[dict]:
    ranked = sorted(scored_routes, key=lambda route: route["total_score"], reverse=True)
    final: list[dict] = []
    for index, route in enumerate(ranked[:50], start=1):
        tier, tier_label = classify_tier(route["total_score"])
        final.append({**route, "rank": index, "tier": tier, "tier_label": tier_label})
    return final

