import logging
import os
from enum import Enum
from pathlib import Path
from typing import Optional, List, Any, get_args, Annotated, cast

import typer
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    PrivateAttr,
    validate_call,
)

from bearish.database.crud import BearishDb
from bearish.exceptions import InvalidApiKeyError, LimitApiKeyReachedError
from bearish.exchanges.exchanges import (
    Countries,
    exchanges_factory,
    ExchangeQuery,
    Exchanges,
)
from bearish.interface.interface import BearishDbBase
from bearish.models.api_keys.api_keys import SourceApiKeys
from bearish.models.assets.assets import Assets
from bearish.models.base import Ticker, Tracker, TrackerQuery
from bearish.models.financials.base import Financials
from bearish.models.price.price import Price, Prices
from bearish.models.query.query import AssetQuery, Symbols
from bearish.sources.base import AbstractSource
from bearish.sources.financedatabase import FinanceDatabaseSource
from bearish.sources.financial_modelling_prep import FmpAssetsSource, FmpSource
from bearish.sources.investpy import InvestPySource
from bearish.sources.tiingo import TiingoSource
from bearish.sources.yfinance import yFinanceSource
from bearish.types import SeriesLength, Sources

logger = logging.getLogger(__name__)
app = typer.Typer()


class Bearish(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: Path
    api_keys: SourceApiKeys = Field(default_factory=SourceApiKeys)
    _bearish_db: BearishDbBase = PrivateAttr()
    exchanges: Exchanges = Field(default_factory=exchanges_factory)
    asset_sources: List[AbstractSource] = Field(
        default_factory=lambda: [
            FinanceDatabaseSource(),
            InvestPySource(),
            FmpAssetsSource(),
        ]
    )
    detailed_asset_sources: List[AbstractSource] = Field(
        default_factory=lambda: [yFinanceSource(), FmpSource()]
    )
    financials_sources: List[AbstractSource] = Field(
        default_factory=lambda: [
            yFinanceSource(),
            FmpSource(),
        ]
    )
    price_sources: List[AbstractSource] = Field(
        default_factory=lambda: [
            yFinanceSource(),
            TiingoSource(),
        ]
    )

    def model_post_init(self, __context: Any) -> None:
        self._bearish_db = BearishDb(database_path=self.path)
        for source in set(
            self.financials_sources
            + self.price_sources
            + self.asset_sources
            + self.detailed_asset_sources
        ):
            try:
                source.set_api_key(
                    self.api_keys.keys.get(
                        source.__source__, os.environ.get(source.__source__.upper())  # type: ignore
                    )
                )
            except Exception as e:  # noqa: PERF203
                logger.error(
                    f"Invalid API key for {source.__source__}: {e}. It will be removed from sources"
                )
                for sources in [
                    self.financials_sources,
                    self.price_sources,
                    self.asset_sources,
                    self.detailed_asset_sources,
                ]:
                    if source in sources:
                        sources.remove(source)

    def get_asset_sources(self) -> List[Sources]:
        return [source.__source__ for source in self.asset_sources]

    def get_detailed_asset_sources(self) -> List[Sources]:
        return [source.__source__ for source in self.detailed_asset_sources]

    def write_assets(self, query: Optional[AssetQuery] = None) -> None:
        existing_sources = self._bearish_db.read_sources()
        asset_sources = [
            asset_source
            for asset_source in self.asset_sources
            if asset_source.__source__ not in existing_sources
        ]
        return self._write_base_assets(asset_sources, query)

    def write_detailed_assets(self, query: Optional[AssetQuery] = None) -> None:
        return self._write_base_assets(
            self.detailed_asset_sources, query, use_all_sources=False
        )

    def _write_base_assets(
        self,
        asset_sources: List[AbstractSource],
        query: Optional[AssetQuery] = None,
        use_all_sources: bool = True,
    ) -> None:
        if query:
            cached_assets = self.read_assets(AssetQuery.model_validate(query))
            query.update_symbols(cached_assets)
        for source in asset_sources:

            logger.info(f"Fetching assets from source {type(source).__name__}")
            assets_ = source.read_assets(query)
            if assets_.is_empty():
                logger.warning(f"No assets found from {type(source).__name__}")
                continue
            self._bearish_db.write_assets(assets_)
            self._bearish_db.write_source(source.__source__)
            if use_all_sources:
                continue
            if not assets_.failed_query.symbols:
                break
            else:
                query = AssetQuery(
                    symbols=Symbols(equities=assets_.failed_query.symbols)  # type: ignore
                )

    def read_assets(self, assets_query: AssetQuery) -> Assets:
        return self._bearish_db.read_assets(assets_query)

    def read_financials(self, assets_query: AssetQuery) -> Financials:
        return self._bearish_db.read_financials(assets_query)

    def read_series(self, assets_query: AssetQuery) -> List[Price]:
        return self._bearish_db.read_series(assets_query)

    def _get_tracked_tickers(self, tracker_query: TrackerQuery) -> List[Ticker]:
        return self._bearish_db.read_tracker(tracker_query)

    def get_tickers_without_financials(self, tickers: List[Ticker]) -> List[Ticker]:
        return [
            t
            for t in tickers
            if t not in self._get_tracked_tickers(TrackerQuery(financials=True))
        ]

    def get_tickers_without_price(self, tickers: List[Ticker]) -> List[Ticker]:
        return [
            t
            for t in tickers
            if t not in self._get_tracked_tickers(TrackerQuery(price=True))
        ]

    def get_ticker_with_price(self) -> List[Ticker]:
        return [
            Ticker(symbol=t)
            for t in self._get_tracked_tickers(TrackerQuery(price=True))
        ]

    def write_many_financials(self, tickers: List[Ticker]) -> None:
        tickers = self.get_tickers_without_financials(tickers)
        financials = Financials()
        for ticker in tickers:
            for source in self.financials_sources:
                try:
                    financials_ = source.read_financials(ticker)
                except (InvalidApiKeyError, LimitApiKeyReachedError, Exception) as e:
                    logger.error(f"Error reading data using {source.__source__}: {e}")
                    continue
                if financials_.is_empty():
                    continue
                financials.add(financials_)
                self._bearish_db.write_tracker(
                    Tracker(
                        symbol=ticker.symbol, source=source.__source__, financials=True
                    )
                )
                break
        self._bearish_db.write_financials(financials)

    @validate_call
    def write_many_series(self, tickers: List[Ticker], type: SeriesLength) -> None:
        tickers = self.get_tickers_without_price(tickers)
        for ticker in tickers:
            for source in self.price_sources:
                try:
                    series_ = source.read_series(ticker, type)
                except (InvalidApiKeyError, LimitApiKeyReachedError, Exception) as e:
                    logger.error(f"Error reading series: {e}")
                    continue
                if series_:
                    price_date = Prices(prices=series_).get_last_date()
                    self._bearish_db.write_series(series_)
                    self._bearish_db.write_tracker(
                        Tracker(
                            symbol=ticker.symbol,
                            source=source.__source__,
                            exchange=ticker.exchange,
                            price=True,
                            price_date=price_date,
                        )
                    )
                    break

    def read_sources(self) -> List[str]:
        return self._bearish_db.read_sources()

    def get_tickers(self, exchange_query: ExchangeQuery) -> List[Ticker]:
        return self._bearish_db.get_tickers(exchange_query)

    def get_detailed_tickers(self, countries: List[Countries]) -> None:
        tickers = self.get_tickers(
            self.exchanges.get_exchange_query(
                cast(List[Countries], countries), self.get_asset_sources()  # type: ignore
            )
        )
        asset_query = AssetQuery(symbols=Symbols(equities=tickers))  # type: ignore
        self.write_detailed_assets(asset_query)

    def get_financials(self, countries: List[Countries]) -> None:
        tickers = self.get_tickers(
            self.exchanges.get_exchange_query(
                cast(List[Countries], countries), self.get_detailed_asset_sources()  # type: ignore
            )
        )
        self.write_many_financials(tickers)

    def get_prices(self, countries: List[Countries]) -> None:
        tickers = self.get_tickers(
            self.exchanges.get_exchange_query(
                cast(List[Countries], countries), self.get_detailed_asset_sources()  # type: ignore
            )
        )
        self.write_many_series(tickers, "max")

    def update_prices(self, symbols: List[str]) -> None:
        tickers = self._get_tracked_tickers(TrackerQuery(price=True))
        tickers = [t for t in tickers if t.symbol in symbols]
        self.write_many_series(tickers, "max")


class CountryEnum(str, Enum): ...


CountriesEnum = Enum(  # type: ignore
    "CountriesEnum",
    {country: country for country in get_args(Countries)},
    type=CountryEnum,
)


@app.command()
def tickers(
    path: Path,
    countries: Annotated[List[CountriesEnum], typer.Argument()],
    api_keys: Optional[Path] = None,
) -> None:

    logger.info(
        f"Writing assets to database for countries: {countries}",
    )
    source_api_keys = SourceApiKeys.from_file(api_keys)
    bearish = Bearish(path=path, api_keys=source_api_keys)
    bearish.write_assets()
    bearish.get_detailed_tickers(countries)  # type: ignore


@app.command()
def financials(
    path: Path,
    countries: Annotated[List[CountriesEnum], typer.Argument()],
    api_keys: Optional[Path] = None,
) -> None:
    source_api_keys = SourceApiKeys.from_file(api_keys)
    bearish = Bearish(path=path, api_keys=source_api_keys)
    bearish.get_financials(countries)  # type: ignore


@app.command()
def prices(
    path: Path,
    countries: Annotated[List[CountriesEnum], typer.Argument()],
    api_keys: Optional[Path] = None,
) -> None:
    source_api_keys = SourceApiKeys.from_file(api_keys)
    bearish = Bearish(path=path, api_keys=source_api_keys)
    bearish.get_prices(countries)  # type: ignore


@app.command()
def update_prices(
    path: Path,
    symbols: Annotated[List[str], typer.Argument()],
    api_keys: Optional[Path] = None,
) -> None:
    source_api_keys = SourceApiKeys.from_file(api_keys)
    bearish = Bearish(path=path, api_keys=source_api_keys)
    bearish.update_prices(symbols)


if __name__ == "__main__":
    app()
