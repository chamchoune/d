import csv
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data'
FIG = BASE / 'figures'
FIG.mkdir(parents=True, exist_ok=True)

COLORS = {
    'DQN-EON': '#1f77b4',
    'PPO-EON': '#2ca02c',
    'Heuristic-FF': '#d62728',
}


def read_results(path):
    rows = []
    with open(path, newline='') as f:
        for r in csv.DictReader(f):
            rows.append(
                {
                    'load_erl': float(r['load_erl']),
                    'method': r['method'],
                    'blocking_prob': float(r['blocking_prob']),
                    'spectrum_utilization': float(r['spectrum_utilization']),
                    'service_acceptance': float(r['service_acceptance']),
                    'avg_reward': float(r['avg_reward']),
                }
            )
    return rows


def read_training(path):
    rows = []
    with open(path, newline='') as f:
        for r in csv.DictReader(f):
            rows.append(
                {
                    'episode': float(r['episode']),
                    'dqn_reward': float(r['dqn_reward']),
                    'ppo_reward': float(r['ppo_reward']),
                }
            )
    return rows


def scale(value, vmin, vmax, out_min, out_max):
    if vmax == vmin:
        return (out_min + out_max) / 2
    ratio = (value - vmin) / (vmax - vmin)
    return out_min + ratio * (out_max - out_min)


def _svg_canvas(width, height, title):
    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    )
    out.append('<rect width="100%" height="100%" fill="white"/>')
    out.append(
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="22" font-family="Arial">{title}</text>'
    )
    return out


def line_chart(filename, title, x_label, y_label, series):
    width, height = 900, 560
    left, top, right, bottom = 80, 50, 40, 80
    plot_w = width - left - right
    plot_h = height - top - bottom

    all_x = [x for _, pts in series for x, _ in pts]
    all_y = [y for _, pts in series for _, y in pts]
    xmin, xmax = min(all_x), max(all_x)
    ymin, ymax = min(all_y), max(all_y)
    ypad = (ymax - ymin) * 0.1 if ymax > ymin else 0.1
    ymin, ymax = ymin - ypad, ymax + ypad

    out = _svg_canvas(width, height, title)

    x0, y0 = left, top + plot_h
    x1, y1 = left + plot_w, top
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="black"/>')
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="black"/>')

    for i in range(6):
        y_val = ymin + i * (ymax - ymin) / 5
        y_px = scale(y_val, ymin, ymax, y0, y1)
        out.append(f'<line x1="{x0}" y1="{y_px:.1f}" x2="{x1}" y2="{y_px:.1f}" stroke="#e8e8e8"/>')
        out.append(
            f'<text x="{x0-8}" y="{y_px+4:.1f}" text-anchor="end" font-size="12" font-family="Arial">{y_val:.3f}</text>'
        )

    x_ticks = sorted(set(all_x))
    for xv in x_ticks:
        x_px = scale(xv, xmin, xmax, x0, x1)
        out.append(f'<line x1="{x_px:.1f}" y1="{y0}" x2="{x_px:.1f}" y2="{y0+5}" stroke="black"/>')
        out.append(
            f'<text x="{x_px:.1f}" y="{y0+22}" text-anchor="middle" font-size="12" font-family="Arial">{xv:g}</text>'
        )

    for label, pts in series:
        color = COLORS.get(label, '#444')
        p = []
        for x, y in pts:
            xp = scale(x, xmin, xmax, x0, x1)
            yp = scale(y, ymin, ymax, y0, y1)
            p.append((xp, yp))
        path = ' '.join((f'{"M" if i == 0 else "L"}{xp:.1f},{yp:.1f}' for i, (xp, yp) in enumerate(p)))
        out.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for xp, yp in p:
            out.append(f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="3.5" fill="{color}"/>')

    out.append(
        f'<text x="{width/2}" y="{height-20}" text-anchor="middle" font-size="14" font-family="Arial">{x_label}</text>'
    )
    out.append(
        f'<text x="20" y="{height/2}" transform="rotate(-90 20 {height/2})" text-anchor="middle" font-size="14" font-family="Arial">{y_label}</text>'
    )

    lx, ly = width - 190, 80
    out.append(f'<rect x="{lx-12}" y="{ly-22}" width="180" height="{28*len(series)+16}" fill="white" stroke="#ccc"/>')
    for i, (label, _) in enumerate(series):
        y = ly + i * 28
        color = COLORS.get(label, '#444')
        out.append(f'<line x1="{lx}" y1="{y}" x2="{lx+24}" y2="{y}" stroke="{color}" stroke-width="3"/>')
        out.append(f'<text x="{lx+32}" y="{y+4}" font-size="13" font-family="Arial">{label}</text>')

    out.append('</svg>')
    (FIG / filename).write_text('\n'.join(out))


def bar_chart(filename, title, x_label, y_label, categories, values, colors):
    width, height = 900, 560
    left, top, right, bottom = 80, 50, 40, 90
    plot_w = width - left - right
    plot_h = height - top - bottom

    ymin = 0.0
    ymax = max(values) * 1.2 if values else 1.0

    out = _svg_canvas(width, height, title)
    x0, y0 = left, top + plot_h
    x1, y1 = left + plot_w, top
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="black"/>')
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="black"/>')

    for i in range(6):
        y_val = ymin + i * (ymax - ymin) / 5
        y_px = scale(y_val, ymin, ymax, y0, y1)
        out.append(f'<line x1="{x0}" y1="{y_px:.1f}" x2="{x1}" y2="{y_px:.1f}" stroke="#ececec"/>')
        out.append(
            f'<text x="{x0-8}" y="{y_px+4:.1f}" text-anchor="end" font-size="12" font-family="Arial">{y_val:.3f}</text>'
        )

    count = len(categories)
    gap = plot_w / max(count, 1)
    bar_w = gap * 0.55

    for i, (cat, val, c) in enumerate(zip(categories, values, colors)):
        cx = x0 + (i + 0.5) * gap
        x = cx - bar_w / 2
        y = scale(val, ymin, ymax, y0, y1)
        h = y0 - y
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="{c}"/>')
        out.append(f'<text x="{cx:.1f}" y="{y0+22}" text-anchor="middle" font-size="12" font-family="Arial">{cat}</text>')
        out.append(f'<text x="{cx:.1f}" y="{y-8:.1f}" text-anchor="middle" font-size="12" font-family="Arial">{val:.3f}</text>')

    out.append(
        f'<text x="{width/2}" y="{height-20}" text-anchor="middle" font-size="14" font-family="Arial">{x_label}</text>'
    )
    out.append(
        f'<text x="20" y="{height/2}" transform="rotate(-90 20 {height/2})" text-anchor="middle" font-size="14" font-family="Arial">{y_label}</text>'
    )

    out.append('</svg>')
    (FIG / filename).write_text('\n'.join(out))


def heatmap_chart(filename, title, methods, loads, values, cbar_label):
    width, height = 980, 580
    left, top, right, bottom = 140, 70, 130, 90
    plot_w = width - left - right
    plot_h = height - top - bottom

    rows = len(methods)
    cols = len(loads)

    out = _svg_canvas(width, height, title)
    all_vals = [v for row in values for v in row]
    vmin, vmax = min(all_vals), max(all_vals)

    def color_map(v):
        t = 0 if vmax == vmin else (v - vmin) / (vmax - vmin)
        r = int(245 - 170 * t)
        g = int(245 - 230 * t)
        b = int(255 - 95 * t)
        return f'#{r:02x}{g:02x}{b:02x}'

    cell_w = plot_w / cols
    cell_h = plot_h / rows

    for i, m in enumerate(methods):
        y = top + i * cell_h
        out.append(
            f'<text x="{left-12}" y="{y + cell_h/2 + 5:.1f}" text-anchor="end" font-size="13" font-family="Arial">{m}</text>'
        )
        for j, load in enumerate(loads):
            x = left + j * cell_w
            v = values[i][j]
            out.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w:.1f}" height="{cell_h:.1f}" fill="{color_map(v)}" stroke="white"/>'
            )
            out.append(
                f'<text x="{x + cell_w/2:.1f}" y="{y + cell_h/2 + 5:.1f}" text-anchor="middle" font-size="12" font-family="Arial">{v:.3f}</text>'
            )

    for j, load in enumerate(loads):
        x = left + j * cell_w + cell_w / 2
        out.append(f'<text x="{x:.1f}" y="{top + plot_h + 24}" text-anchor="middle" font-size="12" font-family="Arial">{load:g}</text>')

    out.append(
        f'<text x="{width/2}" y="{height-20}" text-anchor="middle" font-size="14" font-family="Arial">Traffic Load (Erlangs)</text>'
    )

    cb_x = left + plot_w + 35
    cb_y = top
    cb_w = 26
    cb_h = plot_h
    steps = 80
    for s in range(steps):
        t0 = s / steps
        val = vmin + t0 * (vmax - vmin)
        y = cb_y + (1 - t0) * cb_h
        out.append(
            f'<rect x="{cb_x}" y="{y:.1f}" width="{cb_w}" height="{cb_h/steps + 1:.1f}" fill="{color_map(val)}" stroke="none"/>'
        )

    out.append(f'<rect x="{cb_x}" y="{cb_y}" width="{cb_w}" height="{cb_h}" fill="none" stroke="#999"/>')
    for k in range(6):
        val = vmin + k * (vmax - vmin) / 5
        y = scale(val, vmin, vmax, cb_y + cb_h, cb_y)
        out.append(f'<line x1="{cb_x+cb_w}" y1="{y:.1f}" x2="{cb_x+cb_w+5}" y2="{y:.1f}" stroke="black"/>')
        out.append(
            f'<text x="{cb_x+cb_w+8}" y="{y+4:.1f}" text-anchor="start" font-size="11" font-family="Arial">{val:.3f}</text>'
        )
    out.append(
        f'<text x="{cb_x+cb_w+52}" y="{cb_y-10}" text-anchor="middle" font-size="12" font-family="Arial">{cbar_label}</text>'
    )

    out.append('</svg>')
    (FIG / filename).write_text('\n'.join(out))


def grouped_by_method(results, metric):
    methods = sorted(set(r['method'] for r in results))
    data = {
        m: sorted([(r['load_erl'], r[metric]) for r in results if r['method'] == m], key=lambda t: t[0])
        for m in methods
    }
    return methods, data


def compute_relative_improvement(results, metric, baseline='Heuristic-FF'):
    methods = sorted(set(r['method'] for r in results))
    loads = sorted(set(r['load_erl'] for r in results))

    table = {(r['method'], r['load_erl']): r[metric] for r in results}
    improvements = {}
    for m in methods:
        if m == baseline:
            continue
        series = []
        for ld in loads:
            base = table[(baseline, ld)]
            val = table[(m, ld)]
            if metric == 'blocking_prob':
                imp = ((base - val) / base) * 100.0 if base else 0.0
            else:
                imp = ((val - base) / base) * 100.0 if base else 0.0
            series.append((ld, imp))
        improvements[m] = series
    return improvements


def moving_average(points, window=3):
    smoothed = []
    for i in range(len(points)):
        left = max(0, i - window + 1)
        chunk = points[left : i + 1]
        avg = sum(p[1] for p in chunk) / len(chunk)
        smoothed.append((points[i][0], avg))
    return smoothed


def main():
    results = read_results(DATA / 'illustrative_results.csv')
    training = read_training(DATA / 'illustrative_training_curve.csv')

    methods, blocking_data = grouped_by_method(results, 'blocking_prob')
    _, util_data = grouped_by_method(results, 'spectrum_utilization')
    _, acc_data = grouped_by_method(results, 'service_acceptance')
    _, reward_data = grouped_by_method(results, 'avg_reward')

    line_chart(
        'blocking_probability_vs_load.svg',
        'Blocking Probability vs. Traffic Load',
        'Traffic Load (Erlangs)',
        'Blocking Probability',
        [(m, blocking_data[m]) for m in methods],
    )
    line_chart(
        'spectrum_utilization_vs_load.svg',
        'Spectrum Utilization vs. Traffic Load',
        'Traffic Load (Erlangs)',
        'Spectrum Utilization',
        [(m, util_data[m]) for m in methods],
    )
    line_chart(
        'service_acceptance_vs_load.svg',
        'Service Acceptance vs. Traffic Load',
        'Traffic Load (Erlangs)',
        'Service Acceptance Rate',
        [(m, acc_data[m]) for m in methods],
    )
    line_chart(
        'avg_reward_vs_load.svg',
        'Average Reward vs. Traffic Load',
        'Traffic Load (Erlangs)',
        'Average Reward',
        [(m, reward_data[m]) for m in methods],
    )

    blocking_gain = compute_relative_improvement(results, 'blocking_prob')
    line_chart(
        'blocking_improvement_over_heuristic.svg',
        'Blocking Reduction over Heuristic-FF (%)',
        'Traffic Load (Erlangs)',
        'Improvement (%)',
        [(m, pts) for m, pts in blocking_gain.items()],
    )

    high_load = max(r['load_erl'] for r in results)
    high_load_rows = [r for r in results if r['load_erl'] == high_load]
    bar_chart(
        'acceptance_at_peak_load.svg',
        f'Service Acceptance at Peak Load ({high_load:g} Erlangs)',
        'Method',
        'Service Acceptance',
        [r['method'] for r in high_load_rows],
        [r['service_acceptance'] for r in high_load_rows],
        [COLORS.get(r['method'], '#444') for r in high_load_rows],
    )

    loads = sorted(set(r['load_erl'] for r in results))
    heat_values = []
    for m in methods:
        row = []
        for ld in loads:
            row.append(next(r['blocking_prob'] for r in results if r['method'] == m and r['load_erl'] == ld))
        heat_values.append(row)
    heatmap_chart(
        'blocking_heatmap.svg',
        'Blocking Probability Heatmap (Method × Load)',
        methods,
        loads,
        heat_values,
        'Blocking',
    )

    dqn_points = [(r['episode'], r['dqn_reward']) for r in training]
    ppo_points = [(r['episode'], r['ppo_reward']) for r in training]
    tr_series = [
        ('DQN-EON', dqn_points),
        ('PPO-EON', ppo_points),
    ]
    line_chart(
        'training_convergence.svg',
        'DRL Training Convergence',
        'Training Episode (x1000 requests)',
        'Average Episodic Reward',
        tr_series,
    )

    tr_smooth = [
        ('DQN-EON', moving_average(dqn_points, window=3)),
        ('PPO-EON', moving_average(ppo_points, window=3)),
    ]
    line_chart(
        'training_convergence_smoothed.svg',
        'DRL Training Convergence (Smoothed)',
        'Training Episode (x1000 requests)',
        'Smoothed Reward (window=3)',
        tr_smooth,
    )

    generated = sorted(p.name for p in FIG.glob('*.svg'))
    print('Generated SVG graphs:')
    for name in generated:
        print(f'- {name}')


if __name__ == '__main__':
    main()
