from typing import Dict, List
# import json


CONTACT_PATTERNS = {
    "keyword": [
        "email",
        "phone",
        "website",
        "person_id",
        "organization_profile_id",
        "owner_profile_id",
        "source",
        "photo_url",
        "photo_file_name",
        "name_prefix",
        "name_suffix",
        "nickname",
        "title",
        "department",
        "country",
        "state",
        "postal_code"
    ],
    "date": [
        "birthday",
        "anniversary"
    ],
    "integer": [
        "day",
        "month",
        "year"
    ],
    "boolean": [
        "is_test_data"
    ],
    "text": [
        "first_name",
        "last_name",
        "additional_name",
        "full_name",
        "display_as",
        "notes",
        "street",
        "city",
        "account_name",
        "job_title",
        "organization"
    ]
}

EVENT_PATTERNS = {
    "keyword": [
        "event_id",
        "identifier",
        "type",
        "sub_type",
        "genre",
        "sub_genre",
        "segement",
        "visibility_id",
        "location_id",
        "location_id_temp",
        "organizers_profile_id",
        "parent_event_id",
        "created_effective_profile_id",
        "created_effective_user_id",
        "created_real_user_id",
        "created_user_id",
        "updated_effective_profile_id",
        "updated_effective_user_id",
        "updated_real_user_id",
        "updated_user_id"
    ],
    "date": [
        "timestamp",
        "start_timestamp",
        "end_timestamp",
        "access_start_timestamp",
        "created_timestamp",
        "updated_timestamp"
    ],
    "boolean": [
        "is_",
        "is_beakfast",
        "is_lunch",
        "is_dinner",
        "is_family",
        "is_event_approved",
        "is_event_has_promoters",
        "is_paid",
        "is_can_be_paid_at_the_entrance_in_cash",
        "is_require_end_user_registration",
        "is_require_end_user_arrival_confirmation",
        "is_require_organizer_registration_confirmation",
        "is_show_end_timestamp",
        "is_test_data",
        "is_waitinglist"
    ],
    "text": [
        "name",
        "description",
        "facebook_event_url",
        "meetup_event_url",
        "registration_url",
        "website_url"
    ]
}

GROUP_PATTERNS = {
    "keyword": [
        "hashtag",
        "group_id",
        "parent_group_id",
        "location_id",
        "location_list_id",
        "group_category_id",
        "system_id",
        "profile_id",
        "main_group_type_id",
        "event_id",
        "visibility_id",
        "non_members_visibility_id",
        "members_visibility_id"
    ],
    "boolean": [
        "is_approved",
        "is_interest",
        "is_job_title",
        "is_role",
        "is_skill",
        "is_organization",
        "is_geo",
        "is_continent",
        "is_country",
        "is_state",
        "is_county",
        "is_region",
        "is_city",
        "is_neighbourhood",
        "is_street",
        "is_zip_code",
        "is_building",
        "is_relationship",
        "is_marital_status",
        "is_official",
        "is_first_name",
        "is_last_name",
        "is_campaign",
        "is_activity",
        "is_sport",
        "is_language",
        "location_id",
        "is_event",
        "is_test_data"
    ],
    "text": [
        "name",
        "system_group_name",
        "coordinate"
    ]
}


def get_patterns(object_type: str) -> Dict[str, List[str]]:
    """
    Get the appropriate field patterns for a given object type.

    Args:
        object_type: Type of object ('contact', 'event', or 'group')

    Returns:
        Dict containing the field patterns for the specified object type
    """
    patterns_map = {
        'contact': CONTACT_PATTERNS,
        'event': EVENT_PATTERNS,
        'group': GROUP_PATTERNS
    }

    return patterns_map.get(object_type.lower(), None)


def generate_index_body(object_type: str, shards: int = 2, replicas: int = 1) -> dict:
    """
    Generate a static index mapping with properties based on the object_type.
    """
    patterns = get_patterns(object_type)
    if not patterns:
        raise ValueError(f"Invalid object type: {object_type}")

    properties = {}
    for type, list in patterns.items():
        for pattern in list:
            if pattern not in properties:
                properties[pattern] = {"type": type}

    index_body = {
        "settings": {
            "index": {
                "number_of_shards": shards,
                "number_of_replicas": replicas
            }
        },
        "mappings": {
            "properties": properties
        }
    }
    return index_body


# if __name__ == "__main__":
    # contact_index_body = generate_index_body("contact")
    # print a formatted version of the index body
    # print(json.dumps(contact_index_body, indent=4))
    # event_index_body = generate_index_body("event")
    # print(json.dumps(event_index_body, indent=1))
    # group_index_body = generate_index_body("group")
    # print(json.dumps(group_index_body, indent=1))
    # invalid_index_body = generate_index_body("invalid")
    # print(json.dumps(invalid_index_body, indent=1))
