CBPS_SCHEMA = {
    "name": "cbps_dashboard",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "dashboard": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "applications_to_date": {"type": ["integer", "null"]},
                },
                "required": ["title", "applications_to_date"],
            },
            "overview_by_status": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "compliance_and_exemption_applications": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "approved_or_pre_approved": {"type": ["integer", "null"]},
                            "pending": {"type": ["integer", "null"]},
                            "withdrawn": {"type": ["integer", "null"]},
                            "denied": {"type": ["integer", "null"]},
                        },
                        "required": [
                            "approved_or_pre_approved",
                            "pending",
                            "withdrawn",
                            "denied",
                        ],
                    },
                    "tier_1": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "approved_or_pre_approved": {"type": ["integer", "null"]},
                            "pending": {"type": ["integer", "null"]},
                            "withdrawn": {"type": ["integer", "null"]},
                            "denied": {"type": ["integer", "null"]},
                        },
                        "required": [
                            "approved_or_pre_approved",
                            "pending",
                            "withdrawn",
                            "denied",
                        ],
                    },
                    "tier_2": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "approved": {"type": ["integer", "null"]},
                            "pending": {"type": ["integer", "null"]},
                            "withdrawn": {"type": ["integer", "null"]},
                            "denied": {"type": ["integer", "null"]},
                        },
                        "required": ["approved", "pending", "withdrawn", "denied"],
                    },
                },
                "required": [
                    "compliance_and_exemption_applications",
                    "tier_1",
                    "tier_2",
                ],
            },
            "gross_floor_area_sq_ft": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "total_application_gfa": {"type": ["integer", "null"]},
                    "approved_gfa": {"type": ["integer", "null"]},
                },
                "required": ["total_application_gfa", "approved_gfa"],
            },
            "overview_by_application_type": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "counts": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "compliance": {"type": ["integer", "null"]},
                            "exemption": {"type": ["integer", "null"]},
                        },
                        "required": ["compliance", "exemption"],
                    }
                },
                "required": ["counts"],
            },
            "building_tier": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "counts": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "tier_1": {"type": ["integer", "null"]},
                            "tier_2": {"type": ["integer", "null"]},
                        },
                        "required": ["tier_1", "tier_2"],
                    }
                },
                "required": ["counts"],
            },
            # Strict-mode friendly representation for variable activity labels:
            # arrays of {label, percent}/{label, count}
            "overview_by_building_activity_type": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "portion_of_applications_percent": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "label": {"type": "string"},
                                "percent": {"type": ["integer", "null"]},
                            },
                            "required": ["label", "percent"],
                        },
                    },
                    "activity_type_counts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "label": {"type": "string"},
                                "count": {"type": ["integer", "null"]},
                            },
                            "required": ["label", "count"],
                        },
                    },
                },
                "required": ["portion_of_applications_percent", "activity_type_counts"],
            },
            "cumulative_applications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "period": {"type": "string"},
                        "applications": {"type": ["integer", "null"]},
                    },
                    "required": ["period", "applications"],
                },
            },
        },
        "required": [
            "dashboard",
            "overview_by_status",
            "gross_floor_area_sq_ft",
            "overview_by_application_type",
            "building_tier",
            "overview_by_building_activity_type",
            "cumulative_applications",
        ],
    },
}
