import matplotlib.pyplot as plt
import seaborn as sns
import glob
import re
import os
import numpy as np

def analyze_sram_mc(subdir='mc_results', file_prefix='single_cell_mc.sp.mt*'):
    search_path = os.path.join(subdir, file_prefix)
    mt_files = sorted(glob.glob(search_path))
    
    if not mt_files:
        print(f"Error: No files found in {search_path}")
        return

    delay0, delay1 = [], []
    # 正则匹配 Key = Value 格式
    p0 = re.compile(r'T_WRITE0_DELAY\s*=\s*([eE\d\.-]+)')
    p1 = re.compile(r'T_WRITE1_DELAY\s*=\s*([eE\d\.-]+)')

    for f in mt_files:
        with open(f, 'r') as file:
            content = file.read()
            m0, m1 = p0.search(content), p1.search(content)
            # 只有当测量值大于0时才认为是有效写入
            if m0 and float(m0.group(1)) > 0: delay0.append(float(m0.group(1)) * 1e12)
            if m1 and float(m1.group(1)) > 0: delay1.append(float(m1.group(1)) * 1e12)

    # 统计与良率分析
    total_samples = len(mt_files)
    
    def print_stats(name, data):
        if not data: return
        mu, sigma = np.mean(data), np.std(data)
        yield_rate = (len(data) / total_samples) * 100
        print(f"\n--- {name} Statistics ---")
        print(f"Samples: {len(data)}/{total_samples} (Yield: {yield_rate:.2f}%)")
        print(f"Mean (μ): {mu:.2f} ps")
        print(f"Std Dev (σ): {sigma:.2f} ps")
        print(f"3σ Range: [{mu-3*sigma:.2f}, {mu+3*sigma:.2f}] ps")

    print_stats("Write 0", delay0)
    print_stats("Write 1", delay1)

    # 绘图
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    if delay0: sns.histplot(delay0, kde=True, color="dodgerblue", label="Write 0 Delay", bins=40)
    if delay1: sns.histplot(delay1, kde=True, color="orangered", label="Write 1 Delay", bins=40)
    
    plt.title(f"SRAM 9T Monte Carlo Analysis ({total_samples} Iterations)")
    plt.xlabel("Delay (ps)")
    plt.legend()
    plt.savefig('mc_final_report.png', dpi=300)
    print("\nReport saved as mc_final_report.png")
    plt.show()

if __name__ == "__main__":
    analyze_sram_mc()