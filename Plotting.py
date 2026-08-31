import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Patch
from pathlib import Path

def plottingFP2050():
    cat_order = ['Kerosene', 'Hydrogen', 'Batteries', 'Kerosene and Hydrogen', 'Kerosene and Batteries', 'Hydrogen and Batteries', 'Kerosene, Hydrogen, and Batteries']

    data_dir = Path("DATA")
    def load_list(filename, name):
        filename = data_dir / Path(filename).with_suffix(".json")
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[name]

    file_name = "FP2050"

    rewards_random_avg_50 = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_50 = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_50 = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_50 = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_50 = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_50 = load_list(file_name, "rewards_model_v6")

    file_name = "CMAES2050"
    rewards_cmaes = load_list(file_name, "rewards_model_v2")

    file_name = "10CMAES2050"
    rewards_10cmaes = load_list(file_name, "rewards_model_v2")

    case2050 = (rewards_random_avg_50, rewards_model_v2_50, rewards_model_v3_50, rewards_model_v4_50, rewards_model_v5_50, rewards_model_v6_50, rewards_10cmaes, rewards_cmaes)

    def plot_single_case(cat_order, case_data):
        fig = plt.figure(figsize=(10, 10), constrained_layout=True)
        gs = fig.add_gridspec(nrows=3, ncols=1, height_ratios=[1.2, 10, 1.2])

        top_leg_ax = fig.add_subplot(gs[0, 0])
        ax = fig.add_subplot(gs[1, 0])
        leg_ax = fig.add_subplot(gs[2, 0])

        top_leg_ax.set_axis_off()
        leg_ax.set_axis_off()

        # 2. Configuration (Colors and Abbreviations)
        model_labels = [r'$0$', r'$1 \cdot 10^4$', r'$3 \cdot 10^4$', r'$7 \cdot 10^4$', r'$1.5 \cdot 10^5$', r'$3 \cdot 10^5$', r'$1 \cdot 10^1$', r'$1 \cdot 10^3$']
        cmap = plt.get_cmap('tab10')
        model_colors = [cmap(i) for i in range(len(model_labels))]

        pastel_cmap = plt.get_cmap('Pastel1')
        bg_colors = [pastel_cmap(0), pastel_cmap(1), pastel_cmap(2)]

        abbr = {
            'Kerosene': 'CJF',
            'Hydrogen': r'H$_2$',
            'Batteries': 'BAT',
            'Kerosene and Hydrogen': r'CJF & H$_2$',
            'Kerosene and Batteries': 'CJF & BAT',
            'Hydrogen and Batteries': r'H$_2$ & BAT',
            'Kerosene, Hydrogen, and Batteries': r'CJF, H$_2$ & BAT',
            'FC': 'FC present',
            'NO FC': 'No FC present',
        }

        # 3. Process Data
        per_model = []
        for lbl, items in zip(model_labels, case_data):
            dct = {}
            for r, t, _, _ in items:
                r = float(r)
                if (r > -11) and np.isfinite(r):
                    dct.setdefault(t, []).append(r)
            per_model.append((lbl, dct))

        types_present = [t for t in cat_order if any(t in d for _, d in per_model)]

        max_data_len = 0
        min_data_len = float('inf')

        for m_idx, (lbl, dct) in enumerate(per_model):
            for t in types_present:
                data_len = len(dct.get(t, []))
                if data_len > 0:
                    if data_len > max_data_len:
                        max_data_len = data_len
                    if data_len < min_data_len:
                        min_data_len = data_len

        # 4. Plotting Logic
        gap_abs = 0.10
        base_width = 0.5
        min_box_width = 0.3
        row_gap_edge = 0.4

        cur_edge = 0.0
        y_centers = []

        for idx, t in enumerate(types_present):
            # Calculate vertical positioning
            gh = len(model_labels) * base_width + (len(model_labels) - 1) * gap_abs
            center = cur_edge + gh / 2.0 if idx == 0 else cur_edge + row_gap_edge + gh / 2.0
            y_centers.append(center)

            # Position each box within the group
            start = center - 0.5 * gh
            for m_idx, (lbl, dct) in enumerate(per_model):
                data = dct.get(t, [])
                if not data: continue

                pos = start + 0.5 * base_width + m_idx * (base_width + gap_abs)

                dynamic_height = min_box_width + (len(data) - min_data_len) * (base_width - min_box_width) / (max_data_len - min_data_len)
                bp = ax.boxplot([data], positions=[pos], vert=False, widths=[dynamic_height],
                           patch_artist=True, showcaps=True, whis=(5, 95), showfliers=False,
                           showmeans=True, meanline=True,
                           meanprops=dict(color='black', linewidth=1.2, linestyle='-'),
                           medianprops=dict(visible=False))

                for box in bp['boxes']:
                    box.set_facecolor(model_colors[m_idx])
                    box.set_edgecolor('black')
                    box.set_linestyle('-')  # Ensure border is solid
                    box.set_linewidth(1.0)  # Set standard width

                    if lbl == '1e3' or lbl == '1e1':
                        box.set_hatch('//')

            cur_edge = center + gh / 2.0

        ax.set_yticks(y_centers)
        ax.set_yticklabels([abbr.get(t, t) for t in types_present])
        ax.set_xlim(-10.1, 10.1)
        ax.invert_yaxis()  # Keep CJF at the top
        ax.tick_params(axis='y', rotation=45)

        # Background color zones
        ax.axvspan(-10.1, -5, facecolor=bg_colors[0], alpha=1, zorder=-1)
        ax.axvspan(-5, -1, facecolor=bg_colors[1], alpha=1, zorder=-1)
        ax.axvspan(-1, 10.1, facecolor=bg_colors[2], alpha=1, zorder=-1)

        # Top Labels
        top_box = FancyBboxPatch((0.0, 0.01), 0.999, 0.9, boxstyle="square,pad=0.",
                                 facecolor='lightgrey', alpha=0.2, edgecolor='black')
        top_leg_ax.add_patch(top_box)

        top_leg_ax.text(0.5, 0.65, "Design Feasibility", ha='center', fontsize=12)

        top_leg_ax.add_patch(plt.Rectangle((0.02, 0.15), 0.22, 0.4, facecolor=bg_colors[0], edgecolor='none'))
        top_leg_ax.text(0.072, 0.35, "Payload < 0", va='center', fontsize=12)

        top_leg_ax.add_patch(plt.Rectangle((0.26, 0.15), 0.18, 0.4, facecolor=bg_colors[1], edgecolor='none'))
        top_leg_ax.text(0.2875, 0.35, "Infeasible CG", va='center', fontsize=12)

        top_leg_ax.add_patch(plt.Rectangle((0.46, 0.15), 0.52, 0.4, facecolor=bg_colors[2], edgecolor='none'))
        top_leg_ax.text(0.65, 0.35, "Feasible design", va='center', fontsize=12)

        # Box 1: RL
        box1_x, box1_w = 0., 0.735
        fancy_box1 = FancyBboxPatch((box1_x, 0.01), box1_w, 0.95, boxstyle="square,pad=0.",
                                    facecolor='lightgrey', alpha=0.2, edgecolor='black')
        leg_ax.add_patch(fancy_box1)

        xs_rl = np.linspace(.05, box1_x + box1_w - 0.11, 6)

        for i, x in enumerate(xs_rl):
            lbl = model_labels[i]
            color = model_colors[i]
            leg_ax.add_patch(
                plt.Rectangle((x - 0.015, 0.6), 0.03, 0.2, facecolor=color, edgecolor='black', linestyle='-',
                              linewidth=1.0))
            leg_ax.text(x + 0.02, 0.68, lbl, va='center', fontsize=12)
        leg_ax.text(box1_x + box1_w / 2, 0.2, "Number of training steps (RL)", ha='center', fontsize=12)

        # Box 2: CMA-ES
        box2_x, box2_w = 0.755, 0.2445
        fancy_box2 = FancyBboxPatch((box2_x, 0.01), box2_w, 0.95, boxstyle="square,pad=0.",
                                    facecolor='lightgrey', alpha=0.2, edgecolor='black')
        leg_ax.add_patch(fancy_box2)

        xs_cmaes = np.linspace(box2_x + 0.05, box2_x + box2_w - 0.09, 2)
        for i, x in enumerate(xs_cmaes):
            lbl = model_labels[i+6]
            color = model_colors[i+6]
            leg_ax.add_patch(plt.Rectangle((x - 0.015, 0.6), 0.03, 0.2, facecolor=color, edgecolor='black', linestyle='-',
                              linewidth=1.0, hatch='//'))
            leg_ax.text(x + 0.02, 0.68, lbl, va='center', fontsize=12)

        leg_ax.text(box2_x + box2_w / 2, 0.1, "Number of generations \n (CMA-ES)", ha='center', fontsize=12)

        #plt.show()
        plt.savefig("FP2050_new.pdf", format='pdf', bbox_inches='tight')

    plot_single_case(cat_order, case2050)

def plottingFP2050FC():
    cat_order = ['FC', 'NO FC']

    data_dir = Path("DATA")
    def load_list(filename, name):
        filename = data_dir / Path(filename).with_suffix(".json")
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[name]

    file_name = "FP2050FC"

    rewards_random_avg_50 = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_50 = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_50 = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_50 = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_50 = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_50 = load_list(file_name, "rewards_model_v6")

    file_name = "CMAES2050FC"
    rewards_cmaes = load_list(file_name, "rewards_model_v2")

    file_name = "10CMAES2050FC"
    rewards_10cmaes = load_list(file_name, "rewards_model_v2")

    case2050 = (rewards_random_avg_50, rewards_model_v2_50, rewards_model_v3_50, rewards_model_v4_50, rewards_model_v5_50, rewards_model_v6_50, rewards_10cmaes, rewards_cmaes)

    def plot_single_case(cat_order, case_data):
        fig = plt.figure(figsize=(10, 10), constrained_layout=True)
        gs = fig.add_gridspec(nrows=3, ncols=1, height_ratios=[1.2, 10, 1.2])

        top_leg_ax = fig.add_subplot(gs[0, 0])
        ax = fig.add_subplot(gs[1, 0])
        leg_ax = fig.add_subplot(gs[2, 0])

        top_leg_ax.set_axis_off()
        leg_ax.set_axis_off()

        # 2. Configuration (Colors and Abbreviations)
        model_labels = [r'$0$', r'$1 \cdot 10^4$', r'$3 \cdot 10^4$', r'$7 \cdot 10^4$', r'$1.5 \cdot 10^5$', r'$3 \cdot 10^5$', r'$1 \cdot 10^1$', r'$1 \cdot 10^3$']
        cmap = plt.get_cmap('tab10')
        model_colors = [cmap(i) for i in range(len(model_labels))]

        pastel_cmap = plt.get_cmap('Pastel1')
        bg_colors = [pastel_cmap(0), pastel_cmap(1), pastel_cmap(2)]

        abbr = {
            'Kerosene': 'CJF',
            'Hydrogen': r'H$_2$',
            'Batteries': 'BAT',
            'Kerosene and Hydrogen': r'CJF & H$_2$',
            'Kerosene and Batteries': 'CJF & BAT',
            'Hydrogen and Batteries': r'H$_2$ & BAT',
            'Kerosene, Hydrogen, and Batteries': r'CJF, H$_2$ & BAT',
            'FC': 'FC present',
            'NO FC': 'No FC present',
        }

        # 3. Process Data
        per_model = []
        for lbl, items in zip(model_labels, case_data):
            dct = {}
            for r, t, _, _ in items:
                r = float(r)
                if (r > -11) and np.isfinite(r):
                    dct.setdefault(t, []).append(r)
            per_model.append((lbl, dct))

        types_present = [t for t in cat_order if any(t in d for _, d in per_model)]

        max_data_len = 0
        min_data_len = float('inf')

        for m_idx, (lbl, dct) in enumerate(per_model):
            for t in types_present:
                data_len = len(dct.get(t, []))
                if data_len > 0:
                    if data_len > max_data_len:
                        max_data_len = data_len
                    if data_len < min_data_len:
                        min_data_len = data_len

        # 4. Plotting Logic
        gap_abs = 0.10
        base_width = 0.5
        min_box_width = 0.3
        row_gap_edge = 0.4

        cur_edge = 0.0
        y_centers = []

        for idx, t in enumerate(types_present):
            # Calculate vertical positioning
            gh = len(model_labels) * base_width + (len(model_labels) - 1) * gap_abs
            center = cur_edge + gh / 2.0 if idx == 0 else cur_edge + row_gap_edge + gh / 2.0
            y_centers.append(center)

            # Position each box within the group
            start = center - 0.5 * gh
            for m_idx, (lbl, dct) in enumerate(per_model):
                data = dct.get(t, [])
                if not data: continue

                pos = start + 0.5 * base_width + m_idx * (base_width + gap_abs)

                dynamic_height = min_box_width + (len(data) - min_data_len) * (base_width - min_box_width) / (max_data_len - min_data_len)
                bp = ax.boxplot([data], positions=[pos], vert=False, widths=[dynamic_height],
                           patch_artist=True, showcaps=True, whis=(5, 95), showfliers=False,
                           showmeans=True, meanline=True,
                           meanprops=dict(color='black', linewidth=1.2, linestyle='-'),
                           medianprops=dict(visible=False))

                for box in bp['boxes']:
                    box.set_facecolor(model_colors[m_idx])
                    box.set_edgecolor('black')
                    box.set_linestyle('-')  # Ensure border is solid
                    box.set_linewidth(1.0)  # Set standard width

                    if lbl == '1e3' or lbl == '1e1':
                        box.set_hatch('//')

            cur_edge = center + gh / 2.0

        # 5. Aesthetics and Zones
        ax.set_yticks(y_centers)
        ax.set_yticklabels([abbr.get(t, t) for t in types_present])
        ax.set_xlim(-10.1, 10.1)
        ax.invert_yaxis()  # Keep CJF at the top
        ax.tick_params(axis='y', rotation=45)

        # Background color zones
        ax.axvspan(-10.1, -5, facecolor=bg_colors[0], alpha=1, zorder=-1)
        ax.axvspan(-5, -1, facecolor=bg_colors[1], alpha=1, zorder=-1)
        ax.axvspan(-1, 10.1, facecolor=bg_colors[2], alpha=1, zorder=-1)

        # Top Labels
        top_box = FancyBboxPatch((0.0, 0.01), 0.999, 0.9, boxstyle="square,pad=0.",
                                 facecolor='lightgrey', alpha=0.2, edgecolor='black')
        top_leg_ax.add_patch(top_box)

        top_leg_ax.text(0.5, 0.65, "Design Feasibility", ha='center', fontsize=12)

        top_leg_ax.add_patch(plt.Rectangle((0.02, 0.15), 0.22, 0.4, facecolor=bg_colors[0], edgecolor='none'))
        top_leg_ax.text(0.072, 0.35, "Payload < 0", va='center', fontsize=12)

        top_leg_ax.add_patch(plt.Rectangle((0.26, 0.15), 0.18, 0.4, facecolor=bg_colors[1], edgecolor='none'))
        top_leg_ax.text(0.2875, 0.35, "Infeasible CG", va='center', fontsize=12)

        top_leg_ax.add_patch(plt.Rectangle((0.46, 0.15), 0.52, 0.4, facecolor=bg_colors[2], edgecolor='none'))
        top_leg_ax.text(0.65, 0.35, "Feasible design", va='center', fontsize=12)

        # Box 1: RL
        box1_x, box1_w = 0., 0.735
        fancy_box1 = FancyBboxPatch((box1_x, 0.01), box1_w, 0.95, boxstyle="square,pad=0.",
                                    facecolor='lightgrey', alpha=0.2, edgecolor='black')
        leg_ax.add_patch(fancy_box1)

        xs_rl = np.linspace(.05, box1_x + box1_w - 0.11, 6)
        for i, x in enumerate(xs_rl):
            lbl = model_labels[i]
            color = model_colors[i]
            leg_ax.add_patch(
                plt.Rectangle((x - 0.015, 0.6), 0.03, 0.2, facecolor=color, edgecolor='black', linestyle='-',
                              linewidth=1.0))
            leg_ax.text(x + 0.02, 0.68, lbl, va='center', fontsize=12)
        leg_ax.text(box1_x + box1_w / 2, 0.2, "Number of training steps (RL)", ha='center', fontsize=12)

        # Box 2: CMA-ES
        box2_x, box2_w = 0.755, 0.2445
        fancy_box2 = FancyBboxPatch((box2_x, 0.01), box2_w, 0.95, boxstyle="square,pad=0.",
                                    facecolor='lightgrey', alpha=0.2, edgecolor='black')
        leg_ax.add_patch(fancy_box2)

        xs_cmaes = np.linspace(box2_x + 0.05, box2_x + box2_w - 0.09, 2)
        for i, x in enumerate(xs_cmaes):
            lbl = model_labels[i+6]
            color = model_colors[i+6]
            leg_ax.add_patch(plt.Rectangle((x - 0.015, 0.6), 0.03, 0.2, facecolor=color, edgecolor='black', linestyle='-',
                              linewidth=1.0, hatch='//'))
            leg_ax.text(x + 0.02, 0.68, lbl, va='center', fontsize=12)

        leg_ax.text(box2_x + box2_w / 2, 0.1, "Number of generations \n (CMA-ES)", ha='center', fontsize=12)

        #plt.show()
        plt.savefig("FP2050FC_new.pdf", format='pdf', bbox_inches='tight')

    plot_single_case(cat_order, case2050)

def breakdownsFP():
    size = 20
    plt.rcParams.update({
        'axes.titlesize': size,
        'axes.labelsize': size,
        'xtick.labelsize': size,
        'ytick.labelsize': size,
        'legend.fontsize': size,
    })

    RLFP2050 = {
        'CJF': 342.44495750000004,  #kg
        r'H$_2$': 2474.699167578125,  #kg
        'GT': 436.4106432360743, #kg
        'FC': 1540.088986013986, #kg
        'EM': (34.45235853909465+ 61.380390946502054), #kg
        'PM': 56.469929487179485, #kg
        #'OEM - Powertrain': 12543, #kg
        'Payload': 5511.05356669904,  # kg
        'Payload_r': -4.643489354600661, # kg
        'ERF': 41.9853121588667,  # mW/m^2
        'CO2': 1052.0670083194445, # -
        'NOX': 3.117908900483896, #-
    }

    CMAESFP2050 = {
        'CJF': 491.5490021601214,  #kg
        r'H$_2$': 2298.086045580864,  #kg
        'GT': 539.9667440318302, #kg
        'FC': 1249.2935314685315, #kg
        'EM': 72.78291666666667, #kg
        'PM': 45.80742948717948, #kg
        #'OEM - Powertrain': 12543, #kg
        'Payload': 5759.514330604807,  # kg
        'Payload_r': 0, # kg
        'ERF': 55.21722879889349,  # mW/m^2
        'CO2': 1510.1477677474838,  # -
        'NOX': 3.1659722921479916,  # -
    }

    data_list = [RLFP2050, CMAESFP2050]
    titles = [r'(a) Optimal design found by RL', '(b) Optimal design found by CMA-ES']

    # 2. Setup Consistent Colors based on DICTIONARY ORDER
    master_keys = [k for k in RLFP2050.keys() if k != 'ERF' and k != 'CO2' and k != 'NOX']
    cmap = plt.get_cmap('Paired')
    colors = [cmap(i) for i in range(8)]
    key_color_map = {key: colors[i % len(colors)] for i, key in enumerate(master_keys)}

    def arrange_labels(ax, wedges, texts, threshold_degrees=20, start_length=1.1):

        current_length = start_length

        i = 0
        j = 0
        for w, t in zip(wedges, texts):
            if not t.get_text():
                continue
            # Standard geometry calculations
            angle = w.theta2 - w.theta1
            theta = (w.theta1 + w.theta2) / 2.0
            center = w.center
            r = w.r

            clock_angle = (90 - theta) % 360

            if angle > threshold_degrees:
                inner_r = r * 0.6
                x_in = inner_r * np.cos(np.deg2rad(theta)) + center[0]
                y_in = inner_r * np.sin(np.deg2rad(theta)) + center[1]
                if clock_angle < 140 and clock_angle > 135:
                    x_in += 0.075
                t.set_position((x_in, y_in))
                t.set_horizontalalignment('center')
                t.set_verticalalignment('center')

            else:
                if clock_angle > 270 or clock_angle < 90:
                    if i == 0:
                        current_length = start_length
                    else:
                        current_length += 0.1
                    i+=1
                elif clock_angle > 90 and clock_angle < 150:
                    current_length = start_length
                elif clock_angle >155 and clock_angle < 180:
                    if j == 0:
                        current_length = start_length
                    else:
                        current_length += 0.2
                    j+=1
                else:
                    if j == 0:
                        current_length = start_length + 0.2
                    else:
                        current_length = start_length
                    j+=1

                x_out = (r * current_length) * np.cos(np.deg2rad(theta)) + center[0]
                y_out = (r * current_length) * np.sin(np.deg2rad(theta)) + center[1]

                t.set_position((x_out, y_out))
                t.set_verticalalignment('center')

                if x_out > 0:
                    t.set_horizontalalignment('left')
                else:
                    t.set_horizontalalignment('right')

                # Draw line
                x_edge = r * np.cos(np.deg2rad(theta)) + center[0]
                y_edge = r * np.sin(np.deg2rad(theta)) + center[1]
                ax.annotate('', xy=(x_edge, y_edge), xytext=(x_out, y_out),
                            arrowprops=dict(arrowstyle='-', color='black', lw=1))

    # 3. Create the Plot
    fig, axes = plt.subplots(1, 2, figsize=(18, 9))

    for ax, d, title in zip(axes, data_list, titles):
        filtered_data = {k: v for k, v in d.items() if k != 'ERF' and k != 'CO2' and k != 'NOX' and v > 0}

        sorted_items = sorted(filtered_data.items(), key=lambda x: master_keys.index(x[0]))

        labels = [k for k, v in sorted_items]
        sizes = [v for k, v in sorted_items]

        chart_colors = []
        for k in labels:
            if k == 'Payload_r':
                chart_colors.append((0, 0, 0, 0))
            else:
                chart_colors.append(key_color_map[k])

        plot_labels = [f"{v:.0f} kg" if k != 'Payload_r' else "" for k, v in sorted_items]

        # Initialize Pie
        wedges, texts = ax.pie(
            sizes,
            labels=plot_labels,
            colors=chart_colors,
            startangle=90,
            counterclock=False,
            labeldistance=1.2,
            wedgeprops={'edgecolor': 'black', 'linewidth': 1, 'antialiased': True}
        )

        for i, k in enumerate(labels):
            if k == 'Payload_r':
                wedges[i].set_edgecolor('none')
                wedges[i].set_linewidth(0)

        arrange_labels(ax, wedges, texts, threshold_degrees=42)

        ax.set_title(title, pad=20)

        co2 = d.get('CO2', 0)
        payload = d.get('Payload', 0)
        nox = d.get('NOX', 0)

        co2_pp_baseline = 8080.78997925 / 6807.853228990148
        nox_pp_baseline = 31660.564192850526/1000


        co2_goal = 100 - (co2 / payload) / co2_pp_baseline * 100
        nox_goal = 100 - nox / nox_pp_baseline * 100

        mtom_val = (23000 - d.get('Payload_r', 0))/1000

        ax.text(0.5, -0.08, f"CO$_2$ emissions per pkm reduction= {co2_goal:.1f}%",
                transform=ax.transAxes,
                ha='center', va='top', fontsize=size, color='black')

        ax.text(0.5, -0.16, f"NO$_x$ emissions reduction= {nox_goal:.1f}%",
                transform=ax.transAxes,
                ha='center', va='top', fontsize=size, color='black')

        ax.text(0.5, -0.24, f"MTOM = {mtom_val:.2f} $\cdot 10^{{3}}$ kg",
                transform=ax.transAxes,
                ha='center', va='top', fontsize=size, color='black')

    # 4. Global Legend
    legend_handles = []
    for key in master_keys:
        is_present = any(d.get(key, 0) > 0 for d in data_list)
        if is_present and key != 'Payload_r':
            patch = mpatches.Patch(facecolor=key_color_map[key], label=key, edgecolor='black', linewidth=1)
            legend_handles.append(patch)

    fig.legend(
        handles=legend_handles,
        loc='lower center',
        ncol=len(legend_handles),
        bbox_to_anchor=(0.5, 0),
        frameon=False,
    )

    plt.subplots_adjust(left=0.03, bottom=0.275, right=0.97, top=0.85)
    plt.savefig("MBDFP50.pdf", format='pdf', bbox_inches='tight')
    #plt.show()

if __name__ == '__main__':
    #plottingFP2050()
    #plottingFP2050FC()
    #breakdownsFP()