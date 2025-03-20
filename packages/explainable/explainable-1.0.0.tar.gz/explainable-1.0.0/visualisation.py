from explainable import ContextManager, Graph, TextNode, RowNode, ColumnNode, PixelNode



def neuron_node(
    label: str,
    object_id: str,
    default_x: int = 0,
    default_y: int = 0,
):
    return ColumnNode([
            RowNode([
                TextNode("abc"),
                TextNode("cba"),
            ]),
            TextNode(label),
            RowNode([
                PixelNode({
                    "size": 20,
                    "color": "#ff0000" if int(label) % 3 == 0 else "#ffffff",
                }),
                PixelNode({
                    "size": 20,
                    "color": "#ff0000" if int(label) % 3 == 1 else "#ffffff",
                }),
                PixelNode({
                    "size": 20,
                    "color": "#ff0000" if int(label) % 3 == 2 else "#ffffff",
                }),
            ])
        ],
        object_id=object_id,
        default_x=default_x,
        default_y=default_y,
    )


def draw(cm: ContextManager):
    ctx = cm.get("main")

    if 'initial_cells' not in ctx:
        return

    initial_cells = ctx["initial_cells"]
    
    return Graph(
        nodes=[
            neuron_node(
                label=str(x),
                object_id=f"xs_{idx}",
                default_x=idx * 1000,
                default_y=200,
            )
            for idx, x in enumerate(initial_cells)
        ],
        edges=[],
    )
