# -*- coding: utf-8 -*-
"""
TASK2 完整分析脚本
芯动联科 (688582.SH) 技术指标计算与可视化分析
包含：数据诊断、RSI、MACD、布林带、KDJ、ATR、OBV等指标
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.gridspec as gridspec
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 中文字体配置
# ============================================================
def get_cn_font():
    font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for fp in font_paths:
        fp_lower = fp.lower()
        if any(k in fp_lower for k in ['msyh', 'simhei', 'simsun', 'microsoftyahei', 'simfang', 'kaiti']):
            return fp
    return None

cn_font_path = get_cn_font()
if cn_font_path:
    prop = fm.FontProperties(fname=cn_font_path)
    plt.rcParams['font.family'] = prop.get_name()
else:
    prop = fm.FontProperties()
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 1. 加载数据 & 基础诊断分析
# ============================================================
print("=" * 60)
print("Step 1: 加载数据 & 基础诊断分析")
print("=" * 60)

csv_path = r"C:\Users\TaoZi\Desktop\ED\BA工作坊\芯动联科_688582_年度日交易数据.csv"
df = pd.read_csv(csv_path, encoding='utf-8-sig')
df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
df = df.sort_values('trade_date').reset_index(drop=True)

print(f"\n数据基本信息：")
print(f"  数据条数: {len(df)}")
print(f"  日期范围: {df['trade_date'].min().date()} ~ {df['trade_date'].max().date()}")
print(f"  字段列表: {list(df.columns.tolist())}")

# 缺失值检查
print(f"\n缺失值检查：")
missing = df.isnull().sum()
if missing.sum() == 0:
    print("  ✅ 无缺失值")
else:
    for col, val in missing[missing > 0].items():
        print(f"  ⚠️ {col}: {val} 个缺失值")

# 描述性统计量
print(f"\n描述性统计量（收盘价）：")
close_desc = df['close'].describe()
for k, v in close_desc.items():
    print(f"  {k}: {v:.4f}")

print(f"\n描述性统计量（成交量）：")
vol_desc = df['vol'].describe()
for k, v in vol_desc.items():
    print(f"  {k}: {v:.2f}")

# 保存诊断结果文本
diag_text = f"""
数据诊断分析报告
====================================
股票代码: 688582.SH (芯动联科)
数据区间: {df['trade_date'].min().date()} ~ {df['trade_date'].max().date()}
交易日数: {len(df)}

【缺失值检查】
{df.isnull().sum().to_string()}

【收盘价描述性统计】
{close_desc.to_string()}

【成交量描述性统计】
{vol_desc.to_string()}
"""

# ============================================================
# 2. 技术指标计算
# ============================================================
print("\n" + "=" * 60)
print("Step 2: 技术指标计算")
print("=" * 60)

# --- 2.1 移动平均线 MA ---
def calc_ma(close, windows=[5, 10, 20, 60]):
    for w in windows:
        df[f'MA{w}'] = close.rolling(window=w).mean()
    return df

# --- 2.2 RSI（相对强弱指标）---
def calc_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# --- 2.3 MACD ---
def calc_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

# --- 2.4 布林带（Bollinger Bands）---
def calc_bollinger(close, period=20, std_dev=2):
    mid = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = mid + std_dev * std
    lower = mid - std_dev * std
    return upper, mid, lower

# --- 2.5 KDJ ---
def calc_kdj(high, low, close, period=9):
    low_n = low.rolling(window=period).min()
    high_n = high.rolling(window=period).max()
    rsv = (close - low_n) / (high_n - low_n) * 100
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    j = 3 * k - 2 * d
    return k, d, j

# --- 2.6 ATR（平均真实波幅）---
def calc_atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

# --- 2.7 OBV（能量潮）---
def calc_obv(close, vol):
    obv = [0]
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.append(obv[-1] + vol.iloc[i])
        elif close.iloc[i] < close.iloc[i-1]:
            obv.append(obv[-1] - vol.iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=close.index)

# --- 2.8 成交量均线 ---
def calc_vol_ma(vol, windows=[5, 10, 20]):
    for w in windows:
        df[f'VOL_MA{w}'] = vol.rolling(window=w).mean()
    return df

# 执行计算
df = calc_ma(df['close'])
df['RSI_14'] = calc_rsi(df['close'])
macd_line, signal_line, histogram = calc_macd(df['close'])
df['MACD'] = macd_line
df['MACD_signal'] = signal_line
df['MACD_hist'] = histogram
bb_upper, bb_mid, bb_lower = calc_bollinger(df['close'])
df['BB_upper'] = bb_upper
df['BB_mid'] = bb_mid
df['BB_lower'] = bb_lower
k, d, j = calc_kdj(df['high'], df['low'], df['close'])
df['KDJ_K'] = k
df['KDJ_D'] = d
df['KDJ_J'] = j
df['ATR_14'] = calc_atr(df['high'], df['low'], df['close'])
df['OBV'] = calc_obv(df['close'], df['vol'])
df = calc_vol_ma(df['vol'])

# 保存完整指标数据
output_csv = r"C:\Users\TaoZi\Desktop\ED\BA工作坊\TASK2\TASK2_完整技术指标数据.csv"
df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"✅ 指标计算完成，数据已保存: {output_csv}")

# ============================================================
# 3. 绘制可视化图形
# ============================================================
print("\n" + "=" * 60)
print("Step 3: 绘制可视化图形")
print("=" * 60)

plot_dir = r"C:\Users\TaoZi\Desktop\ED\BA工作坊\TASK2"
dates = df['trade_date']

# --- 图1: 收盘价 + 布林带 ---
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(dates, df['close'], label='收盘价', color='#1f77b4', linewidth=1.5)
ax.plot(dates, df['BB_upper'], label='布林上轨', color='#ff7f0e', linestyle='--', linewidth=1)
ax.plot(dates, df['BB_mid'], label='布林中轨', color='#2ca02c', linestyle='--', linewidth=1)
ax.plot(dates, df['BB_lower'], label='布林下轨', color='#ff7f0e', linestyle='--', linewidth=1)
ax.fill_between(dates, df['BB_upper'], df['BB_lower'], alpha=0.1, color='orange')
ax.set_title('图1  芯动联科 K线收盘价与布林带指标', fontsize=13, fontproperties=prop)
ax.set_xlabel('交易日期', fontproperties=prop)
ax.set_ylabel('价格 (元)', fontproperties=prop)
ax.legend(prop=prop)
ax.grid(True, linestyle=':', alpha=0.5)
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig(f'{plot_dir}/TASK2_图1_布林带.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图1 布林带 已保存")

# --- 图2: MACD ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True,
                               gridspec_kw={'height_ratios': [2, 1]})
ax1.plot(dates, df['close'], color='#1f77b4', linewidth=1.2)
ax1.plot(dates, df['MA5'], label='MA5', color='#ff7f0e', linewidth=1)
ax1.plot(dates, df['MA10'], label='MA10', color='#2ca02c', linewidth=1)
ax1.plot(dates, df['MA20'], label='MA20', color='#d62728', linewidth=1)
ax1.set_title('图2  MACD指标分析', fontsize=13, fontproperties=prop)
ax1.set_ylabel('价格 (元)', fontproperties=prop)
ax1.legend(prop=prop)
ax1.grid(True, linestyle=':', alpha=0.5)

colors = ['#d62728' if v >= 0 else '#2ca02c' for v in df['MACD_hist']]
ax2.plot(dates, df['MACD'], label='MACD线', color='#1f77b4', linewidth=1.2)
ax2.plot(dates, df['MACD_signal'], label='信号线', color='#ff7f0e', linewidth=1.2)
ax2.bar(dates, df['MACD_hist'], color=colors, alpha=0.7, width=0.8)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax2.set_ylabel('MACD', fontproperties=prop)
ax2.set_xlabel('交易日期', fontproperties=prop)
ax2.legend(prop=prop)
ax2.grid(True, linestyle=':', alpha=0.5)
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig(f'{plot_dir}/TASK2_图2_MACD.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图2 MACD 已保存")

# --- 图3: RSI + KDJ ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
ax1.plot(dates, df['RSI_14'], label='RSI(14)', color='#1f77b4', linewidth=1.5)
ax1.axhline(y=80, color='red', linestyle='--', linewidth=1, alpha=0.7)
ax1.axhline(y=20, color='green', linestyle='--', linewidth=1, alpha=0.7)
ax1.axhline(y=50, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
ax1.fill_between(dates, 80, 100, alpha=0.1, color='red')
ax1.fill_between(dates, 0, 20, alpha=0.1, color='green')
ax1.set_title('图3  RSI与KDJ指标分析', fontsize=13, fontproperties=prop)
ax1.set_ylabel('RSI', fontproperties=prop)
ax1.set_ylim(0, 100)
ax1.legend(prop=prop)
ax1.grid(True, linestyle=':', alpha=0.5)

ax2.plot(dates, df['KDJ_K'], label='K值', color='#1f77b4', linewidth=1.2)
ax2.plot(dates, df['KDJ_D'], label='D值', color='#ff7f0e', linewidth=1.2)
ax2.plot(dates, df['KDJ_J'], label='J值', color='#2ca02c', linewidth=1.2)
ax2.axhline(y=80, color='red', linestyle='--', linewidth=0.8, alpha=0.6)
ax2.axhline(y=20, color='green', linestyle='--', linewidth=0.8, alpha=0.6)
ax2.set_ylabel('KDJ', fontproperties=prop)
ax2.set_xlabel('交易日期', fontproperties=prop)
ax2.set_ylim(0, 100)
ax2.legend(prop=prop)
ax2.grid(True, linestyle=':', alpha=0.5)
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig(f'{plot_dir}/TASK2_图3_RSI_KDJ.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图3 RSI+KDJ 已保存")

# --- 图4: ATR + OBV ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
ax1.plot(dates, df['ATR_14'], label='ATR(14)', color='#d62728', linewidth=1.5)
ax1.set_title('图4  ATR与OBV指标分析', fontsize=13, fontproperties=prop)
ax1.set_ylabel('ATR (元)', fontproperties=prop)
ax1.legend(prop=prop)
ax1.grid(True, linestyle=':', alpha=0.5)

obv_ma = df['OBV'].rolling(window=20).mean()
ax2.plot(dates, df['OBV'], label='OBV', color='#1f77b4', linewidth=1.2)
ax2.plot(dates, obv_ma, label='OBV_MA20', color='#ff7f0e', linewidth=1)
ax2.set_ylabel('OBV', fontproperties=prop)
ax2.set_xlabel('交易日期', fontproperties=prop)
ax2.legend(prop=prop)
ax2.grid(True, linestyle=':', alpha=0.5)
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig(f'{plot_dir}/TASK2_图4_ATR_OBV.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图4 ATR+OBV 已保存")

# --- 图5: 成交量 ---
fig, ax = plt.subplots(figsize=(14, 5))
colors_vol = ['#d62728' if c >= p else '#2ca02c' for c, p in zip(df['close'], df['pre_close'])]
ax.bar(dates, df['vol'], color=colors_vol, alpha=0.7, width=0.8)
ax.plot(dates, df['VOL_MA5'], label='成交量MA5', color='#ff7f0e', linewidth=1.2)
ax.plot(dates, df['VOL_MA10'], label='成交量MA10', color='#2ca02c', linewidth=1.2)
ax.plot(dates, df['VOL_MA20'], label='成交量MA20', color='#1f77b4', linewidth=1.2)
ax.set_title('图5  成交量分析', fontsize=13, fontproperties=prop)
ax.set_xlabel('交易日期', fontproperties=prop)
ax.set_ylabel('成交量 (手)', fontproperties=prop)
ax.legend(prop=prop)
ax.grid(True, linestyle=':', alpha=0.5)
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig(f'{plot_dir}/TASK2_图5_成交量.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图5 成交量 已保存")

# --- 图6: 综合面板（收盘价+MA+成交量） ---
fig = plt.figure(figsize=(14, 10))
gs = gridspec.GridSpec(3, 1, height_ratios=[2, 1, 1], hspace=0.08)

ax1 = fig.add_subplot(gs[0])
ax1.plot(dates, df['close'], color='black', linewidth=1.5, label='收盘价')
ax1.plot(dates, df['MA5'], label='MA5', color='#ff7f0e', linewidth=1)
ax1.plot(dates, df['MA10'], label='MA10', color='#2ca02c', linewidth=1)
ax1.plot(dates, df['MA20'], label='MA20', color='#d62728', linewidth=1)
ax1.plot(dates, df['MA60'], label='MA60', color='#9467bd', linewidth=1)
ax1.fill_between(dates, df['BB_upper'], df['BB_lower'], alpha=0.05, color='orange')
ax1.set_ylabel('价格 (元)', fontproperties=prop)
ax1.legend(prop=prop, loc='upper left')
ax1.grid(True, linestyle=':', alpha=0.4)
ax1.set_title('图6  芯动联科技术指标综合面板', fontproperties=prop, fontsize=13)

ax2 = fig.add_subplot(gs[1], sharex=ax1)
ax2.plot(dates, df['MACD'], label='MACD', color='#1f77b4', linewidth=1)
ax2.plot(dates, df['MACD_signal'], label='Signal', color='#ff7f0e', linewidth=1)
macd_colors = ['#d62728' if v >= 0 else '#2ca02c' for v in df['MACD_hist']]
ax2.bar(dates, df['MACD_hist'], color=macd_colors, alpha=0.6, width=0.8)
ax2.axhline(y=0, color='black', linewidth=0.8)
ax2.set_ylabel('MACD', fontproperties=prop)
ax2.legend(prop=prop, loc='upper left')
ax2.grid(True, linestyle=':', alpha=0.4)

ax3 = fig.add_subplot(gs[2], sharex=ax1)
ax3.plot(dates, df['RSI_14'], label='RSI(14)', color='purple', linewidth=1.2)
ax3.axhline(y=80, color='red', linestyle='--', alpha=0.5)
ax3.axhline(y=20, color='green', linestyle='--', alpha=0.5)
ax3.set_ylabel('RSI', fontproperties=prop)
ax3.set_xlabel('交易日期', fontproperties=prop)
ax3.legend(prop=prop, loc='upper left')
ax3.grid(True, linestyle=':', alpha=0.4)
ax3.set_ylim(0, 100)

fig.autofmt_xdate()
plt.tight_layout()
plt.savefig(f'{plot_dir}/TASK2_图6_综合面板.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图6 综合面板 已保存")

print("\n所有图形绘制完成！")
print("=" * 60)
