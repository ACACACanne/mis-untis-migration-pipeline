from typing import Any, Callable, Dict, List


class DiffEngine:
    """Calculates timetable differences between Untis master schedule and active MIS records."""

    @staticmethod
    def compute_diff(
        incoming_untis_slots: List[Dict[str, Any]],
        existing_mis_slots: List[Dict[str, Any]],
        key_resolver: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        diff_results = []
        matched_existing_ids = set()

        for untis_slot in incoming_untis_slots:
            resolved = key_resolver(untis_slot)

            # Match criteria: cohort/group, day, and period
            matching_slot = next(
                (
                    s
                    for s in existing_mis_slots
                    if s.get("day_number") == resolved.get("day_of_week")
                    and s.get("period_number") == resolved.get("period_number")
                    and s.get("group_code") == resolved.get("mis_group_code")
                ),
                None,
            )

            if not matching_slot:
                diff_results.append({
                    "change_type": "CREATE",
                    "untis_lesson_id": untis_slot.get("untis_lesson_id"),
                    "day_number": untis_slot.get("day_of_week"),
                    "period_number": untis_slot.get("period_number"),
                    "details": "New slot to schedule in MIS",
                    "slot_payload": resolved,
                })
            else:
                matched_existing_ids.add(matching_slot.get("slot_id"))

                staff_changed = matching_slot.get("staff_id") != resolved.get("mis_staff_id")
                room_changed = matching_slot.get("room_id") != resolved.get("mis_room_id")

                if staff_changed or room_changed:
                    diff_results.append({
                        "change_type": "UPDATE",
                        "mis_slot_id": matching_slot.get("slot_id"),
                        "untis_lesson_id": untis_slot.get("untis_lesson_id"),
                        "day_number": untis_slot.get("day_of_week"),
                        "period_number": untis_slot.get("period_number"),
                        "details": "Staff or room modification detected",
                        "slot_payload": resolved,
                    })
                else:
                    diff_results.append({
                        "change_type": "UNCHANGED",
                        "mis_slot_id": matching_slot.get("slot_id"),
                        "untis_lesson_id": untis_slot.get("untis_lesson_id"),
                        "day_number": untis_slot.get("day_of_week"),
                        "period_number": untis_slot.get("period_number"),
                        "details": "Slot matches active MIS schedule",
                        "slot_payload": resolved,
                    })

        # Check for slots removed from Untis master
        for mis_slot in existing_mis_slots:
            if mis_slot.get("slot_id") not in matched_existing_ids:
                diff_results.append({
                    "change_type": "DELETE",
                    "mis_slot_id": mis_slot.get("slot_id"),
                    "day_number": mis_slot.get("day_number"),
                    "period_number": mis_slot.get("period_number"),
                    "details": "Slot absent in master; deprecate in MIS",
                    "slot_payload": mis_slot,
                })

        return diff_results