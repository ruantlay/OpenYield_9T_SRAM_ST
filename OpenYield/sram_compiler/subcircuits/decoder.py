from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Unit import u_Ohm, u_pF
from .base_subcircuit import BaseSubcircuit
from math import ceil, log2
from .standard_cell import PNAND2, PNAND3, PINV

# ======================= AND3 =======================
class AND3(BaseSubcircuit):
    NAME = "AND3"
    NODES = ('VDD', 'VSS', 'A', 'B', 'C', 'Z')

    def __init__(self, nmos_model_name, pmos_model_name,
                 base_nand_pmos_width=0.27e-6, base_nand_nmos_width=0.18e-6,
                 base_inv_pmos_width=0.27e-6, base_inv_nmos_width=0.09e-6,
                 length=0.05e-6, w_rc=False, pi_res=100 @ u_Ohm,
                 pi_cap=0.001 @ u_pF, sweep=False,
                 pmos_model_choices='PMOS_VTG', nmos_model_choices='NMOS_VTG'):

        super().__init__(nmos_model_name, pmos_model_name,
                         base_nand_nmos_width, base_nand_pmos_width, length,
                         w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap)
        self.sweep = sweep
        self.pmos_model_choices = pmos_model_choices
        self.nmos_model_choices = nmos_model_choices

        self.nand_gate = PNAND3(nmos_model_name, pmos_model_name,
                                base_nmos_width=base_nand_nmos_width,
                                base_pmos_width=base_nand_pmos_width,
                                length=length,
                                sweep=self.sweep,
                                pmos_model_choices=self.pmos_model_choices,
                                nmos_model_choices=self.nmos_model_choices)
        self.subcircuit(self.nand_gate)

        self.inv_driver = PINV(nmos_model_name, pmos_model_name,
                               base_nmos_width=base_inv_nmos_width,
                               base_pmos_width=base_inv_pmos_width,
                               length=length,
                               sweep=self.sweep,
                               pmos_model_choices=self.pmos_model_choices,
                               nmos_model_choices=self.nmos_model_choices)
        self.subcircuit(self.inv_driver)

        self.add_and3_components()

    def add_and3_components(self):
        a_node = 'A' if not self.w_rc else self.add_rc_networks_to_node('A', num_segs=2)
        b_node = 'B' if not self.w_rc else self.add_rc_networks_to_node('B', num_segs=2)
        c_node = 'C' if not self.w_rc else self.add_rc_networks_to_node('C', num_segs=2)
        zb_node = 'zb_int' if not self.w_rc else self.add_rc_networks_to_node('zb_int', num_segs=2)
        z_node = 'Z' if not self.w_rc else self.add_rc_networks_to_node('Z', num_segs=2)

        self.X('PNAND3', self.nand_gate.name, 'VDD', 'VSS', a_node, b_node, c_node, zb_node)
        self.X('PINV', self.inv_driver.name, 'VDD', 'VSS', zb_node, z_node)

# ======================= AND2 =======================
class AND2(BaseSubcircuit):
    NAME = "AND2"
    NODES = ('VDD', 'VSS', 'A', 'B', 'Z')

    def __init__(self, nmos_model_name, pmos_model_name,
                 base_nand_pmos_width=0.27e-6, base_nand_nmos_width=0.18e-6,
                 base_inv_pmos_width=0.27e-6, base_inv_nmos_width=0.09e-6,
                 length=0.05e-6, w_rc=False, pi_res=100 @ u_Ohm,
                 pi_cap=0.001 @ u_pF, sweep=False,
                 pmos_model_choices='PMOS_VTG', nmos_model_choices='NMOS_VTG'):

        super().__init__(nmos_model_name, pmos_model_name,
                         base_nand_nmos_width, base_nand_pmos_width, length,
                         w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap)
        self.sweep = sweep
        self.pmos_model_choices = pmos_model_choices
        self.nmos_model_choices = nmos_model_choices

        self.nand_gate = PNAND2(nmos_model_name, pmos_model_name,
                                base_nmos_width=base_nand_nmos_width,
                                base_pmos_width=base_nand_pmos_width,
                                length=length,
                                sweep=self.sweep,
                                pmos_model_choices=self.pmos_model_choices,
                                nmos_model_choices=self.nmos_model_choices)
        self.subcircuit(self.nand_gate)

        self.inv_driver = PINV(nmos_model_name, pmos_model_name,
                               base_nmos_width=base_inv_nmos_width,
                               base_pmos_width=base_inv_pmos_width,
                               length=length,
                               sweep=self.sweep,
                               pmos_model_choices=self.pmos_model_choices,
                               nmos_model_choices=self.nmos_model_choices)
        self.subcircuit(self.inv_driver)

        self.add_and3_components()

    def add_and3_components(self):
        a_node = 'A' if not self.w_rc else self.add_rc_networks_to_node('A', num_segs=2)
        b_node = 'B' if not self.w_rc else self.add_rc_networks_to_node('B', num_segs=2)
        zb_node = 'zb_int' if not self.w_rc else self.add_rc_networks_to_node('zb_int', num_segs=2)
        z_node = 'Z' if not self.w_rc else self.add_rc_networks_to_node('Z', num_segs=2)

        self.X('PNAND2', self.nand_gate.name, 'VDD', 'VSS', a_node, b_node, zb_node)
        self.X('PINV', self.inv_driver.name, 'VDD', 'VSS', zb_node, z_node)

# ======================= DECODER3_8 =======================
class DECODER3_8(BaseSubcircuit):
    NAME = "DECODER3_8"

    def __init__(self, nmos_model_name, pmos_model_name,
                 base_inv_pmos_width=0.27e-6, base_inv_nmos_width=0.09e-6,
                 base_nand_pmos_width=0.27e-6, base_nand_nmos_width=0.18e-6,
                 length=0.05e-6, w_rc=False, pi_res=100 @ u_Ohm,
                 pi_cap=0.001 @ u_pF, sweep=False,
                 pmos_model_choices='PMOS_VTG', nmos_model_choices='NMOS_VTG'):

        super().__init__(nmos_model_name, pmos_model_name,
                         base_nand_nmos_width, base_nand_pmos_width, length,
                         w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap)

        self.sweep = sweep
        self.pmos_model_choices = pmos_model_choices
        self.nmos_model_choices = nmos_model_choices

        # Inverters for A0-A2
        self.inv_A0 = PINV(nmos_model_name, pmos_model_name, sweep=self.sweep)
        self.inv_A1 = PINV(nmos_model_name, pmos_model_name, sweep=self.sweep)
        self.inv_A2 = PINV(nmos_model_name, pmos_model_name, sweep=self.sweep)
        self.subcircuit(self.inv_A0)
        self.subcircuit(self.inv_A1)
        self.subcircuit(self.inv_A2)

        # 8 AND3 gates and 8 AND2 gates
        self.and_gates = [AND3(nmos_model_name, pmos_model_name, sweep=self.sweep) for _ in range(8)]
        self.and_en_gates = [AND2(nmos_model_name, pmos_model_name, sweep=self.sweep) for _ in range(8)]
        for g in self.and_gates + self.and_en_gates:
            self.subcircuit(g)

        self.add_decoder_components()

    def add_decoder_components(self):
        # Connect inverters
        self.X('INV_A0', self.inv_A0.name, 'VDD', 'VSS', 'A0', 'A0b')
        self.X('INV_A1', self.inv_A1.name, 'VDD', 'VSS', 'A1', 'A1b')
        self.X('INV_A2', self.inv_A2.name, 'VDD', 'VSS', 'A2', 'A2b')

        input_combinations = [
            ('A0b', 'A1b', 'A2b'), ('A0b', 'A1b', 'A2'), ('A0b', 'A1', 'A2b'), ('A0b', 'A1', 'A2'),
            ('A0', 'A1b', 'A2b'), ('A0', 'A1b', 'A2'), ('A0', 'A1', 'A2b'), ('A0', 'A1', 'A2')
        ]

        for i in range(8):
            self.X(f'AND{i}', self.and_gates[i].NAME, 'VDD', 'VSS',
                   *input_combinations[i], f'WL{i}_pre')
            self.X(f'AND_EN{i}', self.and_en_gates[i].NAME, 'VDD', 'VSS',
                   f'WL{i}_pre', 'EN', f'WL{i}')

# ======================= DECODER_CASCADE =======================
class DECODER_CASCADE(BaseSubcircuit):
    NAME = "DECODER_CASCADE"

    def __init__(self, nmos_model_name, pmos_model_name, num_rows=16,
                 base_inv_pmos_width=0.27e-6, base_inv_nmos_width=0.09e-6,
                 base_nand_pmos_width=0.27e-6, base_nand_nmos_width=0.18e-6,
                 length=0.05e-6, w_rc=False, pi_res=100 @ u_Ohm,
                 pi_cap=0.001 @ u_pF, sweep=False,
                 pmos_model_choices='PMOS_VTG', nmos_model_choices='NMOS_VTG'):

        super().__init__(nmos_model_name, pmos_model_name,
                         base_nand_nmos_width, base_nand_pmos_width, length,
                         w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap)

        self.sweep = sweep
        self.num_rows = num_rows
        self.pmos_model_choices = pmos_model_choices
        self.nmos_model_choices = nmos_model_choices

        self.n_bits = ceil(log2(num_rows)) if num_rows > 1 else 1
        self.n_levels = ceil(self.n_bits / 3.0)

        level_groups = [0] * self.n_levels
        level_groups[self.n_levels - 1] = ceil(num_rows / 8.0)
        for level in range(self.n_levels - 2, -1, -1):
            level_groups[level] = ceil(level_groups[level + 1] / 8.0)
        self.level_groups = level_groups

        nodes = ['VDD', 'VSS'] + [f'A{i}' for i in range(self.n_bits)] + [f'WL{i}' for i in range(num_rows)]
        self.NODES = nodes

        self.decoders_by_level = []
        self.level_output_nodes = [[] for _ in range(self.n_levels)]

        for level in range(self.n_levels):
            level_decoders = []
            for decoder_idx in range(self.level_groups[level]):
                start_bit = 3 * (self.n_levels - level - 1)
                address_nodes = [f'A{start_bit+bit}' if 0 <= start_bit+bit < self.n_bits else 'VSS' for bit in range(3)]

                decoder = DECODER3_8(nmos_model_name, pmos_model_name,
                                     sweep=self.sweep,
                                     base_inv_pmos_width=base_inv_pmos_width,
                                     base_inv_nmos_width=base_inv_nmos_width,
                                     base_nand_pmos_width=base_nand_pmos_width,
                                     base_nand_nmos_width=base_nand_nmos_width,
                                     length=length, w_rc=w_rc)
                self.subcircuit(decoder)
                level_decoders.append(decoder)

                enable_signal = 'VDD' if level == 0 else self.level_output_nodes[level - 1][decoder_idx] if decoder_idx < len(self.level_output_nodes[level - 1]) else 'VSS'

                output_nodes = []
                for out_idx in range(8):
                    if level == self.n_levels - 1:
                        wl_idx = decoder_idx * 8 + out_idx
                        node_name = f'WL{wl_idx}' if wl_idx < num_rows else f'NC_{level}_{decoder_idx}_{out_idx}'
                    else:
                        node_name = f'EN_{level}_{decoder_idx}_{out_idx}'
                    output_nodes.append(node_name)

                self.level_output_nodes[level].extend(output_nodes)

                self.X(f'DEC_{level}_{decoder_idx}', decoder.NAME,
                       'VDD', 'VSS', enable_signal,
                       *address_nodes[::-1], *output_nodes)

            self.decoders_by_level.append(level_decoders)
