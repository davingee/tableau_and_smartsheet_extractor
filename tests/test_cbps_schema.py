import copy

import jsonschema
import pytest

from cbps_schema import CBPS_SCHEMA

SCHEMA = CBPS_SCHEMA["schema"]

VALID_PAYLOAD = {
    "dashboard": {
        "title": "CBPS Dashboard",
        "applications_to_date": 123,
    },
    "overview_by_status": {
        "compliance_and_exemption_applications": {
            "approved_or_pre_approved": 10,
            "pending": 5,
            "withdrawn": 2,
            "denied": 1,
        },
        "tier_1": {
            "approved_or_pre_approved": 8,
            "pending": 3,
            "withdrawn": 1,
            "denied": 0,
        },
        "tier_2": {
            "approved": 6,
            "pending": 2,
            "withdrawn": 1,
            "denied": 0,
        },
    },
    "gross_floor_area_sq_ft": {
        "total_application_gfa": 50000,
        "approved_gfa": 40000,
    },
    "overview_by_application_type": {
        "counts": {
            "compliance": 70,
            "exemption": 30,
        }
    },
    "building_tier": {
        "counts": {
            "tier_1": 60,
            "tier_2": 40,
        }
    },
    "overview_by_building_activity_type": {
        "portion_of_applications_percent": [
            {"label": "New Construction", "percent": 55},
            {"label": "Renovation", "percent": 45},
        ],
        "activity_type_counts": [
            {"label": "New Construction", "count": 55},
            {"label": "Renovation", "count": 45},
        ],
    },
    "cumulative_applications": [
        {"period": "2024-Q1", "applications": 10},
        {"period": "2024-Q2", "applications": 25},
    ],
}


def validate(payload):
    jsonschema.validate(instance=payload, schema=SCHEMA)


def invalid(payload):
    with pytest.raises(jsonschema.ValidationError):
        validate(payload)


# --- schema metadata ---


def test_schema_name():
    assert CBPS_SCHEMA["name"] == "cbps_dashboard"


def test_schema_strict():
    assert CBPS_SCHEMA["strict"] is True


# --- valid payload ---


def test_valid_full_payload():
    validate(VALID_PAYLOAD)


def test_valid_nulls_allowed():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["dashboard"]["applications_to_date"] = None
    payload["overview_by_status"]["tier_1"]["approved_or_pre_approved"] = None
    payload["gross_floor_area_sq_ft"]["approved_gfa"] = None
    payload["overview_by_application_type"]["counts"]["exemption"] = None
    payload["building_tier"]["counts"]["tier_2"] = None
    payload["overview_by_building_activity_type"]["portion_of_applications_percent"][0]["percent"] = None
    payload["overview_by_building_activity_type"]["activity_type_counts"][0]["count"] = None
    payload["cumulative_applications"][0]["applications"] = None
    validate(payload)


def test_valid_empty_activity_arrays():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["overview_by_building_activity_type"]["portion_of_applications_percent"] = []
    payload["overview_by_building_activity_type"]["activity_type_counts"] = []
    validate(payload)


def test_valid_empty_cumulative_applications():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["cumulative_applications"] = []
    validate(payload)


# --- missing required top-level fields ---


@pytest.mark.parametrize(
    "field",
    [
        "dashboard",
        "overview_by_status",
        "gross_floor_area_sq_ft",
        "overview_by_application_type",
        "building_tier",
        "overview_by_building_activity_type",
        "cumulative_applications",
    ],
)
def test_missing_required_top_level_field(field):
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload[field]
    invalid(payload)


# --- dashboard ---


def test_dashboard_missing_title():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["dashboard"]["title"]
    invalid(payload)


def test_dashboard_title_must_be_string():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["dashboard"]["title"] = 42
    invalid(payload)


def test_dashboard_no_extra_properties():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["dashboard"]["extra"] = "oops"
    invalid(payload)


# --- overview_by_status ---


@pytest.mark.parametrize("section", ["compliance_and_exemption_applications", "tier_1", "tier_2"])
def test_overview_by_status_missing_section(section):
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["overview_by_status"][section]
    invalid(payload)


def test_tier_2_uses_approved_not_approved_or_pre_approved():
    # tier_2 has "approved", not "approved_or_pre_approved"
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["overview_by_status"]["tier_2"]["approved_or_pre_approved"] = 5
    invalid(payload)


def test_tier_1_missing_field():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["overview_by_status"]["tier_1"]["pending"]
    invalid(payload)


def test_overview_by_status_no_extra_properties():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["overview_by_status"]["tier_3"] = {"approved": 1, "pending": 0, "withdrawn": 0, "denied": 0}
    invalid(payload)


# --- gross_floor_area_sq_ft ---


def test_gfa_missing_field():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["gross_floor_area_sq_ft"]["total_application_gfa"]
    invalid(payload)


def test_gfa_no_extra_properties():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["gross_floor_area_sq_ft"]["other"] = 999
    invalid(payload)


# --- overview_by_application_type ---


def test_application_type_missing_counts():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["overview_by_application_type"]["counts"]
    invalid(payload)


def test_application_type_counts_missing_field():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["overview_by_application_type"]["counts"]["compliance"]
    invalid(payload)


# --- building_tier ---


def test_building_tier_missing_counts():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["building_tier"]["counts"]
    invalid(payload)


def test_building_tier_counts_no_extra():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["building_tier"]["counts"]["tier_3"] = 5
    invalid(payload)


# --- overview_by_building_activity_type ---


def test_activity_type_missing_portion():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["overview_by_building_activity_type"]["portion_of_applications_percent"]
    invalid(payload)


def test_activity_type_missing_counts():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["overview_by_building_activity_type"]["activity_type_counts"]
    invalid(payload)


def test_activity_type_item_missing_label():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["overview_by_building_activity_type"]["portion_of_applications_percent"][0]["label"]
    invalid(payload)


def test_activity_type_item_missing_percent():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["overview_by_building_activity_type"]["portion_of_applications_percent"][0]["percent"]
    invalid(payload)


def test_activity_type_count_item_missing_count():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["overview_by_building_activity_type"]["activity_type_counts"][0]["count"]
    invalid(payload)


def test_activity_type_item_no_extra_properties():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["overview_by_building_activity_type"]["portion_of_applications_percent"][0]["extra"] = "x"
    invalid(payload)


def test_activity_type_label_must_be_string():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["overview_by_building_activity_type"]["activity_type_counts"][0]["label"] = 123
    invalid(payload)


# --- cumulative_applications ---


def test_cumulative_applications_item_missing_period():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["cumulative_applications"][0]["period"]
    invalid(payload)


def test_cumulative_applications_item_missing_applications():
    payload = copy.deepcopy(VALID_PAYLOAD)
    del payload["cumulative_applications"][0]["applications"]
    invalid(payload)


def test_cumulative_applications_item_no_extra_properties():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["cumulative_applications"][0]["extra"] = "bad"
    invalid(payload)


def test_cumulative_applications_period_must_be_string():
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["cumulative_applications"][0]["period"] = 2024
    invalid(payload)
