import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from pathlib import Path


def plottingNominal():
    cat_order = ['Kerosene', 'Hydrogen', 'Batteries', 'Kerosene and Hydrogen', 'Kerosene and Batteries', 'Hydrogen and Batteries', 'Kerosene, Hydrogen, and Batteries']

    data_dir = Path("")
    def load_list(filename, name):
        filename = data_dir / Path(filename).with_suffix(".json")
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[name]

    file_name = "PAS2030"

    rewards_random_avg_30_pas = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_30_pas = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_30_pas = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_30_pas = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_30_pas = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_30_pas = load_list(file_name, "rewards_model_v6")

    file_name = "PAS2040"

    rewards_random_avg_40_pas = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_40_pas = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_40_pas = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_40_pas = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_40_pas = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_40_pas = load_list(file_name, "rewards_model_v6")

    file_name = "PAS2050"

    rewards_random_avg_50_pas = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_50_pas = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_50_pas = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_50_pas = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_50_pas = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_50_pas = load_list(file_name, "rewards_model_v6")

    file_name = "CARGO2030"

    rewards_random_avg_30_cargo = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_30_cargo = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_30_cargo = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_30_cargo = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_30_cargo = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_30_cargo = load_list(file_name, "rewards_model_v6")

    file_name = "CARGO2040"

    rewards_random_avg_40_cargo = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_40_cargo = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_40_cargo = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_40_cargo = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_40_cargo = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_40_cargo = load_list(file_name, "rewards_model_v6")

    file_name = "CARGO2050"

    rewards_random_avg_50_cargo = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_50_cargo = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_50_cargo = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_50_cargo = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_50_cargo = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_50_cargo = load_list(file_name, "rewards_model_v6")

    case2030_pas = (rewards_random_avg_30_pas, rewards_model_v2_30_pas, rewards_model_v3_30_pas, rewards_model_v4_30_pas, rewards_model_v5_30_pas, rewards_model_v6_30_pas)

    case2040_pas = (rewards_random_avg_40_pas, rewards_model_v2_40_pas, rewards_model_v3_40_pas, rewards_model_v4_40_pas, rewards_model_v5_40_pas, rewards_model_v6_40_pas)

    case2050_pas = (rewards_random_avg_50_pas, rewards_model_v2_50_pas, rewards_model_v3_50_pas, rewards_model_v4_50_pas, rewards_model_v5_50_pas, rewards_model_v6_50_pas)


    case2030_cargo = (rewards_random_avg_30_cargo, rewards_model_v2_30_cargo, rewards_model_v3_30_cargo,
                rewards_model_v4_30_cargo, rewards_model_v5_30_cargo, rewards_model_v6_30_cargo)

    case2040_cargo = (rewards_random_avg_40_cargo, rewards_model_v2_40_cargo, rewards_model_v3_40_cargo,
                rewards_model_v4_40_cargo, rewards_model_v5_40_cargo, rewards_model_v6_40_cargo)

    case2050_cargo = (rewards_random_avg_50_cargo, rewards_model_v2_50_cargo, rewards_model_v3_50_cargo,
                rewards_model_v4_50_cargo, rewards_model_v5_50_cargo, rewards_model_v6_50_cargo)

    def plot_single_case(cat_order, case_data, title="Passenger aircraft with 2030 technology projections"):
        # 1. Setup figure and GridSpec (One plot + One legend row)
        fig = plt.figure(figsize=(10, 8), constrained_layout=True)
        gs = fig.add_gridspec(nrows=2, ncols=1, height_ratios=[10, 1])

        ax = fig.add_subplot(gs[0, 0])
        leg_ax = fig.add_subplot(gs[1, 0])
        leg_ax.set_axis_off()

        # 2. Configuration (Colors and Abbreviations)
        model_labels = ['0', '2e4', '1e5', '2e5', '4e5', '1e6']
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
            'Kerosene, Hydrogen, and Batteries': r'CJF, H$_2$ & BAT'
        }

        # 3. Process Data
        # case_data is expected to be a tuple of 6 lists (one for each training step)
        per_model = []
        for lbl, items in zip(model_labels, case_data):
            dct = {}
            for r, t, _, _ in items:
                r = float(r)
                if (r > -11) and np.isfinite(r):
                    dct.setdefault(t, []).append(r)
            per_model.append((lbl, dct))

        types_present = [t for t in cat_order if any(t in d for _, d in per_model)]

        # 4. Plotting Logic
        gap_abs = 0.10
        base_width = 0.36
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
                ax.boxplot([data], positions=[pos], vert=False, widths=[base_width],
                           patch_artist=True, showcaps=True, whis=(5, 95), showfliers=False,
                           showmeans=True, meanline=True,
                           meanprops=dict(color='black', linewidth=1.2, linestyle='-'),
                           medianprops=dict(visible=False))

                # Set colors (same as original)
                for box in ax.findobj(mpatches.PathPatch)[-1:]:  # Target the last added box
                    box.set_facecolor(model_colors[m_idx])

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
        y_text_pos = ax.get_ylim()[1] - 0.6
        props = dict(ha='center', va='top', fontsize=10, fontweight='bold')
        ax.text(-7.5, y_text_pos, "Payload < 0", color='#EE6462', **props)
        ax.text(-3, y_text_pos, "Infeasible CG", color='#009ef6', **props)
        ax.text(4.5, y_text_pos, "Feasible design", color='#4ca346', **props)

        ax.set_title(title, pad=20)
        ax.set_xlabel('Scaled Reward')
        ax.grid(axis="x", linestyle="--", alpha=0.5)

        # 6. Legend (Simplified)
        fancy_box = FancyBboxPatch((0.05, 0.1), 0.9, 0.8, boxstyle="square,pad=0.",
                                   facecolor='lightgrey', alpha=0.2, edgecolor='black')
        leg_ax.add_patch(fancy_box)

        xs = np.linspace(0.15, 0.85, len(model_labels))
        for x, lbl, color in zip(xs, model_labels, model_colors):
            leg_ax.add_patch(plt.Rectangle((x - 0.02, 0.5), 0.04, 0.2, facecolor=color, edgecolor='black'))
            leg_ax.text(x + 0.03, 0.6, lbl, va='center', fontsize=12)
        leg_ax.text(0.5, 0.2, "Number of training steps", ha='center', fontsize=12)

        plt.show()

    #plot_single_case(cat_order, case2030_pas)

    def plot_three_cases(cat_order, cases, titles):
        # 1. Configuration (Colors and Abbreviations from your first function)
        model_labels = ['0', '1e4', '3e4', '7e4', '1.5e5', '3e5']
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
            'Kerosene, Hydrogen, and Batteries': r'CJF, H$_2$ & BAT'
        }

        # 2. Setup Figure and Grid (3 columns for the 3 cases)
        fig = plt.figure(figsize=(18, 11), constrained_layout=True)
        # 3 rows: 0=Plots, 1=Spacer, 2=Legend (Following your first function's height ratios)
        gs = fig.add_gridspec(nrows=3, ncols=3, height_ratios=[20, 0.5, 2])

        axes = []
        for c in range(3):
            axes.append(fig.add_subplot(gs[0, c]))

        leg_ax = fig.add_subplot(gs[2, :])
        leg_ax.set_axis_off()

        # 3. Plotting Loop (Using your original logic for drawing panels)
        for i, ax in enumerate(axes):
            case_data = cases[i]

            # Helper to process data for this specific panel
            def rewards_by_type(items):
                out = {}
                for r, t, _, _ in items:
                    r = float(r)
                    if (r > -11) and np.isfinite(r):
                        out.setdefault(t, []).append(r)
                return out

            per_model = [(lbl, rewards_by_type(items)) for lbl, items in zip(model_labels, case_data)]
            types_present = [t for t in cat_order if any(t in d for _, d in per_model)]

            # Spacing logic from your first function
            gap_abs, min_width, base_width, row_gap_edge = 0.10, 0.12, 0.36, 0.4
            cur_edge = 0.0
            row_centers = {}

            for idx, t in enumerate(types_present):
                gh = len(model_labels) * base_width + (len(model_labels) - 1) * gap_abs
                if idx == 0:
                    row_centers[t] = gh / 2.0
                    cur_edge = gh
                else:
                    low_edge = cur_edge + row_gap_edge
                    row_centers[t] = low_edge + gh / 2.0
                    cur_edge = low_edge + gh

            for t in types_present:
                y_center = row_centers[t]
                start = y_center - 0.5 * (len(model_labels) * base_width + (len(model_labels) - 1) * gap_abs)

                for m_idx, (lbl, dct) in enumerate(per_model):
                    data = dct.get(t, [])
                    if not data: continue
                    pos = start + 0.5 * base_width + m_idx * (base_width + gap_abs)

                    bp = ax.boxplot([data], positions=[pos], vert=False, widths=[base_width],
                                    patch_artist=True, showcaps=True, whis=(5, 95), showfliers=False,
                                    showmeans=True, meanline=True,
                                    meanprops=dict(color='black', linewidth=1.2, linestyle='-'),
                                    medianprops=dict(visible=False))

                    for box in bp['boxes']:
                        box.set_facecolor(model_colors[m_idx])

            # 4. Aesthetics and Tick handling (from your first function)
            ax.set_xlim(-10.1, 10.1)
            ax.set_xticks(np.arange(-5, 10 + 1, 5))  # [cite: 25, 26, 27]
            ax.invert_yaxis()

            # Only show labels on the leftmost axis (index 0)
            if i == 0:
                ax.set_yticks([row_centers[t] for t in types_present])
                ax.set_yticklabels([abbr.get(t, t) for t in types_present])
                ax.tick_params(axis='y', rotation=45)
            else:
                ax.set_yticks([row_centers[t] for t in types_present])  # Ticks remain, but no labels
                ax.set_yticklabels([])

            # Zone backgrounds [cite: 14, 15]
            ax.axvspan(-10.1, -5, facecolor=bg_colors[0], alpha=1, zorder=-1)
            ax.axvspan(-5, -1, facecolor=bg_colors[1], alpha=1, zorder=-1)
            ax.axvspan(-1, 10.1, facecolor=bg_colors[2], alpha=1, zorder=-1)

            # Text labels at the top
            y_text_pos = -0.8
            props = dict(ha='center', va='top', fontsize=11, fontweight='bold')
            ax.text(-7.5, y_text_pos, "Payload < 0", color='#EE6462', **props)  #
            ax.text(-3, y_text_pos, "Infeasible CG", color='#009ef6', **props)  #
            ax.text(4.5, y_text_pos, "Feasible design", color='#4ca346', **props)  #

            ax.set_title(titles[i], pad=30)
            ax.set_xlabel('Scaled Reward')  # [cite: 36]
            ax.grid(axis="x", linestyle="--", linewidth=0.5, alpha=0.5)

        # 5. Legend (Rectangular style as requested)
        fancy_box = FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="square,pad=0",
                                   facecolor='lightgrey', alpha=0.2, edgecolor='black', linewidth=1.0)
        leg_ax.add_patch(fancy_box)

        xs = np.linspace(0.12, 0.88, len(model_labels))
        for x, lbl, color in zip(xs, model_labels, model_colors):
            leg_ax.add_patch(plt.Rectangle((x - 0.02, 0.5), 0.04, 0.2, facecolor=color, edgecolor='black'))
            leg_ax.text(x + 0.03, 0.6, lbl, ha='left', va='center', fontsize=14)
        leg_ax.text(0.5, 0.1, "Number of training steps", ha='center', va='bottom', fontsize=16)  #

        plt.show()

    #plot_three_cases(cat_order, [case2030_pas, case2040_pas, case2050_pas], ["a) Passenger aircraft with 2030 technology projections", "b) Passenger aircraft with 2040 technology projections", "c) Passenger aircraft with 2050 technology projections"])

    def boxplot_six_cases(
            cat_order,
            # Row 1 Inputs
            case1, case2, case3,
            # Row 2 Inputs
            case4, case5, case6,
            titles=(
                    "a) Passenger aircraft with 2030 technology projections", "b) Passenger aircraft with 2040 technology projections", "c) Passenger aircraft with 2050 technology projections",
                    "d) Cargo aircraft with 2030 technology projections", "e) Cargo aircraft with 2040 technology projections", "f) Cargo aircraft with 2050 technology projections"
            ),
            gap_abs=0.10,
            min_width=0.12,
            base_width=0.36,
            row_gap_edge=0.4,
            figsize=(16, 19)  # Increased height for two rows
    ):

        # Colors and model labels (fixed and consistent across all three panels)
        model_labels = ['0', '1e4', '3e4', '7e4', '1.5e5', '3e5']
        cmap = plt.get_cmap('tab10')
        model_colors = [cmap(i) for i in range(len(model_labels))]

        pastel_cmap = plt.get_cmap('Pastel1')
        bg_colors = [pastel_cmap(0), pastel_cmap(1), pastel_cmap(2)]

        # Short y-tick labels
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

        def rewards_by_type(items):
            out = {}
            for r, t, _, _ in items:
                r = float(r)
                if (r <= -11) or (not np.isfinite(r)):
                    continue
                out.setdefault(t, []).append(r)
            return out

        def edge_spaced_positions(widths, center, gap):
            total = sum(widths) + gap * (len(widths) - 1)
            start = center - 0.5 * total
            pos = []
            cur = start
            for w in widths:
                pos.append(cur + 0.5 * w)
                cur += w + gap
            return pos, total

        def draw_one_panel(ax, title, datasets, is_top_row=False):
            DATASETS = list(zip(model_labels, datasets))
            K = len(DATASETS)
            per_model = [(lbl, rewards_by_type(items)) for (lbl, items) in DATASETS]
            types_present = [t for t in cat_order if any(t in d for _, d in per_model)]

            type_counts = {}
            for t in types_present:
                type_counts[t] = max((len(d.get(t, [])) for _, d in per_model), default=0)
            max_count = max(type_counts.values()) if type_counts else 1

            row_box_height = {t: max(min_width, base_width * (type_counts[t] / max_count)) for t in types_present}
            row_group_height = {t: K * row_box_height[t] + (K - 1) * gap_abs for t in types_present}

            row_centers = {}
            cur_edge = 0.0
            for idx, t in enumerate(types_present):
                gh = row_group_height[t]
                if idx == 0:
                    row_centers[t] = gh / 2.0
                    cur_edge = gh
                else:
                    low_edge = cur_edge + row_gap_edge
                    row_centers[t] = low_edge + gh / 2.0
                    cur_edge = low_edge + gh

            for t in types_present:
                width_t = row_box_height[t]
                widths_row = [width_t] * K
                centers_row, _ = edge_spaced_positions(widths_row, row_centers[t], gap_abs)

                for m_idx, (lbl, dct) in enumerate(per_model):
                    data = dct.get(t, [])
                    if not data: continue
                    bp = ax.boxplot([data], positions=[centers_row[m_idx]], vert=False, widths=[widths_row[m_idx]],
                                    patch_artist=True, showcaps=True, whis=(5, 95), showfliers=False,
                                    showmeans=True, meanline=True,
                                    meanprops=dict(color='black', linewidth=1.2, linestyle='-'),
                                    medianprops=dict(visible=False, linewidth=0))
                    for box in bp['boxes']: box.set(facecolor=model_colors[m_idx], edgecolor='black', linewidth=0.8)
                    for whisk in bp['whiskers']: whisk.set(color='black', linewidth=0.8)
                    for cap in bp['caps']: cap.set(color='black', linewidth=0.8)

            y_centers = [row_centers[t] for t in types_present]
            ax.set_yticks(y_centers)
            ax.set_yticklabels([abbr.get(t, t) for t in types_present])

            total_stack_height = cur_edge
            pad = 0.2

            # --- ADJUST LIMITS FOR TOP ROW TO FIT BRACKETS ---
            # If it's the top row, we extend the 'top' (negative y) limit significantly
            top_limit = -4.0 if is_top_row else -pad
            ax.set_ylim(total_stack_height + pad, top_limit)

            ax.set_xlabel('Scaled Reward')
            ax.grid(axis="x", linestyle="--", linewidth=0.5, alpha=0.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            #ax.set_title(title, pad=30)

            return model_labels, model_colors

        # -------- single figure with 2x3 GridSpec (top = plots, bottom = legend) --------

        # -------- CHANGED: 2x3 Grid + Legend Row --------

        fig = plt.figure(figsize=figsize, constrained_layout=True)

        gs = fig.add_gridspec(nrows=4, ncols=3, height_ratios=[20, 0.25, 20, 2])

        axes = []

        # 2. Update Axes Creation
        # Top Row (Row index 0)
        for c in range(3):
            axes.append(fig.add_subplot(gs[0, c]))

        # Bottom Row (Row index 2) -> We SKIP index 1 (the spacer)
        for c in range(3):
            axes.append(fig.add_subplot(gs[2, c]))

        # Legend (Row index 3)
        leg_ax = fig.add_subplot(gs[3, :])
        leg_ax.set_axis_off()

        # gs = fig.add_gridspec(nrows=3, ncols=3, height_ratios=[20, 20, 4])
        #
        # # Create flattened list of axes: [Row1_1, Row1_2, Row1_3, Row2_1, Row2_2, Row2_3]
        # axes = []
        # for r in range(2):
        #     for c in range(3):
        #         axes.append(fig.add_subplot(gs[r, c]))
        #
        # leg_ax = fig.add_subplot(gs[2, :])  # Legend is now row index 2
        # leg_ax.set_axis_off()

        # Organize inputs for looping
        all_cases = [case1, case2, case3, case4, case5, case6]

        # Draw all 6 panels
        # We capture labs/cols from the first one to draw the legend later
        labs, cols = draw_one_panel(axes[0], titles[0], all_cases[0])

        for i in range(1, 6):
            draw_one_panel(axes[i], titles[i], all_cases[i])

        # Formatting Loop
        for i, ax in enumerate(axes):
            ax.set_xlim(-10.1, 10.1)
            ax.set_xticks(np.arange(-5, 10 + 1, 5))

            # Logic for Y-labels: Only show on the leftmost column (indices 0 and 3)
            if i % 3 != 0:
                ax.set_yticklabels([])
                ax.set_ylabel('')
            else:
                ax.tick_params(axis='y', rotation=45)
                pass
                #ax.set_ylabel('Architectures with hydrogen as energy source')

            if i < 3:
                ax.set_xlabel('')  # Removes the text "Scaled Reward"
                ax.tick_params(labelbottom=False)  # Removes the numbers (-5, 0, 5...)
                title_pad = 30
                ax.axvspan(-10.1, -5, facecolor=bg_colors[0], alpha=1, zorder=-1)
                # Region 2: -5 to 0
                ax.axvspan(-5, -1, facecolor=bg_colors[1], alpha=1, zorder=-1)
                # Region 3: 0 to 10
                ax.axvspan(-1, 10.1, facecolor=bg_colors[2], alpha=1, zorder=-1)

            # y_tip = -0.2
            # height= 0.15
            # draw_brace(ax, (-10, -5),"Payload < 0", y_tip=y_tip, height=height)
            # draw_brace(ax, (-5, 0), "Infeasible CG", y_tip=y_tip, height=height)
            # draw_brace(ax, (0, 10), "Feasible design", y_tip=y_tip, height=height)

                # --- ADDED: Simple text labels at the top (optional, for clarity) ---
                # Since we removed braces, we place text slightly inside the plot area
                #y_text_pos = ax.get_ylim()[1] + 0.05 * (ax.get_ylim()[0] - ax.get_ylim()[1])  # Near top

                y_text_pos = -0.53

                # ee6462
                # 009ef6
                # 4ca346

                # You can comment these out if you strictly want ONLY colors and no text at all
                props = dict(ha='center', va='top', fontsize=11, fontweight='bold', alpha=1)
                ax.text(-8, y_text_pos, "Payload < 0", color='#EE6462', **props)
                ax.text(-3, y_text_pos, "Infeasible CG", color='#009ef6', **props)
                ax.text(4.5, y_text_pos, "Feasible design", color='#4ca346', **props)
            else:
                ax.axvspan(-10.1, -5, facecolor=bg_colors[0], alpha=1, zorder=-1)
                # Region 3: 0 to 10
                ax.axvspan(-1, 10.1, facecolor=bg_colors[2], alpha=1, zorder=-1)
                title_pad = 8

            ax.set_title(titles[i], pad=title_pad)

        # ... [Keep the Legend generation code exactly as before] ...
        handles = [mpatches.Patch(facecolor=c, edgecolor='black', linewidth=0.9, label=l)
                   for l, c in zip(labs, cols)]

        leg_ax.set_xlim(0, 1)
        leg_ax.set_ylim(0, 1)

        # ##### CHANGE 2: FANCY ROUNDED BOX #####
        # boxstyle="round,pad=0.1" gives the rounded corners
        # facecolor='lightgrey', alpha=0.3 gives the transparent grey fill
        fancy_box = FancyBboxPatch(
            (0.05, 0.05), 0.9, 0.9,  # (x, y), width, height
            boxstyle="round,pad=0.04",  # Rounded corners style
            facecolor='lightgrey',  # Grey fill
            alpha=0.4,  # Transparency (0.0 to 1.0)
            edgecolor='black',  # Border color
            linewidth=1.0,  # Border width
            mutation_scale=0.1,  # Scale for the rounded corners (optional)
            zorder=0  # Draw behind text
        )
        leg_ax.add_patch(fancy_box)

        # Draw Items
        xs = np.linspace(0.12, 0.88, len(handles))
        y_pos = 0.6
        for x, h in zip(xs, handles):
            leg_ax.add_patch(plt.Rectangle((x - 0.02, y_pos - 0.1), 0.04, 0.2,
                                           facecolor=h.get_facecolor(),
                                           edgecolor='black', linewidth=0.9,
                                           zorder=1))
            leg_ax.text(x + 0.03, y_pos, h.get_label(), ha='left', va='center', fontsize=14, zorder=1)

        leg_ax.text(0.5, 0.1, "Number of training steps", ha='center', va='bottom', fontsize=16, zorder=1)

        plt.savefig("PASCARGOBOX.pdf", format='pdf', bbox_inches='tight')
        #plt.show()



    boxplot_six_cases(cat_order, case2030_pas, case2040_pas, case2050_pas, case2030_cargo, case2040_cargo, case2050_cargo)

def plottingFC():
    cat_order = ['FC', 'NO FC']

    data_dir = Path("")
    def load_list(filename, name):
        filename = data_dir / Path(filename).with_suffix(".json")
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[name]

    file_name = "PAS2030FC2"

    rewards_random_avg_30_pas = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_30_pas = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_30_pas = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_30_pas = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_30_pas = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_30_pas = load_list(file_name, "rewards_model_v6")

    file_name = "PAS2040FC2"

    rewards_random_avg_40_pas = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_40_pas = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_40_pas = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_40_pas = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_40_pas = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_40_pas = load_list(file_name, "rewards_model_v6")

    file_name = "PAS2050FC2"

    rewards_random_avg_50_pas = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_50_pas = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_50_pas = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_50_pas = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_50_pas = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_50_pas = load_list(file_name, "rewards_model_v6")

    file_name = "CARGO2030FC2"

    rewards_random_avg_30_cargo = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_30_cargo = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_30_cargo = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_30_cargo = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_30_cargo = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_30_cargo = load_list(file_name, "rewards_model_v6")

    file_name = "CARGO2040FC2"

    rewards_random_avg_40_cargo = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_40_cargo = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_40_cargo = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_40_cargo = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_40_cargo = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_40_cargo = load_list(file_name, "rewards_model_v6")

    file_name = "CARGO2050FC2"

    rewards_random_avg_50_cargo = load_list(file_name, "rewards_random_avg")
    rewards_model_v2_50_cargo = load_list(file_name, "rewards_model_v2")
    rewards_model_v3_50_cargo = load_list(file_name, "rewards_model_v3")
    rewards_model_v4_50_cargo = load_list(file_name, "rewards_model_v4")
    rewards_model_v5_50_cargo = load_list(file_name, "rewards_model_v5")
    rewards_model_v6_50_cargo = load_list(file_name, "rewards_model_v6")

    def boxplot_six_cases(
            cat_order,
            # Row 1 Inputs
            case1, case2, case3,
            # Row 2 Inputs
            case4, case5, case6,
            titles=(
                    "a) Passenger aircraft with 2030 technology projections", "b) Passenger aircraft with 2040 technology projections", "c) Passenger aircraft with 2050 technology projections",
                    "d) Cargo aircraft with 2030 technology projections", "e) Cargo aircraft with 2040 technology projections", "f) Cargo aircraft with 2050 technology projections"
            ),
            gap_abs=0.10,
            min_width=0.12,
            base_width=0.36,
            row_gap_edge=0.4,
            figsize=(16, 10)  # Increased height for two rows
    ):
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        import matplotlib.path as mpath
        from matplotlib.patches import FancyBboxPatch

        # Colors and model labels (fixed and consistent across all three panels)
        model_labels = ['0', '1e4', '3e4', '7e4', '1.5e5', '3e5']
        cmap = plt.get_cmap('tab10')
        model_colors = [cmap(i) for i in range(len(model_labels))]

        pastel_cmap = plt.get_cmap('Pastel1')
        bg_colors = [pastel_cmap(0), pastel_cmap(1), pastel_cmap(2)]

        # Short y-tick labels
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

        def rewards_by_type(items):
            out = {}
            for r, t, _, _ in items:
                r = float(r)
                if (r <= -11) or (not np.isfinite(r)):
                    continue
                out.setdefault(t, []).append(r)
            return out

        def edge_spaced_positions(widths, center, gap):
            total = sum(widths) + gap * (len(widths) - 1)
            start = center - 0.5 * total
            pos = []
            cur = start
            for w in widths:
                pos.append(cur + 0.5 * w)
                cur += w + gap
            return pos, total

        def draw_one_panel(ax, title, datasets, is_top_row=False):
            DATASETS = list(zip(model_labels, datasets))
            K = len(DATASETS)
            per_model = [(lbl, rewards_by_type(items)) for (lbl, items) in DATASETS]
            types_present = [t for t in cat_order if any(t in d for _, d in per_model)]

            type_counts = {}
            for t in types_present:
                type_counts[t] = max((len(d.get(t, [])) for _, d in per_model), default=0)
            max_count = max(type_counts.values()) if type_counts else 1

            row_box_height = {t: max(min_width, base_width * (type_counts[t] / max_count)) for t in types_present}
            row_group_height = {t: K * row_box_height[t] + (K - 1) * gap_abs for t in types_present}

            row_centers = {}
            cur_edge = 0.0
            for idx, t in enumerate(types_present):
                gh = row_group_height[t]
                if idx == 0:
                    row_centers[t] = gh / 2.0
                    cur_edge = gh
                else:
                    low_edge = cur_edge + row_gap_edge
                    row_centers[t] = low_edge + gh / 2.0
                    cur_edge = low_edge + gh

            for t in types_present:
                width_t = row_box_height[t]
                widths_row = [width_t] * K
                centers_row, _ = edge_spaced_positions(widths_row, row_centers[t], gap_abs)

                for m_idx, (lbl, dct) in enumerate(per_model):
                    data = dct.get(t, [])
                    if not data: continue
                    bp = ax.boxplot([data], positions=[centers_row[m_idx]], vert=False, widths=[widths_row[m_idx]],
                                    patch_artist=True, showcaps=True, whis=(5, 95), showfliers=False,
                                    showmeans=True, meanline=True,
                                    meanprops=dict(color='black', linewidth=1.2, linestyle='-'),
                                    medianprops=dict(visible=False, linewidth=0))
                    for box in bp['boxes']: box.set(facecolor=model_colors[m_idx], edgecolor='black', linewidth=0.8)
                    for whisk in bp['whiskers']: whisk.set(color='black', linewidth=0.8)
                    for cap in bp['caps']: cap.set(color='black', linewidth=0.8)

            y_centers = [row_centers[t] for t in types_present]
            ax.set_yticks(y_centers)
            ax.set_yticklabels([abbr.get(t, t) for t in types_present])

            total_stack_height = cur_edge
            pad = 0.2

            # --- ADJUST LIMITS FOR TOP ROW TO FIT BRACKETS ---
            # If it's the top row, we extend the 'top' (negative y) limit significantly
            top_limit = -4.0 if is_top_row else -pad
            ax.set_ylim(total_stack_height + pad, top_limit)

            ax.set_xlabel('Scaled Reward')
            ax.grid(axis="x", linestyle="--", linewidth=0.5, alpha=0.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            #ax.set_title(title, pad=30)

            return model_labels, model_colors

        # -------- single figure with 2x3 GridSpec (top = plots, bottom = legend) --------

        # -------- CHANGED: 2x3 Grid + Legend Row --------

        fig = plt.figure(figsize=figsize, constrained_layout=True)

        gs = fig.add_gridspec(nrows=4, ncols=3, height_ratios=[20, 1, 20, 4])

        axes = []

        # 2. Update Axes Creation
        # Top Row (Row index 0)
        for c in range(3):
            axes.append(fig.add_subplot(gs[0, c]))

        # Bottom Row (Row index 2) -> We SKIP index 1 (the spacer)
        for c in range(3):
            axes.append(fig.add_subplot(gs[2, c]))

        # Legend (Row index 3)
        leg_ax = fig.add_subplot(gs[3, :])
        leg_ax.set_axis_off()

        # gs = fig.add_gridspec(nrows=3, ncols=3, height_ratios=[20, 20, 4])
        #
        # # Create flattened list of axes: [Row1_1, Row1_2, Row1_3, Row2_1, Row2_2, Row2_3]
        # axes = []
        # for r in range(2):
        #     for c in range(3):
        #         axes.append(fig.add_subplot(gs[r, c]))
        #
        # leg_ax = fig.add_subplot(gs[2, :])  # Legend is now row index 2
        # leg_ax.set_axis_off()

        # Organize inputs for looping
        all_cases = [case1, case2, case3, case4, case5, case6]

        # Draw all 6 panels
        # We capture labs/cols from the first one to draw the legend later
        labs, cols = draw_one_panel(axes[0], titles[0], all_cases[0])

        for i in range(1, 6):
            draw_one_panel(axes[i], titles[i], all_cases[i])

        # Formatting Loop
        for i, ax in enumerate(axes):
            ax.set_xlim(-10.1, 10.1)
            ax.set_xticks(np.arange(-5, 10 + 1, 5))

            # Logic for Y-labels: Only show on the leftmost column (indices 0 and 3)
            if i % 3 != 0:
                ax.set_yticklabels([])
                ax.set_ylabel('')
            else:
                ax.tick_params(axis='y', rotation=45)
                pass
                #ax.set_ylabel('Architectures with hydrogen as energy source')



            if i < 3:
                ax.set_xlabel('')  # Removes the text "Scaled Reward"
                ax.tick_params(labelbottom=False)  # Removes the numbers (-5, 0, 5...)
                title_pad = 30
                ax.axvspan(-10.1, -5, facecolor=bg_colors[0], alpha=1, zorder=-1)
                # Region 2: -5 to 0
                ax.axvspan(-5, 0, facecolor=bg_colors[1], alpha=1, zorder=-1)
                # Region 3: 0 to 10
                ax.axvspan(0, 10.1, facecolor=bg_colors[2], alpha=1, zorder=-1)
            # y_tip = -0.2
            # height= 0.15
            # draw_brace(ax, (-10, -5),"Payload < 0", y_tip=y_tip, height=height)
            # draw_brace(ax, (-5, 0), "Infeasible CG", y_tip=y_tip, height=height)
            # draw_brace(ax, (0, 10), "Feasible design", y_tip=y_tip, height=height)

                # --- ADDED: Simple text labels at the top (optional, for clarity) ---
                # Since we removed braces, we place text slightly inside the plot area
                #y_text_pos = ax.get_ylim()[1] + 0.05 * (ax.get_ylim()[0] - ax.get_ylim()[1])  # Near top

                y_text_pos = -0.5

                # ee6462
                # 009ef6
                # 4ca346

                # You can comment these out if you strictly want ONLY colors and no text at all
                props = dict(ha='center', va='top', fontsize=11, fontweight='bold', alpha=1)
                ax.text(-7.5, y_text_pos, "Payload < 0", color='#EE6462', **props)
                ax.text(-2.5, y_text_pos, "Infeasible CG", color='#009ef6', **props)
                ax.text(5.0, y_text_pos, "Feasible design", color='#4ca346', **props)
            else:
                ax.axvspan(-10.1, -5, facecolor=bg_colors[0], alpha=1, zorder=-1)
                # Region 2: -5 to 0
                # Region 3: 0 to 10
                ax.axvspan(0, 10.1, facecolor=bg_colors[2], alpha=1, zorder=-1)
                title_pad = 10

            ax.set_title(titles[i], pad=title_pad)

        # ... [Keep the Legend generation code exactly as before] ...
        handles = [mpatches.Patch(facecolor=c, edgecolor='black', linewidth=0.9, label=l)
                   for l, c in zip(labs, cols)]

        leg_ax.set_xlim(0, 1)
        leg_ax.set_ylim(0, 1)

        # ##### CHANGE 2: FANCY ROUNDED BOX #####
        # boxstyle="round,pad=0.1" gives the rounded corners
        # facecolor='lightgrey', alpha=0.3 gives the transparent grey fill
        fancy_box = FancyBboxPatch(
            (0.05, 0.05), 0.9, 0.9,  # (x, y), width, height
            boxstyle="round,pad=0.04",  # Rounded corners style
            facecolor='lightgrey',  # Grey fill
            alpha=0.4,  # Transparency (0.0 to 1.0)
            edgecolor='black',  # Border color
            linewidth=1.0,  # Border width
            mutation_scale=0.1,  # Scale for the rounded corners (optional)
            zorder=0  # Draw behind text
        )
        leg_ax.add_patch(fancy_box)

        # Draw Items
        xs = np.linspace(0.12, 0.88, len(handles))
        y_pos = 0.6
        for x, h in zip(xs, handles):
            leg_ax.add_patch(plt.Rectangle((x - 0.02, y_pos - 0.1), 0.04, 0.2,
                                           facecolor=h.get_facecolor(),
                                           edgecolor='black', linewidth=0.9,
                                           zorder=1))
            leg_ax.text(x + 0.03, y_pos, h.get_label(), ha='left', va='center', fontsize=14, zorder=1)

        leg_ax.text(0.5, 0.1, "Number of training steps", ha='center', va='bottom', fontsize=16, zorder=1)

        plt.savefig("PASCARGOBOXFC.pdf", format='pdf', bbox_inches='tight')
        #plt.show()

    case2030_pas = (rewards_random_avg_30_pas, rewards_model_v2_30_pas, rewards_model_v3_30_pas,
                rewards_model_v4_30_pas, rewards_model_v5_30_pas, rewards_model_v6_30_pas)

    case2040_pas = (rewards_random_avg_40_pas, rewards_model_v2_40_pas, rewards_model_v3_40_pas,
                rewards_model_v4_40_pas, rewards_model_v5_40_pas, rewards_model_v6_40_pas)

    case2050_pas = (rewards_random_avg_50_pas, rewards_model_v2_50_pas, rewards_model_v3_50_pas,
                rewards_model_v4_50_pas, rewards_model_v5_50_pas, rewards_model_v6_50_pas)

    case2030_cargo = (rewards_random_avg_30_cargo, rewards_model_v2_30_cargo, rewards_model_v3_30_cargo,
                rewards_model_v4_30_cargo, rewards_model_v5_30_cargo, rewards_model_v6_30_cargo)

    case2040_cargo = (rewards_random_avg_40_cargo, rewards_model_v2_40_cargo, rewards_model_v3_40_cargo,
                rewards_model_v4_40_cargo, rewards_model_v5_40_cargo, rewards_model_v6_40_cargo)

    case2050_cargo = (rewards_random_avg_50_cargo, rewards_model_v2_50_cargo, rewards_model_v3_50_cargo,
                rewards_model_v4_50_cargo, rewards_model_v5_50_cargo, rewards_model_v6_50_cargo)

    boxplot_six_cases(cat_order, case2030_pas, case2040_pas, case2050_pas, case2030_cargo, case2040_cargo, case2050_cargo)

def breakdowns2030():
    size = 20
    plt.rcParams.update({
        'axes.titlesize': size,
        'axes.labelsize': size,
        'xtick.labelsize': size,
        'ytick.labelsize': size,
        'legend.fontsize': size,
    })

    CON2030 = {
        'CJF': 2191.8960542857144,  #kg
        r'H$_2$': 0,  #kg
        'GT': 1018.8715517241379, #kg
        'FC': 0, #kg
        'EM': 0, #kg
        'PM': 0, #kg
        #'OEM - Powertrain': 12543, #kg
        'Payload': 7246.232393990147,  # kg
        'Payload_r': 0, # kg
        'ERF': 293.5160354745374,  # mW/m^2
    }

    RL2030 = {
        'CJF': 1190.7254128571428,  #kg
        r'H$_2$': 2552.5459591666668,  #kg
        'GT': 622.4398541114058, #kg
        'FC': 1401.7004545454545, #kg
        'EM': 78.29932765151516+ 26.324090909090913+ 35.845267518939394, #kg
        'PM': 51.39568333333333, #kg
        #'OEM - Powertrain': 12543, #kg
        'Payload': 4497.723949906451,  # kg
        'Payload_r': 0, #kg
        'ERF': 158.93913222522664, #mW/m^2
    }

    CMA2030 = {
        'CJF': 829.4546778571428,  #kg
        r'H$_2$': 3493.235216641235,  #kg
        'GT': 693.7245358090186, #kg
        'FC': 1556.8473863636361, #kg
        'EM': 128.43991477272726, #kg
        'PM': 57.084404166666666, #kg
        #'OEM - Powertrain': 12543, #kg
        'Payload': 3698.2138643895737,  # kg
        'Payload_r': 0, # kg
        'ERF': 90.77978359550472,  # mW/m^2
    }

    data_list = [CON2030, RL2030, CMA2030]
    titles = ['a) Conventional design for a \npassenger aircraft with\n2030 technology projections', 'b) Optimal design found by RL for a\npassenger aircraft with\n2030 technology projections', 'c) Optimal design found by CMA-ES for a\npassenger aircraft with\n2030 technology projections']

    # 2. Setup Consistent Colors based on DICTIONARY ORDER
    master_keys = [k for k in CON2030.keys() if k != 'ERF']
    cmap = plt.get_cmap('Paired')
    colors = [cmap(i) for i in range(8)]
    key_color_map = {key: colors[i % len(colors)] for i, key in enumerate(master_keys)}

    def arrange_labels(ax, wedges, texts, counter, threshold_degrees=20, start_length=1.1):

        # Initialize a dynamic length tracker
        current_length = start_length

        i = 0
        j = 0
        k = 0
        for w, t in zip(wedges, texts):
            k+=1
            if not t.get_text():
                continue
            # Standard geometry calculations
            angle = w.theta2 - w.theta1
            theta = (w.theta1 + w.theta2) / 2.0
            center = w.center
            r = w.r

            # Convert Matplotlib angle (CCW from Right) to Clockwise from Top (12 o'clock)
            # 0=Top, 90=Right, 180=Bottom, 270=Left
            clock_angle = (90 - theta) % 360

            if counter == 1:
                threshold_degrees = 30
            if angle > threshold_degrees:
                # --- INSIDE LABEL ---
                inner_r = r * 0.6
                x_in = inner_r * np.cos(np.deg2rad(theta)) + center[0]
                y_in = inner_r * np.sin(np.deg2rad(theta)) + center[1]
                print(x_in, y_in)
                if counter == 2 and k == 1:
                    x_in = x_in + 0.05
                    y_in = y_in + 0.05
                elif counter == 2 and k == 4:
                    y_in = y_in -0.15
                elif counter ==3 and k == 4:
                    x_in = x_in - 0.05
                    y_in = y_in - 0.05
                t.set_position((x_in, y_in))
                t.set_horizontalalignment('center')
                t.set_verticalalignment('center')

                # Reset length when we go back inside?
                # Optional: current_length = start_length

            else:
                # --- OUTSIDE LABEL ---

                # APPLY USER LOGIC:
                # If after 270 degrees (Top-Left quadrant), INCREASE length (Step Out)
                # Otherwise, DECREASE length (Step In)
                if clock_angle > 270 or clock_angle < 90:
                    if i == 0:
                        current_length = start_length
                    else:
                        current_length += 0.2
                    i+=1
                elif clock_angle > 90 and clock_angle < 180:
                    current_length = start_length
                else:
                    if j == 0:
                        current_length = start_length + 0.2
                    else:
                        current_length = start_length
                    j+=1

                # Calculate position using the dynamic current_length
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
    fig, axes = plt.subplots(1, 3, figsize=(18, 8.5))

    counter = 0
    for ax, d, title in zip(axes, data_list, titles):
        counter +=1
        filtered_data = {k: v for k, v in d.items() if k != 'ERF' and v > 0}

        # Sort by Master Key Order
        sorted_items = sorted(filtered_data.items(), key=lambda x: master_keys.index(x[0]))

        labels = [k for k, v in sorted_items]
        sizes = [v for k, v in sorted_items]

        chart_colors = []
        for k in labels:
            if k == 'Payload_r':
                chart_colors.append((0, 0, 0, 0))
            else:
                chart_colors.append(key_color_map[k])

        # Label: Mass only
        plot_labels = [f"{v:.0f} kg" if k != 'Payload_r' else "" for k, v in sorted_items]

        # Initialize Pie (Labels start outside at distance 1.2)
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

        # Apply Smart Label Logic
        # Threshold: If slice is smaller than 15 degrees (~4%), label goes outside.
        arrange_labels(ax, wedges, texts, counter, threshold_degrees=45)

        ax.set_title(title, pad=0)

        erf_val = d.get('ERF', 0)

        mtom_val = (23000 - d.get('Payload_r', 0))/1000
        if erf_val > 0:
            ax.text(0.5, -0.1, f"ERF = {erf_val:.1f} $\cdot 10^{{-6}}$ mW/m$^2$",
                    transform=ax.transAxes,
                    ha='center', va='top', fontsize=size, color='black')
        else:
            ax.text(0.5, -0.1, f"ERF = {erf_val:.1f} mW/m$^2$",
                    transform=ax.transAxes,
                    ha='center', va='top', fontsize=size, color='black')

        ax.text(0.5, -0.2, f"MTOM = {mtom_val:.2f} $\cdot 10^{{3}}$ kg",
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

    plt.subplots_adjust(left=0.01, bottom=0.2, right=0.98, top=0.95)
    plt.savefig("MBD2030.pdf", format='pdf', bbox_inches='tight')
    #plt.show()

def breakdowns():
    size = 20
    plt.rcParams.update({
        'axes.titlesize': size,
        'axes.labelsize': size,
        'xtick.labelsize': size,
        'ytick.labelsize': size,
        'legend.fontsize': size,
    })
    PAS2030 = {
        'CJF': 1467.8056628571428,  #kg
        r'H$_2$': 2091.3266621875005,  #kg
        'GT': 932.4442307692308, #kg
        'FC': 761.028409090909, #kg
        'EM': 62.78484375, #kg
        'PM': 27.904375, #kg
        #'OEM - Powertrain': 12543, #kg
        'Payload': 5113.7058163452175,  # kg
        'Payload_r': 0, #kg
        'ERF': 165.77070812162302, #mW/m^2
    }

    CARGO2030 = {
        'CJF': 0,  #kg
        r'H$_2$': 5577.628256666667,  #kg
        'GT': 0, #kg
        'FC': 3490.8597727272722, #kg
        'EM': 287.99592803030305, #kg
        'PM': 127.99819166666666, #kg
        #'OEM - Powertrain': 12543, #kg
        'Payload': 740.8399701590911,  # kg
        'Payload_r': 231.67788074999993, # kg
        'ERF': 0,  # mW/m^2
    }

    PAS2040 = {
        'CJF': 0,  #kg
        r'H$_2$': 3317.3520375,  #kg
        'GT': 0, #kg
        'FC': 2894.1316287878785, #kg
        'EM': 185.39466911764708, #kg
        'PM': 106.11815972222222, #kg
        #'OEM - Powertrain': 12543, #kg
        'Payload': 3702.0857493722524,  # kg
        'Payload_r': 251.9177555, # kg
        'ERF': 0,  # mW/m^2
    }

    PAS2050 = {
        'CJF': 0,  #kg
        r'H$_2$': 2919.6084067307693,  #kg
        'GT': 0, #kg
        'FC': 2657.875874125874, #kg
        'EM': 154.84588477366256, #kg
        'PM': 97.45544871794871, #kg
        #'OEM - Powertrain': 12543, #kg
        'Payload': 4356.763478526745,  # kg
        'Payload_r': 270.450907125, #kg
        'ERF': 0,  # mW/m^2
    }

    data_list = [CARGO2030, PAS2040, PAS2050]
    titles = ['a) Optimal design found by RL and \nCMA-ES for a cargo aircraft\nwith 2040 technology projections', 'b) Optimal design found by RL and\nCMA-ES for a passenger and cargo aircraft\nwith 2040 technology projections', 'c) Optimal design found by RL and\nCMA-ES for a passenger and cargo aircraft\nwith 2050 technology projections']

    # 2. Setup Consistent Colors based on DICTIONARY ORDER
    master_keys = [k for k in PAS2030.keys() if k != 'ERF']
    cmap = plt.get_cmap('Paired')
    colors = [cmap(i) for i in range(8)]
    key_color_map = {key: colors[i % len(colors)] for i, key in enumerate(master_keys)}

    def arrange_labels(ax, wedges, texts, threshold_degrees=20, start_length=1.1):

        # Initialize a dynamic length tracker
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

            # Convert Matplotlib angle (CCW from Right) to Clockwise from Top (12 o'clock)
            # 0=Top, 90=Right, 180=Bottom, 270=Left
            clock_angle = (90 - theta) % 360

            if angle > threshold_degrees:
                # --- INSIDE LABEL ---
                inner_r = r * 0.6
                x_in = inner_r * np.cos(np.deg2rad(theta)) + center[0]
                y_in = inner_r * np.sin(np.deg2rad(theta)) + center[1]
                t.set_position((x_in, y_in))
                t.set_horizontalalignment('center')
                t.set_verticalalignment('center')

                # Reset length when we go back inside?
                # Optional: current_length = start_length

            else:
                # --- OUTSIDE LABEL ---

                # APPLY USER LOGIC:
                # If after 270 degrees (Top-Left quadrant), INCREASE length (Step Out)
                # Otherwise, DECREASE length (Step In)
                if clock_angle > 270 or clock_angle < 90:
                    if i == 0:
                        current_length = start_length
                    else:
                        current_length += 0.1
                    i+=1
                elif clock_angle > 90 and clock_angle < 180:
                    current_length = start_length
                else:
                    if j == 0:
                        current_length = start_length + 0.2
                    else:
                        current_length = start_length
                    j+=1

                # Calculate position using the dynamic current_length
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
    fig, axes = plt.subplots(1, 3, figsize=(18.1, 8.5))

    for ax, d, title in zip(axes, data_list, titles):
        filtered_data = {k: v for k, v in d.items() if k != 'ERF' and v > 0}

        # Sort by Master Key Order
        sorted_items = sorted(filtered_data.items(), key=lambda x: master_keys.index(x[0]))

        labels = [k for k, v in sorted_items]
        sizes = [v for k, v in sorted_items]

        chart_colors = []
        for k in labels:
            if k == 'Payload_r':
                chart_colors.append((0, 0, 0, 0))
            else:
                chart_colors.append(key_color_map[k])

        # Label: Mass only
        plot_labels = [f"{v:.0f} kg" if k != 'Payload_r' else "" for k, v in sorted_items]

        # Initialize Pie (Labels start outside at distance 1.2)
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

        # Apply Smart Label Logic
        # Threshold: If slice is smaller than 15 degrees (~4%), label goes outside.
        arrange_labels(ax, wedges, texts, threshold_degrees=51)

        ax.set_title(title, pad=20)

        erf_val = d.get('ERF', 0)

        mtom_val = (23000 - d.get('Payload_r', 0))/1000
        if erf_val > 0:
            ax.text(0.5, -0.1, f"ERF = {erf_val:.1f} $\cdot 10^{{-6}}$ mW/m$^2$",
                    transform=ax.transAxes,
                    ha='center', va='top', fontsize=size, color='black')
        else:
            ax.text(0.5, -0.1, f"ERF = {erf_val:.1f} mW/m$^2$",
                    transform=ax.transAxes,
                    ha='center', va='top', fontsize=size, color='black')

        ax.text(0.5, -0.2, f"MTOM = {mtom_val:.2f} $\cdot 10^{{3}}$ kg",
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

    plt.subplots_adjust(left=0.03, bottom=0.15, right=0.97, top=0.95)
    plt.savefig("MBD4050.pdf", format='pdf', bbox_inches='tight')
    #plt.show()

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
    titles = ['a) Optimal design found by RL', 'b) Optimal design found by CMA-ES']

    # 2. Setup Consistent Colors based on DICTIONARY ORDER
    master_keys = [k for k in RLFP2050.keys() if k != 'ERF' and k != 'CO2' and k != 'NOX']
    cmap = plt.get_cmap('Paired')
    colors = [cmap(i) for i in range(8)]
    key_color_map = {key: colors[i % len(colors)] for i, key in enumerate(master_keys)}

    def arrange_labels(ax, wedges, texts, threshold_degrees=20, start_length=1.1):

        # Initialize a dynamic length tracker
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

            # Convert Matplotlib angle (CCW from Right) to Clockwise from Top (12 o'clock)
            # 0=Top, 90=Right, 180=Bottom, 270=Left
            clock_angle = (90 - theta) % 360

            if angle > threshold_degrees:
                print(clock_angle)
                # --- INSIDE LABEL ---
                inner_r = r * 0.6
                x_in = inner_r * np.cos(np.deg2rad(theta)) + center[0]
                y_in = inner_r * np.sin(np.deg2rad(theta)) + center[1]
                if clock_angle < 140 and clock_angle > 135:
                    x_in += 0.075
                t.set_position((x_in, y_in))
                t.set_horizontalalignment('center')
                t.set_verticalalignment('center')

                # Reset length when we go back inside?
                # Optional: current_length = start_length

            else:
                # --- OUTSIDE LABEL ---
                if clock_angle > 270 or clock_angle < 90:
                    if i == 0:
                        current_length = start_length
                    else:
                        current_length += 0.1
                    i+=1
                elif clock_angle > 90 and clock_angle < 150:
                    current_length = start_length
                elif clock_angle >155 and clock_angle < 180:
                    print(j)
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

                # Calculate position using the dynamic current_length
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

        # Sort by Master Key Order
        sorted_items = sorted(filtered_data.items(), key=lambda x: master_keys.index(x[0]))

        labels = [k for k, v in sorted_items]
        sizes = [v for k, v in sorted_items]

        chart_colors = []
        for k in labels:
            if k == 'Payload_r':
                chart_colors.append((0, 0, 0, 0))
            else:
                chart_colors.append(key_color_map[k])

        # Label: Mass only
        plot_labels = [f"{v:.0f} kg" if k != 'Payload_r' else "" for k, v in sorted_items]

        # Initialize Pie (Labels start outside at distance 1.2)
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

        # Apply Smart Label Logic
        # Threshold: If slice is smaller than 15 degrees (~4%), label goes outside.
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

def sensitivity():
    import matplotlib.pyplot as plt
    size = 18
    plt.rcParams.update({
        'axes.titlesize': size,
        'axes.labelsize': size,
        'xtick.labelsize': size,
        'ytick.labelsize': size,
        'legend.fontsize': size
    })
    from Powertrain_env import Powertrain
    from Components import Component
    from Flightsim import FlightSimulation, ActionFeasibilityWrapper
    from Characteristics import CHARACTERISTICS2030 as CHARACTERISTICS
    Component.set_characteristics(CHARACTERISTICS)
    import matplotlib.colors as mcolors
    import matplotlib as mpl
    # Initialize unique architecture based on saved actions
    pt = Powertrain()

    resolution = 1000

    points = {
        "2050": (0.6, 15.6),
        "2040": (0.575, 14.4),
        "2030": (0.55, 9),
    }

    densities = np.linspace(5, 20, resolution + 1)
    efficiencies = np.linspace(0.25, 0.83, resolution + 1)
    rewards_matrix = np.zeros((len(densities), len(efficiencies)))
    for i, density in enumerate(densities):
        for j, efficiency in enumerate(efficiencies):
            if i % 100 == 0 and j % 100 == 0:
                print(i, j)
            CHARACTERISTICS['HydrogenStorage']['grav_energy_density'] = density
            CHARACTERISTICS['FuelCell']['efficiency'] = efficiency
            # print('#########################################')
            # print(density)
            # print(efficiency)
            Component.set_characteristics(CHARACTERISTICS)
            env = ActionFeasibilityWrapper(FlightSimulation(CHARACTERISTICS, False, False))
            obs = env.reset()
            done = False
            while not done:
                action = env.action_space.sample()
                obs, reward, done, _, info = env.step(action)
            rewards_matrix[i, j] = reward
    X, Y = np.meshgrid(efficiencies, densities)

    # 2. Plot
    fig, ax = plt.subplots(figsize=(10, 7.5))

    # Define your exact levels and corresponding Pastel1 colors
    my_levels = [-15, -5, -1, 10]
    my_colors = [plt.cm.Pastel1(0), plt.cm.Pastel1(1), plt.cm.Pastel1(2)]

    # Use contourf: It automatically fills the regions between 'levels' with 'colors'
    cs = plt.contourf(X, Y, rewards_matrix, levels=my_levels, colors=my_colors)

    label_offsets = {
        "Negative Payload": (0, 1),  # No shift
        "Outside Feasible CG Range": (0, -1),  # Example: Move UP by 2 density units
        "Feasible Design": (0, 0)  # Example: Move LEFT by 0.05 efficiency units
    }

    labels = ["Payload < 0", "Infeasible CG", "Feasible Design"]
    centers = [-7.5, -3.5, 9.8]  # Changed 10 to 9.5 slightly to ensure mask catches the data < 10

    for label, center_val in zip(labels, centers):
        # Mask to find the region
        mask = (rewards_matrix > center_val - 2) & (rewards_matrix < center_val + 2)

        if np.any(mask):
            print(label, center_val)
            # 1. Calculate the automatic center
            mean_x = np.mean(X[mask])
            mean_y = np.mean(Y[mask])

            # 2. Retrieve manual offsets (default to 0,0 if not found)
            dx, dy = label_offsets.get(label, (0, 0))
            dx = 0.05
            # 3. Apply the shift
            final_x = mean_x + dx
            final_y = mean_y + dy

            plt.text(final_x, final_y, label, ha='center', va='center', fontsize=size, fontweight='bold')

    markers = ['P', 'd', 'X']  # Circle, Square, Diamond
    marker_cycle = iter(markers)

    for label, (eff, dens) in points.items():
        # Get next marker style
        current_marker = next(marker_cycle, 'o')

        # Plot the point
        # zorder=5 ensures points are plotted on top of the contour plot
        ax.scatter(eff, dens, color='black', marker=current_marker, s=100, zorder=5, label=label)
        ax.legend(loc='upper left')

    ax.set_xlabel('Fuel cell efficiency [-]')
    ax.set_ylabel(r'H$_2$ Storage system energy density [MJ/kg]')

    plt.tight_layout()
    plt.savefig("SEN.pdf", format='pdf', bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    #plottingNominal()
    #plottingFC()
    #breakdowns()
    #sensitivity()
    #breakdowns2030()
    breakdownsFP()