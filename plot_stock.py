import json, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

with open(r'C:\Users\TaoZi\Desktop\ED\BA工作坊\stock_data.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
df = df.sort_values('trade_date').reset_index(drop=True)

# 1. 保存CSV
csv_path = r'C:\Users\TaoZi\Desktop\ED\BA工作坊\芯动联科_688582_年度日交易数据.csv'
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print('CSV saved:', csv_path)
print('Rows:', len(df))
print('Date range:', df['trade_date'].min().date(), '~', df['trade_date'].max().date())

# 2. 绘图
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(15, 7))
ax.plot(df['trade_date'], df['close'], color='#E04040', linewidth=1.8, label='收盘价')
ax.set_title('芯动联科 (688582.SH) 每日收盘价走势图\n2025-06-30 至 2026-06-26', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('交易日期', fontsize=12)
ax.set_ylabel('收盘价 (元)', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.4, color='#999999')
ax.legend(loc='upper left', fontsize=11, framealpha=0.9)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')

# 标注最高最低价
max_close = df['close'].max()
min_close = df['close'].min()
max_date = df.loc[df['close'] == max_close, 'trade_date'].values[0]
min_date = df.loc[df['close'] == min_close, 'trade_date'].values[0]
ax.annotate('最高: %.2f' % max_close, xy=(max_date, max_close), xytext=(10, 15), textcoords='offset points', fontsize=10, color='#E04040', arrowprops=dict(arrowstyle='->', color='#E04040', lw=1.2))
ax.annotate('最低: %.2f' % min_close, xy=(min_date, min_close), xytext=(10, -25), textcoords='offset points', fontsize=10, color='#00AA00', arrowprops=dict(arrowstyle='->', color='#00AA00', lw=1.2))

# 统计信息
gain_pct = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
stats = '数据期间: %s ~ %s\n交易天数: %d 天\n最高价: %.2f 元\n最低价: %.2f 元\n期间涨幅: %.2f%%' % (df['trade_date'].min().strftime('%Y-%m-%d'), df['trade_date'].max().strftime('%Y-%m-%d'), len(df), max_close, min_close, gain_pct)
ax.text(0.02, 0.97, stats, transform=ax.transAxes, fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.25))

plt.tight_layout()

img_path = r'C:\Users\TaoZi\Desktop\ED\BA工作坊\芯动联科_收盘价走势图.png'
plt.savefig(img_path, dpi=150, bbox_inches='tight')
print('Chart saved:', img_path)
print('Done!')
