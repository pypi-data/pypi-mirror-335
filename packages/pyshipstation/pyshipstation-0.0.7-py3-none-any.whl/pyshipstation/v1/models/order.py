from typing import Optional

from pydantic import Field

from pyshipstation.v1.models.address import ShipStationAddressCreate
from pyshipstation.v1.models.advanced_options import AdvancedOptionsCreate
from pyshipstation.v1.models.common import ShipStationBaseModel


class _ShipStationOrderBase(ShipStationBaseModel):
    """
    https://www.shipstation.com/docs/api/models/order/
    """

    order_number: str = Field(
        ...,
        alias="orderNumber",
        examples=["ABC-DEL-0004"],
    )
    order_date: str = Field(
        ...,
        alias="orderDate",
        examples=[
            "2015-06-29T08:46:27.0000000",
        ],
    )
    order_status: str = Field(..., examples=["awaiting_shipment"], alias="orderStatus")
    customer_username: Optional[str] = Field(
        None, examples=["JOEBLOGGS1"], alias="customerUsername"
    )
    customer_email: Optional[str] = Field(
        None, examples=["joe@bloggs.com"], alias="customerEmail"
    )
    bill_to: ShipStationAddressCreate = Field(..., alias="billTo")
    ship_to: ShipStationAddressCreate = Field(..., alias="shipTo")
    items: Optional[list] = Field(
        None,
    )
    internal_notes: Optional[str] = Field(
        None,
        alias="internalNotes",
        description="Private notes that are only visible to the seller.",
    )
    advanced_options: Optional[AdvancedOptionsCreate] = Field(
        None,
        alias="advancedOptions",
        description="Various AdvancedOptions may be available depending on the shipping carrier that is used to ship the order.",
    )


class ShipStationOrderCreate(_ShipStationOrderBase):
    pass


class ShipStationOrderRead(_ShipStationOrderBase):
    order_id: int = Field(..., alias="orderId", examples=[259162565])
    order_key: str = Field(
        ..., alias="orderKey", examples=["aaabc5462beb41c882cf4222fb965e97"]
    )
    create_date: str = Field(
        ..., alias="createDate", examples=["2025-03-17T08:23:24.1730000"]
    )
    modify_date: str = Field(
        ..., alias="modifyDate", examples=["2025-03-17T08:23:23.9630000"]
    )
