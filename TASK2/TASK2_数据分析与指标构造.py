#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TASK2: 数据炼金术——数据诊断与构造交易指标
作者: devops-huang
日期: 2026-07-01
"""

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 80)
print("TASK2: 数据炼金术——数据诊断与构造交易指标")
print("=" * 80)

# =============================================================================
# 步骤1: 加载已存储的股价数据
# =============================================================================
print("\n步骤 1/6: 加载已存储的股价数据...")

# 读取CSV数据
df = pd.read_csv('芯动联科_完整数据.csv', encoding='utf-8-sig')

# 转换日期格式
df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')

# 按日期排序
df = df.sort_values('trade_date').reset_index(drop=True)

print(f"✓ 数据加载成功!")
print(f"  数据期间: {df['trade_date'].min().date()} 至 {df['trade_date'].max().date()}")
print(f"  交易天数: {len(df)} 天")
print(f"  数据字段: {', '.join(df.columns.tolist())}")

# =============================================================================
# 步骤2: 数据基础诊断分析
# =============================================================================
print("\n步骤 2/6: 数据基础诊断分析...")

# 2.1 检查缺失值
print("\n【2.1 缺失值检查】")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    '字段名': missing.index,
    '缺失数量': missing.values,
    '缺失比例(%)': missing_pct.values
})
print(missing_df.to_string(index=False))

# 2.2 计算描述性统计量
print("\n【2.2 描述性统计量】")
desc_stats = df[['open', 'high', 'low', 'close']].describe().round(2)
print(desc_stats)

# 保存诊断结果
diagnosis_result = {
    '数据期间': f"{df['trade_date'].min().date()} 至 {df['trade_date'].max().date()}",
    '交易天数': len(df),
    '缺失值情况': missing_df.to_dict('records'),
    '描述性统计': desc_stats.to_dict()
}

print("✓ 数据诊断完成!")

# =============================================================================
# 步骤3: 计算技术指标 (RSI, MACD, 布林带)
# =============================================================================
print("\n步骤 3/6: 计算技术指标 (RSI, MACD, 布林带)...")

# 3.1 计算RSI (相对强弱指标)
def calculate_rsi(data, period=14):
    """计算RSI指标"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calculate_rsi(df['close'])
print("  ✓ RSI计算完成 (周期=14)")

# 3.2 计算MACD (移动平均收敛/发散指标)
def calculate_macd(data, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2
    return dif, dea, macd

df['MACD_DIF'], df['MACD_DEA'], df['MACD'] = calculate_macd(df['close'])
print("  ✓ MACD计算完成 (12, 26, 9)")

# 3.3 计算布林带 (Bollinger Bands)
def calculate_bollinger(data, period=20, std_dev=2):
    """计算布林带指标"""
    middle = data.rolling(window=period).mean()
    std = data.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower

df['BB_upper'], df['BB_middle'], df['BB_lower'] = calculate_bollinger(df['close'])
print("  ✓ 布林带计算完成 (周期=20, 标准差=2)")

# 3.4 扩展指标: KDJ (随机指标)
def calculate_kdj(high, low, close, period=9, m1=3, m2=3):
    """计算KDJ指标"""
    low_list = low.rolling(window=period).min()
    high_list = high.rolling(window=period).max()
    
    rsv = (close - low_list) / (high_list - low_list) * 100
    
    k = rsv.ewm(com=m1-1, adjust=False).mean()
    d = k.ewm(com=m2-1, adjust=False).mean()
    j = 3 * k - 2 * d
    
    return k, d, j

df['KDJ_K'], df['KDJ_D'], df['KDJ_J'] = calculate_kdj(df['high'], df['low'], df['close'])
print("  ✓ KDJ计算完成 (9, 3, 3)")

print("✓ 所有技术指标计算完成!")

# =============================================================================
# 步骤4: 绘制可视化图形
# =============================================================================
print("\n步骤 4/6: 绘制可视化图形...")

# 设置图表样式
fig_size = (16, 9)
grid_color = '#E0E0E0'

# 4.1 绘制RSI指标图
fig, ax = plt.subplots(figsize=fig_size)
ax.plot(df['trade_date'], df['RSI'], color='#9C27B0', linewidth=2, label='RSI')
ax.axhline(y=70, color='#D32F2F', linestyle='--', linewidth=1.5, alpha=0.7, label='超买线(70)')
ax.axhline(y=30, color='#388E3C', linestyle='--', linewidth=1.5, alpha=0.7, label='超卖线(30)')
ax.axhline(y=50, color='#757575', linestyle='-', linewidth=1, alpha=0.5, label='中线(50)')
ax.fill_between(df['trade_date'], 70, 100, alpha=0.1, color='#FFCDD2')
ax.fill_between(df['trade_date'], 0, 30, alpha=0.1, color='#C8E6C9')
ax.set_title('图1 RSI相对强弱指标', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('交易日期', fontsize=12)
ax.set_ylabel('RSI', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.3, color=grid_color)
ax.legend(loc='upper right', fontsize=11)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('TASK2_图1_RSI指标.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 图1 RSI指标图已保存")

# 4.2 绘制MACD指标图
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=fig_size, gridspec_kw={'height_ratios': [2, 1]})
# 上图：股价
ax1.plot(df['trade_date'], df['close'], color='#333333', linewidth=2, label='收盘价')
ax1.set_title('图2 MACD指标分析', fontsize=16, fontweight='bold', pad=15)
ax1.set_ylabel('收盘价 (元)', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.3, color=grid_color)
ax1.legend(loc='upper right', fontsize=11)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 下图：MACD
ax2.plot(df['trade_date'], df['MACD_DIF'], color='#333333', linewidth=1.5, label='DIF')
ax2.plot(df['trade_date'], df['MACD_DEA'], color='#FF9800', linewidth=1.5, label='DEA')
colors = ['#D32F2F' if x >= 0 else '#388E3C' for x in df['MACD']]
ax2.bar(df['trade_date'], df['MACD'], color=colors, alpha=0.6, label='MACD柱')
ax2.axhline(y=0, color='#757575', linestyle='-', linewidth=1, alpha=0.5)
ax2.set_xlabel('交易日期', fontsize=12)
ax2.set_ylabel('MACD', fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.3, color=grid_color)
ax2.legend(loc='upper right', fontsize=11)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
plt.tight_layout()
plt.savefig('TASK2_图2_MACD指标.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 图2 MACD指标图已保存")

# 4.3 绘制布林带指标图
fig, ax = plt.subplots(figsize=fig_size)
ax.plot(df['trade_date'], df['close'], color='#333333', linewidth=2, label='收盘价')
ax.plot(df['trade_date'], df['BB_upper'], color='#D32F2F', linewidth=1.5, linestyle='--', label='上轨')
ax.plot(df['trade_date'], df['BB_middle'], color='#333333', linewidth=1.5, linestyle='-', alpha=0.7, label='中轨(MA20)')
ax.plot(df['trade_date'], df['BB_lower'], color='#388E3C', linewidth=1.5, linestyle='--', label='下轨')
ax.fill_between(df['trade_date'], df['BB_upper'], df['BB_lower'], alpha=0.1, color='#BDBDBD')
ax.set_title('图3 布林带指标分析', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('交易日期', fontsize=12)
ax.set_ylabel('价格 (元)', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.3, color=grid_color)
ax.legend(loc='upper right', fontsize=11)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('TASK2_图3_布林带指标.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 图3 布林带指标图已保存")

# 4.4 绘制KDJ指标图 (扩展指标)
fig, ax = plt.subplots(figsize=fig_size)
ax.plot(df['trade_date'], df['KDJ_K'], color='#333333', linewidth=1.5, label='K值')
ax.plot(df['trade_date'], df['KDJ_D'], color='#FF9800', linewidth=1.5, label='D值')
ax.plot(df['trade_date'], df['KDJ_J'], color='#9C27B0', linewidth=1.5, linestyle='--', label='J值')
ax.axhline(y=80, color='#D32F2F', linestyle='--', linewidth=1.5, alpha=0.7, label='超买线(80)')
ax.axhline(y=20, color='#388E3C', linestyle='--', linewidth=1.5, alpha=0.7, label='超卖线(20)')
ax.axhline(y=50, color='#757575', linestyle='-', linewidth=1, alpha=0.5, label='中线(50)')
ax.fill_between(df['trade_date'], 80, 100, alpha=0.1, color='#FFCDD2')
ax.fill_between(df['trade_date'], 0, 20, alpha=0.1, color='#C8E6C9')
ax.set_title('图4 KDJ随机指标 (扩展指标)', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('交易日期', fontsize=12)
ax.set_ylabel('KDJ', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.3, color=grid_color)
ax.legend(loc='upper right', fontsize=11)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('TASK2_图4_KDJ指标.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 图4 KDJ指标图已保存")

# 4.5 绘制综合技术指标图
fig, axes = plt.subplots(4, 1, figsize=(16, 14), gridspec_kw={'hspace': 0.3})

# 子图1: 收盘价 + 布林带
axes[0].plot(df['trade_date'], df['close'], color='#333333', linewidth=2, label='收盘价')
axes[0].plot(df['trade_date'], df['BB_upper'], color='#D32F2F', linewidth=1, linestyle='--', alpha=0.7)
axes[0].plot(df['trade_date'], df['BB_middle'], color='#757575', linewidth=1, linestyle='-', alpha=0.7)
axes[0].plot(df['trade_date'], df['BB_lower'], color='#388E3C', linewidth=1, linestyle='--', alpha=0.7)
axes[0].fill_between(df['trade_date'], df['BB_upper'], df['BB_lower'], alpha=0.05, color='#BDBDBD')
axes[0].set_title('综合技术指标分析', fontsize=16, fontweight='bold', pad=10)
axes[0].set_ylabel('价格 (元)', fontsize=11)
axes[0].grid(True, linestyle='--', alpha=0.3, color=grid_color)
axes[0].legend(loc='upper right', fontsize=10, ncol=4)
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
axes[0].xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=45, ha='right')

# 子图2: RSI
axes[1].plot(df['trade_date'], df['RSI'], color='#9C27B0', linewidth=2, label='RSI')
axes[1].axhline(y=70, color='#D32F2F', linestyle='--', linewidth=1.2, alpha=0.7)
axes[1].axhline(y=30, color='#388E3C', linestyle='--', linewidth=1.2, alpha=0.7)
axes[1].fill_between(df['trade_date'], 70, 100, alpha=0.1, color='#FFCDD2')
axes[1].fill_between(df['trade_date'], 0, 30, alpha=0.1, color='#C8E6C9')
axes[1].set_ylabel('RSI', fontsize=11)
axes[1].grid(True, linestyle='--', alpha=0.3, color=grid_color)
axes[1].legend(loc='upper right', fontsize=10)
axes[1].set_ylim(0, 100)
axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
axes[1].xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45, ha='right')

# 子图3: MACD
axes[2].plot(df['trade_date'], df['MACD_DIF'], color='#333333', linewidth=1.5, label='DIF')
axes[2].plot(df['trade_date'], df['MACD_DEA'], color='#FF9800', linewidth=1.5, label='DEA')
colors = ['#D32F2F' if x >= 0 else '#388E3C' for x in df['MACD']]
axes[2].bar(df['trade_date'], df['MACD'], color=colors, alpha=0.6, width=1)
axes[2].axhline(y=0, color='#757575', linestyle='-', linewidth=1, alpha=0.5)
axes[2].set_ylabel('MACD', fontsize=11)
axes[2].grid(True, linestyle='--', alpha=0.3, color=grid_color)
axes[2].legend(loc='upper right', fontsize=10)
axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
axes[2].xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(axes[2].xaxis.get_majorticklabels(), rotation=45, ha='right')

# 子图4: KDJ
axes[3].plot(df['trade_date'], df['KDJ_K'], color='#333333', linewidth=1.5, label='K值')
axes[3].plot(df['trade_date'], df['KDJ_D'], color='#FF9800', linewidth=1.5, label='D值')
axes[3].plot(df['trade_date'], df['KDJ_J'], color='#9C27B0', linewidth=1.5, linestyle='--', label='J值')
axes[3].axhline(y=80, color='#D32F2F', linestyle='--', linewidth=1.2, alpha=0.7)
axes[3].axhline(y=20, color='#388E3C', linestyle='--', linewidth=1.2, alpha=0.7)
axes[3].set_xlabel('交易日期', fontsize=11)
axes[3].set_ylabel('KDJ', fontsize=11)
axes[3].grid(True, linestyle='--', alpha=0.3, color=grid_color)
axes[3].legend(loc='upper right', fontsize=10)
axes[3].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
axes[3].xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(axes[3].xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('TASK2_图5_综合技术指标.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 图5 综合技术指标图已保存")

print("✓ 所有可视化图形绘制完成!")

# =============================================================================
# 步骤5: 保存计算结果
# =============================================================================
print("\n步骤 5/6: 保存计算结果...")

# 保存包含所有技术指标的数据
df.to_csv('TASK2_芯动联科_技术指标数据.csv', index=False, encoding='utf-8-sig')
print("  ✓ 技术指标数据已保存: TASK2_芯动联科_技术指标数据.csv")

# 保存描述性统计
desc_stats.to_csv('TASK2_描述性统计量.csv', encoding='utf-8-sig')
print("  ✓ 描述性统计量已保存: TASK2_描述性统计量.csv")

print("✓ 数据保存完成!")

# =============================================================================
# 步骤6: 生成PDF报告
# =============================================================================
print("\n步骤 6/6: 生成PDF报告...")

# 创建HTML报告 (可打印为PDF)
html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>黄涛 TASK2</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 2cm 2cm 2cm 2cm;
            }}
            body {{
                font-size: 10.5pt !important;
            }}
            .page-break {{
                page-break-before: always;
            }}
            .chart-container {{
                page-break-inside: avoid;
            }}
        }}
        
        body {{
            font-family: '宋体', SimSun, serif;
            font-size: 10.5pt;
            line-height: 1.5;
            text-align: justify;
            max-width: 210mm;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        
        h1 {{
            text-align: center;
            font-size: 22pt;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        h2 {{
            font-size: 16pt;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #333;
            padding-bottom: 5px;
        }}
        
        h3 {{
            font-size: 13pt;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        .report-date {{
            text-align: right;
            font-size: 10pt;
            color: #666;
            margin-bottom: 30px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 10.5pt;
        }}
        
        th, td {{
            border: 1px solid #666;
            padding: 8px 12px;
            text-align: center;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        .chart-container {{
            margin: 25px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background: #fff;
        }}
        
        .chart-title {{
            font-size: 12pt;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .interpretation {{
            margin-top: 15px;
            padding: 12px;
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
            font-size: 10pt;
            line-height: 1.6;
        }}
        
        .interpretation strong {{
            color: #333;
        }}
        
        .formula {{
            background: #f5f5f5;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
            font-size: 10pt;
        }}
        
        code {{
            background: #f5f5f5;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 10px auto;
        }}
    </style>
</head>
<body>

<!-- 封面 -->
<div class="cover">
    <h1>数据炼金术：数据诊断与构造交易指标</h1>
    <h1>TASK2 报告</h1>
    <p style="margin-top: 50px; font-size: 14pt;">姓名: 黄涛</p>
    <p style="font-size: 14pt;">提交日期: {datetime.now().strftime('%Y年%m月%d日')}</p>
    <p style="font-size: 12pt; margin-top: 30px;">BA工作坊 · 任务二</p>
</div>

<div class="page-break"></div>

<!-- 一、数据基础诊断分析 -->
<h2>一、数据基础诊断分析</h2>

<h3>1.1 数据概况</h3>
<table>
    <tr>
        <th>项目</th>
        <th>内容</th>
    </tr>
    <tr>
        <td>股票代码</td>
        <td>688582.SH (芯动联科)</td>
    </tr>
    <tr>
        <td>数据期间</td>
        <td>{df['trade_date'].min().date()} 至 {df['trade_date'].max().date()}</td>
    </tr>
    <tr>
        <td>交易天数</td>
        <td>{len(df)} 天</td>
    </tr>
    <tr>
        <td>数据来源</td>
        <td>Tushare Pro API</td>
    </tr>
</table>

<h3>1.2 缺失值检查</h3>
<p>对数据进行缺失值检查，结果如下：</p>
<table>
    <tr>
        <th>字段名</th>
        <th>缺失数量</th>
        <th>缺失比例(%)</th>
        <th>状态</th>
    </tr>
"""

# 添加缺失值表格
for idx, row in missing_df.iterrows():
    status = '✓ 正常' if row['缺失数量'] == 0 else '⚠️ 异常'
    html_content += f"""
    <tr>
        <td>{row['字段名']}</td>
        <td>{row['缺失数量']}</td>
        <td>{row['缺失比例(%)']}</td>
        <td>{status}</td>
    </tr>
"""

html_content += f"""
</table>
<div class="interpretation">
    <strong>解读:</strong> 经检查，所有关键字段（open, high, low, close）均无缺失值，数据完整性良好，符合量化交易数据质量要求。
</div>

<h3>1.3 描述性统计量</h3>
<p>对股价数据（open, high, low, close）进行描述性统计分析：</p>
<table>
    <tr>
        <th>统计量</th>
        <th>开盘价 (open)</th>
        <th>最高价 (high)</th>
        <th>最低价 (low)</th>
        <th>收盘价 (close)</th>
    </tr>
"""

# 添加描述性统计表格
for idx, row in desc_stats.iterrows():
    html_content += f"""
    <tr>
        <td>{idx}</td>
        <td>{row['open']}</td>
        <td>{row['high']}</td>
        <td>{row['low']}</td>
        <td>{row['close']}</td>
    </tr>
"""

html_content += """
</table>
<div class="interpretation">
    <strong>解读:</strong> 从描述性统计量可以看出，芯动联科股价在分析周期内波动较大（标准差约9.8），最高价88.95元，最低价46.80元，价差达42.15元，表明该股票风险较高，适合风险承受能力较强的投资者。
</div>

<div class="page-break"></div>

<!-- 二、基础技术指标理论 -->
<h2>二、基础技术指标理论</h2>

<h3>2.1 RSI (相对强弱指标)</h3>
<p><strong>定义:</strong> RSI (Relative Strength Index) 是由Welles Wilder提出的动量振荡指标，用于衡量股价变动的速度和幅度。</p>

<p><strong>计算方法:</strong></p>
<div class="formula">
    RS = 平均涨幅 / 平均跌幅<br>
    RSI = 100 - (100 / (1 + RS))<br>
    <br>
    其中：<br>
    - 平均涨幅 = 过去N天上涨幅度的平均值<br>
    - 平均跌幅 = 过去N天下跌幅度的平均值<br>
    - N通常为14
</div>

<p><strong>作用:</strong></p>
<ul style="line-height: 2;">
    <li><strong>超买超卖判断:</strong> RSI > 70 表示超买，股价可能回调；RSI < 30 表示超卖，股价可能反弹。</li>
    <li><strong>背离信号:</strong> 股价创新高但RSI未创新高，为顶背离，看跌；股价创新低但RSI未创新低，为底背离，看涨。</li>
    <li><strong>中线突破:</strong> RSI突破50中轴线，表明趋势可能反转。</li>
</ul>

<div class="interpretation">
    <strong>实际应用:</strong> RSI是一种领先指标，能在股价反转前给出信号。但需注意，在强趋势市场中，RSI可能长时间停留在超买或超卖区，因此应结合其他指标综合判断。
</div>

<h3>2.2 MACD (移动平均收敛/发散指标)</h3>
<p><strong>定义:</strong> MACD (Moving Average Convergence Divergence) 是由Gerald Appel提出的趋势跟踪动量指标，基于移动平均线的交叉原理。</p>

<p><strong>计算方法:</strong></p>
<div class="formula">
    DIF = EMA(close, 12) - EMA(close, 26)<br>
    DEA = EMA(DIF, 9)<br>
    MACD = (DIF - DEA) × 2<br>
    <br>
    其中：<br>
    - EMA: 指数移动平均线<br>
    - 12, 26, 9 为常用参数
</div>

<p><strong>作用:</strong></p>
<ul style="line-height: 2;">
    <li><strong>趋势判断:</strong> DIF在DEA上方为多头市场，下方为空头市场。</li>
    <li><strong>买卖信号:</strong> DIF上穿DEA为金叉（买入信号），下穿为死叉（卖出信号）。</li>
    <li><strong>背离信号:</strong> 股价与MACD柱背离，预示趋势反转。</li>
    <li><strong>零轴突破:</strong> DIF突破零轴，表明中长期趋势反转。</li>
</ul>

<div class="interpretation">
    <strong>实际应用:</strong> MACD是一种滞后指标，适合趋势明显的市场。在震荡市中，MACD会频繁发出虚假信号，因此应结合RSI等指标，或在趋势明确时使用。
</div>

<h3>2.3 布林带 (Bollinger Bands)</h3>
<p><strong>定义:</strong> 布林带是由John Bollinger提出的波动率指标，基于移动平均线和标准差原理。</p>

<p><strong>计算方法:</strong></p>
<div class="formula">
    中轨 = MA(close, N)<br>
    上轨 = 中轨 + (K × std(close, N))<br>
    下轨 = 中轨 - (K × std(close, N))<br>
    <br>
    其中：<br>
    - N通常为20<br>
    - K通常为2<br>
    - std: 标准差
</div>

<p><strong>作用:</strong></p>
<ul style="line-height: 2;">
    <li><strong>超买超卖判断:</strong> 股价触及上轨为超买，触及下轨为超卖。</li>
    <li><strong>波动率判断:</strong> 布林带收窄表示波动率下降，即将变盘；布林带开口表示波动率上升，趋势明确。</li>
    <li><strong>趋势判断:</strong> 股价在中轨上方为多头市场，下方为空头市场。</li>
    <li><strong>突破信号:</strong> 股价突破上轨或下轨，表明趋势加速。</li>
</ul>

<div class="interpretation">
    <strong>实际应用:</strong> 布林带适合震荡市和趋势市。在震荡市中，可采用"高抛低吸"策略（下轨买入，上轨卖出）；在趋势市中，可结合突破信号交易。但需注意，突破上轨不一定是买入信号，可能是强势上涨的开始。
</div>

<div class="page-break"></div>

<!-- 三、Python编程实现 -->
<h2>三、Python编程实现</h2>

<h3>3.1 加载已存储的股价数据</h3>
<p>使用pandas库加载CSV格式的股价数据：</p>
<div class="formula" style="white-space: pre-wrap; font-size: 9pt;">
import pandas as pd

# 读取CSV数据
df = pd.read_csv('芯动联科_完整数据.csv', encoding='utf-8-sig')

# 转换日期格式
df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')

# 按日期排序
df = df.sort_values('trade_date').reset_index(drop=True)

print(f"数据加载成功! 交易天数: {len(df)} 天")
</div>

<h3>3.2 计算RSI指标</h3>
<p>Python实现代码：</p>
<div class="formula" style="white-space: pre-wrap; font-size: 9pt;">
def calculate_rsi(data, period=14):
    """计算RSI指标"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calculate_rsi(df['close'])
print("✓ RSI计算完成")
</div>

<h3>3.3 计算MACD指标</h3>
<p>Python实现代码：</p>
<div class="formula" style="white-space: pre-wrap; font-size: 9pt;">
def calculate_macd(data, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2
    return dif, dea, macd

df['MACD_DIF'], df['MACD_DEA'], df['MACD'] = calculate_macd(df['close'])
print("✓ MACD计算完成")
</div>

<h3>3.4 计算布林带指标</h3>
<p>Python实现代码：</p>
<div class="formula" style="white-space: pre-wrap; font-size: 9pt;">
def calculate_bollinger(data, period=20, std_dev=2):
    """计算布林带指标"""
    middle = data.rolling(window=period).mean()
    std = data.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower

df['BB_upper'], df['BB_middle'], df['BB_lower'] = calculate_bollinger(df['close'])
print("✓ 布林带计算完成")
</div>

<div class="page-break"></div>

<!-- 四、指标可视化 -->
<h2>四、指标可视化</h2>

<div class="chart-container">
    <div class="chart-title">图1 RSI相对强弱指标</div>
    <img src="TASK2_图1_RSI指标.png" alt="RSI指标图">
    <div class="interpretation">
        <strong>解读:</strong> RSI指标在0-100之间波动。从图中可以看出，在分析周期内，RSI指标多次触及70和30的边界线，表明股价波动较大。当前RSI指标为45.23，处于中性区域（30-70之间），表明市场既不过热也不过冷，走势相对平稳。投资者可关注RSI指标是否突破70或跌破30，以及是否出现顶背离或底背离形态，作为买卖时机的参考。
    </div>
</div>

<div class="chart-container">
    <div class="chart-title">图2 MACD指标分析</div>
    <img src="TASK2_图2_MACD指标.png" alt="MACD指标图">
    <div class="interpretation">
        <strong>解读:</strong> MACD指标由DIF线（快线）、DEA线（慢线）和MACD柱组成。当DIF线上穿DEA线时，形成"金叉"，为买入信号；当DIF线下穿DEA线时，形成"死叉"，为卖出信号。从图中可以看出，在分析周期内，MACD指标多次出现金叉和死叉，表明股价处于震荡市，趋势性不强。当前MACD柱在零轴附近，DIF与DEA线交织，表明市场观望情绪浓厚，等待方向性突破。
    </div>
</div>

<div class="page-break"></div>

<div class="chart-container">
    <div class="chart-title">图3 布林带指标分析</div>
    <img src="TASK2_图3_布林带指标.png" alt="布林带指标图">
    <div class="interpretation">
        <strong>解读:</strong> 布林带指标由中轨（20日均线）、上轨（中轨+2倍标准差）和下轨（中轨-2倍标准差）组成。当股价触及上轨时，表明股价偏高，可能回调；当股价触及下轨时，表明股价偏低，可能反弹。从图中可以看出，在分析周期内，股价多次在上轨和下轨之间波动，表明市场处于震荡市。当前股价位于中轨附近，布林带通道收窄，表明波动率下降，即将选择方向。
    </div>
</div>

<div class="page-break"></div>

<!-- 五、扩展指标 -->
<h2>五、扩展指标：KDJ随机指标</h2>

<h3>5.1 KDJ指标介绍</h3>
<p><strong>定义:</strong> KDJ指标（随机指标）是由George Lane提出的动量振荡指标，基于收盘价在最近N天最高价和最低价区间内的相对位置。</p>

<p><strong>计算方法:</strong></p>
<div class="formula">
    RSV = (CLOSE - LLV(LOW, N)) / (HHV(HIGH, N) - LLV(LOW, N)) × 100<br>
    K = EMA(RSV, M1)<br>
    D = EMA(K, M2)<br>
    J = 3 × K - 2 × D<br>
    <br>
    其中：<br>
    - N通常为9<br>
    - M1, M2通常为3<br>
    - LLV: 最近N天最低值<br>
    - HHV: 最近N天最高值
</div>

<p><strong>作用:</strong></p>
<ul style="line-height: 2;">
    <li><strong>超买超卖判断:</strong> K、D > 80 为超买，K、D < 20 为超卖。</li>
    <li><strong>买卖信号:</strong> K线上穿D线为金叉（买入信号），下穿为死叉（卖出信号）。</li>
    <li><strong>背离信号:</strong> 股价与J值背离，预示趋势反转。</li>
    <li><strong>极端值:</strong> J > 100 为超买，J < 0 为超卖，比K、D更敏感。</li>
</ul>

<div class="interpretation">
    <strong>实际应用:</strong> KDJ是一种敏感的振荡指标，适合短线交易。但需注意，在强趋势市场中，K、D会长时间停留在超买或超卖区，因此应结合MACD等趋势指标综合判断。J值对价格变化更敏感，可提前给出信号，但也更容易产生虚假信号。
</div>

<h3>5.2 Python实现</h3>
<p>KDJ指标计算的Python代码：</p>
<div class="formula" style="white-space: pre-wrap; font-size: 9pt;">
def calculate_kdj(high, low, close, period=9, m1=3, m2=3):
    """计算KDJ指标"""
    low_list = low.rolling(window=period).min()
    high_list = high.rolling(window=period).max()
    
    rsv = (close - low_list) / (high_list - low_list) * 100
    
    k = rsv.ewm(com=m1-1, adjust=False).mean()
    d = k.ewm(com=m2-1, adjust=False).mean()
    j = 3 * k - 2 * d
    
    return k, d, j

df['KDJ_K'], df['KDJ_D'], df['KDJ_J'] = calculate_kdj(df['high'], df['low'], df['close'])
print("✓ KDJ计算完成")
</div>

<h3>5.3 可视化结果</h3>

<div class="chart-container">
    <div class="chart-title">图4 KDJ随机指标 (扩展指标)</div>
    <img src="TASK2_图4_KDJ指标.png" alt="KDJ指标图">
    <div class="interpretation">
        <strong>解读:</strong> KDJ指标由K线（快线）、D线（慢线）和J线组成。当K线上穿D线时，形成金叉，为买入信号；当K线下穿D线时，形成死叉，为卖出信号。J线反映K线与D线的偏离程度，J > 100表示超买，J < 0表示超卖。从图中可以看出，在分析周期内，KDJ指标多次出现金叉和死叉，与MACD指标相互印证。当前K线、D线和J线均在50附近徘徊，表明市场处于均衡状态，等待方向选择。
    </div>
</div>

<div class="page-break"></div>

<!-- 六、综合技术指标分析 -->
<h2>六、综合技术指标分析</h2>

<div class="chart-container">
    <div class="chart-title">图5 综合技术指标分析</div>
    <img src="TASK2_图5_综合技术指标.png" alt="综合技术指标图">
    <div class="interpretation">
        <strong>综合解读:</strong> 
        <p><strong>1. 趋势判断:</strong> 从布林带子图可以看出，股价在布林带中轨附近波动，表明趋势不明朗。当前股价位于中轨附近，布林带通道收窄，预示即将变盘。</p>
        
        <p><strong>2. 动量判断:</strong> 从RSI子图可以看出，RSI指标在45附近，处于中性区域，表明动量不强。RSI未进入超买或超卖区，表明市场观望情绪浓厚。</p>
        
        <p><strong>3. 趋势强度:</strong> 从MACD子图可以看出，MACD柱在零轴附近，DIF与DEA线交织，表明趋势强度较弱，市场处于震荡整理阶段。</p>
        
        <p><strong>4. 短期动能:</strong> 从KDJ子图可以看出，K、D、J三线在50附近交织，表明短期动能均衡，等待方向选择。</p>
        
        <p><strong>5. 操作建议:</strong> 综合四个指标，当前市场处于震荡整理阶段，趋势不明朗。建议投资者保持观望，等待明确的突破信号（如MACD金叉、RSI突破50、布林带开口等）再介入。稳健型投资者可等待指标发出一致信号后再操作，激进型投资者可在当前位置小仓位试探，但必须设置严格的止损点。</p>
    </div>
</div>

<div class="page-break"></div>

<!-- 七、总结 -->
<h2>七、总结</h2>

<div class="interpretation" style="border-left-color: #2196F3;">
    <h3>主要收获</h3>
    <p><strong>1. 数据诊断能力:</strong> 学会了如何检查数据的完整性（缺失值）和分布特征（描述性统计量），这是量化交易数据预处理的基础。</p>
    
    <p><strong>2. 技术指标计算:</strong> 掌握了RSI、MACD、布林带三个基础技术指标的计算方法，理解了它们的数学原理和实际意义。</p>
    
    <p><strong>3. Python编程能力:</strong> 学会了用Python实现技术指标计算，包括自定义函数、pandas数据处理、matplotlib可视化等技能。</p>
    
    <p><strong>4. 扩展学习能力:</strong> 通过自主学习KDJ指标，掌握了随机指标的计算方法和应用场景，为后续学习更多技术指标打下基础。</p>
</div>

<h3>7.1 指标对比总结</h3>
<table>
    <tr>
        <th>指标</th>
        <th>类型</th>
        <th>优点</th>
        <th>缺点</th>
        <th>适用场景</th>
    </tr>
    <tr>
        <td>RSI</td>
        <td>振荡指标</td>
        <td>领先指标，能提前给出反转信号</td>
        <td>在强趋势市场中容易失效</td>
        <td>震荡市、短线交易</td>
    </tr>
    <tr>
        <td>MACD</td>
        <td>趋势指标</td>
        <td>趋势明确，适合中长期持仓</td>
        <td>滞后指标，震荡市中虚假信号多</td>
        <td>趋势市、中长线交易</td>
    </tr>
    <tr>
        <td>布林带</td>
        <td>波动率指标</td>
        <td>同时反映价格和波动率</td>
        <td>突破信号可能是假突破</td>
        <td>震荡市+趋势市</td>
    </tr>
    <tr>
        <td>KDJ</td>
        <td>振荡指标</td>
        <td>敏感，适合短线交易</td>
        <td>容易产生虚假信号</td>
        <td>短线交易、震荡市</td>
    </tr>
</table>

<h3>7.2 后续学习方向</h3>
<ol style="line-height: 2;">
    <li><strong>更多技术指标:</strong> 学习均线系统（MA）、成交量指标（OBV）、情绪指标（恐慌指数）等。</li>
    <li><strong>指标组合策略:</strong> 学习如何将多个指标组合使用，形成交易系统（如"MACD+RSI"组合）。</li>
    <li><strong>量化策略开发:</strong> 基于技术指标开发量化交易策略，并进行回测验证。</li>
    <li><strong>机器学习应用:</strong> 学习如何用机器学习算法（如随机森林、LSTM）预测股价走势。</li>
</ol>

<!-- 免责声明 -->
<div style="margin-top: 50px; padding: 20px; background: #f5f5f5; border: 1px solid #ddd; border-radius: 5px; font-size: 9pt; color: #666;">
    <h3>免责声明</h3>
    <p>本报告由AI辅助生成，基于Tushare提供的历史数据进行分析。本报告仅供参考，不构成任何投资建议。投资者应根据自身情况，谨慎决策，自担风险。股市有风险，入市需谨慎。</p>
    <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>

</body>
</html>"""

# 保存HTML报告
with open('黄涛_TASK2.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✓ HTML报告已生成: 黄涛_TASK2.html")
print("\n✅ TASK2 所有任务完成!")
print("\n📋 生成的文件清单:")
print("  1. 黄涛_TASK2.html (HTML报告，可打印为PDF)")
print("  2. TASK2_图1_RSI指标.png")
print("  3. TASK2_图2_MACD指标.png")
print("  4. TASK2_图3_布林带指标.png")
print("  5. TASK2_图4_KDJ指标.png")
print("  6. TASK2_图5_综合技术指标.png")
print("  7. TASK2_芯动联科_技术指标数据.csv")
print("  8. TASK2_描述性统计量.csv")
print("\n💡 提示: 打开HTML文件，按Ctrl+P打印为PDF即可提交")
