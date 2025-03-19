# tokens
# TODO: split into several files as the number of tokens grow

from enum import Enum


class StrEnum(str, Enum):
    """Enum where members are also (and must be) str"""


class NAMESPACES(StrEnum):
    COMFORT = "comfort"
    CONSUMPTION = "consumption"
    CONTACT = "contact"
    ENERGY = "energy"  # is consumption?
    INFRASTRUCTURE = "infrastructure"
    RADIATION = "radiation"  # is a TYPE?
    SOCIAL_MEDIA = "social_media"
    TRACKING = "tracking"
    TRAFFIC = "traffic"
    WARNINGS = "warning"
    WASTE = "waste"
    WATERING = "watering"  # is a TYPE?
    WEATHER = "weather"


class TYPES(StrEnum):
    AIR = "air"
    BUILDING = "building"
    CONTAINER = "container"
    ELECTRICITY = "electricity"
    ELECTROMAGNETIC = "electromagnetic"
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    METEOROLOGICAL = "meteorological"
    NOISE = "noise"
    OCCUPANCY = "occupancy"
    PERSON = "people"
    POLLUTANTS = "pollutants"
    SOLAR = "solar"
    STRUCTURE = "structure"
    WATER = "water"
    XYLOPHAGES = "xylophages"
    CONTENT = "content"


class LOCATION(StrEnum):
    ANY = "any"
    BUILDING = "building"
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    PARKING = "parking"


class METHOD(StrEnum):
    RSSI = "rssi"
    MOBILE = "mobile"
    CAMARA = "camara"


class ASPECT(StrEnum):
    EMAIL = "email"
    CAMPAIGN = "campaign"
    COMMENT = "comment"
    GENERAL = "general"
    STORY = "story"
    ANALYTICS = "analytics"
    SURVEY = "survey"
    TICKETING = "ticketing"
    QUALITY = "quality"
    VIDEO = "video"
    POST = "post"
    INFO = "info"


class APPLICATION(StrEnum):
    ODOO = "odoo"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    BOOKING = "booking"
    LINKEDIN = "linkedin"
    TRIPADVISOR = "tripadvisor"
    TIKTOK = "tiktok"
    TWITTER = "twitter"

