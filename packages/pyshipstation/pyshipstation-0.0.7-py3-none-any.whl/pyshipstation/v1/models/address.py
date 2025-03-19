from pydantic import Field

from pyshipstation.v1.models.common import ShipStationBaseModel


class _ShipStationAddressBase(ShipStationBaseModel):
    """
    https://www.shipstation.com/docs/api/models/address/
    """

    name: str = Field(
        ...,
        description="Name of person.",
    )
    company: str = Field(..., description="Name of company.")
    street_1: str = Field(..., description="First line of address.", alias="street1")
    street_2: str = Field(..., description="Second line of address.", alias="street2")
    street_3: str = Field(..., description="Third line of address.", alias="street3")
    city: str = Field(..., description="City.")
    state: str = Field(..., description="State.")
    postal_code: str = Field(
        ...,
        description="Postal Code.",
        alias="postalCode",
    )
    country: str = Field(
        ..., min_length=2, max_length=2, description="Two-letter ISO country code."
    )
    phone: str = Field(..., description="Telephone number.")
    residential: bool | None = Field(
        ...,
        description="Specifies whether the given address is residential.",
    )


class ShipStationAddressCreate(_ShipStationAddressBase):
    pass


class ShipStationAddressRead(_ShipStationAddressBase):
    address_verified: str | None = Field(
        ...,
        description="ShipStation address verification status.",
        examples=[
            "Address not yet validated",
            "Address validated successfully",
            "Address validation warning",
            "Address validation failed",
        ],
        alias="addressVerified",
    )
