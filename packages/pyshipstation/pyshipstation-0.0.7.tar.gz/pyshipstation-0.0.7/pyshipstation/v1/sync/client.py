import requests

from pyshipstation.v1.models.order import ShipStationOrderCreate, ShipStationOrderRead


class ShipStationClient:
    BASE_URL = "https://ssapi.shipstation.com"

    def __init__(
        self,
        header_basic_auth: str,
        timeout: int = 10,
    ):
        """
        :param header_basic_auth: Basic ...
        :param timeout:
        """
        self.header_basic_auth = header_basic_auth
        self.timeout = timeout

    def create_order(self, order: ShipStationOrderCreate) -> ShipStationOrderRead:
        """
        https://www.shipstation.com/docs/api/orders/create-update-order/
        """
        response = requests.post(
            url=f"{self.BASE_URL}/orders/createorder",
            headers={"Authorization": self.header_basic_auth},
            json=order.model_dump(by_alias=True),
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        shipstation_order = ShipStationOrderRead.model_validate(data)
        return shipstation_order
