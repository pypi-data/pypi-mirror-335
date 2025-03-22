import enum

SUBREDDIT_COUNTRY_MAPPING = {
    "japantravel": "japan",
    "koreatravel": "korea",
}


class ClassificationType(enum.Enum):
    travel_tip = "travel_tip"
    travel_suggestion = "travel_suggestion"
    other = "other"
