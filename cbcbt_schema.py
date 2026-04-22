CBCBT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["crosstab", "covered_building_count_by_tiers"],
    "properties": {
        "crosstab": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["County", "Building Count", "Owner Count", "Parcel Count"],
                "properties": {
                    "County": {"type": ["string", "null"]},
                    "Building Count": {"type": ["integer", "null"]},
                    "Owner Count": {"type": ["integer", "null"]},
                    "Parcel Count": {"type": ["integer", "null"]},
                },
            },
        },
        "covered_building_count_by_tiers": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,  # <- MUST exist here
                "required": [
                    "County",
                    "Grand Total",
                    "Tier1 >220K",
                    "Tier1 >50K-90K",
                    "Tier1 >90K-220K",
                    "Tier1 Total",
                    "Tier2 >20K Condos",
                    "Tier2 >20K MF (5+)",
                    "Tier2 >20K Other Residential",
                    "Tier2 >20K-50K",
                    "Tier2 Total",
                ],
                "properties": {
                    "County": {"type": ["string", "null"]},
                    "Grand Total": {"type": ["integer", "null"]},
                    "Tier1 >220K": {"type": ["integer", "null"]},
                    "Tier1 >50K-90K": {"type": ["integer", "null"]},
                    "Tier1 >90K-220K": {"type": ["integer", "null"]},
                    "Tier1 Total": {"type": ["integer", "null"]},
                    "Tier2 >20K Condos": {"type": ["integer", "null"]},
                    "Tier2 >20K MF (5+)": {"type": ["integer", "null"]},
                    "Tier2 >20K Other Residential": {"type": ["integer", "null"]},
                    "Tier2 >20K-50K": {"type": ["integer", "null"]},
                    "Tier2 Total": {"type": ["integer", "null"]},
                },
            },
        },
    },
}
