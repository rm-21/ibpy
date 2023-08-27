import asyncio
import logging
from types import TracebackType
from typing import ClassVar, Self, Type

import httpx
from pydantic import (
    BaseModel,
    FieldValidationInfo,
    TypeAdapter,
    field_validator,
    validate_call,
)

from ibpy.endpoints import IBRestEndpoints
from ibpy.exceptions import InvalidSymbol
from ibpy.models import Account, Conids, HistoricalData, Tickle

logger: logging.Logger = logging.getLogger(__name__)


class IBRest(BaseModel):
    url: str = "https://127.0.0.1:5000"
    api: str = "/v1/api"
    ssl: bool = False
    http_client: httpx.AsyncClient | None = None

    # Private attrs
    _hist_semaphore: ClassVar[asyncio.Semaphore] = asyncio.Semaphore(3)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close_http_client()

    @property
    def base_url(self) -> str:
        return f"{self.url}{self.api}"

    @property
    def _http_client(self) -> httpx.AsyncClient:
        if not isinstance(self.http_client, httpx.AsyncClient):
            raise TypeError(
                f"`http_client` is expected to be an instance of "
                f"`httpx.AsyncClient`, not `{type(self.http_client)}`"
            )
        return self.http_client

    async def close_http_client(self) -> None:
        await self._http_client.aclose()

    @field_validator("http_client")
    @classmethod
    def check_or_create_http_client(
        cls,
        value: httpx.AsyncClient | None,
        data: FieldValidationInfo,
    ) -> httpx.AsyncClient:
        if value is None:
            return httpx.AsyncClient(verify=data.data["ssl"], timeout=120)
        return value

    @validate_call(config=dict(arbitrary_types_allowed=True))
    async def tickle(
        self,
    ) -> Tickle:
        res = await self._http_client.get(
            url=f"{self.base_url}{IBRestEndpoints.TICKLE}"
        )
        if res.status_code == 200:
            logger.info(
                f"Successfully pinged the server - Status code: {res.status_code}"
            )
            return TypeAdapter(Tickle).validate_python(res.json())

        logger.info(f"Something went wrong while making the request: {res.text}")
        raise Exception(f"Something went wrong while making the request: {res.text}")

    @validate_call(config=dict(arbitrary_types_allowed=True))
    async def get_accounts(
        self,
    ) -> list[Account]:
        res = await self._http_client.get(
            url=f"{self.base_url}{IBRestEndpoints.PORTFOLIO_ACCOUNTS}"
        )
        if res.status_code == 200:
            logger.info(
                f"Successfully fetched accounts from the server - Status code: {res.status_code}"
            )
            return TypeAdapter(list[Account]).validate_python(res.json())

        logger.info(f"Something went wrong while making the request: {res.text}")
        raise Exception(f"Something went wrong while making the request: {res.text}")

    @validate_call(config=dict(arbitrary_types_allowed=True))
    async def get_contract_details(self, symbols: list[str]) -> Conids:
        res = await self._http_client.get(
            url=f"{self.base_url}{IBRestEndpoints.TRSRV_STOCKS}",
            params={"symbols": ",".join(symbols)},
        )

        if res.status_code == 200:
            logger.info(
                f"Successfully fetched stock contract details from the server - Status code: {res.status_code}"
            )
            return TypeAdapter(Conids).validate_python(res.json())

        logger.info(f"Something went wrong while making the request: {res.text}")
        raise Exception(f"Something went wrong while making the request: {res.text}")

    @validate_call(config=dict(arbitrary_types_allowed=True))
    async def _get_historical_data(
        self,
        conid: str,
        period: str,
        bar: str,
        exchange: str | None,
        outside_rth: bool,
        since: str,
    ) -> HistoricalData:
        res = await self._http_client.get(
            url=f"{self.base_url}{IBRestEndpoints.HISTORICAL_DATA}",
            params={
                "conid": conid,
                "period": period,
                "bar": bar,
                "exchange": exchange,
                "outsideRth": outside_rth,
                "since": since,
            },
        )

        if res.status_code == 200:
            logger.info(
                f"Successfully fetched stock contract details from the server - Status code: {res.status_code}"
            )
            return TypeAdapter(HistoricalData).validate_python(res.json())

        logger.info(f"Something went wrong while making the request: {res.text}")
        raise Exception(f"Something went wrong while making the request: {res.text}")

    @validate_call(config=dict(arbitrary_types_allowed=True))
    async def get_historical_data(
        self,
        symbol: str,
        period: str,
        interval: str,
        from_dt: str,
    ) -> HistoricalData:
        async with IBRest._hist_semaphore:
            # Get contract details
            contract_details = (
                await self.get_contract_details(
                    symbols=[
                        symbol.upper(),
                    ]
                )
            ).root[symbol.upper()]

            if not contract_details:
                raise InvalidSymbol(
                    f"{symbol} is potentially invalid. No contract details found."
                )

            conid = contract_details[0].contracts[0].conid

            # Get historical data
            data = await self._get_historical_data(
                conid=str(conid),
                period=period,
                bar=interval,
                exchange=None,
                outside_rth=False,
                since=from_dt,
            )

            return data

    class Config:
        arbitrary_types_allowed: bool = True
        validate_assignment: bool = True
        str_strip_whitespace: bool = True
        validate_default: bool = True
        use_enum_values: bool = True
