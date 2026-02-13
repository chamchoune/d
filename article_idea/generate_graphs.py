import csv
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
            rows.append({
                'load_erl': float(r['load_erl']),
                'method': r['method'],
                'blocking_prob': float(r['blocking_prob']),
                'spectrum_utilization': float(r['spectrum_utilization']),
                'service_acceptance': float(r['service_acceptance']),
                'avg_reward': float(r['avg_reward']),
            })
    return rows


def read_training(path):
    rows = []
    with open(path, newline='') as f:
        for r in csv.DictReader(f):
            rows.append({
                'episode': float(r['episode']),
                'dqn_reward': float(r['dqn_reward']),
                'ppo_reward': float(r['ppo_reward']),
            })
    return rows


def scale(value, vmin, vmax, out_min, out_max):
    if vmax == vmin:
        return (out_min + out_max) / 2
    ratio = (value - vmin) / (vmax - vmin)
    return out_min + ratio * (out_max - out_min)


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

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    out.append('<rect width="100%" height="100%" fill="white"/>')
    out.append(f'<text x="{width/2}" y="28" text-anchor="middle" font-size="22" font-family="Arial">{title}</text>')

    # axes
    x0, y0 = left, top + plot_h
    x1, y1 = left + plot_w, top
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="black"/>')
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="black"/>')

    # grid and ticks
    for i in range(6):
        y_val = ymin + i * (ymax - ymin) / 5
        y_px = scale(y_val, ymin, ymax, y0, y1)
        out.append(f'<line x1="{x0}" y1="{y_px:.1f}" x2="{x1}" y2="{y_px:.1f}" stroke="#e8e8e8"/>')
        out.append(f'<text x="{x0-8}" y="{y_px+4:.1f}" text-anchor="end" font-size="12" font-family="Arial">{y_val:.3f}</text>')

    x_ticks = sorted(set(all_x))
    for xv in x_ticks:
        x_px = scale(xv, xmin, xmax, x0, x1)
        out.append(f'<line x1="{x_px:.1f}" y1="{y0}" x2="{x_px:.1f}" y2="{y0+5}" stroke="black"/>')
        out.append(f'<text x="{x_px:.1f}" y="{y0+22}" text-anchor="middle" font-size="12" font-family="Arial">{xv:g}</text>')

    # lines
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

    # labels
    out.append(f'<text x="{width/2}" y="{height-20}" text-anchor="middle" font-size="14" font-family="Arial">{x_label}</text>')
    out.append(f'<text x="20" y="{height/2}" transform="rotate(-90 20 {height/2})" text-anchor="middle" font-size="14" font-family="Arial">{y_label}</text>')

    # legend
    lx, ly = width - 190, 80
    out.append(f'<rect x="{lx-12}" y="{ly-22}" width="180" height="{28*len(series)+16}" fill="white" stroke="#ccc"/>')
    for i, (label, _) in enumerate(series):
        y = ly + i * 28
        color = COLORS.get(label, '#444')
        out.append(f'<line x1="{lx}" y1="{y}" x2="{lx+24}" y2="{y}" stroke="{color}" stroke-width="3"/>')
        out.append(f'<text x="{lx+32}" y="{y+4}" font-size="13" font-family="Arial">{label}</text>')

    out.append('</svg>')
    (FIG / filename).write_text('\n'.join(out))


def main():
    results = read_results(DATA / 'illustrative_results.csv')
    training = read_training(DATA / 'illustrative_training_curve.csv')

    methods = sorted(set(r['method'] for r in results))

    def make_series(metric):
        return [
            (m, sorted([(r['load_erl'], r[metric]) for r in results if r['method'] == m], key=lambda t: t[0]))
            for m in methods
        ]

    line_chart('blocking_probability_vs_load.svg', 'Blocking Probability vs. Traffic Load', 'Traffic Load (Erlangs)', 'Blocking Probability', make_series('blocking_prob'))
    line_chart('spectrum_utilization_vs_load.svg', 'Spectrum Utilization vs. Traffic Load', 'Traffic Load (Erlangs)', 'Spectrum Utilization', make_series('spectrum_utilization'))
    line_chart('service_acceptance_vs_load.svg', 'Service Acceptance vs. Traffic Load', 'Traffic Load (Erlangs)', 'Service Acceptance Rate', make_series('service_acceptance'))

    tr_series = [
        ('DQN-EON', [(r['episode'], r['dqn_reward']) for r in training]),
        ('PPO-EON', [(r['episode'], r['ppo_reward']) for r in training]),
    ]
    line_chart('training_convergence.svg', 'DRL Training Convergence', 'Training Episode (x1000 requests)', 'Average Episodic Reward', tr_series)
    print(f'Generated SVG graphs in {FIG}')


if __name__ == '__main__':
    main()
