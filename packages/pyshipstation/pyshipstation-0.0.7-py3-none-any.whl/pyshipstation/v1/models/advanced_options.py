from pydantic import Field

from pyshipstation.v1.models.common import ShipStationBaseModel


class AdvancedOptionsBase(ShipStationBaseModel):
    """
    https://www.shipstation.com/docs/api/models/advanced-options/
    """

    custom_field_1: None | str = Field(
        None,
        description="Field that allows for custom data to be associated with an order.",
        alias="customField1",
    )
    custom_field_2: None | str = Field(
        None,
        description="Field that allows for custom data to be associated with an order.",
        alias="customField2",
    )
    custom_field_3: None | str = Field(
        None,
        description="Field that allows for custom data to be associated with an order.",
        alias="customField3",
    )


class AdvancedOptionsCreate(AdvancedOptionsBase):
    pass


class AdvancedOptionsRead(AdvancedOptionsBase):
    pass
