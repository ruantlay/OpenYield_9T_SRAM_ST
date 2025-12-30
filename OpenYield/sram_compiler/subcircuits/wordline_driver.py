from PySpice.Unit import u_Ohm, u_pF
from .base_subcircuit import BaseSubcircuit
from .standard_cell import PNAND2, PINV
class WordlineDriver(BaseSubcircuit):
    """
    针对 9T Schmitt-Trigger SRAM 优化的字线驱动器
    """
    NAME = "WORDLINEDRIVER"
    NODES = ('VDD', 'VSS', 'A', 'B', 'Z', 'WWLA', 'WWLB')

    def __init__(
        self,
        nmos_model_name,
        pmos_model_name,
        base_nand_pmos_width=0.27e-6,
        base_nand_nmos_width=0.18e-6,
        base_inv_pmos_width=0.27e-6,
        base_inv_nmos_width=0.09e-6,
        length=0.05e-6,
        *,
        w_rc=False,
        pi_res=100 @ u_Ohm,
        pi_cap=0.001 @ u_pF,
        num_cols=4,
        num_rows=None,
        sweep_wordlinedriver=False,
        pmos_model_choices=('PMOS_VTG',),
        nmos_model_choices=('NMOS_VTG',),
        **kwargs
    ):

        super().__init__(
            nmos_model_name,
            pmos_model_name,
            base_nand_nmos_width,
            base_nand_pmos_width,
            length,
            w_rc=w_rc,
            pi_res=pi_res,
            pi_cap=pi_cap,
        )

        self.num_cols = num_cols
        self.num_rows = num_rows
        self.sweep = sweep_wordlinedriver

        # 👉 drive_factor：用列数建模 WL 负载
        nand_drive = max(1.0, num_cols / 4)
        inv_drive  = max(2.0, num_cols / 2)

        # 1️⃣ 行选 NAND
        self.nand_gate = PNAND2(
            nmos_model_name=nmos_model_name,
            pmos_model_name=pmos_model_name,
            base_pmos_width=base_nand_pmos_width,
            base_nmos_width=base_nand_nmos_width,
            length=length,
            drive_factor=nand_drive,
            sweep=self.sweep,
            pmos_model_choices=pmos_model_choices,
            nmos_model_choices=nmos_model_choices,
            **kwargs
        )
        self.subcircuit(self.nand_gate)

        # 2️⃣ WL 驱动 INV
        self.inv_driver = PINV(
            nmos_model_name=nmos_model_name,
            pmos_model_name=pmos_model_name,
            base_pmos_width=base_inv_pmos_width,
            base_nmos_width=base_inv_nmos_width,
            length=length,
            drive_factor=inv_drive,
            sweep=self.sweep,
            pmos_model_choices=pmos_model_choices,
            nmos_model_choices=nmos_model_choices,
            **kwargs
        )
        self.subcircuit(self.inv_driver)

        self.add_driver_components()
    def add_driver_components(self):

        if self.w_rc:
            a_node = self.add_rc_networks_to_node('A', num_segs=2)
            b_node = self.add_rc_networks_to_node('B', num_segs=2)
            zb_node = self.add_rc_networks_to_node('WWLA', num_segs=2)
            z_node = self.add_rc_networks_to_node('Z', num_segs=2)
        else:
            a_node, b_node = 'A', 'B'
            zb_node = 'WWLA'
            z_node = 'Z'

        # NAND2: A, B -> WWLA
        self.X(
            self.nand_gate.NAME,
            self.nand_gate.NAME,
            'VDD', 'VSS',
            a_node, b_node, zb_node
        )

        # INV: WWLA -> Z
        self.X(
            self.inv_driver.NAME,
            self.inv_driver.NAME,
            'VDD', 'VSS',
            zb_node, z_node
        )

        # WWLB = Z
        self.R('short_z_wwlb', z_node, 'WWLB', 0.001 @ u_Ohm)
