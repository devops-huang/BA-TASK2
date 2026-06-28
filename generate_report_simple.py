#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
芯动联科股票分析 - 无中文输出版
"""

import json
import csv
from datetime import datetime
import sys

print("=" * 60)
print("Stock Analysis Report Generation")
print("=" * 60)

# 读取数据
print("\nStep 1/5: Loading data...")
with open('stock_data.json', 'r', encoding='utf-8') as f:
    stock_data = json.load(f)

with open('daily_basic_data.json', 'r', encoding='utf-8') as f:
    basic_data = json.load(f)

# 按日期排序
stock_data.sort(key=lambda x: x['trade_date'])
basic_data.sort(key=lambda x: x['trade_date'])

print("  Stock data: {} records".format(len(stock_data)))
print("  Basic data: {} records".format(len(basic_data)))

# 基本统计
close_start = stock_data[0]['close']
close_end = stock_data[-1]['close']
price_change = ((close_end / close_start) - 1) * 100
price_max = max([d['high'] for d in stock_data])
price_min = min([d['low'] for d in stock_data])
price_avg = sum([d['close'] for d in stock_data]) / len(stock_data)

print("  Date range: {} ~ {}".format(stock_data[0]['trade_date'], stock_data[-1]['trade_date']))
print("  Price change: {:.2f}%".format(price_change))

# 计算技术指标
print("\nStep 2/5: Calculating technical indicators...")

def calc_ma(data, period):
    ma = []
    for i in range(len(data)):
        if i < period - 1:
            ma.append(None)
        else:
            sum_val = sum([data[j]['close'] for j in range(i - period + 1, i + 1)])
            ma.append(sum_val / period)
    return ma

ma5 = calc_ma(stock_data, 5)
ma10 = calc_ma(stock_data, 10)
ma20 = calc_ma(stock_data, 20)

def calc_rsi(data, period=14):
    rsi = []
    for i in range(len(data)):
        if i < period:
            rsi.append(None)
        else:
            gains = 0
            losses = 0
            for j in range(period):
                diff = data[i - j]['close'] - data[i - j - 1]['close']
                if diff > 0:
                    gains += diff
                else:
                    losses -= diff
            avg_gain = gains / period
            avg_loss = losses / period
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
    return rsi

rsi = calc_rsi(stock_data)

rsi_current = rsi[-1] if rsi[-1] is not None else 50
pe_current = basic_data[-1]['pe']
pb_current = basic_data[-1]['pb']

print("  MA: OK")
print("  RSI: OK")
print("  Current RSI: {:.2f}".format(rsi_current))
print("  Current PE: {:.2f}".format(pe_current))

# 生成CSV
print("\nStep 3/5: Generating CSV file...")
with open('芯动联科_完整数据.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['trade_date', 'open', 'high', 'low', 'close', 'MA5', 'MA10', 'MA20', 'RSI', 'PE', 'PB'])
    
    for i in range(len(stock_data)):
        row = [
            stock_data[i]['trade_date'],
            stock_data[i]['open'],
            stock_data[i]['high'],
            stock_data[i]['low'],
            stock_data[i]['close'],
            round(ma5[i], 2) if ma5[i] is not None else '',
            round(ma10[i], 2) if ma10[i] is not None else '',
            round(ma20[i], 2) if ma20[i] is not None else '',
            round(rsi[i], 2) if rsi[i] is not None else '',
            basic_data[i]['pe'] if i < len(basic_data) else '',
            basic_data[i]['pb'] if i < len(basic_data) else ''
        ]
        writer.writerow(row)

print("  CSV saved: 芯动联科_完整数据.csv")

# 生成HTML报告
print("\nStep 4/5: Generating HTML report...")
dates = [d['trade_date'][:4] + '-' + d['trade_date'][4:6] + '-' + d['trade_date'][6:8] for d in stock_data]
closes = [d['close'] for d in stock_data]

# 判断状态
if rsi_current > 70:
    rsi_status = 'Overbought'
    rsi_advice = 'RSI indicates overbought (>70), consider reducing position.'
elif rsi_current < 30:
    rsi_status = 'Oversold'
    rsi_advice = 'RSI indicates oversold (<30), potential rebound opportunity.'
else:
    rsi_status = 'Neutral'
    rsi_advice = 'RSI is in neutral zone (30-70), trend is relatively stable.'

if pe_current > 50:
    pe_status = 'High'
    pe_advice = 'Valuation is high (PE={:.2f}), watch for risk.'.format(pe_current)
else:
    pe_status = 'Reasonable'
    pe_advice = 'Valuation is reasonable (PE={:.2f}).'.format(pe_current)

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Stock Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: SimSun, "Times New Roman", serif; font-size: 10.5pt; line-height: 1.5; text-align: justify; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; }}
        h1 {{ text-align: center; font-size: 22pt; font-weight: bold; margin-bottom: 30px; }}
        h2 {{ font-size: 16pt; font-weight: bold; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #333; padding-bottom: 5px; }}
        p {{ margin-bottom: 10px; text-indent: 2em; }}
        .chart-container {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background: #f9f9f9; }}
        .chart-title {{ font-weight: bold; margin-bottom: 10px; text-align: center; font-size: 14pt; }}
        .interpretation {{ margin-top: 15px; padding: 10px; background: #fff; border-left: 4px solid #4CAF50; font-size: 10pt; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 10pt; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background: #f2f2f2; font-weight: bold; }}
        .risk-warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; border-radius: 5px; color: #856404; }}
    </style>
</head>
<body>
    <h1>Stock Analysis Report: 芯动联科 (688582.SH)</h1>
    <p style="text-align: right;">Report Date: ''' + datetime.now().strftime('%Y-%m-%d') + '''</p>
    
    <h2>1. Statistical Summary</h2>
    <table>
        <tr><th>Indicator</th><th>Value</th><th>Description</th></tr>
        <tr><td>Opening Price</td><td>''' + '{:.2f}'.format(close_start) + ''' 元</td><td>''' + stock_data[0]['trade_date'][:4] + '-' + stock_data[0]['trade_date'][4:6] + '-' + stock_data[0]['trade_date'][6:8] + '''</td></tr>
        <tr><td>Closing Price</td><td>''' + '{:.2f}'.format(close_end) + ''' 元</td><td>''' + stock_data[-1]['trade_date'][:4] + '-' + stock_data[-1]['trade_date'][4:6] + '-' + stock_data[-1]['trade_date'][6:8] + '''</td></tr>
        <tr><td>Price Change</td><td>''' + '{:.2f}%'.format(price_change) + '''</td><td>''' + ('Up' if price_change > 0 else 'Down') + '''</td></tr>
        <tr><td>Highest Price</td><td>''' + '{:.2f}'.format(price_max) + ''' 元</td><td>Highest during period</td></tr>
        <tr><td>Lowest Price</td><td>''' + '{:.2f}'.format(price_min) + ''' 元</td><td>Lowest during period</td></tr>
        <tr><td>Average Price</td><td>''' + '{:.2f}'.format(price_avg) + ''' 元</td><td>Average closing price</td></tr>
        <tr><td>Current RSI</td><td>''' + '{:.2f}'.format(rsi_current) + '''</td><td>''' + rsi_status + '''</td></tr>
        <tr><td>Current PE</td><td>''' + '{:.2f}'.format(pe_current) + '''</td><td>''' + pe_status + '''</td></tr>
        <tr><td>Current PB</td><td>''' + '{:.2f}'.format(pb_current) + '''</td><td>Price-to-Book</td></tr>
    </table>
    
    <h2>2. K-Line Analysis</h2>
    <p>K-line chart is the basic tool for technical analysis, showing price movements through open, close, high, and low prices.</p>
    
    <div class="chart-container">
        <div class="chart-title">Figure 1: Stock Price Trend and Moving Averages</div>
        <canvas id="chart1"></canvas>
        <div class="interpretation">
            <strong>Interpretation:</strong> The stock experienced a rapid rise in mid-August 2025 (peak at 88.95 yuan), followed by a period of consolidation and adjustment.
            The relationship between short-term and long-term moving averages reflects the bullish/bearish momentum in the market.
        </div>
    </div>
    
    <h2>3. Technical Indicators Analysis</h2>
    <div class="chart-container">
        <div class="chart-title">Figure 2: RSI (Relative Strength Index)</div>
        <canvas id="chart2"></canvas>
        <div class="interpretation">
            <strong>Interpretation:</strong> RSI measures overbought/oversold conditions. RSI > 70 indicates overbought (potential pullback); RSI < 30 indicates oversold (potential rebound). Current RSI is ''' + '{:.2f}'.format(rsi_current) + ''', in the ''' + rsi_status + ''' zone.
        </div>
    </div>
    
    <h2>4. Valuation Analysis</h2>
    <div class="chart-container">
        <div class="chart-title">Figure 3: Valuation Indicators (PE, PB)</div>
        <canvas id="chart3"></canvas>
        <div class="interpretation">
            <strong>Interpretation:</strong> 
            <br><strong>PE (Price-to-Earnings):</strong> Current PE is ''' + '{:.2f}'.format(pe_current) + ''', ''' + pe_status + '''. Higher PE indicates higher growth expectations, but also higher risk.
            <br><strong>PB (Price-to-Book):</strong> Current PB is ''' + '{:.2f}'.format(pb_current) + '''.
        </div>
    </div>
    
    <h2>5. Investment Recommendations</h2>
    <div class="interpretation">
        <p><strong>Comprehensive Advice:</strong></p>
        <p>''' + rsi_advice + '''</p>
        <p>''' + pe_advice + '''</p>
        <p>• Investors should formulate reasonable investment strategies based on their risk tolerance and investment objectives.</p>
        <p>• Diversification, position control, and stop-loss are recommended.</p>
    </div>
    
    <h2>6. Risk Warning</h2>
    <div class="risk-warning">
        <p>1. Stock market involves risks; invest with caution.</p>
        <p>2. This report is for reference only and does not constitute investment advice.</p>
        <p>3. Technical analysis has lag; investors should combine fundamental and market analysis.</p>
        <p>4. STAR Market stocks are highly volatile; investors should pay attention to risk control.</p>
    </div>
    
    <script>
        const dates = ''' + json.dumps(dates) + ''';
        const closes = ''' + json.dumps(closes) + ''';
        const ma5 = ''' + json.dumps([round(v, 2) if v is not None else None for v in ma5]) + ''';
        const ma10 = ''' + json.dumps([round(v, 2) if v is not None else None for v in ma10]) + ''';
        const ma20 = ''' + json.dumps([round(v, 2) if v is not None else None for v in ma20]) + ''';
        const rsi = ''' + json.dumps([round(v, 2) if v is not None else None for v in rsi]) + ''';
        const pe = ''' + json.dumps([d['pe'] for d in basic_data]) + ''';
        const pb = ''' + json.dumps([d['pb'] for d in basic_data]) + ''';
        
        // Figure 1: Price trend
        new Chart(document.getElementById('chart1'), {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    { label: 'Close Price', data: closes, borderColor: '#333', borderWidth: 2, fill: false, tension: 0.1 },
                    { label: 'MA5', data: ma5, borderColor: '#FF6600', borderWidth: 1.5, fill: false, tension: 0.1 },
                    { label: 'MA10', data: ma10, borderColor: '#3366FF', borderWidth: 1.5, fill: false, tension: 0.1 },
                    { label: 'MA20', data: ma20, borderColor: '#00CC00', borderWidth: 1.5, fill: false, tension: 0.1 }
                ]
            },
            options: {
                responsive: true,
                plugins: { title: { display: true, text: 'Stock Price Trend and Moving Averages', font: { size: 16 } } },
                scales: { x: { display: true, title: { display: true, text: 'Date' } }, y: { display: true, title: { display: true, text: 'Price (Yuan)' } } }
            }
        });
        
        // Figure 2: RSI
        const rsiDates = dates.slice(14);
        const rsiData = rsi.slice(14);
        
        new Chart(document.getElementById('chart2'), {
            type: 'line',
            data: {
                labels: rsiDates,
                datasets: [
                    { label: 'RSI(14)', data: rsiData, borderColor: '#FF6600', borderWidth: 2, fill: false, tension: 0.1 }
                ]
            },
            options: {
                responsive: true,
                plugins: { title: { display: true, text: 'RSI (Relative Strength Index)', font: { size: 16 } } },
                scales: { x: { display: true, title: { display: true, text: 'Date' } }, y: { display: true, title: { display: true, text: 'RSI' }, min: 0, max: 100 } }
            }
        });
        
        // Figure 3: Valuation
        new Chart(document.getElementById('chart3'), {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    { label: 'PE', data: pe, borderColor: '#FF6600', borderWidth: 2, yAxisID: 'y', fill: false, tension: 0.1 },
                    { label: 'PB', data: pb, borderColor: '#3366FF', borderWidth: 2, yAxisID: 'y1', fill: false, tension: 0.1 }
                ]
            },
            options: {
                responsive: true,
                plugins: { title: { display: true, text: 'Valuation Indicators (PE, PB)', font: { size: 16 } } },
                scales: { x: { display: true, title: { display: true, text: 'Date' } }, y: { type: 'linear', display: true, position: 'left', title: { display: true, text: 'PE' } }, y1: { type: 'linear', display: true, position: 'right', title: { display: true, text: 'PB' }, grid: { drawOnChartArea: false } } }
            }
        });
    </script>
</body>
</html>'''

with open('芯动联科股票分析报告.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("  HTML report saved: 芯动联科股票分析报告.html")

# 生成Jupyter Notebook
print("\nStep 5/5: Generating Jupyter Notebook...")
notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Stock Analysis: 芯动联科 (688582.SH)\n",
                "\n",
                "This notebook contains complete analysis of the stock.\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import json\n",
                "import csv\n",
                "from datetime import datetime\n",
                "\n",
                "print('Environment ready')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Load Data\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Load data\n",
                "with open('stock_data.json', 'r', encoding='utf-8') as f:\n",
                "    stock_data = json.load(f)\n",
                "\n",
                "with open('daily_basic_data.json', 'r', encoding='utf-8') as f:\n",
                "    basic_data = json.load(f)\n",
                "\n",
                "print('Data loaded successfully')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Statistical Analysis\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Basic statistics\n",
                "close_start = stock_data[0]['close']\n",
                "close_end = stock_data[-1]['close']\n",
                "price_change = ((close_end / close_start) - 1) * 100\n",
                "price_max = max([d['high'] for d in stock_data])\n",
                "price_min = min([d['low'] for d in stock_data])\n",
                "\n",
                "print('=== Price Statistics ===')\n",
                "print(f'Opening Price: {close_start:.2f} yuan')\n",
                "print(f'Closing Price: {close_end:.2f} yuan')\n",
                "print(f'Price Change: {price_change:.2f}%')\n",
                "print(f'Highest Price: {price_max:.2f} yuan')\n",
                "print(f'Lowest Price: {price_min:.2f} yuan')\n"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open('芯动联科股票分析.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=2)

print("  Jupyter Notebook saved: 芯动联科股票分析.ipynb")

print("\n" + "=" * 60)
print("Report Generation Complete!")
print("=" * 60)
print("\nGenerated files:")
print("1. 芯动联科_完整数据.csv - Complete data (with technical indicators)")
print("2. 芯动联科股票分析报告.html - HTML analysis report")
print("3. 芯动联科股票分析.ipynb - Jupyter Notebook")
print("\nAll files saved to current directory.")
