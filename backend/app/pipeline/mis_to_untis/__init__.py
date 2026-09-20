# backend/app/pipeline/mis_to_untis/__init__.py

from app.pipeline.mis_to_untis.master_extractor import MisToUntisExtractor

# Provide aliases so imports never fail regardless of naming
MisMasterExtractor = MisToUntisExtractor

__all__ = ["MisToUntisExtractor", "MisMasterExtractor"]