from PySpice.Spice.Netlist import SubCircuitFactory, Circuit
from PySpice.Unit import u_Ohm, u_pF
from .base_subcircuit import BaseSubcircuit
# from utils import model_dict2str
from typing import Dict, Any, Union

##############################################################
#用于 SNM 仿真的9T_cell电路拓扑结构
##############################################################
class Sram9TCell(BaseSubcircuit):#继承自BaseSubcircuit
    ### 9T SRAM Cell SubCircuitFactory ###
    #子电路名称
    NAME = 'SRAM_9T_CELL'
    # 节点：电源, 地, 位线L, 写位线A, 写位线B, 字线
    NODES = ('VDD', 'VSS', 'BL', 'WWLA','WWLB', 'WL')

    #基本9t单元所需参数：pd/pu/pg各自的模型名，晶体管长宽以及rc相关参数
    def __init__(self,
                 pd_nmos_model_name: str, pu_pmos_model_name: str, pg_nmos_model_name: str,
                 pd_width: float, pu_width: float,
                 pg_width: float, length: float,
                 w_rc=False,
                 pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF,
                 disconnect=False,  #是否断开内部数据节点连接
                 param_sweep=False,
                 pmos_model_choices='PMOS_VTG',
                 nmos_model_choices='NMOS_VTG'
                 ):
        if disconnect:
            self.NAME += '_DISCONNECT'                      #如果断开内部数据节点连接，改下子电路名字

        super().__init__(                                   #调用父类初始化
            pd_nmos_model_name, pu_pmos_model_name,
            pd_width, pu_width, length,
            w_rc, pi_res, pi_cap
        )
# 存储参数
        self.pmos_model_choices = pmos_model_choices
        self.nmos_model_choices = nmos_model_choices
        self.pg_width = pg_width
        self.pd_width = pd_width
        self.pu_width = pu_width
        self.pg_nmos_model_name = pg_nmos_model_name
        self.disconnect = disconnect
        self.length = length

        # 节点分配 (假设 NODES 顺序: 0:VDD, 1:VSS, 2:BL, 3:WWLA, 4:WWLB, 5:WL)
        # 注意：9T 单元通常只有一个 BL，原本 6T 的 BLB 位置现在可能被 WWLA/B 占用
        if not self.w_rc:
            bl_node   = self.NODES[2]
            wwla_node = self.NODES[3]
            wwlb_node = self.NODES[4]
            wl_node   = self.NODES[5]
            q_node    = 'Q'
            qb_node   = 'QB'
        else:
            bl_node   = self.add_rc_networks_to_node(self.NODES[2], 1)
            wwla_node = self.add_rc_networks_to_node(self.NODES[3], 1)
            wwlb_node = self.add_rc_networks_to_node(self.NODES[4], 1)
            wl_node   = self.add_rc_networks_to_node(self.NODES[5], 1)
            q_node    = self.add_rc_networks_to_node('Q', 1)
            qb_node   = self.add_rc_networks_to_node('QB', 1)



#创建出各个管子，并定义其拓扑连接方式
        self.add_9T_cell(bl_node, wwla_node, wwlb_node, wl_node, q_node, qb_node, param_sweep)
    def add_9T_cell(self, bl_node, wwla_node, wwlb_node, wl_node, q_node, qb_node, param_sweep):
        """
        根据电路拓扑图添加 9T 单元：
        - 左侧：PUL1, PUL2 (PMOS 堆叠); PDL1, PDL2 (NMOS 堆叠)
        - 右侧：PUR (PMOS); PDR1, PDR2 (NMOS 堆叠); NF (反馈控制管)
        - 访问管：PG (连接 BL 与 Q)
        """
        # 处理断开模式下的内部节点命名（用于 SNM 仿真）
        if self.disconnect:
            data_q = 'QD'
            data_qb = 'QBD'
        else:
            data_q = q_node
            data_qb = qb_node

        # 1. 访问晶体管 (Access Transistor)
        # PG: Gate=WL, Drain=BL, Source=Q
        self.M('PG', bl_node, wl_node, data_q, self.NODES[1],
                model=self.pg_nmos_model_name, w=self.pg_width, l=self.length)


        # 2. 左侧反相器/存储路径 (Left side)
        # PUL1: Gate=QB, Source=VDD, Drain与PUL2连接
        self.M('PUL1', 'N_PUL_INT', qb_node, self.NODES[0], self.NODES[0],
                model=self.pmos_pdk_model, w=self.pu_width, l=self.length)
        # PUL2: Gate=WWLA, Source=N_PUL_INT, Drain=Q
        self.M('PUL2', data_q, wwla_node, 'N_PUL_INT', self.NODES[0],
                model=self.pmos_pdk_model, w=self.pu_width, l=self.length)

        # PDL1: Gate=WWLB, Drain=Q, Source与PDL2连接
        self.M('PDL1', data_q, wwlb_node, 'N_PDL_INT', self.NODES[1],
                model=self.nmos_pdk_model, w=self.pd_width, l=self.length)
        # PDL2: Gate=QB, Drain=N_PDL_INT, Source=VSS
        self.M('PDL2', 'N_PDL_INT', qb_node, self.NODES[1], self.NODES[1],
                model=self.nmos_pdk_model, w=self.pd_width, l=self.length)


        # 3. 右侧反相器/反馈路径 (Right side)
        # PUR: Gate=Q, Source=VDD, Drain=QB
        self.M('PUR', qb_node, q_node, self.NODES[0], self.NODES[0],
                model=self.pmos_pdk_model, w=self.pu_width, l=self.length)

        # PDR1: Gate=Q, Drain=QB, Source=VX
        self.M('PDR1', data_qb, q_node, 'VX', self.NODES[1],
                model=self.nmos_pdk_model, w=self.pd_width, l=self.length)
        # PDR2: Gate=Q, Drain=VX, Source=VSS
        self.M('PDR2', 'VX', q_node, self.NODES[1], self.NODES[1],
                model=self.nmos_pdk_model, w=self.pd_width, l=self.length)

        # NF: Gate=QB, Drain=VX, Source=WWLB
        self.M('NF', 'VX', qb_node, wwlb_node, self.NODES[1],
                model=self.nmos_pdk_model, w=self.pd_width, l=self.length)

        # 调试打印
        if not param_sweep:
            print(f"[DEBUG] 9T Cell '{self.NAME}' initialized with stack structures and NF feedback.")






##############################################################
#支持良率分析的9T_cell电路拓扑结构
##############################################################
class Sram9TCellForYield(Sram9TCell):#支持良率分析的9t sram单元
    def __init__(self, bl_node, wwla_node, wwlb_node, wl_node, q_node, qb_node, param_sweep):
        """
        按照 9T 电路拓扑逐个添加晶体管实例。
        每个晶体管都拥有唯一的自定义模型，以支持良率分析中的失配仿真。
        """
        # 1. 静态噪声容限 (SNM) 仿真模式下的节点处理
        data_q = 'QD' if self.disconnect else q_node
        data_qb = 'QBD' if self.disconnect else qb_node

        # 定义长度参数
        l_val = 'length' if param_sweep else self.length

        # ------------------------------------------------------------------
        # 1. 访问晶体管 (Access Transistor)
        # ------------------------------------------------------------------
        pg_udf_model = f"{self.pg_nmos_model_name}_PG{self.suffix}"
        pg_w = 'nmos_width_pg' if param_sweep else self.pg_width
        # PG: Drain=BL, Gate=WL, Source=Q, Bulk=VSS
        self.M('PG', bl_node, wl_node, data_q, self.NODES[1],
                model=pg_udf_model, w=pg_w, l=l_val)
        self.add_usrdefine_mos_model(self.pg_nmos_model_name, pg_udf_model)

        # ------------------------------------------------------------------
        # 2. 左侧存储路径 (Left side Stack)
        # ------------------------------------------------------------------
        pu_w = 'pmos_width_pu' if param_sweep else self.pu_width
        pd_w = 'nmos_width_pd' if param_sweep else self.pd_width

        # PUL1: PMOS 上拉1, 受 QB 控制
        pul1_udf = f"{self.pmos_pdk_model}_PUL1{self.suffix}"
        self.M('PUL1', 'N_PUL_INT', qb_node, self.NODES[0], self.NODES[0],
                model=pul1_udf, w=pu_w, l=l_val)
        self.add_usrdefine_mos_model(self.pmos_pdk_model, pul1_udf)

        # PUL2: PMOS 上拉2, 受 WWLA 控制
        pul2_udf = f"{self.pmos_pdk_model}_PUL2{self.suffix}"
        self.M('PUL2', data_q, wwla_node, 'N_PUL_INT', self.NODES[0],
                model=pul2_udf, w=pu_w, l=l_val)
        self.add_usrdefine_mos_model(self.pmos_pdk_model, pul2_udf)

        # PDL1: NMOS 下拉1, 受 WWLB 控制
        pdl1_udf = f"{self.nmos_pdk_model}_PDL1{self.suffix}"
        self.M('PDL1', data_q, wwlb_node, 'N_PDL_INT', self.NODES[1],
                model=pdl1_udf, w=pd_w, l=l_val)
        self.add_usrdefine_mos_model(self.nmos_pdk_model, pdl1_udf)

        # PDL2: NMOS 下拉2, 受 QB 控制
        pdl2_udf = f"{self.nmos_pdk_model}_PDL2{self.suffix}"
        self.M('PDL2', 'N_PDL_INT', qb_node, self.NODES[1], self.NODES[1],
                model=pdl2_udf, w=pd_w, l=l_val)
        self.add_usrdefine_mos_model(self.nmos_pdk_model, pdl2_udf)

        # ------------------------------------------------------------------
        # 3. 右侧反馈路径 (Right side)
        # ------------------------------------------------------------------
        # PUR: PMOS 上拉, 受 Q 控制
        pur_udf = f"{self.pmos_pdk_model}_PUR{self.suffix}"
        self.M('PUR', qb_node, q_node, self.NODES[0], self.NODES[0],
                model=pur_udf, w=pu_w, l=l_val)
        self.add_usrdefine_mos_model(self.pmos_pdk_model, pur_udf)

        # PDR1: NMOS 下拉1, 受 Q 控制
        pdr1_udf = f"{self.nmos_pdk_model}_PDR1{self.suffix}"
        self.M('PDR1', data_qb, q_node, 'VX', self.NODES[1],
                model=pdr1_udf, w=pd_w, l=l_val)
        self.add_usrdefine_mos_model(self.nmos_pdk_model, pdr1_udf)

        # PDR2: NMOS 下拉2, 受 Q 控制
        pdr2_udf = f"{self.nmos_pdk_model}_PDR2{self.suffix}"
        self.M('PDR2', 'VX', q_node, self.NODES[1], self.NODES[1],
                model=pdr2_udf, w=pd_w, l=l_val)
        self.add_usrdefine_mos_model(self.nmos_pdk_model, pdr2_udf)

        # NF: 反馈控制 NMOS, 受 QB 控制
        nf_udf = f"{self.nmos_pdk_model}_NF{self.suffix}"
        self.M('NF', 'VX', qb_node, wwlb_node, self.NODES[1],
                model=nf_udf, w=pd_w, l=l_val)
        self.add_usrdefine_mos_model(self.nmos_pdk_model, nf_udf)

        # 4. 调试输出
        if not param_sweep:
            print(f"[DEBUG] 9T_Cell '{self.NAME}' initialized: 9 independent models created for yield analysis.")
    def add_usrdefine_mos_model(self, pdk_model_name, udf_model_name):
        """
        为指定的晶体管实例创建一个唯一的、参数化的 SPICE 模型副本。
        参数:
        pdk_model_name: 原始 PDK 提供的基础模型名 (如 'nmos_vtg')
        udf_model_name: 为当前管子定义的唯一模型副本名 (如 'nmos_vtg_PG_cell_0_0')
        """
        # 1. 从预定义的模型字典中检索原始 PDK 工艺参数数据
        model_data = self.model_dict[pdk_model_name]
        # 2. 获取器件类型（nmos 或 pmos），用于 SPICE .model 语句的语法
        mos_type = model_data['type']
        # 3. 开始构建 SPICE 语法字符串：.model <模型名> <类型>
        self.raw_spice += f'.model {udf_model_name} {mos_type} '
        # 4. 获取该模型所有的物理参数列表（如 vth0, u0, cgdo 等）
        params = model_data['parameters']
        # 5. 遍历每一个物理参数，准备写入网表
        for param_name, param_value in params.items():
            # --- 格式化数值部分 ---
            if isinstance(param_value, float):
                # 针对极小值（如寄生电容）或极大值使用科学计数法，防止精度丢失
                if abs(param_value) < 1e-3 or abs(param_value) > 1e6:
                    param_str = f"{param_value:.3e}"
                else:
                    param_str = str(param_value)
            else:
                param_str = str(param_value)
            # --- 核心：参数变量化 (Key of Monte Carlo) ---
            # 如果参数是阈值电压(vth0)、迁移率(u0)或截止偏置(voff)，则不直接写入数值。
            # 而是将其替换为一个唯一的变量名（用单引号包裹），例如 'vth0_nmos_vtg_PG_0_0'。
            # 这样 SPICE 仿真器在运行时可以从外部统计块中读取该变量的随机值。
            if param_name in ['vth0', 'u0', 'voff']:
                param_str = f"'{param_name}_{udf_model_name}'"
            # 6. 将处理好的 参数=值 键值对拼接进 raw_spice 字符串
            self.raw_spice += f"{param_name}={param_str} "
        # 7. 该模型定义结束，换行
        self.raw_spice += "\n"







##############################################################
#        构建sram阵列
##############################################################
class Sram9TCore(SubCircuitFactory):
    """
    9T SRAM 存储阵列子电路工厂类。
    支持配置行数、列数，并自动生成对应的读写控制网络。
    """

    def __init__(self, num_rows: int, num_cols: int,
                 pd_nmos_model_name: str, pu_pmos_model_name: str, pg_nmos_model_name: str,
                 pd_width=0.205e-6, pu_width=0.09e-6,
                 pg_width=0.135e-6, length=50e-9,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF,
                 param_sweep=False,
                 pmos_model_choices='PMOS_VTG',
                 nmos_model_choices='NMOS_VTG'
                 ):

        self.NAME = f"SRAM_9T_CORE_{num_rows}x{num_cols}"

        # 1. 动态生成阵列节点定义
        self.NODES = (
            'VDD',  # 电源
            'VSS',  # 地
            *[f'BL{i}' for i in range(num_cols)],     # 每一列的位线 (只支持单BL结构)
            *[f'WWLA{j}' for j in range(num_rows)],   # 每一行的写字线 A
            *[f'WWLB{j}' for j in range(num_rows)],   # 每一行的写字线 B
            *[f'WL{j}' for j in range(num_rows)],     # 每一行的读字线
        )

        super().__init__()

        # 存储阵列配置
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.pd_nmos_pdk_model = pd_nmos_model_name
        self.pu_pmos_pdk_model = pu_pmos_model_name
        self.pg_nmos_pdk_model = pg_nmos_model_name
        # 存储管子尺寸
        self.pg_width = pg_width
        self.pd_width = pd_width
        self.pu_width = pu_width
        self.length = length
        # 寄生 RC 与扫描设置
        self.w_rc = w_rc
        self.pi_res = pi_res
        self.pi_cap = pi_cap
        self.param_sweep = param_sweep
        self.pmos_model_choices = pmos_model_choices
        self.nmos_model_choices = nmos_model_choices

        # 2. 构建阵列拓扑
        self.build_array(num_rows, num_cols)
        # 设置实例前缀
        self.inst_prefix = "XSRAM_9T_CELL"

    def build_array(self, num_rows, num_cols):
        """
        创建 9T 单元子电路蓝图并进行阵列实例化连接。
        """
        # A. 创建单个 9T SRAM 单元子电路实例
        subckt_9t_cell = Sram9TCell(
            self.pd_nmos_pdk_model, self.pu_pmos_pdk_model, self.pg_nmos_pdk_model,
            pd_width=self.pd_width, pu_width=self.pu_width,
            pg_width=self.pg_width, length=self.length,
            w_rc=self.w_rc,
            pi_res=self.pi_res, pi_cap=self.pi_cap,
            param_sweep=self.param_sweep,
            pmos_model_choices=self.pmos_model_choices,
            nmos_model_choices=self.nmos_model_choices
        )

        # B. 将 9T 单元定义添加到当前的阵列子电路中
        self.subcircuit(subckt_9t_cell)

        # C. 遍历所有行列，按照 9T 的节点顺序进行实例化
        for row in range(num_rows):
            for col in range(num_cols):
                self.X(
                    f"{subckt_9t_cell.name}_{row}_{col}", # 实例名 (e.g. SRAM_9T_CELL_0_0)
                    subckt_9t_cell.name,                  # 子电路类型名
                    self.NODES[0],   # VDD
                    self.NODES[1],   # VSS
                    f'BL{col}',      # 连接到对应列的位线
                    f'WWLA{row}',    # 连接到对应行的写字线 A
                    f'WWLB{row}',    # 连接到对应行的写字线 B
                    f'WL{row}'       # 连接到对应行的读字线
                )

        if not self.param_sweep:
            print(f"[DEBUG] 9T Core '{self.NAME}' initialized with {num_rows}x{num_cols} cells.")





##############################################################
#          支持良率分析的 9T SRAM 阵列
##############################################################
class Sram9TCoreForYield(Sram9TCore):
    """
    支持良率分析的 9T SRAM 阵列类。
    通过为每个行列坐标实例化独立的 Sram9TCellForYield，
    实现晶体管级的失配（Mismatch）仿真。
    """

class Sram9TCellForYield(Sram9TCell):
    # 修改 1: 增加 suffix 参数接收，增加 model_dict 接收
    def __init__(self, pd_nmos_model_name, pu_pmos_model_name, pg_nmos_model_name,
                 model_dict, pd_width, pu_width, pg_width, length,
                 w_rc=False, pi_res=100@u_Ohm, pi_cap=0.001@u_pF,
                 suffix='', disconnect=False, param_sweep=False):
        
        self.suffix = suffix
        self.model_dict = model_dict
        
        # 修改 2: 调用父类 Sram9TCell 的初始化
        super().__init__(
            pd_nmos_model_name, pu_pmos_model_name, pg_nmos_model_name,
            pd_width, pu_width, pg_width, length,
            w_rc, pi_res, pi_cap, disconnect, param_sweep
        )
        self.pd_nmos_pdk_model = pd_nmos_model_name
        self.pu_pmos_pdk_model = pu_pmos_model_name
        self.pg_nmos_pdk_model = pg_nmos_model_name
        self.param_sweep = param_sweep

    def build_array(self, num_rows, num_cols):
        """
        重写阵列构建函数：
        在 9T 阵列中，为每一个 (row, col) 位置创建一个专属的 9T Cell 子电路定义。
        """
        # 遍历所有行和列
        for row in range(num_rows):
            for col in range(num_cols):
                # 1. 实例化当前坐标独有的 9T Cell 工厂
                # suffix=f'_{row}_{col}' 确保了该 Cell 内部所有管子模型名称的唯一性
                subckt_9t_cell = Sram9TCellForYield(
                    self.pd_nmos_pdk_model, 
                    self.pu_pmos_pdk_model, 
                    self.pg_nmos_pdk_model,
                    self.model_dict,
                    self.pd_width, 
                    self.pu_width,
                    self.pg_width, 
                    self.length,
                    w_rc=self.w_rc,
                    pi_res=self.pi_res, 
                    pi_cap=self.pi_cap,
                    suffix=f'_{row}_{col}',  # 关键：传入坐标后缀
                    param_sweep=self.param_sweep
                )

                # 2. 将此独立定义的单元子电路添加到阵列工厂中
                self.subcircuit(subckt_9t_cell)

                # 3. 按照 9T 的拓扑结构进行 X 实例连接
                # 注意：9T 节点顺序依次为 VDD, VSS, BL, WWLA, WWLB, WL
                self.X(
                    subckt_9t_cell.name,      # 实例名 (包含坐标后缀)
                    subckt_9t_cell.name,      # 子电路定义名 (包含坐标后缀)
                    self.NODES[0],            # VDD (全局)
                    self.NODES[1],            # VSS (全局)
                    f'BL{col}',               # 对应列的位线
                    f'WWLA{row}',             # 对应行的写字线 A
                    f'WWLB{row}',             # 对应行的写字线 B
                    f'WL{row}'                # 对应行的读字线
                )

        if not self.param_sweep:
            print(f"[DEBUG] 9T Yield Array {num_rows}x{num_cols} initialized.")

# if __name__ == '__main__':
#     pdk_path = 'model_lib/models.spice'
#     nmos_model_name = 'NMOS_VTG'
#     pmos_model_name = 'PMOS_VTG'
#     pd_width=0.205e-6
#     pu_width=0.09e-6
#     pg_width=0.135e-6
#     length=50e-9

# #     # bc = SRAM_6T_Cell_for_Yield(
# #     #     nmos_model_name, pmos_model_name,
# #     #     pd_width=0.1e-6, pu_width=0.2e-6, pg_width=1.5e-6, length=45e-9,
# #     #     suffix='_0_0', disconnect=True,
# #     # )
# #     # print(bc)

#     array = Sram6TCoreForYield(
#         2, 2,
#         nmos_model_name, pmos_model_name,
#         pd_width=pd_width, pu_width=pu_width, pg_width=pg_width, length=length,
#         w_rc=True, pi_res=100 @ u_Ohm, pi_cap=0.010 @ u_pF
#     )
#     print(array)
