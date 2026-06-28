#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
芯动联科股票分析 - 简化版
使用纯Python标准库，不依赖第三方库
"""

import json
import csv
from datetime import datetime

print("=" * 60)
print("芯动联科 (688582.SH) 股票分析")
print("=" * 60)

# 读取数据
print("\n步骤 1/4: 读取数据...")
with open('stock_data.json', 'r', encoding='utf-8') as f:
    stock_data = json.load(f)

with open('daily_basic_data.json', 'r', encoding='utf-8') as f:
    basic_data = json.load(f)

# 按日期排序
stock_data.sort(key=lambda x: x['trade_date'])
basic_data.sort(key=lambda x: x['trade_date'])

print("√ 日交易数据: {} 条记录".format(len(stock_data)))
print("√ 每日指标数据: {} 条记录".format(len(basic_data)))

# 基本统计
close_start = stock_data[0]['close']
close_end = stock_data[-1]['close']
price_change = ((close_end / close_start) - 1) * 100
price_max = max([d['high'] for d in stock_data])
price_min = min([d['low'] for d in stock_data])
price_avg = sum([d['close'] for d in stock_data]) / len(stock_data)

print(f"✓ 数据时间范围: {stock_data[0]['trade_date']} ~ {stock_data[-1]['trade_date']}")
print(f"✓ 期间涨跌幅: {price_change:.2f}%")

# 计算简单移动平均线
def calc_ma(data, period):
    ma = []
    for i in range(len(data)):
        if i < period - 1:
            ma.append(None)
        else:
            sum_val = sum([data[j]['close'] for j in range(i - period + 1, i + 1)])
            ma.append(sum_val / period)
    return ma

print("\n步骤 2/4: 计算技术指标...")
ma5 = calc_ma(stock_data, 5)
ma10 = calc_ma(stock_data, 10)
ma20 = calc_ma(stock_data, 20)

# 计算RSI
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

# 当前值
rsi_current = rsi[-1] if rsi[-1] is not None else 50
pe_current = basic_data[-1]['pe']
pb_current = basic_data[-1]['pb']

print("✓ MA均线 (5, 10, 20)")
print("✓ RSI指标")
print(f"✓ 当前RSI: {rsi_current:.2f}")
print(f"✓ 当前PE: {pe_current:.2f}")

# 生成CSV（含技术指标）
print("\n步骤 3/4: 生成CSV文件...")
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

print("✓ CSV已保存: 芯动联科_完整数据.csv")

# 生成HTML报告
print("\n步骤 4/4: 生成HTML报告...")
dates = [d['trade_date'][:4] + '-' + d['trade_date'][4:6] + '-' + d['trade_date'][6:8] for d in stock_data]
closes = [d['close'] for d in stock_data]

# 判断RSI状态
if rsi_current > 70:
    rsi_status = '超买'
    rsi_advice = 'RSI指标显示超买（>70），建议谨慎操作，可适当减仓。'
elif rsi_current < 30:
    rsi_status = '超卖'
    rsi_advice = 'RSI指标显示超卖（<30），可能存在反弹机会，可适当关注。'
else:
    rsi_status = '中性'
    rsi_advice = 'RSI指标处于中性区域（30-70），走势相对平稳。'

# 判断PE状态
if pe_current > 50:
    pe_status = '偏高'
    pe_advice = f'估值偏高（PE={pe_current:.2f}），注意投资风险。'
else:
    pe_status = '合理'
    pe_advice = f'估值相对合理（PE={pe_current:.2f}）。'

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>芯动联科股票分析报告</title>
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
    <h1>芯动联科 (688582.SH) 股票分析报告</h1>
    <p style="text-align: right;">报告日期: {datetime.now().strftime('%Y年%m月%d日')}</p>
    
    <h2>一、数据统计摘要</h2>
    <table>
        <tr><th>指标</th><th>数值</th><th>说明</th></tr>
        <tr><td>期初价格</td><td>{close_start:.2f} 元</td><td>{stock_data[0]['trade_date'][:4]}-{stock_data[0]['trade_date'][4:6]}-{stock_data[0]['trade_date'][6:8]}</td></tr>
        <tr><td>期末价格</td><td>{close_end:.2f} 元</td><td>{stock_data[-1]['trade_date'][:4]}-{stock_data[-1]['trade_date'][4:6]}-{stock_data[-1]['trade_date'][6:8]}</td></tr>
        <tr><td>期间涨跌幅</td><td>{price_change:.2f}%</td><td>{'上涨' if price_change > 0 else '下跌'}</td></tr>
        <tr><td>最高价</td><td>{price_max:.2f} 元</td><td>期间最高</td></tr>
        <tr><td>最低价</td><td>{price_min:.2f} 元</td><td>期间最低</td></tr>
        <tr><td>平均收盘价</td><td>{price_avg:.2f} 元</td><td>期间平均</td></tr>
        <tr><td>当前RSI</td><td>{rsi_current:.2f}</td><td>{rsi_status}</td></tr>
        <tr><td>当前PE</td><td>{pe_current:.2f}</td><td>{pe_status}</td></tr>
        <tr><td>当前PB</td><td>{pb_current:.2f}</td><td>市净率</td></tr>
    </table>
    
    <h2>二、K线分析</h2>
    <p>K线图是技术分析的基础工具，通过每日的开盘价、收盘价、最高价、最低价四个价格，直观展示股价的波动情况。</p>
    
    <div class="chart-container">
        <div class="chart-title">图1: 芯动联科股价走势与均线分析</div>
        <canvas id="chart1"></canvas>
        <div class="interpretation">
            <strong>解读:</strong> 从数据可以看出，该股票在2025年8月中旬出现一波快速上涨（最高88.95元），随后进入震荡调整阶段。
            均线系统显示，短期均线与长期均线的关系反映了市场的多空力量对比。当短期均线在长期均线上方时，表明中长期趋势向上；反之则表明趋势向下。
        </div>
    </div>
    
    <h2>三、技术指标分析</h2>
    <div class="chart-container">
        <div class="chart-title">图2: RSI相对强弱指标</div>
        <canvas id="chart2"></canvas>
        <div class="interpretation">
            <strong>解读:</strong> RSI指标衡量股价的超买超卖情况。RSI>70为超买区域，股价可能面临回调压力；RSI<30为超卖区域，股价可能存在反弹机会；30≤RSI≤70为中性区域，股价走势相对平稳。
            当前RSI为{rsi_current:.2f}，处于{rsi_status}区域。
        </div>
    </div>
    
    <h2>四、估值指标分析</h2>
    <div class="chart-container">
        <div class="chart-title">图3: 估值指标分析（PE、PB）</div>
        <canvas id="chart3"></canvas>
        <div class="interpretation">
            <strong>解读:</strong> 
            <br><strong>市盈率(PE):</strong> 当前PE为{pe_current:.2f}，{pe_status}。PE越高，表明市场对公司未来增长预期越高，但也意味着投资风险越大。
            <br><strong>市净率(PB):</strong> 当前PB为{pb_current:.2f}。PB>1表明市场对公司资产质量有信心；PB<1可能被低估，但也可能反映公司盈利能力较弱。
        </div>
    </div>
    
    <h2>五、投资建议</h2>
    <div class="interpretation">
        <p><strong>综合建议:</strong></p>
        <p>{rsi_advice}</p>
        <p>{pe_advice}</p>
        <p>• 建议投资者根据自身风险承受能力和投资目标，制定合理的投资策略。</p>
        <p>• 建议分散投资，控制仓位，设置止损点。</p>
        <p>• 科创板股票波动较大，投资者应注意风险控制。</p>
    </div>
    
    <h2>六、风险提示</h2>
    <div class="risk-warning">
        <p>1. 股市有风险，投资需谨慎。</p>
        <p>2. 本报告仅供参考，不构成投资建议。</p>
        <p>3. 技术分析存在滞后性，投资者应结合基本面和市场环境综合判断。</p>
        <p>4. 科创板股票波动较大，投资者应注意风险控制。</p>
        <p>5. 本报告数据来源于Tushare，数据的准确性和完整性有待验证。</p>
    </div>
    
    <hr>
    <p style="text-align: center; font-size: 9pt; color: #666;">本报告由AI自动生成，仅供学习研究使用。</p>
    
    <script>
        // 图表数据
        const dates = {json.dumps(dates)};
        const closes = {json.dumps(closes)};
        const ma5 = {json.dumps([round(v, 2) if v is not None else None for v in ma5])};
        const ma10 = {json.dumps([round(v, 2) if v is not None else None for v in ma10])};
        const ma20 = {json.dumps([round(v, 2) if v is not None else None for v in ma20])};
        const rsi = {json.dumps([round(v, 2) if v is not None else None for v in rsi])};
        const pe = {json.dumps([d['pe'] for d in basic_data])};
        const pb = {json.dumps([d['pb'] for d in basic_data])};
        
        // 图1: 股价走势与均线
        new Chart(document.getElementById('chart1'), {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [
                    {{ label: '收盘价', data: closes, borderColor: '#333', borderWidth: 2, fill: false, tension: 0.1 }},
                    {{ label: 'MA5', data: ma5, borderColor: '#FF6600', borderWidth: 1.5, fill: false, tension: 0.1 }},
                    {{ label: 'MA10', data: ma10, borderColor: '#3366FF', borderWidth: 1.5, fill: false, tension: 0.1 }},
                    {{ label: 'MA20', data: ma20, borderColor: '#00CC00', borderWidth: 1.5, fill: false, tension: 0.1 }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{ display: true, text: '股价走势与均线', font: {{ size: 16 }} }}
                }},
                scales: {{
                    x: {{ display: true, title: {{ display: true, text: '交易日期' }} }},
                    y: {{ display: true, title: {{ display: true, text: '价格(元)' }} }}
                }}
            }}
        }});
        
        // 图2: RSI指标
        const rsiDates = dates.slice(14);  // RSI需要前14个数据来计算
        const rsiData = rsi.slice(14);
        
        new Chart(document.getElementById('chart2'), {{
            type: 'line',
            data: {{
                labels: rsiDates,
                datasets: [
                    {{ label: 'RSI(14)', data: rsiData, borderColor: '#FF6600', borderWidth: 2, fill: false, tension: 0.1 }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{ display: true, text: 'RSI相对强弱指标', font: {{ size: 16 }} }},
                    annotation: {{
                        annotations: {{
                            line1: {{
                                type: 'line',
                                yMin: 70,
                                yMax: 70,
                                borderColor: 'red',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {{ content: '超买线(70)', enabled: true, position: 'start' }}
                            }},
                            line2: {{
                                type: 'line',
                                yMin: 30,
                                yMax: 30,
                                borderColor: 'green',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {{ content: '超卖线(30)', enabled: true, position: 'start' }}
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ display: true, title: {{ display: true, text: '交易日期' }} }},
                    y: {{ display: true, title: {{ display: true, text: 'RSI' }}, min: 0, max: 100 }}
                }}
            }}
        }});
        
        // 图3: 估值指标
        new Chart(document.getElementById('chart3'), {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [
                    {{ label: '市盈率(PE)', data: pe, borderColor: '#FF6600', borderWidth: 2, yAxisID: 'y', fill: false, tension: 0.1 }},
                    {{ label: '市净率(PB)', data: pb, borderColor: '#3366FF', borderWidth: 2, yAxisID: 'y1', fill: false, tension: 0.1 }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{ display: true, text: '估值指标分析', font: {{ size: 16 }} }}
                }},
                scales: {{
                    x: {{ display: true, title: {{ display: true, text: '交易日期' }} }},
                    y: {{ type: 'linear', display: true, position: 'left', title: {{ display: true, text: 'PE' }} }},
                    y1: {{ type: 'linear', display: true, position: 'right', title: {{ display: true, text: 'PB' }}, grid: {{ drawOnChartArea: false }} }}
                }}
            }}
        }});
    </script>
</body>
</html>'''

with open('芯动联科股票分析报告.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ HTML报告已保存: 芯动联科股票分析报告.html")

# 生成Jupyter Notebook
print("\n步骤 5/5: 生成Jupyter Notebook...")
notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# 芯动联科 (688582.SH) 股票分析\n",
                "\n",
                "本Notebook包含对芯动联科股票的完整分析。\n"
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
                "print('环境准备完成')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. 读取数据\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 读取数据\n",
                "with open('stock_data.json', 'r', encoding='utf-8') as f:\n",
                "    stock_data = json.load(f)\n",
                "\n",
                "with open('daily_basic_data.json', 'r', encoding='utf-8') as f:\n",
                "    basic_data = json.load(f)\n",
                "\n",
                "print(f'日交易数据: {len(stock_data)} 条')\n",
                "print(f'每日指标数据: {len(basic_data)} 条')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. 统计分析\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 基本统计\n",
                "close_start = stock_data[0]['close']\n",
                "close_end = stock_data[-1]['close']\n",
                "price_change = ((close_end / close_start) - 1) * 100\n",
                "price_max = max([d['high'] for d in stock_data])\n",
                "price_min = min([d['low'] for d in stock_data])\n",
                "\n",
                "print('=== 价格统计 ===')\n",
                "print(f'期初价格: {close_start:.2f} 元')\n",
                "print(f'期末价格: {close_end:.2f} 元')\n",
                "print(f'期间涨跌幅: {price_change:.2f}%')\n",
                "print(f'最高价: {price_max:.2f} 元')\n",
                "print(f'最低价: {price_min:.2f} 元')\n"
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

print("✓ Jupyter Notebook已保存: 芯动联科股票分析.ipynb")

print("\n" + "=" * 60)
print("分析完成！")
print("=" * 60)
print("\n生成的文件:")
print("1. 芯动联科_完整数据.csv - 完整数据（含技术指标）")
print("2. 芯动联科股票分析报告.html - HTML分析报告")
print("3. 芯动联科股票分析.ipynb - Jupyter Notebook")
print("\n所有文件已保存到当前目录。")
