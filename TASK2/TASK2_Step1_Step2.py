#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TASK2: Data Alchemy - Data Diagnosis and Trading Indicator Construction
Author: devops-huang (Huang Tao)
Date: 2026-07-01
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

# Set Chinese font
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 80)
print("TASK2: Data Alchemy - Data Diagnosis and Trading Indicators")
print("=" * 80)

# =============================================================================
# Step 1: Load stored stock price data
# =============================================================================
print("\nStep 1/6: Loading stored stock price data...")

# Read CSV data
df = pd.read_csv('芯动联科_完整数据.csv', encoding='utf-8-sig')

# Convert date format
df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')

# Sort by date
df = df.sort_values('trade_date').reset_index(drop=True)

print(f"Data loaded successfully!")
print(f"  Period: {df['trade_date'].min().date()} to {df['trade_date'].max().date()}")
print(f"  Trading days: {len(df)}")
print(f"  Columns: {', '.join(df.columns.tolist())}")

# =============================================================================
# Step 2: Basic data diagnosis
# =============================================================================
print("\nStep 2/6: Basic data diagnosis...")

# 2.1 Check missing values
print("\n[2.1 Missing Value Check]")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    'Column': missing.index,
    'Missing_Count': missing.values,
    'Missing_Pct': missing_pct.values
})
print(missing_df.to_string(index=False))

# 2.2 Calculate descriptive statistics
print("\n[2.2 Descriptive Statistics]")
desc_stats = df[['open', 'high', 'low', 'close']].describe().round(2)
print(desc_stats)

print("Data diagnosis completed!")
