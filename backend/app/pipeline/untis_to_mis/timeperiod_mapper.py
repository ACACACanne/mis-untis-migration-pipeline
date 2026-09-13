from typing import Dict, List, Optional, Tuple
from app.schemas.untis_xml import UntisTimePeriod


class TimePeriodMapper:
    """Translates Untis XML time periods into target MIS timetable slots and bell schedules."""

    @staticmethod
    def format_time_string(raw_time: str) -> str:
        """Converts Untis HHMM (e.g. '0900', '900') to standard HH:MM (e.g. '09:00')."""
        cleaned = raw_time.strip().zfill(4)
        return f"{cleaned[:2]}:{cleaned[2:]}"

    @classmethod
    def build_lookup_table(
        cls, periods: List[UntisTimePeriod]
    ) -> Dict[Tuple[int, int], Dict[str, str]]:
        """
        Builds a (day_of_week, period_number) -> {id, start_time, end_time} lookup table.
        Day: 1 (Mon) through 5/7, Period: 1..20.
        """
        lookup = {}
        for p in periods:
            key = (p.day, p.period)
            lookup[key] = {
                "period_id": p.id,
                "start_time": cls.format_time_string(p.start_time),
                "end_time": cls.format_time_string(p.end_time),
            }
        return lookup

    @classmethod
    def match_mis_slot(
        cls,
        day: int,
        period: int,
        mis_slots: List[Dict],
        target_mis: str = "ARBOR",
    ) -> Optional[int]:
        """Matches day and period to an active MIS TimetableSlot ID."""
        target_mis = target_mis.upper()
        for slot in mis_slots:
            if target_mis == "ARBOR":
                if slot.get("day_of_week") == day and slot.get("period_number") == period:
                    return slot.get("id")
            elif target_mis == "BROMCOM":
                if slot.get("DayNumber") == day and slot.get("PeriodNumber") == period:
                    return slot.get("SlotId")
        return None