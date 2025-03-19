from pydantic import BaseModel, ConfigDict


class ShipStationBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        strict=True,
        populate_by_name=True,
    )
