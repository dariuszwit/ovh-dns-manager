import networkx as nx
import matplotlib.pyplot as plt
import logging


def build_static_graph(all_data, output_file):
    G = nx.DiGraph()
    color_map = {}
    node_shapes = {}

    for key, data in all_data.items():
        accounts = data.get('accounts', [])
        forwardings = data.get('forwardings', [])

        # Dodaj konta główne (MXPLAN / Email Pro / Exchange)
        for acc in accounts:
            if acc not in G:
                G.add_node(acc)
                color_map[acc] = 'purple' if 'exchange' in key.lower() else 'blue'
                node_shapes[acc] = 'o'  # dot

        # Dodaj forwardingi (zielone) i DMARC (pomarańczowe)
        for fwd in forwardings:
            from_id = fwd.get('from')
            to_id = fwd.get('to')
            if not from_id or not to_id:
                continue

            # Węzły
            for node_id in [from_id, to_id]:
                if node_id not in G:
                    G.add_node(node_id)

                if node_id.lower().startswith('_dmarc') or 'v=DMARC1' in node_id:
                    color_map[node_id] = 'orange'
                    node_shapes[node_id] = '^'  # triangle for DMARC
                else:
                    color_map[node_id] = 'green'
                    node_shapes[node_id] = 's'  # square

            # Krawędź
            G.add_edge(from_id, to_id)

    if not G.nodes:
        logging.warning("❗ Graf jest pusty – pomijam zapis.")
        return

    # Pozycje węzłów
    pos = nx.spring_layout(G, k=0.8, iterations=50, seed=42)

    plt.figure(figsize=(18, 18))
    for shape in {'o', 's', '^'}:
        nodes = [n for n in G.nodes if node_shapes.get(n, 'o') == shape]
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=nodes,
            node_color=[color_map[n] for n in nodes],
            node_shape=shape,
            node_size=900
        )

    nx.draw_networkx_edges(
        G, pos,
        arrowstyle='-|>',
        arrowsize=20,
        edge_color='gray',
        width=2,
        connectionstyle='arc3,rad=0.15'
    )
    nx.draw_networkx_labels(G, pos, font_size=10)

    plt.axis('off')
    plt.title("Graf kont i przekierowań (forwardingów)", fontsize=16)

    # Legenda
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='Konto (MXPLAN / Email Pro)', markerfacecolor='blue', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Konto Exchange', markerfacecolor='purple', markersize=10),
        plt.Line2D([0], [0], marker='s', color='w', label='Forwarding', markerfacecolor='green', markersize=10),
        plt.Line2D([0], [0], marker='^', color='w', label='DMARC (_dmarc)', markerfacecolor='orange', markersize=10)
    ]
    plt.legend(handles=legend_elements, loc='lower left')

    plt.tight_layout()
    plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    logging.info(f"📷 Statyczny graf zapisany do {output_file}")
