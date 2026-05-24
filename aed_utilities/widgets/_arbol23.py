"""Tutorial interactivo de Árboles 2-3 para Jupyter.

Uso desde un notebook:

    import aed_utilities as aed
    aed.demo_arbol_23()
"""

import copy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import ipywidgets as widgets
from IPython.display import display, clear_output

from ._common import COLOR_MAP

__all__ = ["demo_arbol_23"]


# ---------- Estructura del árbol 2-3 ----------
class Nodo23:
    __slots__ = ("keys", "children")
    def __init__(self, keys=None, children=None):
        self.keys = list(keys) if keys else []
        self.children = list(children) if children else []

    def es_hoja(self):
        return len(self.children) == 0


def _convertir23(obj):
    if obj is None:
        return None
    if hasattr(obj, "raiz"):
        return _convertir23(obj.raiz)
    if hasattr(obj, "keys"):
        n = Nodo23()
        n.keys = list(obj.keys)
        if hasattr(obj, "children"):
            n.children = [_convertir23(c) for c in obj.children]
        return n
    return None


def _esta_vacio(t):
    return t is None or (len(t.keys) == 0 and t.es_hoja())


def _node_at(root, path):
    n = root
    for d in path:
        n = n.children[int(d)]
    return n


def _trail(d):
    return dict(d)


# ---------- Layout y dibujo ----------
def _layout23(root):
    nodes, edges = [], []
    counter = [0]

    def rec(n, depth, path):
        if n.es_hoja():
            num_slots = max(1, len(n.keys))
            x_start = counter[0]
            counter[0] += num_slots
            x = x_start + (num_slots - 1) / 2
            nodes.append({"id": path, "x": x, "y": -depth,
                          "keys": list(n.keys)})
            return x
        child_xs = []
        for i, ch in enumerate(n.children):
            child_xs.append(rec(ch, depth + 1, path + str(i)))
        x = (child_xs[0] + child_xs[-1]) / 2
        nodes.append({"id": path, "x": x, "y": -depth,
                      "keys": list(n.keys)})
        for cx in child_xs:
            edges.append((x, -depth, cx, -depth - 1))
        return x

    rec(root, 0, "")
    return nodes, edges


def _dibujar23(ax, root, highlights):
    ax.clear(); ax.set_axis_off()
    if _esta_vacio(root):
        ax.text(0.5, 0.5, "☐  árbol vacío",
                ha="center", va="center", fontsize=13,
                color="#94a3b8", transform=ax.transAxes)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        return

    nodes, edges = _layout23(root)
    for x1, y1, x2, y2 in edges:
        ax.plot([x1, x2], [y1, y2], color="#cbd5e1", lw=1.6, zorder=1)

    for nd in nodes:
        st = highlights.get(nd["id"])
        fc, ec = COLOR_MAP.get(st, ("#ffffff", "#475569"))
        n_keys = max(1, len(nd["keys"]))
        cell_w, h = 0.55, 0.45
        width = cell_w * n_keys
        x_left = nd["x"] - width / 2
        y_bot = nd["y"] - h / 2
        rect = mpatches.FancyBboxPatch(
            (x_left, y_bot), width, h,
            boxstyle="round,pad=0.0,rounding_size=0.08",
            facecolor=fc, edgecolor=ec,
            lw=2.6 if st else 1.6, zorder=2)
        ax.add_patch(rect)
        for i, k in enumerate(nd["keys"]):
            kx = x_left + (i + 0.5) * cell_w
            ax.text(kx, nd["y"], str(k), ha="center", va="center",
                    fontsize=10, fontweight="bold", zorder=3)
        if n_keys >= 2:
            for s in range(1, n_keys):
                sep_x = x_left + s * cell_w
                ax.plot([sep_x, sep_x], [y_bot + 0.08, y_bot + h - 0.08],
                        color=ec, lw=0.9, zorder=2.5, alpha=0.7)

    xs = [n["x"] for n in nodes]; ys = [n["y"] for n in nodes]
    ax.set_xlim(min(xs) - 0.9, max(xs) + 0.9)
    ax.set_ylim(min(ys) - 0.7, max(ys) + 0.8)
    ax.set_aspect("equal")


# ---------- Descenso recordando pasos ----------
def _walk_down(root, x, pasos, visited):
    """Desciende desde la raíz buscando x. Registra los pasos del recorrido.

    Retorna (path, found) donde path apunta al nodo donde se detuvo y
    found indica si x está en ese nodo."""
    path, n = "", root
    while True:
        if x in n.keys:
            return path, True
        if n.es_hoja():
            return path, False
        i = 0
        while i < len(n.keys) and x > n.keys[i]:
            i += 1
        if len(n.keys) == 1:
            msg = (f"Comparamos: {x} < {n.keys[0]}. Bajamos hacia el subárbol IZQUIERDO."
                   if i == 0 else
                   f"Comparamos: {x} > {n.keys[0]}. Bajamos hacia el subárbol DERECHO.")
        else:
            if i == 0:
                msg = f"Comparamos: {x} < {n.keys[0]}. Bajamos hacia el subárbol IZQUIERDO."
            elif i == 1:
                msg = (f"Comparamos: {n.keys[0]} < {x} < {n.keys[1]}. "
                       f"Bajamos hacia el subárbol DEL MEDIO.")
            else:
                msg = f"Comparamos: {x} > {n.keys[1]}. Bajamos hacia el subárbol DERECHO."
        pasos.append({"msg": msg,
                      "highlights": {**_trail(visited), path: "visiting"}})
        visited[path] = "trail"
        path += str(i)
        n = n.children[i]


# ---------- Generadores de pasos ----------
def _pasos_search(root, x):
    pasos, visited = [], {}
    if _esta_vacio(root):
        pasos.append({"msg": f"El árbol está vacío. La llave {x} no está.",
                      "highlights": {}})
        return pasos, copy.deepcopy(root) if root else None

    pasos.append({
        "msg": f"Comenzamos la búsqueda de {x} en la raíz (llaves {root.keys}).",
        "highlights": {"": "visiting"},
    })
    path, found = _walk_down(root, x, pasos, visited)
    if found:
        pasos.append({
            "msg": f"{x} está en este nodo. ¡Búsqueda exitosa!",
            "highlights": {**_trail(visited), path: "found"},
        })
    else:
        pasos.append({
            "msg": f"Llegamos a una hoja sin encontrar {x}. La búsqueda concluye "
                   f"infructuosa: {x} NO está en el árbol.",
            "highlights": {**_trail(visited), path: "notfound"},
        })
    return pasos, copy.deepcopy(root)


def _pasos_insert(root, x):
    pasos = []

    if _esta_vacio(root):
        pasos.append({
            "msg": f"El árbol está vacío. Se crea una nueva raíz con la llave {x}.",
            "highlights": {"": "target"},
        })
        nuevo = Nodo23(keys=[x])
        pasos.append({
            "msg": f"Listo: ahora el árbol tiene un único nodo (que también es hoja) "
                   f"con la llave {x}.",
            "highlights": {"": "inserted"}, "tree": nuevo,
        })
        return pasos, nuevo

    visited = {}
    pasos.append({
        "msg": f"Para insertar {x} hacemos una búsqueda que debe ser infructuosa, "
               f"hasta llegar a una hoja.",
        "highlights": {"": "visiting"},
    })
    path, found = _walk_down(root, x, pasos, visited)

    if found:
        pasos.append({
            "msg": f"La llave {x} ya está en el árbol. Un 2-3 no admite duplicados, "
                   f"no se inserta nada.",
            "highlights": {**_trail(visited), path: "duplicate"},
        })
        return pasos, copy.deepcopy(root)

    pasos.append({
        "msg": f"Llegamos a una hoja. La búsqueda terminó infructuosa: insertaremos {x} aquí.",
        "highlights": {**_trail(visited), path: "target"},
    })

    tree = copy.deepcopy(root)
    leaf = _node_at(tree, path)
    i = 0
    while i < len(leaf.keys) and x > leaf.keys[i]:
        i += 1
    leaf.keys.insert(i, x)

    if len(leaf.keys) <= 2:
        msg = (f"Insertamos {x} en la hoja. Era binaria, ahora es ternaria."
               if len(leaf.keys) == 2 else
               f"Insertamos {x} en la hoja.")
        pasos.append({"msg": msg,
                      "highlights": {**_trail(visited), path: "inserted"},
                      "tree": copy.deepcopy(tree)})
        return pasos, tree

    pasos.append({
        "msg": f"Insertamos {x} en la hoja, que ahora tiene 3 llaves {leaf.keys}: "
               f"se produce OVERFLOW. Hay que hacer split.",
        "highlights": {**_trail(visited), path: "imbalance"},
        "tree": copy.deepcopy(tree),
    })

    cur_path = path
    while True:
        cur_node = _node_at(tree, cur_path)
        mid_key = cur_node.keys[1]
        izq_n = Nodo23(keys=[cur_node.keys[0]])
        der_n = Nodo23(keys=[cur_node.keys[2]])
        if not cur_node.es_hoja():
            izq_n.children = cur_node.children[:2]
            der_n.children = cur_node.children[2:]

        if cur_path == "":
            nueva_raiz = Nodo23(keys=[mid_key], children=[izq_n, der_n])
            pasos.append({
                "msg": f"Split en la raíz: la mediana {mid_key} sube como NUEVA RAÍZ "
                       f"y el árbol crece un nivel.",
                "highlights": {"": "inserted"},
                "tree": nueva_raiz,
            })
            return pasos, nueva_raiz

        parent_path = cur_path[:-1]
        ci = int(cur_path[-1])
        padre = _node_at(tree, parent_path)
        padre.children[ci:ci + 1] = [izq_n, der_n]
        padre.keys.insert(ci, mid_key)

        if len(padre.keys) <= 2:
            pasos.append({
                "msg": f"Split: la mediana {mid_key} sube al padre, que era binario "
                       f"y ahora es ternario. El árbol queda válido.",
                "highlights": {**_trail(visited), parent_path: "inserted"},
                "tree": copy.deepcopy(tree),
            })
            return pasos, tree

        pasos.append({
            "msg": f"Split: la mediana {mid_key} sube al padre, pero éste queda con "
                   f"3 llaves {padre.keys}. El overflow se PROPAGA hacia arriba.",
            "highlights": {**_trail(visited), parent_path: "imbalance"},
            "tree": copy.deepcopy(tree),
        })
        cur_path = parent_path


def _pasos_delete(root, x):
    pasos = []
    if _esta_vacio(root):
        pasos.append({"msg": "El árbol está vacío: no hay nada que eliminar.",
                      "highlights": {}})
        return pasos, copy.deepcopy(root) if root else None

    visited = {}
    pasos.append({
        "msg": f"Para eliminar {x} primero hay que ubicarla. Empezamos en la raíz.",
        "highlights": {"": "visiting"},
    })
    path, found = _walk_down(root, x, pasos, visited)
    if not found:
        pasos.append({
            "msg": f"Llegamos a una hoja sin encontrar {x}: la llave no está en el árbol, "
                   f"no se hace nada.",
            "highlights": {**_trail(visited), path: "notfound"},
        })
        return pasos, copy.deepcopy(root)

    pasos.append({
        "msg": f"Encontramos {x} en este nodo.",
        "highlights": {**_trail(visited), path: "toDelete"},
    })

    tree = copy.deepcopy(root)
    cur = _node_at(tree, path)
    x_orig = x

    # Si no está en una hoja, reemplazar por el sucesor in-order
    if not cur.es_hoja():
        idx_x = cur.keys.index(x)
        succ_path = path + str(idx_x + 1)
        succ_node = _node_at(tree, succ_path)
        pasos.append({
            "msg": f"{x} no está en una hoja. Buscaremos su SUCESOR in-order, "
                   f"que está en el subárbol a su derecha.",
            "highlights": {**_trail(visited), path: "toDelete", succ_path: "visiting"},
            "tree": copy.deepcopy(tree),
        })
        while not succ_node.es_hoja():
            visited[succ_path] = "trail"
            succ_path += "0"
            succ_node = _node_at(tree, succ_path)
            pasos.append({
                "msg": "Bajamos por la IZQUIERDA mientras el nodo tenga hijo izquierdo.",
                "highlights": {**_trail(visited), path: "toDelete", succ_path: "visiting"},
                "tree": copy.deepcopy(tree),
            })
        succ_key = succ_node.keys[0]
        pasos.append({
            "msg": f"El sucesor es {succ_key} y está en una hoja (siempre lo está). "
                   f"Lo eliminaremos desde ahí.",
            "highlights": {**_trail(visited), path: "toDelete", succ_path: "successor"},
            "tree": copy.deepcopy(tree),
        })
        cur.keys[idx_x] = succ_key
        pasos.append({
            "msg": f"Sobreescribimos {x_orig} con su sucesor {succ_key}. "
                   f"Ahora hay que eliminar {succ_key} de la hoja.",
            "highlights": {**_trail(visited), path: "inserted", succ_path: "toDelete"},
            "tree": copy.deepcopy(tree),
        })
        path = succ_path
        x = succ_key

    # Ahora x está en una hoja en `path`. Lo quitamos.
    hoja = _node_at(tree, path)
    hoja.keys.remove(x)

    if len(hoja.keys) > 0:
        pasos.append({
            "msg": f"Quitamos {x} de la hoja. El nodo era ternario, queda binario "
                   f"y sigue siendo válido.",
            "highlights": {**_trail(visited), path: "inserted"},
            "tree": copy.deepcopy(tree),
        })
        return pasos, tree

    pasos.append({
        "msg": f"Quitamos {x} de la hoja, que queda sin llaves: UNDERFLOW. "
               f"Hay que repararlo.",
        "highlights": {**_trail(visited), path: "imbalance"},
        "tree": copy.deepcopy(tree),
    })

    # Propagar underflow hacia arriba
    cur_path = path
    while cur_path != "":
        parent_path = cur_path[:-1]
        ci = int(cur_path[-1])
        padre = _node_at(tree, parent_path)
        cur_node = padre.children[ci]

        # Caso A: hermano DERECHO ternario -> redistribución
        if ci < len(padre.children) - 1 and len(padre.children[ci + 1].keys) == 2:
            der = padre.children[ci + 1]
            sep_key = padre.keys[ci]
            cur_node.keys.append(sep_key)
            padre.keys[ci] = der.keys.pop(0)
            if not cur_node.es_hoja():
                cur_node.children.append(der.children.pop(0))
            sib_path = parent_path + str(ci + 1)
            pasos.append({
                "msg": f"El hermano DERECHO es ternario: hacemos REDISTRIBUCIÓN. "
                       f"{sep_key} baja desde el padre al nodo vacío, y la menor del "
                       f"hermano sube como nuevo separador.",
                "highlights": {**_trail(visited),
                               cur_path: "inserted",
                               parent_path: "successor",
                               sib_path: "trail"},
                "tree": copy.deepcopy(tree),
            })
            return pasos, tree

        # Caso B: hermano IZQUIERDO ternario -> redistribución
        if ci > 0 and len(padre.children[ci - 1].keys) == 2:
            izq = padre.children[ci - 1]
            sep_key = padre.keys[ci - 1]
            cur_node.keys.insert(0, sep_key)
            padre.keys[ci - 1] = izq.keys.pop()
            if not cur_node.es_hoja():
                cur_node.children.insert(0, izq.children.pop())
            sib_path = parent_path + str(ci - 1)
            pasos.append({
                "msg": f"El hermano IZQUIERDO es ternario: hacemos REDISTRIBUCIÓN. "
                       f"{sep_key} baja desde el padre al nodo vacío, y la mayor del "
                       f"hermano sube como nuevo separador.",
                "highlights": {**_trail(visited),
                               cur_path: "inserted",
                               parent_path: "successor",
                               sib_path: "trail"},
                "tree": copy.deepcopy(tree),
            })
            return pasos, tree

        # Caso C: ningún hermano ternario -> fusión
        if ci < len(padre.children) - 1:
            der = padre.children[ci + 1]
            sep_key = padre.keys[ci]
            padre.keys.pop(ci)
            fusion = Nodo23(keys=[sep_key] + der.keys,
                            children=cur_node.children + der.children)
            padre.children[ci:ci + 2] = [fusion]
            new_ci = ci
            lado = "DERECHO"
        else:
            izq = padre.children[ci - 1]
            sep_key = padre.keys[ci - 1]
            padre.keys.pop(ci - 1)
            fusion = Nodo23(keys=izq.keys + [sep_key],
                            children=izq.children + cur_node.children)
            padre.children[ci - 1:ci + 1] = [fusion]
            new_ci = ci - 1
            lado = "IZQUIERDO"

        new_cur_path = parent_path + str(new_ci)

        if len(padre.keys) > 0:
            pasos.append({
                "msg": f"Ningún hermano es ternario: hacemos FUSIÓN con el "
                       f"{lado}. {sep_key} baja desde el padre al nuevo nodo "
                       f"ternario. El padre sigue siendo válido.",
                "highlights": {**_trail(visited), new_cur_path: "inserted"},
                "tree": copy.deepcopy(tree),
            })
            return pasos, tree

        pasos.append({
            "msg": f"Hacemos FUSIÓN con el hermano {lado}: {sep_key} baja del "
                   f"padre, pero ahora el padre queda sin llaves. El underflow "
                   f"se PROPAGA hacia arriba.",
            "highlights": {**_trail(visited),
                           parent_path: "imbalance",
                           new_cur_path: "trail"},
            "tree": copy.deepcopy(tree),
        })
        cur_path = parent_path

    # La raíz quedó vacía
    if tree.es_hoja():
        pasos.append({
            "msg": "El árbol queda completamente vacío.",
            "highlights": {}, "tree": None,
        })
        return pasos, None

    nueva_raiz = tree.children[0]
    pasos.append({
        "msg": "La raíz quedó sin llaves: la eliminamos y su único hijo pasa a "
               "ser la nueva raíz. El árbol pierde un nivel.",
        "highlights": {"": "inserted"}, "tree": nueva_raiz,
    })
    return pasos, nueva_raiz


# ---------- Árbol de ejemplo ----------
def _arbol_ejemplo():
    return Nodo23(
        keys=[50],
        children=[
            Nodo23(keys=[15, 30], children=[
                Nodo23(keys=[10]),
                Nodo23(keys=[20]),
                Nodo23(keys=[40]),
            ]),
            Nodo23(keys=[70], children=[
                Nodo23(keys=[60]),
                Nodo23(keys=[80, 90]),
            ]),
        ],
    )


# ---------- App ----------
class _Arbol23App:
    def __init__(self, arbol_inicial=None):
        if arbol_inicial is None:
            self.tree = _arbol_ejemplo()
        else:
            self.tree = _convertir23(arbol_inicial)
        self.op = None
        self.idx = 0
        self._build_ui()
        self._redibujar()

    def _build_ui(self):
        self.entrada = widgets.IntText(value=45, description="Llave:",
                                       layout=widgets.Layout(width="170px"))
        self.btn_ins = widgets.Button(description="Insertar", icon="plus",
                                      button_style="success")
        self.btn_bus = widgets.Button(description="Buscar", icon="search",
                                      button_style="warning")
        self.btn_del = widgets.Button(description="Eliminar", icon="trash",
                                      button_style="danger")
        self.btn_ej  = widgets.Button(description="Árbol ejemplo", icon="refresh")
        self.btn_vac = widgets.Button(description="Vaciar")
        for b, op in [(self.btn_ins, "insert"),
                      (self.btn_bus, "search"),
                      (self.btn_del, "delete")]:
            b.on_click(lambda _, o=op: self._iniciar(o))
        self.btn_ej.on_click(lambda _: self._cargar(_arbol_ejemplo()))
        self.btn_vac.on_click(lambda _: self._cargar(None))

        self.btn_prev = widgets.Button(description="Anterior", icon="chevron-left")
        self.btn_next = widgets.Button(description="Siguiente", icon="chevron-right")
        self.btn_apl  = widgets.Button(description="Aplicar", icon="check",
                                       button_style="success")
        self.btn_can  = widgets.Button(description="Cancelar")
        self.btn_prev.on_click(lambda _: self._mover(-1))
        self.btn_next.on_click(lambda _: self._mover(+1))
        self.btn_apl.on_click(lambda _: self._aplicar())
        self.btn_can.on_click(lambda _: self._cancelar())

        self.lbl_paso = widgets.HTML()
        self.lbl_msg  = widgets.HTML()
        self.out = widgets.Output()

        controles = widgets.HBox([self.entrada, self.btn_ins, self.btn_bus,
                                  self.btn_del, self.btn_ej, self.btn_vac])
        nav = widgets.HBox([self.btn_prev, self.btn_next, self.btn_apl, self.btn_can])
        self.caja_pasos = widgets.VBox([self.lbl_paso, self.lbl_msg, nav])
        self.caja_pasos.layout.display = "none"

        leyenda = widgets.HTML(
            '<div style="font-size:11px;color:#64748b;margin-top:6px">'
            '🟡 nodo en revisión · 🟢 encontrado/insertado · 🟣 sucesor · '
            '🔴 a eliminar / no está · 🟠 overflow / underflow</div>')

        self.ui = widgets.VBox([
            widgets.HTML(
                '<h3 style="margin:4px 0">Árboles 2-3 — tutorial paso a paso</h3>'),
            controles, self.out, self.caja_pasos, leyenda,
        ])

    def show(self):
        display(self.ui)

    def _cargar(self, arbol):
        self._cancelar()
        self.tree = arbol
        self._redibujar()

    def _iniciar(self, tipo):
        x = self.entrada.value
        gen = {"insert": _pasos_insert,
               "search": _pasos_search,
               "delete": _pasos_delete}[tipo]
        pasos, final = gen(copy.deepcopy(self.tree) if self.tree else None, x)
        self.op = {"tipo": tipo, "valor": x, "pasos": pasos, "final": final}
        self.idx = 0
        self.caja_pasos.layout.display = ""
        self._redibujar()

    def _cancelar(self):
        self.op = None; self.idx = 0
        self.caja_pasos.layout.display = "none"
        self._redibujar()

    def _mover(self, delta):
        if not self.op:
            return
        self.idx = max(0, min(len(self.op["pasos"]) - 1, self.idx + delta))
        self._redibujar()

    def _aplicar(self):
        if self.op:
            self.tree = self.op["final"]
            self.op = None; self.idx = 0
            self.caja_pasos.layout.display = "none"
            self._redibujar()

    def _redibujar(self):
        if self.op:
            paso = self.op["pasos"][self.idx]
            arbol = paso.get("tree", self.tree)
            hl = paso["highlights"]
            nombres = {"insert": "Inserción", "search": "Búsqueda",
                       "delete": "Eliminación"}
            self.lbl_paso.value = (
                f"<b>{nombres[self.op['tipo']]} de {self.op['valor']}</b> · "
                f"paso {self.idx + 1} / {len(self.op['pasos'])}")
            self.lbl_msg.value = (
                f"<div style='background:#f8fafc;border:1px solid #e2e8f0;"
                f"padding:8px;border-radius:6px;font-size:13px'>{paso['msg']}</div>")
        else:
            arbol, hl = self.tree, {}
        with self.out:
            clear_output(wait=True)
            fig, ax = plt.subplots(figsize=(8, 4.5))
            _dibujar23(ax, arbol, hl)
            plt.tight_layout()
            plt.show()


# ---------- Punto de entrada público ----------
def demo_arbol_23(arbol=None):
    """Lanza el tutorial interactivo de Árboles 2-3 en una celda del notebook.

    Parámetros
    ----------
    arbol : objeto con `keys`/`children`, o con atributo `raiz`, opcional
        Árbol inicial a mostrar. Si se omite, usa un árbol de ejemplo.

    Ejemplos
    --------
    >>> import aed_utilities as aed
    >>> aed.demo_arbol_23()
    >>> aed.demo_arbol_23(mi_arbol)
    """
    _Arbol23App(arbol).show()
