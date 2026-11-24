import json
from typing import Any, Dict, List

from ..models.db_models import Scheme
from ..models.schemas import MatchedSchemeOut, ProfileCreate, SchemeOut


def scheme_to_schema(scheme: Scheme) -> SchemeOut:
    """Convert an ORM Scheme row into a SchemeOut Pydantic model."""
    return SchemeOut(
        id=scheme.id,
        slug=scheme.slug,
        name=scheme.name,
        category=scheme.category,
        description=scheme.description,
        benefits=scheme.benefits,
        eligibility_rules=json.loads(scheme.eligibility_rules_json),
        application_guidance=scheme.application_guidance,
        source_url=scheme.source_url,
        last_reviewed=scheme.last_reviewed,
    )


def _matches_list(user_value: str, allowed_values: List[str]) -> bool:
    normalized = user_value.strip().lower()
    for allowed in allowed_values:
        token = allowed.strip().lower()
        if token == "all" or token in normalized or normalized in token:
            return True
    return False


def evaluate_eligibility(profile: ProfileCreate, schemes: List[Scheme]) -> List[MatchedSchemeOut]:
    """Filter schemes against explicit rule-based criteria and explain matched conditions."""
    matches: List[MatchedSchemeOut] = []

    for row in schemes:
        rules: Dict[str, Any] = json.loads(row.eligibility_rules_json)
        reasons: List[str] = []

        min_age = rules.get("min_age")
        max_age = rules.get("max_age")
        if min_age is not None and profile.age < min_age:
            continue
        if max_age is not None and profile.age > max_age:
            continue
        if min_age is not None or max_age is not None:
            age_range = f"{min_age or 0}–{max_age or 'any'}"
            reasons.append(f"Age ({profile.age}) fits scheme age criteria ({age_range} years).")

        max_income = rules.get("max_income")
        if max_income is not None:
            if profile.income > max_income:
                continue
            reasons.append(
                f"Annual income (Rs. {profile.income:,}) is within the Rs. {max_income:,} limit."
            )

        allowed_occupations = rules.get("occupations", ["all"])
        if not _matches_list(profile.occupation, allowed_occupations):
            continue
        if "all" not in [o.lower() for o in allowed_occupations]:
            reasons.append(f"Occupation ({profile.occupation}) matches target group.")
        else:
            reasons.append("Open to all occupations subject to scheme conditions.")

        allowed_locations = rules.get("locations", ["all"])
        if not _matches_list(profile.location, allowed_locations):
            continue
        if "all" not in [loc.lower() for loc in allowed_locations]:
            reasons.append(f"Location ({profile.location}) is covered by this scheme.")
        else:
            reasons.append("Available across India.")

        for condition in rules.get("conditions", []):
            reasons.append(f"Note: {condition}")

        matches.append(
            MatchedSchemeOut(
                scheme=scheme_to_schema(row),
                match_reasons=reasons,
            )
        )

    return matches
