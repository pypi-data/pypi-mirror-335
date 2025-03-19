# Ping

Types:

```python
from hedgewise.types import PingPingResponse
```

Methods:

- <code title="get /ping">client.ping.<a href="./src/hedgewise/resources/ping.py">ping</a>() -> <a href="./src/hedgewise/types/ping_ping_response.py">PingPingResponse</a></code>

# Data

Types:

```python
from hedgewise.types import Tick, DataRetrieveResponse
```

Methods:

- <code title="get /v1/data">client.data.<a href="./src/hedgewise/resources/data.py">retrieve</a>() -> <a href="./src/hedgewise/types/data_retrieve_response.py">DataRetrieveResponse</a></code>

# Assets

Types:

```python
from hedgewise.types import AssetListResponse
```

Methods:

- <code title="get /v1/assets">client.assets.<a href="./src/hedgewise/resources/assets/assets.py">list</a>() -> <a href="./src/hedgewise/types/asset_list_response.py">AssetListResponse</a></code>

## Futures

Types:

```python
from hedgewise.types.assets import (
    FutureListResponse,
    FutureGetHistoricalPricesResponse,
    FutureGetTradingCalendarResponse,
)
```

Methods:

- <code title="get /v1/assets/futures">client.assets.futures.<a href="./src/hedgewise/resources/assets/futures/futures.py">list</a>() -> <a href="./src/hedgewise/types/assets/future_list_response.py">FutureListResponse</a></code>
- <code title="get /v1/assets/futures/prices/{symbol}">client.assets.futures.<a href="./src/hedgewise/resources/assets/futures/futures.py">get_historical_prices</a>(symbol, \*\*<a href="src/hedgewise/types/assets/future_get_historical_prices_params.py">params</a>) -> <a href="./src/hedgewise/types/assets/future_get_historical_prices_response.py">FutureGetHistoricalPricesResponse</a></code>
- <code title="get /v1/assets/futures/calendars/{symbol}">client.assets.futures.<a href="./src/hedgewise/resources/assets/futures/futures.py">get_trading_calendar</a>(symbol, \*\*<a href="src/hedgewise/types/assets/future_get_trading_calendar_params.py">params</a>) -> <a href="./src/hedgewise/types/assets/future_get_trading_calendar_response.py">FutureGetTradingCalendarResponse</a></code>

### Forecasts

Types:

```python
from hedgewise.types.assets.futures import Asset, ForecastGetResponse, ForecastGetLongTermResponse
```

Methods:

- <code title="get /v1/assets/futures/forecasts/{symbol}">client.assets.futures.forecasts.<a href="./src/hedgewise/resources/assets/futures/forecasts.py">get</a>(symbol, \*\*<a href="src/hedgewise/types/assets/futures/forecast_get_params.py">params</a>) -> <a href="./src/hedgewise/types/assets/futures/forecast_get_response.py">ForecastGetResponse</a></code>
- <code title="get /v1/assets/futures/forecasts/{symbol}/long_term_forecast">client.assets.futures.forecasts.<a href="./src/hedgewise/resources/assets/futures/forecasts.py">get_long_term</a>(symbol, \*\*<a href="src/hedgewise/types/assets/futures/forecast_get_long_term_params.py">params</a>) -> <a href="./src/hedgewise/types/assets/futures/forecast_get_long_term_response.py">ForecastGetLongTermResponse</a></code>

### Indicators

Types:

```python
from hedgewise.types.assets.futures import IndicatorListResponse, IndicatorGetHedgeResponse
```

Methods:

- <code title="get /v1/assets/futures/indicators">client.assets.futures.indicators.<a href="./src/hedgewise/resources/assets/futures/indicators.py">list</a>() -> <a href="./src/hedgewise/types/assets/futures/indicator_list_response.py">IndicatorListResponse</a></code>
- <code title="get /v1/assets/futures/indicators/hedge/{symbol}">client.assets.futures.indicators.<a href="./src/hedgewise/resources/assets/futures/indicators.py">get_hedge</a>(symbol, \*\*<a href="src/hedgewise/types/assets/futures/indicator_get_hedge_params.py">params</a>) -> <a href="./src/hedgewise/types/assets/futures/indicator_get_hedge_response.py">IndicatorGetHedgeResponse</a></code>

# Forex

Types:

```python
from hedgewise.types import ForexData, ForexRetrieveResponse, ForexListResponse
```

Methods:

- <code title="get /v1/forex/{code}">client.forex.<a href="./src/hedgewise/resources/forex.py">retrieve</a>(code, \*\*<a href="src/hedgewise/types/forex_retrieve_params.py">params</a>) -> <a href="./src/hedgewise/types/forex_retrieve_response.py">ForexRetrieveResponse</a></code>
- <code title="get /v1/forex">client.forex.<a href="./src/hedgewise/resources/forex.py">list</a>() -> <a href="./src/hedgewise/types/forex_list_response.py">ForexListResponse</a></code>

# Features

Types:

```python
from hedgewise.types import (
    TransformedFeature,
    FeatureListResponse,
    FeatureRetrieveHistoricalResponse,
)
```

Methods:

- <code title="get /v1/features">client.features.<a href="./src/hedgewise/resources/features.py">list</a>(\*\*<a href="src/hedgewise/types/feature_list_params.py">params</a>) -> <a href="./src/hedgewise/types/feature_list_response.py">FeatureListResponse</a></code>
- <code title="get /v1/features/weighted_index/">client.features.<a href="./src/hedgewise/resources/features.py">get_weighted_index</a>(\*\*<a href="src/hedgewise/types/feature_get_weighted_index_params.py">params</a>) -> <a href="./src/hedgewise/types/transformed_feature.py">TransformedFeature</a></code>
- <code title="get /v1/features/historical/{feature_code}">client.features.<a href="./src/hedgewise/resources/features.py">retrieve_historical</a>(feature_code, \*\*<a href="src/hedgewise/types/feature_retrieve_historical_params.py">params</a>) -> <a href="./src/hedgewise/types/feature_retrieve_historical_response.py">FeatureRetrieveHistoricalResponse</a></code>
- <code title="get /v1/features/transform/{feature_code}">client.features.<a href="./src/hedgewise/resources/features.py">transform_historical</a>(feature_code, \*\*<a href="src/hedgewise/types/feature_transform_historical_params.py">params</a>) -> <a href="./src/hedgewise/types/transformed_feature.py">TransformedFeature</a></code>

# Models

## Performance

Types:

```python
from hedgewise.types.models import PerformanceRetrieveResponse, PerformanceListResponse
```

Methods:

- <code title="get /v1/models/performance/{symbol}">client.models.performance.<a href="./src/hedgewise/resources/models/performance.py">retrieve</a>(symbol, \*\*<a href="src/hedgewise/types/models/performance_retrieve_params.py">params</a>) -> <a href="./src/hedgewise/types/models/performance_retrieve_response.py">PerformanceRetrieveResponse</a></code>
- <code title="get /v1/models/performance">client.models.performance.<a href="./src/hedgewise/resources/models/performance.py">list</a>() -> <a href="./src/hedgewise/types/models/performance_list_response.py">PerformanceListResponse</a></code>

# Supply

Types:

```python
from hedgewise.types import FeatureCategory, SupplyRetrieveResponse, SupplyListResponse
```

Methods:

- <code title="get /v1/supply/{symbol}">client.supply.<a href="./src/hedgewise/resources/supply.py">retrieve</a>(symbol, \*\*<a href="src/hedgewise/types/supply_retrieve_params.py">params</a>) -> <a href="./src/hedgewise/types/supply_retrieve_response.py">SupplyRetrieveResponse</a></code>
- <code title="get /v1/supply">client.supply.<a href="./src/hedgewise/resources/supply.py">list</a>() -> <a href="./src/hedgewise/types/supply_list_response.py">SupplyListResponse</a></code>
