import re
from typing import Optional


def normalize_academic_year(value: Optional[str]) -> str:
    normalized = " ".join((value or "").casefold().split())
    semester_match = re.search(
        r"\b(\d+)\s*(?:(?:st|nd|rd|th|rs)\s*)?(?:semester|sem)\b",
        normalized,
    )
    if not semester_match:
        semester_match = re.search(r"\b(?:semester|sem)\s*(\d+)\b", normalized)
    if semester_match:
        return f"semester:{int(semester_match.group(1))}"
    return normalized
