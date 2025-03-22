# level2-order-book

[![PyPI version](https://badge.fury.io/py/level2-order-book.svg)](https://badge.fury.io/py/level2-order-book)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 简介

`level2-order-book` 是一个用于处理和分析 Level 2 行情数据的 Python 库，专注于订单簿的构建、更新和撮合功能。该库可以帮助金融分析师、量化交易员和研究人员更好地理解市场微观结构。

## 主要功能

- **订单簿构建**：根据逐笔委托数据构建完整的订单簿
- **订单簿更新**：支持通过逐笔委托和逐笔成交数据实时更新订单簿
- **订单撮合模拟**：模拟交易所撮合引擎的行为
- **快照功能**：提供订单簿的实时快照，包括买卖盘各档位的价格和数量

## 安装

```bash
pip install level2-order-book
```

## 快速开始

### 基本使用

```python
from level2_order_book import OrderBook

# 创建订单簿
order_book = OrderBook(symbol="000001.SZ")

# 获取订单簿快照
previous_snapshot, current_snapshot = order_book.snapshot()
print(current_snapshot)
```

### 通过逐笔委托更新订单簿

```python
# 准备委托数据
entrusts = [
    {
        "order_type": OrdActionType.ADD,
        "seq_no": 1,
        "order_id": "12345",
        "symbol": "000001.SZ",
        "price": 10.5,
        "volume": 100,
        "order_side": Direction.BUY
    },
    {
        "order_type": OrdActionType.ADD,
        "seq_no": 2,
        "order_id": "12346",
        "symbol": "000001.SZ",
        "price": 10.6,
        "volume": 200,
        "order_side": Direction.SELL
    }
]

# 更新订单簿
order_book.update_by_entrusts(entrusts)

# 获取更新后的快照
previous_snapshot, current_snapshot = order_book.snapshot()
```

### 通过逐笔成交更新订单簿

```python
# 准备成交数据
trades = [
    {
        "trade_type": TrdType.BUY,
        "volume": 50,
        "buy_order_no": "12345",
        "sell_order_no": "12346",
        "trade_date": 20230101,
        "transact_time": 93000000
    }
]

# 更新订单簿
results = order_book.update_by_trades(trades)
```

## 核心类

### OrderBook

订单簿类，维护买卖盘的价格和数量信息。

主要方法：
- `add_order(order)`: 添加订单到订单簿
- `cancel_order(order)`: 从订单簿中撤销订单
- `reduce_order(order_id, volume)`: 减少指定订单的数量
- `update_by_entrusts(entrusts)`: 通过逐笔委托列表更新订单簿
- `update_by_trades(trades)`: 通过逐笔成交列表更新订单簿
- `snapshot(depth=None)`: 获取订单簿快照

### Order

订单类，表示单个委托订单。

属性：
- `seq_no`: 订单序列号
- `order_id`: 订单ID
- `symbol`: 标的代码
- `price`: 委托价格
- `volume`: 委托数量
- `side`: 订单方向（买/卖）

## 依赖

- Python >= 3.7
- l2data-reader >= 0.1.13

## 许可证

MIT

## 贡献

欢迎提交问题和拉取请求！

## 作者

JasonJiang0303 (chinese88+0303@2925.com)