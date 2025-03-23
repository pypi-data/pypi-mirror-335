import clientapi_barion
from clientapi_barion import BarionSmartGatewayApi, BarionWalletApi


class Barion:

    def __init__(self, api_key: str, pos_key: str = None, is_live: bool = False):
        if is_live:
            self.configuration = clientapi_barion.Configuration(
                host="https://api.barion.com",
            )
        else:
            self.configuration = clientapi_barion.Configuration(
                host="https://api.test.barion.com",
            )

        self.configuration.api_key['ApiKeyAuth'] = api_key
        if pos_key:
            self.configuration.api_key['PosKeyAuth'] = pos_key

    def BarionSmartGatewayApi(self) -> BarionSmartGatewayApi:
        if 'PosKeyAuth' not in self.configuration.api_key:
            raise Exception('PosKey required for this endpoint')
        with clientapi_barion.ApiClient(configuration=self.configuration) as api_client:
            return clientapi_barion.BarionSmartGatewayApi(api_client)

    def BarionWalletApi(self) -> BarionWalletApi:
        if 'PosKeyAuth' in self.configuration.api_key:
            raise Exception("PosKey is not accepted at this endpoint")
        with clientapi_barion.ApiClient(configuration=self.configuration) as api_client:
            return clientapi_barion.BarionWalletApi(api_client)