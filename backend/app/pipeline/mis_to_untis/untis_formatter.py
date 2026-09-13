from typing import Any, Dict, List
from app.connectors.untis_dif_writer import UntisDifWriter


class UntisFormatter:
    """Prepares MIS baseline data for export to Untis-compliant formats."""

    @staticmethod
    def generate_dif_package(master_catalog: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
        """Returns a dict of DIF filenames and file contents."""
        return UntisDifWriter.bundle_all_dif(master_catalog)

    @staticmethod
    def format_single_dif(file_name: str, records: List[Dict[str, Any]]) -> str:
        name = file_name.upper()
        if "GPU001" in name:
            return UntisDifWriter.generate_gpu001_subjects(records)
        elif "GPU002" in name:
            return UntisDifWriter.generate_gpu002_teachers(records)
        elif "GPU003" in name:
            return UntisDifWriter.generate_gpu003_classes(records)
        elif "GPU004" in name:
            return UntisDifWriter.generate_gpu004_rooms(records)
        elif "GPU005" in name:
            return UntisDifWriter.generate_gpu005_students(records)
        else:
            raise ValueError(f"Unknown DIF table requested: {file_name}")