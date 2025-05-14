from pyvis.network import Network
import logging


def build_interactive_graph(all_data, output_file):
    net = Network(height='900px', width='100%', directed=True, notebook=False)
    net.barnes_hut(spring_length=100)

    for service_name, data in all_data.items():
        accounts = data.get('accounts', [])
        forwardings = data.get('forwardings', [])

        for acc in accounts:
            color = 'purple' if 'exchange' in service_name.lower() else 'blue'
            if acc not in net.node_map:
                net.add_node(acc, label=acc, color=color, shape='dot', size=20)

        for fwd in forwardings:
            from_id = fwd.get('from')
            to_id = fwd.get('to')
            if not from_id or not to_id:
                continue

            # DMARC = specjalne forwardy
            is_dmarc = any(x.lower().startswith(('_dmarc', 'v=dmarc')) for x in [from_id, to_id])

            from_shape = 'triangle' if is_dmarc else 'square'
            to_shape = 'triangle' if is_dmarc else 'square'
            from_color = 'orange' if is_dmarc else 'green'
            to_color = 'orange' if is_dmarc else 'green'

            if from_id not in net.node_map:
                net.add_node(from_id, label=from_id, color=from_color, shape=from_shape, size=16)
            if to_id not in net.node_map:
                net.add_node(to_id, label=to_id, color=to_color, shape=to_shape, size=16)

            net.add_edge(from_id, to_id, title=f"{from_id} ➔ {to_id}")

    # Ustawienia fizyki
    net.set_options("""
    {
      "physics": { "stabilization": false }
    }
    """)

    net.write_html(output_file)
    logging.info(f"✅ Interaktywny graf zapisany do {output_file}")

    # Legenda
    legend_block = """
    <div style="position:fixed; top:10px; right:10px; background:white; border:1px solid gray; padding:10px; z-index:9999; font-size:14px;">
    <b>Legenda:</b><br>
    🔵 Konto MXPLAN / Email Pro (blue dot)<br>
    🟣 Konto Exchange (purple dot)<br>
    🟢 Forwarding (zielony kwadrat)<br>
    🟠 Forwarding DMARC (pomarańczowy trójkąt)
    </div>
    """
    with open(output_file, 'r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace('</body>', legend_block + '</body>')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
