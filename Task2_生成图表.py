import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

print('=' * 60)
print('Task2: 生成技术指标图表')
print('=' * 60)

# 读取数据
with open('stock_data.json', 'r', encoding='utf-8') as f:
    stock_data = json.load(f)

with open('daily_basic_data.json', 'r', encoding='utf-8') as f:
    basic_data = json.load(f)

# 转换为DataFrame
df_stock = pd.DataFrame(stock_data)
df_basic = pd.DataFrame(basic_data)

# 日期格式转换
df_stock['trade_date'] = pd.to_datetime(df_stock['trade_date'], format='%Y%m%d')
df_basic['trade_date'] = pd.to_datetime(df_basic['trade_date'], format='%Y%m%d')

# 按日期排序
df_stock = df_stock.sort_values('trade_date').reset_index(drop=True)
df_basic = df_basic.sort_values('trade_date').reset_index(drop=True)

print(f'✓ 数据加载完成')
print(f'  日交易数据: {len(df_stock)} 条记录')
print(f'  每日指标数据: {len(df_basic)} 条记录')

# 计算RSI
def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(com=period-1, adjust=False).mean()
    avg_loss = loss.ewm(com=period-1, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = rsi
    return df

df_stock = calculate_rsi(df_stock, period=14)
print(f'✓ RSI计算完成')

# 计算MACD
def calculate_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    df['MACD_DIF'] = ema_fast - ema_slow
    df['MACD_DEA'] = df['MACD_DIF'].ewm(span=signal, adjust=False).mean()
    df['MACD'] = (df['MACD_DIF'] - df['MACD_DEA']) * 2
    return df

df_stock = calculate_macd(df_stock, fast=12, slow=26, signal=9)
print(f'✓ MACD计算完成')

# 计算布林带
def calculate_bollinger_bands(df, period=20, std_dev=2):
    df['BB_middle'] = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    df['BB_upper'] = df['BB_middle'] + (std * std_dev)
    df['BB_lower'] = df['BB_middle'] - (std * std_dev)
    return df

df_stock = calculate_bollinger_bands(df_stock, period=20, std_dev=2)
print(f'✓ 布林带计算完成')

# 计算KDJ
def calculate_kdj(df, period=9):
    low_list = df['low'].rolling(window=period).min()
    high_list = df['high'].rolling(window=period).max()
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100
    df['KDJ_K'] = rsv.ewm(com=2, adjust=False).mean()
    df['KDJ_D'] = df['KDJ_K'].ewm(com=2, adjust=False).mean()
    df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
    return df

df_stock = calculate_kdj(df_stock, period=9)
print(f'✓ KDJ计算完成')

# 生成图1: RSI指标
print('\n生成图1: RSI指标...')
fig, ax = plt.subplots(figsize=(16, 9))
ax.plot(df_stock['trade_date'], df_stock['RSI'], color='#9C27B0', linewidth=2.5, label='RSI(14)')
ax.axhline(y=70, color='#E53935', linestyle='--', linewidth=1.5, alpha=0.7, label='超买线 (70)')
ax.axhline(y=30, color='#43A047', linestyle='--', linewidth=1.5, alpha=0.7, label='超卖线 (30)')
ax.axhline(y=50, color='gray', linestyle='-', linewidth=1.0, alpha=0.5, label='多空分界线 (50)')
ax.fill_between(df_stock['trade_date'], 70, 100, alpha=0.1, color='#FFCDD2')
ax.fill_between(df_stock['trade_date'], 0, 30, alpha=0.1, color='#C8E6C9')
ax.set_title('图1: RSI相对强弱指标 (RSI(14))', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('交易日期', fontsize=12)
ax.set_ylabel('RSI值', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.3)
ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('图1_RSI指标.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 图1已保存: 图1_RSI指标.png')

# 生成图2: MACD指标
print('\n生成图2: MACD指标...')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), gridspec_kw={'height_ratios': [2, 1]})
ax1.plot(df_stock['trade_date'], df_stock['close'], color='#333333', linewidth=2.0, label='收盘价')
ax1.plot(df_stock['trade_date'], df_stock['close'].rolling(window=5).mean(), color='orange', linewidth=1.5, alpha=0.8, label='MA5')
ax1.plot(df_stock['trade_date'], df_stock['close'].rolling(window=10).mean(), color='blue', linewidth=1.5, alpha=0.8, label='MA10')
ax1.plot(df_stock['trade_date'], df_stock['close'].rolling(window=20).mean(), color='purple', linewidth=1.5, alpha=0.8, label='MA20')
ax1.set_title('图2: MACD指标分析', fontsize=16, fontweight='bold', pad=15)
ax1.set_ylabel('收盘价 (元)', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.3)
ax1.legend(loc='upper right', fontsize=11)
colors = ['#E53935' if x >= 0 else '#43A047' for x in df_stock['MACD']]
ax2.plot(df_stock['trade_date'], df_stock['MACD_DIF'], color='#333333', linewidth=1.5, label='DIF (快线)')
ax2.plot(df_stock['trade_date'], df_stock['MACD_DEA'], color='orange', linewidth=1.5, label='DEA (慢线)')
ax2.bar(df_stock['trade_date'], df_stock['MACD'], color=colors, alpha=0.6, label='MACD柱')
ax2.axhline(y=0, color='gray', linestyle='-', linewidth=1.0, alpha=0.5)
ax2.set_xlabel('交易日期', fontsize=12)
ax2.set_ylabel('MACD值', fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.3)
ax2.legend(loc='upper right', fontsize=11)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('图2_MACD指标.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 图2已保存: 图2_MACD指标.png')

# 生成图3: 布林带指标
print('\n生成图3: 布林带指标...')
fig, ax = plt.subplots(figsize=(16, 9))
ax.plot(df_stock['trade_date'], df_stock['close'], color='#333333', linewidth=2.0, label='收盘价', zorder=3)
ax.plot(df_stock['trade_date'], df_stock['BB_upper'], color='#E53935', linewidth=1.5, linestyle='--', label='上轨 (UB)', alpha=0.8)
ax.plot(df_stock['trade_date'], df_stock['BB_middle'], color='#333333', linewidth=1.5, linestyle='-', label='中轨 (MB, MA20)', alpha=0.8)
ax.plot(df_stock['trade_date'], df_stock['BB_lower'], color='#43A047', linewidth=1.5, linestyle='--', label='下轨 (LB)', alpha=0.8)
ax.fill_between(df_stock['trade_date'], df_stock['BB_upper'], df_stock['BB_lower'], alpha=0.1, color='gray', label='布林带区域')
ax.set_title('图3: 布林带指标 (Bollinger Bands)', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('交易日期', fontsize=12)
ax.set_ylabel('价格 (元)', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.3)
ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('图3_布林带指标.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 图3已保存: 图3_布林带指标.png')

# 生成图4: KDJ指标
print('\n生成图4: KDJ指标...')
fig, ax = plt.subplots(figsize=(16, 9))
ax.plot(df_stock['trade_date'], df_stock['KDJ_K'], color='#333333', linewidth=1.5, label='K值')
ax.plot(df_stock['trade_date'], df_stock['KDJ_D'], color='orange', linewidth=1.5, label='D值')
ax.plot(df_stock['trade_date'], df_stock['KDJ_J'], color='purple', linewidth=1.5, linestyle='--', label='J值')
ax.axhline(y=80, color='#E53935', linestyle='--', linewidth=1.5, alpha=0.7, label='超买线 (80)')
ax.axhline(y=20, color='#43A047', linestyle='--', linewidth=1.5, alpha=0.7, label='超卖线 (20)')
ax.fill_between(df_stock['trade_date'], 80, 100, alpha=0.1, color='#FFCDD2')
ax.fill_between(df_stock['trade_date'], 0, 20, alpha=0.1, color='#C8E6C9')
ax.set_title('图4: KDJ随机指标 (KDJ(9))', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('交易日期', fontsize=12)
ax.set_ylabel('KDJ值', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.3)
ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('图4_KDJ指标.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 图4已保存: 图4_KDJ指标.png')

# 保存完整数据（含所有技术指标）
print('\n保存完整数据...')
df_final = pd.DataFrame()
df_final['trade_date'] = df_stock['trade_date'].dt.strftime('%Y%m%d')
df_final['open'] = df_stock['open']
df_final['high'] = df_stock['high']
df_final['low'] = df_stock['low']
df_final['close'] = df_stock['close']
df_final['vol'] = df_stock['vol']
df_final['amount'] = df_stock['amount']
df_final['RSI'] = df_stock['RSI']
df_final['MACD_DIF'] = df_stock['MACD_DIF']
df_final['MACD_DEA'] = df_stock['MACD_DEA']
df_final['MACD'] = df_stock['MACD']
df_final['BB_upper'] = df_stock['BB_upper']
df_final['BB_middle'] = df_stock['BB_middle']
df_final['BB_lower'] = df_stock['BB_lower']
df_final['KDJ_K'] = df_stock['KDJ_K']
df_final['KDJ_D'] = df_stock['KDJ_D']
df_final['KDJ_J'] = df_stock['KDJ_J']
df_final['PE'] = df_basic['pe'].values
df_final['PB'] = df_basic['pb'].values
df_final['PS'] = df_basic['ps'].values
df_final['总市值'] = df_basic['total_mv'].values
df_final['换手率'] = df_basic['turnover_rate'].values
output_file = '芯动联科_完整技术指标数据_Task2.csv'
df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f'✓ 数据已保存: {output_file}')
print(f'  总行数: {len(df_final)} 条')
print(f'  总列数: {len(df_final.columns)} 列')

print('\n' + '=' * 60)
print('✓ 所有Task2图表和数据已生成完成！')
print('=' * 60)
print('\n生成的文件:')
print('  1. 图1_RSI指标.png')
print('  2. 图2_MACD指标.png')
print('  3. 图3_布林带指标.png')
print('  4. 图4_KDJ指标.png')
print('  5. 芯动联科_完整技术指标数据_Task2.csv')
