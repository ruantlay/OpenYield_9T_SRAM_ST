import numpy as np
import glob
import re

def generate_yield_report(target_delay_ps=400.0):
    delays = []
    # 从 mc_results 文件夹读取所有数据
    for f in glob.glob('mc_results/*.mt*'):
        with open(f, 'r') as file:
            match = re.search(r'T_WRITE1_DELAY\s*=\s*([eE\d\.-]+)', file.read())
            if match:
                delays.append(float(match.group(1)) * 1e12) # 转为 ps

    delays = np.array(delays)
    mu = np.mean(delays)
    sigma = np.std(delays)
    
    # 计算良率
    passed = delays[delays < target_delay_ps]
    yield_rate = (len(passed) / len(delays)) * 100
    
    print("========== SRAM 可靠性报告 ==========")
    print(f"设定目标时延门限: {target_delay_ps} ps")
    print(f"平均延时 (μ): {mu:.2f} ps")
    print(f"标准差 (σ): {sigma:.2f} ps")
    print(f"最差样本延时: {np.max(delays):.2f} ps")
    print(f"预估良率 (Yield): {yield_rate:.2f}%")
    print(f"6-Sigma 距离: {(target_delay_ps - mu)/sigma:.2f} σ")
    print("====================================")

if __name__ == "__main__":
    generate_yield_report(target_delay_ps=500.0) # 你可以修改此阈值