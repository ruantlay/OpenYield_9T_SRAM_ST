import pandas as pd
import matplotlib.pyplot as plt
import os

file_path = 'single_cell.sp.prn'

if not os.path.exists(file_path):
    print(f"错误: 找不到文件 {file_path}")
    exit()

# 1. 更加鲁棒的数据加载函数
def load_xyce_prn(path):
    # 先读取所有内容
    df = pd.read_csv(path, sep=r'\s+', engine='python', header=None)
    
    # 尝试将所有内容转换为数值，无法转换的变成 NaN
    df = df.apply(pd.to_numeric, errors='coerce')
    
    # 删掉全是 NaN 的行（通常是原来的表头文字）
    df = df.dropna(how='all').reset_index(drop=True)
    
    # 删掉全是 NaN 的列
    df = df.dropna(axis=1, how='all')
    
    return df

data = load_xyce_prn(file_path)

# 2. 定义列名
# 检查列数，Xyce 打印 V(Q) 等可能会有额外的一列 Index
num_cols = data.shape[1]
print(f"检测到 {num_cols} 列有效数据")

if num_cols == 8:
    data.columns = ['Index', 'Time', 'WL', 'WWLA', 'WWLB', 'BL', 'Q', 'QB']
elif num_cols == 7:
    data.columns = ['Time', 'WL', 'WWLA', 'WWLB', 'BL', 'Q', 'QB']
else:
    # 如果列数不对，手动指定前几列
    cols = ['Time', 'WL', 'WWLA', 'WWLB', 'BL', 'Q', 'QB']
    data = data.iloc[:, :len(cols)]
    data.columns = cols

# 3. 转换时间单位并绘图
data['Time'] = data['Time'].astype(float) * 1e9

# --- 绘图部分保持不变 ---
fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
plt.subplots_adjust(hspace=0.3)
colors = {'ctrl': '#1f77b4', 'data': '#d62728', 'assist': '#2ca02c'}

# WL
axes[0].plot(data['Time'], data['WL'], color=colors['ctrl'], lw=2)
axes[0].set_ylabel('WL (V)')
axes[0].set_title('9T SRAM Cell Single Core Function Test')

# Assists
axes[1].plot(data['Time'], data['WWLA'], label='WWLA', color='#ff7f0e', lw=2)
axes[1].plot(data['Time'], data['WWLB'], label='WWLB', color='#9467bd', lw=2)
axes[1].set_ylabel('Assist (V)')
axes[1].legend(loc='upper right')

# BL
axes[2].plot(data['Time'], data['BL'], color='black', lw=1.5, linestyle='--')
axes[2].set_ylabel('BL (V)')

# Q & QB
axes[3].plot(data['Time'], data['Q'], label='Q', color=colors['data'], lw=2.5)
axes[3].plot(data['Time'], data['QB'], label='QB', color='gray', lw=1.5, alpha=0.7)
axes[3].set_ylabel('Storage (V)')
axes[3].set_xlabel('Time (ns)')
axes[3].legend(loc='upper right')

# 标注阶段
for ax in axes:
    ax.grid(True, linestyle='--', alpha=0.6)
    for start, end, label in [(0,10,'Hold'), (10,20,'Read'), (20,30,'Write-0'), (30,40,'Write-1')]:
        ax.axvline(x=start, color='red', linestyle=':', alpha=0.3)
        if ax == axes[0]:
            ax.text(start + 5, 0.7, label, ha='center')

plt.xlim(0, 40)
plt.savefig('sram_9t_waveform.png', dpi=300)
print("绘图成功！图片已保存为 sram_9t_waveform.png")
plt.show()