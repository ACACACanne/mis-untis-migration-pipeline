from typing import Any, Dict, List


class PipelineSimulator:
    """Simulates publishing diff operations against target MIS rules without mutating live records."""

    @staticmethod
    def run_simulation(diff_entries: List[Dict[str, Any]], target_mis: str = "ARBOR") -> Dict[str, Any]:
        summary = {
            "target_mis": target_mis.upper(),
            "is_simulation": True,
            "total_staged": len(diff_entries),
            "projected_creates": 0,
            "projected_updates": 0,
            "projected_deletions": 0,
            "projected_unchanged": 0,
            "potential_conflicts": [],
        }

        for entry in diff_entries:
            change = entry.get("change_type")
            if change == "CREATE":
                summary["projected_creates"] += 1
            elif change == "UPDATE":
                summary["projected_updates"] += 1
            elif change == "DELETE":
                summary["projected_deletions"] += 1
            elif change == "UNCHANGED":
                summary["projected_unchanged"] += 1

            # Validate basic requirements for creates/updates
            payload = entry.get("slot_payload", {})
            if change in ("CREATE", "UPDATE"):
                if not payload.get("mis_staff_id") and not payload.get("staff_id"):
                    summary["potential_conflicts"].append({
                        "lesson_id": entry.get("untis_lesson_id"),
                        "issue": "Missing MIS Staff ID on scheduled slot.",
                    })

        return summary