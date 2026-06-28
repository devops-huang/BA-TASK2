#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
计算股票技术指标并生成JavaScript数据
技术指标包括: MA, MACD, RSI, KDJ, 布林带等
"""

import json
import math

def calculate_ma(data, periods=[5, 10, 20, 60]):
    """计算移动平均线"""
    results = {}
    closes = [d['close'] for d in data]

    for period in periods:
        ma_values = []
        for i in range(len(closes)):
            if i < period - 1:
                ma_values.append(None)
            else:
                ma_values.append(round(sum(closes[i-period+1:i+1]) / period, 2))
        results[f'MA{period}'] = ma_values

    return results

def calculate_macd(data, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    closes = [d['close'] for d in data]
    n = len(closes)

    # 初始化结果数组
    dif = [None] * n
    dea = [None] * n
    macd = [None] * n

    # 计算EMA
    def ema(prices, period):
        """计算EMA"""
        multiplier = 2.0 / (period + 1)
        ema_val = prices[0]
        result = [ema_val]

        for i in range(1, len(prices)):
            ema_val = prices[i] * multiplier + ema_val * (1 - multiplier)
            result.append(ema_val)

        return result

    # 计算EMA快线和慢线
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)

    # 计算DIF (从第slow个数据开始)
    for i in range(slow-1, n):
        dif[i] = round(ema_fast[i] - ema_slow[i], 2)

    # 计算DEA (DIF的EMA)
    # 收集有效的DIF值
    valid_dif = [x for x in dif if x is not None]

    if len(valid_dif) > 0:
        dea_multiplier = 2.0 / (signal + 1)
        dea_val = valid_dif[0]
        dea_idx = 0

        for i in range(n):
            if dif[i] is not None:
                if dea_idx == 0:
                    dea[i] = round(dea_val, 2)
                else:
                    dea_val = dif[i] * dea_multiplier + dea_val * (1 - dea_multiplier)
                    dea[i] = round(dea_val, 2)
                dea_idx += 1

    # 计算MACD柱
    for i in range(n):
        if dif[i] is not None and dea[i] is not None:
            macd[i] = round((dif[i] - dea[i]) * 2, 2)

    return dif, dea, macd

def calculate_rsi(data, period=14):
    """计算RSI指标"""
    closes = [d['close'] for d in data]
    rsi_values = [None] * period

    for i in range(period, len(closes)):
        gains = []
        losses = []

        for j in range(i - period + 1, i + 1):
            change = closes[j] - closes[j-1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))

        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0

        if avg_loss == 0:
            rsi_values.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi_values.append(round(100 - (100 / (1 + rs)), 2))

    return rsi_values

def calculate_kdj(data, n=9, m1=3, m2=3):
    """计算KDJ指标"""
    closes = [d['close'] for d in data]
    highs = [d['high'] for d in data]
    lows = [d['low'] for d in data]

    k_values = [None] * (n - 1)
    d_values = [None] * (n - 1)
    j_values = [None] * (n - 1)

    k = 50
    d = 50

    for i in range(n - 1, len(closes)):
        low_n = min(lows[i-n+1:i+1])
        high_n = max(highs[i-n+1:i+1])

        if high_n == low_n:
            rsv = 50
        else:
            rsv = (closes[i] - low_n) / (high_n - low_n) * 100

        k = (m1 - 1) / m1 * k + 1 / m1 * rsv
        d = (m2 - 1) / m2 * d + 1 / m2 * k
        j = 3 * k - 2 * d

        k_values.append(round(k, 2))
        d_values.append(round(d, 2))
        j_values.append(round(j, 2))

    return k_values, d_values, j_values

def calculate_bollinger_bands(data, period=20, std_dev=2):
    """计算布林带"""
    closes = [d['close'] for d in data]

    middle_band = []
    upper_band = []
    lower_band = []

    for i in range(len(closes)):
        if i < period - 1:
            middle_band.append(None)
            upper_band.append(None)
            lower_band.append(None)
        else:
            slice_data = closes[i-period+1:i+1]
            mean = sum(slice_data) / period
            variance = sum((x - mean) ** 2 for x in slice_data) / period
            std = math.sqrt(variance)

            middle_band.append(round(mean, 2))
            upper_band.append(round(mean + std_dev * std, 2))
            lower_band.append(round(mean - std_dev * std, 2))

    return upper_band, middle_band, lower_band

def main():
    # 读取数据
    with open('stock_data.json', 'r', encoding='utf-8') as f:
        stock_data = json.load(f)

    with open('daily_basic_data.json', 'r', encoding='utf-8') as f:
        basic_data = json.load(f)

    # 计算技术指标
    print("计算移动平均线...")
    ma_data = calculate_ma(stock_data)

    print("计算MACD...")
    dif, dea, macd = calculate_macd(stock_data)

    print("计算RSI...")
    rsi = calculate_rsi(stock_data)

    print("计算KDJ...")
    k_values, d_values, j_values = calculate_kdj(stock_data)

    print("计算布林带...")
    upper_band, middle_band, lower_band = calculate_bollinger_bands(stock_data)

    # 准备日期数据
    dates = [d['trade_date'] for d in stock_data]

    # 生成JavaScript数据
    js_data = f"""
// 股票数据
const stockDates = {json.dumps(dates)};
const stockData = {json.dumps(stock_data)};

// 移动平均线
const ma5Data = {json.dumps(ma_data['MA5'])};
const ma10Data = {json.dumps(ma_data['MA10'])};
const ma20Data = {json.dumps(ma_data['MA20'])};
const ma60Data = {json.dumps(ma_data['MA60'])};

// MACD
const difData = {json.dumps(dif)};
const deaData = {json.dumps(dea)};
const macdData = {json.dumps(macd)};

// RSI
const rsiData = {json.dumps(rsi)};

// KDJ
const kData = {json.dumps(k_values)};
const dData = {json.dumps(d_values)};
const jData = {json.dumps(j_values)};

// 布林带
const upperBandData = {json.dumps(upper_band)};
const middleBandData = {json.dumps(middle_band)};
const lowerBandData = {json.dumps(lower_band)};

// 基本面数据
const basicData = {json.dumps(basic_data)};
"""

    # 保存到文件
    with open('indicators_data.js', 'w', encoding='utf-8') as f:
        f.write(js_data)

    print("技术指标计算完成！数据已保存到 indicators_data.js")

    # 计算统计数据
    closes = [d['close'] for d in stock_data]
    highs = [d['high'] for d in stock_data]
    lows = [d['low'] for d in stock_data]
    print(f"\n数据统计:")
    print(f"数据条数: {len(closes)}")
    print(f"最新收盘价: {closes[-1]}")
    print(f"期间最高价: {max(highs)}")
    print(f"期间最低价: {min(lows)}")
    print(f"平均收盘价: {round(sum(closes) / len(closes), 2)}")

if __name__ == '__main__':
    main()
