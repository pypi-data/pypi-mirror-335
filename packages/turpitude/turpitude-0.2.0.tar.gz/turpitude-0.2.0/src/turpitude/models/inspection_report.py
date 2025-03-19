from datetime import date
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class InspectionReportType(str, Enum):
    RESIDENTIAL_LEASE_CHECK_IN = "residential_lease_check_in"
    RESIDENTIAL_LEASE_CHECK_OUT = "residential_lease_check_out"
    RESIDENTIAL_LEASE_TEMPLATE = "residential_lease_template"


class InspectionReportSignatoryPersonType(str, Enum):
    NATURAL_PERSON = "natural_person"
    LEGAL_PERSON = "legal_person"


class InspectionReportSignatoryType(str, Enum):
    OWNER = "owner"
    REPRESENTATIVE = "representative"
    TENANT = "tenant"


class InspectionReportSignatory(BaseModel):
    type: InspectionReportSignatoryType
    first_name: str
    last_name: str
    person_type: InspectionReportSignatoryPersonType
    email: str
    address: str
    postal_code: str
    city: str


class InspectionReportPropertyType(str, Enum):
    FLAT = "flat"
    HOUSE = "house"
    BOX = "box"
    PARKING = "parking"
    BUSINESS_PREMISE = "business_premise"
    OFFICE = "office"
    OTHER = "other"


class InspectionReportEnergyKind(str, Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"
    HEATING_OIL = "heating_oil"
    AIR_CONDITIONING = "air_conditioning"
    OTHER = "other"


class InspectionReportRoomType(str, Enum):
    ENTRANCE = "entrance"
    TOILET = "toilet"
    BATHROOM = "bathroom"
    LIVING_ROOM = "living_room"
    KITCHEN = "kitchen"
    BEDROOM = "bedroom"
    BALCONY = "balcony"
    TERRASSE = "terrasse"
    CELLAR = "cellar"
    CARPARK = "carpark"
    BOX = "box"
    GARAGE = "garage"
    GARDEN = "garden"
    LAUNDRY_ROOM = "laundry_room"
    PRIVATE_OFFICE = "private_office"
    OPEN_SPACE = "open_space"
    MEETING_ROOM = "meeting_room"
    PHONE_BOOTH = "phone_booth"
    HALL = "hall"
    SHARED_AREAS = "shared_areas"
    OTHER = "other"


class InspectionReportElementCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BAD = "bad"


class InspectionReportElementOperatingState(str, Enum):
    WORKING = "working"
    NOT_WORKING = "not_working"
    NOT_TESTED = "not_tested"
    UNABLE_TO_TEST = "unable_to_test"


class InspectionReportElementCleanlinessState(str, Enum):
    CLEAN = "clean"
    TO_CLEAN = "to_clean"


class InspectionReportElement(BaseModel):
    name: str
    state: Optional[InspectionReportElementCondition] = None
    characteristics: List[str] = Field(default_factory=list)
    colors: List[str] = Field(default_factory=list)
    defects: List[str] = Field(default_factory=list)
    count: Optional[int] = None
    operating_state: Optional[InspectionReportElementOperatingState] = None
    cleanliness_state: Optional[InspectionReportElementCleanlinessState] = None
    photo_ids: List[int] = Field(default_factory=list)
    comment: Optional[str] = None


class InspectionReportRoom(BaseModel):
    name: str
    kind: InspectionReportRoomType
    elements: List[InspectionReportElement]


class InspectionReportMeterType(str, Enum):
    WATER = "water"
    ELECTRICITY = "electricity"
    GAS = "gas"
    THERMAL_ENERGY = "thermal_energy"


class InspectionReportMeter(BaseModel):
    kind: InspectionReportMeterType
    number: Optional[str] = None
    value_1: float
    value_2: Optional[float] = None
    comment: str


class InspectionReportKeyType(str, Enum):
    PRINCIPAL = "principal"
    PASS = "pass"
    CELLAR = "cellar"
    COMMON = "common"
    MAILBOX = "mailbox"
    GARAGE = "garage"
    PORTAL = "portal"
    BIKE_SHED = "bike_shed"
    BIN_STORAGE_AREA = "bin_storage_area"
    OTHER = "other"


class InspectionReportKey(BaseModel):
    kind: InspectionReportKeyType
    count: int
    comment: str
    delivery_date: date
    pictures: List[str] = Field(default_factory=list)


class InspectionReport(BaseModel):
    kind: InspectionReportType
    inventory_date: date
    address: str
    address_2: str
    postal_code: str
    city: str
    property_type: InspectionReportPropertyType
    floor_nb: int
    door_nb: str
    is_furnished: bool
    heating_energy_equipment_kind: InspectionReportEnergyKind
    is_community_heating: bool
    hot_water_energy_equipment_kind: InspectionReportEnergyKind
    is_community_hot_water: bool
    users: List[InspectionReportSignatory]
    rooms: List[InspectionReportRoom]
    index_readings: List[InspectionReportMeter]
    keys: List[InspectionReportKey]
