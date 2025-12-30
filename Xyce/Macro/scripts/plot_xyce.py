import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. 自动定位文件路径
# 获取脚本所在目录，确保在 Windows 路径下不会出错
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'test.sp.prn')

print(f"Reading file: {file_path}")

try:
    # 使用 r'' 原始字符串和正则表达式 \s+ 匹配 Xyce 的空格分隔符
    # index_col=0 将 'Index' 列作为索引
    df = pd.read_csv(file_path, sep=r'\s+', engine='python', index_col=0)
    
    # 清理列名中的空格
    df.columns = [c.strip() for c in df.columns]
    
    # 打印前几行数据，确认翻转情况
    print("Final Q7_3 Voltage:", df['V(Q7_3)'].iloc[-1])

    # 2. 开始绘图
    plt.style.use('seaborn-v0_8-darkgrid') # 使用内置样式美化
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # 子图 1: 控制信号 (Wordline WL7)
    if 'V(WL7)' in df.columns:
        ax1.plot(df['TIME'], df['V(WL7)'], label='WL7 (Wordline)', color='#1f77b4', lw=2)
    ax1.set_ylabel('Voltage (V)', fontsize=12)
    ax1.set_title('9T SRAM Write Cycle Analysis (Row 7, Col 3)', fontsize=14)
    ax1.legend(loc='upper right')
    ax1.grid(True, which='both', linestyle='--', alpha=0.5)

    # 子图 2: 存储节点翻转 (Q7_3 和 QB7_3)
    # 如果有重复列名，Pandas 会自动处理为 V(Q7_3) 和 V(Q7_3).1，我们取第一列
    q_node = 'V(Q7_3)'
    qb_node = 'V(QB7_3)'
    
    ax2.plot(df['TIME'], df[q_node], label='Q7_3 (Data)', color='#d62728', lw=2.5)
    ax2.plot(df['TIME'], df[qb_node], label='QB7_3 (Data_Bar)', color='#ff7f0e', lw=2.5)
    
    # 如果有位线数据也画上去观察
    if 'V(BL3)' in df.columns:
        ax2.plot(df['TIME'], df['V(BL3)'], label='BL3 (Bitline)', color='#2ca02c', lw=1, linestyle='--')

    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Voltage (V)', fontsize=12)
    ax2.legend(loc='center right')
    ax2.grid(True, which='both', linestyle='--', alpha=0.5)

    plt.tight_layout()
    
    # 保存图片
    output_img = os.path.join(current_dir, 'sram_waveform_final.png')
    plt.savefig(output_img, dpi=300)
    print(f"Success! Image saved to: {output_img}")
    
    plt.show()

except Exception as e:
    print(f"Failed to plot: {e}")