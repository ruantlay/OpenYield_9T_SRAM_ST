from math import ceil, log2
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import u_V, u_ns

from sram_compiler.testbenches.base_testbench import BaseTestbench
from sram_compiler.subcircuits.sram_9t_st_core_for_yield import (
    Sram9TCore,
    Sram9TCoreForYield,
    Sram9TCell,
    Sram9TCellForYield
)
from sram_compiler.subcircuits.wordline_driver import WordlineDriver
from sram_compiler.subcircuits.decoder import DECODER_CASCADE
from sram_compiler.subcircuits.precharge_and_write_driver import Precharge, WriteDriver
from sram_compiler.subcircuits.mux_and_sa import ColumnMux, SenseAmp
from utils import parse_spice_models


class Sram9TCoreTestbench(BaseTestbench):
    def __init__(self, sram_config, corner="TT", w_rc=False, custom_mc=False, param_sweep=False, q_init_val=0):
        self.sram_config = sram_config
        self.corner = corner         # 工艺角 (如 TT, SS, FF)
        self.custom_mc = custom_mc   # 是否启用自定义蒙特卡洛模拟（用于良率分析）
        self.param_sweep = param_sweep # 是否启用参数扫描
        self.q_init_val = q_init_val   # 存储节点的初始值

        cfg = sram_config.global_config

        # 调用基类，设置电路名称、电压和模型库路径
        super().__init__(
            f"SRAM_9T_{cfg.num_rows}x{cfg.num_cols}_TB",
            cfg.vdd,
            getattr(cfg, f"pdk_path_{corner}")
        )

        self.num_rows = cfg.num_rows
        self.num_cols = cfg.num_cols
        self.w_rc = w_rc  # 是否包含寄生电阻电容 (RC)

        # 如果是自定义蒙特卡洛，解析 SPICE 模型以便手动注入偏差
        if self.custom_mc:
            self.model_dict = parse_spice_models(getattr(cfg, f"pdk_path_{corner}"))




    # =========================================================
    #  Single Cell SNM Testbench
    # =========================================================
    def create_single_cell_for_snm(self, circuit, operation):
        cell_cfg = self.sram_config.sram_9t_cell

        # Rotated SNM parameter
        circuit.parameter("U", 0)

        # -----------------------------
        # Model selection (from YAML)
        # -----------------------------
        # NMOS
        n_model_pd = cell_cfg.nmos_model.value[0]  # PDL1
        n_model_pg = cell_cfg.nmos_model.value[1]  # PG

        # PMOS
        p_model_pu = cell_cfg.pmos_model.value[0]  # PUL1

        # -----------------------------
        # Widths
        # -----------------------------
        w_pd = cell_cfg.nmos_width.value[0]
        w_pg = cell_cfg.nmos_width.value[1]
        w_pu = cell_cfg.pmos_width.value[0]

        length = cell_cfg.length.value

        # -----------------------------
        # Create 9T Cell
        # -----------------------------
        if self.custom_mc:
            cell = Sram9TCellForYield(
                n_model_pd,
                p_model_pu,
                n_model_pg,
                self.model_dict,
                w_pd,
                w_pu,
                w_pg,
                length,
                disconnect=True,
                param_sweep=self.param_sweep,
                suffix="_0_0"
            )
        else:
            cell = Sram9TCell(
                n_model_pd,
                p_model_pu,
                n_model_pg,
                w_pd,
                w_pu,
                w_pg,
                length,
                disconnect=True,
                param_sweep=self.param_sweep
            )

        circuit.subcircuit(cell)

        # -----------------------------
        # Instantiate single cell
        # Node order: VDD VSS BL WWLA WWLB WL
        # -----------------------------
        circuit.X(
            "X9T",
            cell.name,
            self.power_node,
            self.gnd_node,
            "BL",
            "WWLA",
            "WWLB",
            "WL"
        )

        # -----------------------------
        # Operation modes
        # -----------------------------
        if operation == "hold_snm":
            circuit.V("VWL", "WL", self.gnd_node, 0 @ u_V)

        elif operation == "read_snm":
            circuit.V("VWL", "WL", self.gnd_node, self.vdd)
            circuit.V("VBL", "BL", self.gnd_node, self.vdd)

        elif operation == "write_snm":
            circuit.V("VWL", "WL", self.gnd_node, self.vdd)
            circuit.V("VBL", "BL", self.gnd_node, 0 @ u_V)

        else:
            raise ValueError(f"Unknown SNM operation: {operation}")

        # -----------------------------
        # Rotated SNM VCVS
        # -----------------------------
        self.cell_inst_prefix = "X9T"
        h = ":"

        circuit.VCVS(
            "V1", "V1", "", self.gnd_node, "",
            raw_spice=f"VOL='U+sqrt(2)*V({self.cell_inst_prefix}{h}QBD)'"
        )
        circuit.VCVS(
            "V2", "V2", "", self.gnd_node, "",
            raw_spice=f"VOL='-U+sqrt(2)*V({self.cell_inst_prefix}{h}QD)'"
        )
        circuit.VCVS(
            "Q", f"{self.cell_inst_prefix}{h}Q", "", self.gnd_node, "",
            raw_spice="VOL='1/sqrt(2)*U+1/sqrt(2)*V(V1)'"
        )
        circuit.VCVS(
            "QB", f"{self.cell_inst_prefix}{h}QB", "", self.gnd_node, "",
            raw_spice="VOL='-1/sqrt(2)*U+1/sqrt(2)*V(V2)'"
        )

        return circuit


    # =========================================================
    #  SRAM Array Testbench
    # =========================================================
    def create_testbench(self, operation, target_row=0, target_col=0):
        circuit = Circuit(self.name)
        circuit.include(
            getattr(self.sram_config.global_config, f"pdk_path_{self.corner}")
        )
        # 设置 VDD 和 GND
        circuit.V(self.power_node, self.power_node, self.gnd_node, self.vdd)
        circuit.V(self.gnd_node, self.gnd_node, circuit.gnd, 0 @ u_V)

        if "snm" in operation:
            return self.create_single_cell_for_snm(circuit, operation)
        # 1. 实例化 SRAM Core (存储阵列)
        # 根据配置决定是否带寄生参数(w_rc)或良率分析模型
        # ---------- SRAM Core ----------
        cell_cfg = self.sram_config.sram_9t_cell

        # ---------------------------------------------------------
        # 修复点：根据 YAML 的索引关系提取 Model 和 Width
        # nmos_model 索引: 0:pdl1, 1:pg, 2:pdl2 ...
        # pmos_model 索引: 0:pul1, 1:pul2, 2:pur
        # ---------------------------------------------------------
        n_model_pd = cell_cfg.nmos_model.value[0]  # 对应 pdl1
        p_model_pu = cell_cfg.pmos_model.value[0]  # 对应 pul1
        n_model_pg = cell_cfg.nmos_model.value[1]  # 对应 pg

        # Widths 同理
        w_pd = cell_cfg.nmos_width.value[0]
        w_pu = cell_cfg.pmos_width.value[0]
        w_pg = cell_cfg.nmos_width.value[1]
        
        length = cell_cfg.length.value

        if self.custom_mc:
            core = Sram9TCoreForYield(
                self.num_rows,
                self.num_cols,
                n_model_pd,  # 使用修复后的变量
                p_model_pu,
                n_model_pg,
                self.model_dict,
                w_pd,
                w_pu,
                w_pg,
                length,
                w_rc=self.w_rc,
                param_sweep=self.param_sweep
            )
        else:
            core = Sram9TCore(
                self.num_rows,
                self.num_cols,
                n_model_pd,  # 使用修复后的变量
                p_model_pu,
                n_model_pg,
                w_pd,
                w_pu,
                w_pg,
                length,
                w_rc=self.w_rc,
                param_sweep=self.param_sweep
            )
        circuit.subcircuit(core)

        circuit.X(
            "XARRAY",
            core.name,
            self.power_node,
            self.gnd_node,
            *[f"BL{i}" for i in range(self.num_cols)],
            *[f"WWLA{r}" for r in range(self.num_rows)],
            *[f"WWLB{r}" for r in range(self.num_rows)],
            *[f"WL{r}" for r in range(self.num_rows)],
        )
        # 2. 实例化行译码器 (Decoder)
        # 自动计算地址位数 n_bits = ceil(log2(rows))
        # ---------- Decoder ----------
        dec_cfg = self.sram_config.decoder
        n_bits = ceil(log2(self.num_rows))

        decoder = DECODER_CASCADE(
            dec_cfg.nmos_model.value[0],
            dec_cfg.pmos_model.value[0],
            self.num_rows,
            dec_cfg.pmos_width.value[0],
            dec_cfg.nmos_width.value[0],
            dec_cfg.pmos_width.value[1],
            dec_cfg.nmos_width.value[1],
            dec_cfg.length.value
        )
        circuit.subcircuit(decoder)
# 实例化译码器并将地址线 A0, A1... 与目标行关联
        wl_nodes = [f"DEC_WL{i}" for i in range(self.num_rows)]

        circuit.X(
            "XDEC",
            decoder.name,
            self.power_node,
            self.gnd_node,
            *[f"A{i}" for i in range(n_bits)],
            *wl_nodes
        )

        for i in range(n_bits):
            bit = (target_row >> i) & 1
            circuit.V(
                f"A{i}",
                f"A{i}",
                self.gnd_node,
                self.vdd if bit else 0 @ u_V
            )
        # 3. 字线驱动器 (Wordline Driver)
        # 负责接收译码器信号并受 WL_EN 使能信号控制
        # ---------- Wordline Driver ----------
        wl_cfg = self.sram_config.wordline_driver
        wld = WordlineDriver(
            wl_cfg.nmos_model.value[0],
            wl_cfg.pmos_model.value[0],
            wl_cfg.pmos_width.value[0],
            wl_cfg.nmos_width.value[0],
            wl_cfg.pmos_width.value[1],
            wl_cfg.nmos_width.value[1],
            wl_cfg.length.value,
            self.num_rows
        )
        circuit.subcircuit(wld)

        circuit.PulseVoltageSource(
            "WL_EN",
            "WL_EN",
            self.gnd_node,
            0 @ u_V,
            self.vdd,
            5 @ u_ns,
            self.t_rise,
            self.t_fall,
            10 @ u_ns,
            self.t_period
        )

        for r in range(self.num_rows):
            circuit.X(
                f"XWLD{r}",
                wld.name,
                self.power_node,
                self.gnd_node,
                wl_nodes[r],
                "WL_EN",
                f"WL{r}"
            )


        if operation in ["write_0", "write_1"]:
            self.create_9t_periphery(circuit, operation, target_col)
        if operation == "write_1":
            self.add_write_assist_signals(circuit)
        if operation == "read":
            self.create_read_periphery(circuit, target_col)
        elif operation == "write":
            self.create_write_periphery(circuit)

        return circuit

# =========================================================
    #  Read Periphery (Precharge, Mux, SA) Refined for 9T
    # =========================================================
    def create_read_periphery(self, circuit, target_col):
        # 1. Precharge
        prch_cfg = self.sram_config.precharge
        # 安全地获取宽度：如果是列表取[0]，如果是数值直接用
        p_width = prch_cfg.pmos_width.value
        if isinstance(p_width, list):
            p_width = p_width[0]

        precharge = Precharge(
            pmos_model_name=prch_cfg.pmos_model.value[0], 
            base_pmos_width=p_width, # 使用处理后的变量
            length=prch_cfg.length.value if not isinstance(prch_cfg.length.value, list) else prch_cfg.length.value[0],
            num_rows=self.num_rows,
            w_rc=self.w_rc
        )
        circuit.subcircuit(precharge)
        # Instantiate for all columns. 
        # Note: 9T has no BLB, we pass gnd_node or power_node as a dummy for the 4th port
        for c in range(self.num_cols):
            circuit.X(f"XPRCH{c}", precharge.name, 
                      self.power_node, "PRE_EN", f"BL{c}", self.gnd_node)
# 2. Column Mux
        mux_cfg = getattr(self.sram_config, 'columnmux', None) or \
                  getattr(self.sram_config, 'COLUMNMUX', None)
        
        # 处理宽度和长度可能为 float 的情况
        m_n_width = mux_cfg.nmos_width.value
        if isinstance(m_n_width, list): m_n_width = m_n_width[0]
        
        m_length = mux_cfg.length.value
        if isinstance(m_length, list): m_length = m_length[0]

        mux = ColumnMux(
            mux_cfg.nmos_model.value[0],
            mux_cfg.pmos_model.value[0] if hasattr(mux_cfg, 'pmos_model') else None,
            m_n_width,
            m_length
        )
        circuit.subcircuit(mux)

        circuit.X("XMUX", mux.name, 
                self.power_node, 
                self.gnd_node, 
                f"BL{target_col}", # 连接真实的位线
                self.gnd_node,     # BLB 位置传 GND（占位）
                "SEL", 
                "SA_IN")
    # =========================================================
    #  Write Periphery (Write Driver)
    # =========================================================
    def create_write_periphery(self, circuit):
        """
        实例化写入周边的组件：写驱动器
        """
        wr_cfg = self.sram_config.writedriver
        writer = WriteDriver(
            wr_cfg.nmos_model.value[0],
            wr_cfg.pmos_model.value[0],
            wr_cfg.nmos_width.value[0],
            wr_cfg.pmos_width.value[0],
            wr_cfg.length.value
        )
        circuit.subcircuit(writer)
        # 具体的实例化逻辑可以根据你的 main_sram.py 需求进一步补充

    # =========================================================
    #          在 create_testbench 中定义写 1 辅助信号
    # =========================================================
    def add_write_assist_signals(self, circuit):
        # 正常低电平为 0V，高电平为 VDD
        # 写 1 时，WWLB 需要拉低到负值 (例如 -0.2V)
        v_neg = -0.2 @ u_V

        circuit.PulseVoltageSource(
            "VWWLB_NEG", "WWLB_DRV", self.gnd_node,
            initial_value=self.vdd,     # 默认保持为 1 (打开 PDL1)
            pulsed_value=v_neg,         # 写脉冲期间变为负压
            delay_time=5 @ u_ns,
            rise_time=0.1 @ u_ns,
            fall_time=0.1 @ u_ns,
            pulse_width=6 @ u_ns,       # 文档提到的 T_WWLB = 6ns
            period=self.t_period
        )

    # =========================================================
    #          针对 9T 的外围实例化逻辑
    # =========================================================
    def create_9t_periphery(self, circuit, operation, target_col):
        # 1. 产生列控制信号 (WWLA, WWLB)
        # 注意：这些信号通常是按列控制的 (Column-based)
        if operation == "write_0":
            # WWLA 脉冲变高以断开 PUL2
            circuit.X("WWLA_DRV", "WD_INV", self.power_node, self.gnd_node, "WEN_0", f"WWLA{target_col}")
            circuit.V("BL_DATA", f"BL{target_col}", self.gnd_node, 0 @ u_V)
        elif operation == "write_1":
            # 使用上文提到的负压源驱动 WWLB
            circuit.X("WWLB_DRV", "WD_NEG_DRV", self.power_node, "VWWLB_NEG", f"BL{target_col}")
            circuit.V("BL_DATA", f"BL{target_col}", self.gnd_node, self.vdd)

    def create_read_periphery_sa(self, circuit, target_col):
        # 实例化高偏置反相器作为 SA
        # 输入连接到目标列的 BL
        circuit.X("XSA", "InverterSA", self.power_node, self.gnd_node, f"BL{target_col}", "SA_OUT")