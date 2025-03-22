# L2Data Reader

A Python package for reading Level 2 market data from binary files.

## Installation

```bash
pip install l2data-reader
```

## Usage

```python
import logging
from l2data_reader import MarketDataReader, configure_logging

# 配置日志
logger = configure_logging(level=logging.INFO)

# 初始化读取器
reader = MarketDataReader(
    logger=logger,
    index_file="path/to/market_data.idx",
    data_file="path/to/market_data.bin"
)

# 读取数据
while True:
    result = reader.read_next()
    if not result:
        break
    
    header, market_data = result
    
    # 处理不同类型的市场数据
    if header.msg_type == 1001:  # Tick data
        tick_data = market_data.secu_depth_market_data
        print(f"Symbol: {tick_data.symbol}, Price: {tick_data.last_price}")
    elif header.msg_type == 1002:  # Order data
        order_data = market_data.transaction_entrust_data
        print(f"Symbol: {order_data.symbol}, Order Price: {order_data.order_price}")
    elif header.msg_type == 1003:  # Trade data
        trade_data = market_data.transaction_trade_data
        print(f"Symbol: {trade_data.symbol}, Trade Price: {trade_data.trade_price}")

# 关闭读取器
reader.close()
```

## Features

- Read Level 2 market data from binary files
- Support for tick data, order data, and trade data
- Memory-efficient reading with memory mapping
- Configurable logging

## License

MIT

