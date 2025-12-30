import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

def calculate_rsnm(vin, vq, vqb):
    """ 计算 RSNM：寻找两条 VTC 曲线之间最大的内切正方形边长 """
    # 插值以确保点对齐，用于计算差值
    # 增加点数提高计算精度
    common_v = np.linspace(min(vin), max(vin), 2000)
    
    # 建立插值函数
    f_vq = interp1d(vin, vq, kind='linear', fill_value="extrapolate")
    f_vqb_inv = interp1d(vqb, vin, kind='linear', fill_value="extrapolate")
    
    # 两条曲线在 45 度旋转坐标系下的距离差
    diff = np.abs(f_vq(common_v) - f_vqb_inv(common_v))
    
    # RSNM 约等于 max(|V1-V2|) / sqrt(2)
    rsnm_val = np.max(diff) / np.sqrt(2)
    return rsnm_val

# 获取脚本所在目录，确保路径在任何位置运行都有效
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "../results/raw/RSNM.sp.prn")

def plot_rsnm_from_prn(file_path):
    # --- 核心修复：跳过 Xyce 的头部注释 ---
    start_line = 0
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            # 寻找包含 Index 或主要列名的那一行作为表头
            if 'Index' in line or 'V(VIN_COMMON)' in line:
                start_line = i
                break
    
    try:
        # 使用 r'\s+' 修复 SyntaxWarning，并从数据起始行开始读取
        df = pd.read_csv(file_path, sep=r'\s+', skiprows=start_line, skipinitialspace=True)
        
        # 清洗：如果首列是 'Index'，删除它
        if 'Index' in df.columns:
            df = df.drop(columns=['Index'])
    except Exception as e:
        print(f"解析文件失败: {e}")
        return

    # 自动识别列名（不区分大小写）
    try:
        col_vin = [c for c in df.columns if 'VIN_COMMON' in c.upper()][0]
        col_vq = [c for c in df.columns if 'V(VQ)' in c.upper() and 'VQB' not in c.upper()][0]
        col_vqb = [c for c in df.columns if 'V(VQB)' in c.upper()][0]
    except IndexError:
        print("错误：无法在文件中找到 V(VQ) 或 V(VQB) 列，请检查 SPICE .PRINT 语句")
        return

    # 转换为浮点型并过滤 NaN
    vin = pd.to_numeric(df[col_vin], errors='coerce').dropna().values
    vq = pd.to_numeric(df[col_vq], errors='coerce').dropna().values
    vqb = pd.to_numeric(df[col_vqb], errors='coerce').dropna().values

    # 计算 RSNM
    snm = calculate_rsnm(vin, vq, vqb)
    print(f"--- 仿真分析完成 ---")
    print(f"检测到的 RSNM: {snm*1000:.2f} mV")

    # 绘图
    plt.figure(figsize=(8, 8))
    plt.plot(vin, vq, 'b', label='VTC 1: V(VQ) = f(Vin)', linewidth=2)
    plt.plot(vqb, vin, 'r', label='VTC 2: V(VQB) mirrored', linewidth=2)
    plt.plot([0, 0.5], [0, 0.5], color='black', linestyle='--', alpha=0.3, label='Diagonal')

    plt.title(f'9T SRAM Butterfly Curve\nRSNM = {snm*1000:.1f} mV', fontsize=14)
    plt.xlabel('Voltage at Storage Node Q (V)')
    plt.ylabel('Voltage at Storage Node QB (V)')
    plt.xlim(0, 0.55)
    plt.ylim(0, 0.55)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='lower right')
    plt.gca().set_aspect('equal', adjustable='box')
    
    plt.savefig('rsnm_butterfly_fixed.png', dpi=300)
    print("图像已保存为: rsnm_butterfly_fixed.png")
    plt.show()

if __name__ == "__main__":
    plot_rsnm_from_prn('RSNM.sp.prn')
