# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import date
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["EnhancedData", "Common", "CommonLineItem", "CommonTax", "Fleet", "FleetAmountTotals", "FleetFuel"]


class CommonLineItem(BaseModel):
    amount: Optional[float] = None
    """The price of the item purchased in merchant currency."""

    description: Optional[str] = None
    """A human-readable description of the item."""

    product_code: Optional[str] = None
    """An identifier for the item purchased."""

    quantity: Optional[float] = None
    """The quantity of the item purchased."""


class CommonTax(BaseModel):
    amount: Optional[int] = None
    """The amount of tax collected."""

    exempt: Optional[Literal["TAX_INCLUDED", "TAX_NOT_INCLUDED", "NOT_SUPPORTED"]] = None
    """A flag indicating whether the transaction is tax exempt or not."""

    merchant_tax_id: Optional[str] = None
    """The tax ID of the merchant."""


class Common(BaseModel):
    line_items: List[CommonLineItem]

    tax: CommonTax

    customer_reference_number: Optional[str] = None
    """A customer identifier."""

    merchant_reference_number: Optional[str] = None
    """A merchant identifier."""

    order_date: Optional[date] = None
    """The date of the order."""


class FleetAmountTotals(BaseModel):
    discount: Optional[int] = None
    """The discount applied to the gross sale amount."""

    gross_sale: Optional[int] = None
    """The gross sale amount."""

    net_sale: Optional[int] = None
    """The amount after discount."""


class FleetFuel(BaseModel):
    quantity: Optional[float] = None
    """The quantity of fuel purchased."""

    type: Optional[
        Literal[
            "UNKNOWN",
            "REGULAR",
            "MID_PLUS",
            "PREMIUM_SUPER",
            "MID_PLUS_2",
            "PREMIUM_SUPER_2",
            "ETHANOL_5_7_BLEND",
            "MID_PLUS_ETHANOL_5_7_PERCENT_BLEND",
            "PREMIUM_SUPER_ETHANOL_5_7_PERCENT_BLEND",
            "ETHANOL_7_7_PERCENT_BLEND",
            "MID_PLUS_ETHANOL_7_7_PERCENT_BLEND",
            "GREEN_GASOLINE_REGULAR",
            "GREEN_GASOLINE_MID_PLUS",
            "GREEN_GASOLINE_PREMIUM_SUPER",
            "REGULAR_DIESEL_2",
            "PREMIUM_DIESEL_2",
            "REGULAR_DIESEL_1",
            "COMPRESSED_NATURAL_GAS",
            "LIQUID_PROPANE_GAS",
            "LIQUID_NATURAL_GAS",
            "E_85",
            "REFORMULATED_1",
            "REFORMULATED_2",
            "REFORMULATED_3",
            "REFORMULATED_4",
            "REFORMULATED_5",
            "DIESEL_OFF_ROAD_1_AND_2_NON_TAXABLE",
            "DIESEL_OFF_ROAD_NON_TAXABLE",
            "BIODIESEL_BLEND_OFF_ROAD_NON_TAXABLE",
            "UNDEFINED_FUEL",
            "RACING_FUEL",
            "MID_PLUS_2_10_PERCENT_BLEND",
            "PREMIUM_SUPER_2_10_PERCENT_BLEND",
            "MID_PLUS_ETHANOL_2_15_PERCENT_BLEND",
            "PREMIUM_SUPER_ETHANOL_2_15_PERCENT_BLEND",
            "PREMIUM_SUPER_ETHANOL_7_7_PERCENT_BLEND",
            "REGULAR_ETHANOL_10_PERCENT_BLEND",
            "MID_PLUS_ETHANOL_10_PERCENT_BLEND",
            "PREMIUM_SUPER_ETHANOL_10_PERCENT_BLEND",
            "B2_DIESEL_BLEND_2_PERCENT_BIODIESEL",
            "B5_DIESEL_BLEND_5_PERCENT_BIODIESEL",
            "B10_DIESEL_BLEND_10_PERCENT_BIODIESEL",
            "B11_DIESEL_BLEND_11_PERCENT_BIODIESEL",
            "B15_DIESEL_BLEND_15_PERCENT_BIODIESEL",
            "B20_DIESEL_BLEND_20_PERCENT_BIODIESEL",
            "B100_DIESEL_BLEND_100_PERCENT_BIODIESEL",
            "B1_DIESEL_BLEND_1_PERCENT_BIODIESEL",
            "ADDITIZED_DIESEL_2",
            "ADDITIZED_DIESEL_3",
            "RENEWABLE_DIESEL_R95",
            "RENEWABLE_DIESEL_BIODIESEL_6_20_PERCENT",
            "DIESEL_EXHAUST_FLUID",
            "PREMIUM_DIESEL_1",
            "REGULAR_ETHANOL_15_PERCENT_BLEND",
            "MID_PLUS_ETHANOL_15_PERCENT_BLEND",
            "PREMIUM_SUPER_ETHANOL_15_PERCENT_BLEND",
            "PREMIUM_DIESEL_BLEND_LESS_THAN_20_PERCENT_BIODIESEL",
            "PREMIUM_DIESEL_BLEND_GREATER_THAN_20_PERCENT_BIODIESEL",
            "B75_DIESEL_BLEND_75_PERCENT_BIODIESEL",
            "B99_DIESEL_BLEND_99_PERCENT_BIODIESEL",
            "MISCELLANEOUS_FUEL",
            "JET_FUEL",
            "AVIATION_FUEL_REGULAR",
            "AVIATION_FUEL_PREMIUM",
            "AVIATION_FUEL_JP8",
            "AVIATION_FUEL_4",
            "AVIATION_FUEL_5",
            "BIOJET_DIESEL",
            "AVIATION_BIOFUEL_GASOLINE",
            "MISCELLANEOUS_AVIATION_FUEL",
            "MARINE_FUEL_1",
            "MARINE_FUEL_2",
            "MARINE_FUEL_3",
            "MARINE_FUEL_4",
            "MARINE_FUEL_5",
            "MARINE_OTHER",
            "MARINE_DIESEL",
            "MISCELLANEOUS_MARINE_FUEL",
            "KEROSENE_LOW_SULFUR",
            "WHITE_GAS",
            "HEATING_OIL",
            "OTHER_FUEL_NON_TAXABLE",
            "KEROSENE_ULTRA_LOW_SULFUR",
            "KEROSENE_LOW_SULFUR_NON_TAXABLE",
            "KEROSENE_ULTRA_LOW_SULFUR_NON_TAXABLE",
            "EVC_1_LEVEL_1_CHARGE_110V_15_AMP",
            "EVC_2_LEVEL_2_CHARGE_240V_15_40_AMP",
            "EVC_3_LEVEL_3_CHARGE_480V_3_PHASE_CHARGE",
            "BIODIESEL_BLEND_2_PERCENT_OFF_ROAD_NON_TAXABLE",
            "BIODIESEL_BLEND_5_PERCENT_OFF_ROAD_NON_TAXABLE",
            "BIODIESEL_BLEND_10_PERCENT_OFF_ROAD_NON_TAXABLE",
            "BIODIESEL_BLEND_11_PERCENT_OFF_ROAD_NON_TAXABLE",
            "BIODIESEL_BLEND_15_PERCENT_OFF_ROAD_NON_TAXABLE",
            "BIODIESEL_BLEND_20_PERCENT_OFF_ROAD_NON_TAXABLE",
            "DIESEL_1_OFF_ROAD_NON_TAXABLE",
            "DIESEL_2_OFF_ROAD_NON_TAXABLE",
            "DIESEL_1_PREMIUM_OFF_ROAD_NON_TAXABLE",
            "DIESEL_2_PREMIUM_OFF_ROAD_NON_TAXABLE",
            "ADDITIVE_DOSAGE",
            "ETHANOL_BLENDS_E16_E84",
            "LOW_OCTANE_UNL",
            "BLENDED_DIESEL_1_AND_2",
            "OFF_ROAD_REGULAR_NON_TAXABLE",
            "OFF_ROAD_MID_PLUS_NON_TAXABLE",
            "OFF_ROAD_PREMIUM_SUPER_NON_TAXABLE",
            "OFF_ROAD_MID_PLUS_2_NON_TAXABLE",
            "OFF_ROAD_PREMIUM_SUPER_2_NON_TAXABLE",
            "RECREATIONAL_FUEL_90_OCTANE",
            "HYDROGEN_H35",
            "HYDROGEN_H70",
            "RENEWABLE_DIESEL_R95_OFF_ROAD_NON_TAXABLE",
            "BIODIESEL_BLEND_1_PERCENT_OFF_ROAD_NON_TAXABLE",
            "BIODIESEL_BLEND_75_PERCENT_OFF_ROAD_NON_TAXABLE",
            "BIODIESEL_BLEND_99_PERCENT_OFF_ROAD_NON_TAXABLE",
            "BIODIESEL_BLEND_100_PERCENT_OFF_ROAD_NON_TAXABLE",
            "RENEWABLE_DIESEL_BIODIESEL_6_20_PERCENT_OFF_ROAD_NON_TAXABLE",
            "MISCELLANEOUS_OTHER_FUEL",
        ]
    ] = None
    """The type of fuel purchased."""

    unit_of_measure: Optional[
        Literal["GALLONS", "LITERS", "POUNDS", "KILOGRAMS", "IMPERIAL_GALLONS", "NOT_APPLICABLE", "UNKNOWN"]
    ] = None
    """Unit of measure for fuel disbursement."""

    unit_price: Optional[int] = None
    """The price per unit of fuel."""


class Fleet(BaseModel):
    amount_totals: FleetAmountTotals

    fuel: FleetFuel

    driver_number: Optional[str] = None
    """
    The driver number entered into the terminal at the time of sale, with leading
    zeros stripped.
    """

    odometer: Optional[int] = None
    """The odometer reading entered into the terminal at the time of sale."""

    service_type: Optional[Literal["UNKNOWN", "UNDEFINED", "SELF_SERVICE", "FULL_SERVICE", "NON_FUEL_ONLY"]] = None
    """The type of fuel service."""

    vehicle_number: Optional[str] = None
    """
    The vehicle number entered into the terminal at the time of sale, with leading
    zeros stripped.
    """


class EnhancedData(BaseModel):
    token: str
    """A unique identifier for the enhanced commercial data."""

    common: Common

    event_token: str
    """The token of the event that the enhanced data is associated with."""

    fleet: List[Fleet]

    transaction_token: str
    """The token of the transaction that the enhanced data is associated with."""
