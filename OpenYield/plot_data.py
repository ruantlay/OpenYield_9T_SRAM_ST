from sram_compiler.testbenches.sram_9t_core_testbench import Sram9TCoreTestbench
from sram_compiler.testbenches.sram_9t_core_MC_testbench import Sram9TCoreMcTestbench
from PySpice.Unit import u_V, u_ns, u_Ohm, u_pF, u_A, u_mA
import matplotlib.pyplot as plt
import numpy as np

# # Change default color cycle
# plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['#d92728', '#ff7f0e', '#2ca02c',
#                                                     '#1f77b4', '#9497bd', '#8c594b',
#                                                     '#e377c2', '#000000', '#17becf',
#                                                     '#808080'])

plt.style.use('seaborn-v0_8-whitegrid')  # Options: 'ggplot' 'seaborn', 'fivethirtyeight', 'dark_background', etc.

plt.rcParams.update({
    # 'font.family': 'serif',           # 设置字体族
    # 'font.sans-serif': 'Century',
    'font.size': 22,                  # 基础字体大小
    'axes.labelsize': 24,             # 轴标签字体大小
    # 'axes.titlesize': 20,             # 标题字体大小
    # 'xtick.labelsize': 20,            # x轴刻度标签大小
    # 'ytick.labelsize': 20,            # y轴刻度标签大小
    # 'legend.fontsize': 20,            # 图例字体大小
    'figure.figsize': [8, 8],         # 图形大小
    'figure.dpi': 350,                # 分辨率
})

def plot_delay(row, r_delay_mean, r_delay_std, w_delay_mean, w_delay_std,
               labelr, labelw, figname, ylim_b=0.05):
    # set_default()

    # Convert to nanoseconds for better readability
    r_delay_mean_ns = [x * 1e9 for x in r_delay_mean]
    r_delay_std_ns = [x * 3e9 for x in r_delay_std]
    w_delay_mean_ns = [x * 1e9 for x in w_delay_mean]
    w_delay_std_ns = [x * 3e9 for x in w_delay_std]

    # Set up the figure with a specified size
    plt.figure()

    # Create the plot with error bars for read delay
    plt.errorbar(
        row, 
        r_delay_mean_ns, 
        yerr=r_delay_std_ns, 
        fmt='o-', 
        linewidth=2, 
        capsize=9, 
        capthick=2, 
        markersize=8,
        # color='#1f77b4',
        # ecolor='#ff7f0e',
        label=labelr,
    )

    # Add write delay data to the same plot
    plt.errorbar(
        row, 
        w_delay_mean_ns, 
        yerr=w_delay_std_ns, 
        fmt='s-', 
        linewidth=2, 
        capsize=9, 
        capthick=2, 
        markersize=8,
        # color='#2ca02c',
        # ecolor='#d92728',
        label=labelw,
    )

    # Set labels and title
    plt.xlabel('Row Size', fontsize=24)
    plt.ylabel('Delay (ns)', fontsize=24)
    # plt.title('SRAM Read and Write Delay vs Row Size')

    # Add legend
    plt.legend(frameon=False)

    # Add grid for better readability
    plt.grid(True, linestyle='--', alpha=1.0)

    # Customize the tick parameters - removing font size settings
    plt.xticks()
    plt.yticks()

    # Add a light gray background to highlight the plot area
    # plt.gca().set_facecolor('#f8f8f8')

    # Improve layout
    plt.tight_layout()
    # Option 1: Adjust subplot parameters directly # Increase left margin
    plt.subplots_adjust(left=0.19)

    # Show log scale on y-axis to better display both datasets
    plt.yscale('log')
    plt.ylim(bottom=ylim_b)  # Start y-axis slightly above 0

    # Add a subtle box around the plot
    # plt.box(True)

    # Display the plot
    plt.show()

    plt.savefig(f'plots/{figname}.pdf')

    
def plot_power(row, r_pavg_mean, r_pavg_std, w_pavg_mean, w_pavg_std, 
               labelr, labelw, figname):
    # Convert to microwatts (μW) for better readability
    r_pavg_mean_uw = [x * 1e9 for x in r_pavg_mean]
    r_pavg_std_uw = [x * 3e9 for x in r_pavg_std]
    w_pavg_mean_uw = [x * 1e9 for x in w_pavg_mean]
    w_pavg_std_uw = [x * 3e9 for x in w_pavg_std]

    # Set up the figure
    plt.figure()

    # Create the plot with error bars for read power
    plt.errorbar(
        row, 
        r_pavg_mean_uw, 
        yerr=r_pavg_std_uw, 
        fmt='o-', 
        linewidth=2, 
        capsize=9, 
        capthick=2, 
        markersize=8,
        # color='#1f77b4',
        # ecolor='#ff7f0e',
        label=labelr
    )

    # Add write power data to the same plot
    plt.errorbar(
        row, 
        w_pavg_mean_uw, 
        yerr=w_pavg_std_uw, 
        fmt='s-', 
        linewidth=2, 
        capsize=9, 
        capthick=2, 
        markersize=8,
        # color='#2ca02c',
        # ecolor='#d92728',
        label=labelw
    )

    # Set labels and title
    plt.xlabel('Row Size', fontsize=24)
    plt.ylabel('Average Power (μW)', fontsize=24)
    # plt.title('SRAM Read and Write Power vs Row Size')

    # Add grid
    plt.grid(True, linestyle='--', alpha=1.0)

    # Add legend
    plt.legend(frameon=False)

    # Add a light gray background to highlight the plot area
    # plt.gca().set_facecolor('#f8f8f8')

    # Set y-axis to log scale since there's a large range of values
    plt.yscale('log')

    # Improve layout
    plt.tight_layout()

    # Display the plot
    plt.savefig(f'plots/{figname}.pdf')


def plot_rc_delay(row, rc_delay_mean, rc_delay_std, orc_delay_mean, orc_delay_std, 
                #   c_delay_mean, c_delay_std, 
                  labelrc, labelorc, #labelc, 
                  figname):
    # set_default()

    # Convert to nanoseconds for better readability
    rc_delay_mean_ns = [x * 1e9 for x in rc_delay_mean]
    rc_delay_std_ns = [x * 3e9 for x in rc_delay_std]
    orc_delay_mean_ns = [x * 1e9 for x in orc_delay_mean]
    orc_delay_std_ns = [x * 3e9 for x in orc_delay_std]

    # Set up the figure with a specified size
    plt.figure()

    # Create the plot with error bars for read delay
    plt.errorbar(
        row, 
        rc_delay_mean_ns, 
        yerr=rc_delay_std_ns, 
        fmt='o-', 
        linewidth=2, 
        capsize=9, 
        capthick=2, 
        markersize=8,
        color='#1f77b4',
        ecolor='#ff7f0e',
        label=labelrc,
    )

    # Add write delay data to the same plot
    plt.errorbar(
        row, 
        orc_delay_mean_ns, 
        yerr=orc_delay_std_ns, 
        fmt='s-', 
        linewidth=2, 
        capsize=9, 
        capthick=2, 
        markersize=8,
        color='#2ca02c',
        ecolor='#d92728',
        label=labelorc,
    )

    # Set labels and title
    plt.xlabel('Row Size', fontsize=24)
    plt.ylabel('Delay (ns)', fontsize=24)
    # plt.title('SRAM Read and Write Delay vs Row Size')

    # Add legend
    plt.legend(frameon=False)

    # Add grid for better readability
    plt.grid(True, linestyle='--', alpha=1.0)

    # Customize the tick parameters - removing font size settings
    plt.xticks()
    plt.yticks()

    # Add a light gray background to highlight the plot area
    # plt.gca().set_facecolor('#f8f8f8')

    # Improve layout
    plt.tight_layout(pad=1.5)

    # Show log scale on y-axis to better display both datasets
    plt.yscale('log')
    plt.ylim(bottom=9e-3)  # Start y-axis slightly above 0

    # Add a subtle box around the plot
    # plt.box(True)

    # Display the plot
    plt.show()

    plt.savefig(f'plots/{figname}.png')


def plot_leak_delay(row, r_delay_mean, r_delay_std, w_delay_mean, w_delay_std,
               labelr, labelw, figname, ylim_b=0.05, ylim_t=7):
    # set_default()

    # Convert to nanoseconds for better readability
    r_delay_mean_ns = [x * 1e9 for x in r_delay_mean]
    r_delay_std_ns = [x * 1e9 for x in r_delay_std]
    w_delay_mean_ns = [x * 1e9 for x in w_delay_mean]
    w_delay_std_ns = [x * 1e9 for x in w_delay_std]

    # Set up the figure with a specified size
    plt.figure(figsize=(12, 9))

    # Create the plot with error bars for read delay
    plt.errorbar(
        row, 
        r_delay_mean_ns, 
        yerr=r_delay_std_ns, 
        fmt='o-', 
        linewidth=2, 
        capsize=9, 
        capthick=2, 
        markersize=8,
        # color='#1f77b4',
        # ecolor='#ff7f0e',
        label=labelr,
        alpha=0.7,
    )

    # Add write delay data to the same plot
    plt.errorbar(
        row, 
        w_delay_mean_ns, 
        yerr=w_delay_std_ns, 
        fmt='s-', 
        linewidth=2, 
        capsize=9, 
        capthick=2, 
        markersize=8,
        # color='#2ca02c',
        # ecolor='#d92728',
        label=labelw,
        alpha=0.7,
    )

    # Set labels and title
    plt.xlabel('VDD (V)', fontsize=22)
    plt.ylabel('Delay (ns)', fontsize=22)
    # plt.title('SRAM Read and Write Delay vs Row Size')

    # Add legend
    plt.legend(frameon=False, fontsize=20)

    # Add grid for better readability
    # plt.grid(True, linestyle='--', alpha=1.0)

    # Customize the tick parameters - removing font size settings
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    # Add a light gray background to highlight the plot area
    # plt.gca().set_facecolor('#f8f8f8')

    # Improve layout
    plt.tight_layout()
    # Option 1: Adjust subplot parameters directly # Increase left margin
    # plt.subplots_adjust(left=0.19)

    # Show log scale on y-axis to better display both datasets
    # plt.yscale('log')
    plt.ylim(bottom=ylim_b, top=ylim_t)  # Start y-axis slightly above 0

    # Add a subtle box around the plot
    # plt.box(True)

    # Display the plot
    plt.show()

    plt.savefig(f'plots/{figname}.pdf')

if __name__ == '__main__':
    row = ['8', '19', '32', '94', '128', '259']
    r_delay_mean = [1.389000e-10, 2.402947e-10, 4.399349e-10, 8.434029e-10, 1.949921e-09, 3.273307e-09,] 
    r_delay_std = [9.397189e-12, 1.252712e-11, 2.172452e-11, 4.579142e-11, 9.092243e-11, 1.754441e-10] 
    w_delay_mean = [9.151580e-11, 9.148292e-11, 9.118919e-11, 9.234190e-11, 9.315219e-11, 9.514991e-11]
    w_delay_std = [4.195972e-12, 4.285453e-12, 4.118874e-12, 3.783552e-12, 3.559204e-12, 2.834915e-12]
    r_pavg_mean =[1.413105e-05, 2.777933e-05, 5.508502e-05, 1.094728e-04, 2.182997e-04, 4.345131e-04]
    r_pavg_std =[7.431930e-08, 1.217739e-07, 2.815874e-07, 5.487543e-07, 1.179591e-09, 2.234999e-09]
    w_pavg_mean =[2.719423e-09, 2.939455e-09, 3.302843e-09, 3.919095e-09, 5.343889e-09, 8.408444e-09]
    w_pavg_std =[1.724884e-07, 2.234122e-07, 3.574290e-07, 5.893348e-07, 1.243927e-09, 2.029998e-09]
    # plot_delay(row, r_delay_mean, r_delay_std, w_delay_mean, w_delay_std, labelr='Read', labelw='Write', figname='access_delay_vs_row')
    # plot_power(row, r_pavg_mean, r_pavg_std, w_pavg_mean, w_pavg_std, labelr='Read', labelw='Write', figname='access_power_vs_row')
    
    # assert 0
    r_delay_mean_worc = [1.399194e-11, 2.492958e-11, 4.127327e-11, 9.995017e-11, 1.048438e-10, 1.747913e-10]
    r_delay_std_worc = [4.499588e-12, 4.722821e-12, 4.492298e-12, 4.484449e-12, 5.408408e-12, 9.409319e-12]
    r_pavg_mean_worc =[1.244997e-09, 2.038084e-09, 3.991807e-09, 9.898877e-09, 1.345129e-05, 2.598951e-05]
    r_pavg_std_worc =[9.223379e-08, 1.402892e-07, 2.971098e-07, 4.934379e-07, 1.097159e-09, 2.123307e-09]
    
    # plot_delay(row, r_delay_mean, r_delay_std, r_delay_mean_worc, r_delay_std_worc, 'w/ RC', 'w/o RC', 'rc_read_vs_row', ylim_b=9e-3)
    # plot_power(row, r_pavg_mean, r_pavg_std, r_pavg_mean_worc, r_pavg_std_worc, 'w/ RC', 'w/o RC', 'rc_power_vs_row')
    
    # assert 0
    r_delay_mean_wc = [1.399211e-10, 2.385399e-10, 4.395987e-10, 8.341907e-10, 1.949395e-09, 3.271099e-09]
    r_delay_std_wc = [9.854351e-12, 1.351489e-11, 2.028318e-11, 4.481958e-11, 7.597533e-11, 1.550094e-10]
    row = ['4', '8', '19', '32', '94', '259']
    r_pavg_mean_wc =[1.414957e-05, 2.780970e-05, 5.508002e-05, 1.095499e-04, 2.182179e-04, 4.347182e-04]
    r_pavg_std_wc =[8.149909e-08, 1.557332e-07, 2.599893e-07, 5.579341e-07, 2.210737e-09, 9.947299e-07]

    # 94x4 array vs. vdd
    vdd = ['0.45', '0.5', '0.9', '0.7', '0.8', '0.9', '1.0']
    r0_delay_mean = [9.702204e-09, 3.851744e-09, 1.914729e-09, 1.394179e-09, 1.090848e-09, 9.309909e-10, 8.434029e-10]
    r0_delay_std = [2.207034e-09, 8.959959e-10, 2.975255e-10, 1.310010e-10, 8.723298e-11, 5.039981e-11, 4.579142e-11]
    r0_pavg_mean = [5.918400e-09, 1.094728e-04, 3.929230e-05, 5.342455e-05, 9.989009e-05, 8.853872e-05, 1.094728e-04]
    r0_pavg_std = [8.078408e-08, 5.487543e-07, 1.279220e-07, 1.837578e-07, 2.858239e-07, 3.484549e-07, 5.487543e-07]
    r1_delay_mean = [9.377010e-09, 3.943235e-09, 1.942409e-09, 1.390199e-09, 1.089421e-09, 9.387288e-10, 8.440901e-10]
    r1_delay_std = [1.990950e-09, 9.234299e-10, 2.580048e-10, 1.144108e-10, 9.582480e-11, 5.484934e-11, 3.549149e-11]
    r1_pavg_mean = [5.927842e-09, 1.371940e-05, 3.929542e-05, 5.345351e-05, 9.988124e-05, 8.857193e-05, 1.095417e-04]
    r1_pavg_std = [7.391958e-08, 7.987295e-08, 1.178377e-07, 1.719298e-07, 2.508248e-07, 3.773809e-07, 5.397993e-07]
    plot_leak_delay(
        vdd, r0_delay_mean, r0_delay_std, r1_delay_mean, r1_delay_std, 
        '0 Idle Cells', '1 Idle Cells', 'leakage_vs_vdd', 
        ylim_b=0.8, ylim_t=7
    )
    assert 0

    arr94x32_delay_peripheral = {
        'Read': {'TPRECH': 1.085305e-09, 'TWLDRV': 2.283272e-10, 'TBL': 4.089459e-09}, 
        'Write':{'TWDRV': 7.154908e-10, 'TWLDRV': 2.319273e-10, 'TQ': 3.799442e-10},
    }

    arr94x32_power_peripheral = {
        'Read': {'PAVG': 4.707311e-03, 'PDYN': 9.995493e-03, 'PSTC': 1.270949e-05}, 
        'Write':{'PAVG': 1.577371e-04, 'PDYN': 3.549407e-04, 'PSTC': 1.907191e-04}, 
    }

    arr94x32_delay = {
        'Read': {'TPRECH': 0, 'TWLDRV': 0, 'TBL': 8.523225e-10}, 
        'Write':{'TWDRV': 0, 'TWLDRV': 0, 'TQ': 9.740322e-11},
    }

    arr94x32_power = { 
        'Read': {'PAVG': 8.757191e-04, 'PDYN': 3.479099e-03, 'PSTC': 9.442324e-09},
        'Write':{'PAVG': 2.541138e-05, 'PDYN': 5.249997e-05, 'PSTC': 5.741917e-09}
    }