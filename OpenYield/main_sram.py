import os
from datetime import datetime
import numpy as np
from PySpice.Unit import u_V, u_ns, u_Ohm, u_pF

# 导入自定义模块
from sram_compiler.testbenches.sram_9t_core_testbench import Sram9TCoreTestbench
from sram_compiler.testbenches.sram_9t_core_MC_testbench import Sram9TCoreMcTestbench
from utils import estimate_9t_bitcell_area
from config import SRAM_CONFIG

# config.py

def get_config(self, config_name):
    # 1. 尝试直接获取（精确匹配）
    if config_name in self.data:
        return self.data[config_name]
    
    # 2. 尝试不区分大小写的匹配（鲁棒性增强）
    for key in self.data.keys():
        if key.upper() == config_name.upper():
            return self.data[key]
            
    # 3. 如果还是没找到，打印出当前 YAML 里到底有哪些键，方便调试
    available_keys = list(self.data.keys())
    raise KeyError(f"未找到配置: '{config_name}'。当前 YAML 文件中的可用键为: {available_keys}")
def run_sram_9t_workflow():
    # ================== 1. 环境配置与目录准备 ==================
    sram_config = SRAM_CONFIG()
    sram_config.load_all_configs(
        global_file="sram_compiler/config_yaml/global.yaml",
        circuit_configs={
            "SRAM_9T_CELL": "sram_compiler/config_yaml/sram_9t_cell.yaml",
            "WORDLINEDRIVER": "sram_compiler/config_yaml/wordline_driver.yaml",
            "PRECHARGE": "sram_compiler/config_yaml/precharge.yaml",
            "COLUMNMUX": "sram_compiler/config_yaml/mux.yaml",
            "SENSEAMP": "sram_compiler/config_yaml/sa.yaml",
            "WRITEDRIVER": "sram_compiler/config_yaml/write_driver.yaml",
            "DECODER": "sram_compiler/config_yaml/decoder.yaml"
        }
    )

    # 生成带时间戳的输出目录
    time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    sim_path = os.path.join('sim', f"{time_str}_mc_9t")
    os.makedirs(sim_path, exist_ok=True)

    print(f"\n{'='*20} 9T SRAM Workflow Start {'='*20}")
    print(f"Simulation Path: {sim_path}")

    # ================== 2. 物理指标评估 (面积估算) ==================
    # 提取 9T 特有的宽度列表进行面积评估
    cell_cfg = sram_config.sram_9t_cell
    area = estimate_9t_bitcell_area(
        w_nmos_list=cell_cfg.nmos_width.value,  # [PDL1, PG, PDL2, PDR1, PDR2, NF]
        w_pmos_list=cell_cfg.pmos_width.value,  # [PUL1, PUL2, PUR]
        l_transistor=cell_cfg.length.value
    )
    print(f"[INFO] Estimated 9T SRAM Cell Area: {area*1e12:.4f} µm²")

    # ================== 3. 初始化蒙特卡洛测试平台 ==================
    g_cfg = sram_config.global_config
    
    mc_testbench = Sram9TCoreMcTestbench(
        sram_config,
        w_rc=True,                      # 启用寄生电阻电容
        pi_res=100 @ u_Ohm, 
        pi_cap=0.001 @ u_pF,
        vth_std=0.05,                  # 阈值电压标准差
        custom_mc=False,               # 是否使用自定义工艺参数注入
        param_sweep=False,
        corner='TT',                   # 典型工艺角
        q_init_val=0,                  # 初始存储状态
        sim_path=sim_path
    )

    # ================== 4. 执行仿真任务 ==================
    # 你可以根据需要切换仿真类型：'read', 'write', 'hold_snm', 'read_snm'
    target_op = 'read'  # 目标操作
    print(f"[RUN] Starting Monte Carlo Simulation: Operation={target_op}, Runs={g_cfg.monte_carlo_runs}")

    try:
        if target_op in ['read', 'write']:
            # 瞬态仿真 (Transient Analysis)
            results = mc_testbench.run_mc_simulation(
                operation=target_op,
                target_row=g_cfg.num_rows - 1,
                target_col=g_cfg.num_cols - 1,
                mc_runs=g_cfg.monte_carlo_runs,
                temperature=g_cfg.temperature,
                vars=None
            )
            
            # 解构结果 (假设返回的是 delay 和 power)
            delay, pavg = results
            print(f"[RESULT] {target_op.capitalize()} Delay Mean: {np.mean(delay)*1e9:.3f} ns")
            print(f"[RESULT] {target_op.capitalize()} Power Mean: {np.mean(pavg)*1e6:.3f} µW")

        elif 'snm' in target_op:
            # 静态分析 (DC Analysis)
            snm_results = mc_testbench.run_mc_simulation(
                operation=target_op,
                target_row=g_cfg.num_rows - 1,
                target_col=g_cfg.num_cols - 1,
                mc_runs=g_cfg.monte_carlo_runs,
                temperature=g_cfg.temperature
            )
            print(f"[RESULT] {target_op.upper()} Mean: {np.mean(snm_results)*1e3:.2f} mV")

    except Exception as e:
        print(f"[ERROR] Simulation failed: {str(e)}")
    
    print(f"{'='*20} 9T SRAM Workflow Completed {'='*20}\n")

if __name__ == '__main__':
    run_sram_9t_workflow()