"""Tutorial interactivo de Árboles AVL (versión recursiva del notebook).

Uso desde un notebook:

    import aed_utilities as aed
    aed.demo_avl()
"""

import copy
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

from ._common import (
    Nodoi, Nodoe, es_ext, height, convertir, node_at,
    right_rotation, left_rotation, dibujar,
)

__all__ = ["demo_avl"]


def _refresh_height(n):
    if not es_ext(n):
        n.height = 1 + max(height(n.izq), height(n.der))


def _replace_at_avl(root, path, new_subtree):
    """Como replace_at, pero recomputa las alturas de los ancestros del path."""
    if path == "":
        return new_subtree
    new_root = copy.deepcopy(root)
    nodes_on_path = [new_root]
    for d in path[:-1]:
        nodes_on_path.append(nodes_on_path[-1].izq if d == "L" else nodes_on_path[-1].der)
    parent = nodes_on_path[-1]
    if path[-1] == "L":
        parent.izq = new_subtree
    else:
        parent.der = new_subtree
    for node in reversed(nodes_on_path):
        _refresh_height(node)
    return new_root


# ---------- Inserción AVL sin pasos (para construir el árbol de ejemplo) ----------
def _avl_insert_simple(node, x):
    if es_ext(node):
        return Nodoi(Nodoe(), x, Nodoe())
    if x == node.info:
        return node
    if x < node.info:
        p = Nodoi(_avl_insert_simple(node.izq, x), node.info, node.der)
        if height(p.izq) > height(p.der) + 1:
            if x < p.izq.info:
                p = right_rotation(p)
            else:
                p = right_rotation(Nodoi(left_rotation(p.izq), p.info, p.der))
    else:
        p = Nodoi(node.izq, node.info, _avl_insert_simple(node.der, x))
        if height(p.der) > height(p.izq) + 1:
            if x > p.der.info:
                p = left_rotation(p)
            else:
                p = left_rotation(Nodoi(p.izq, p.info, right_rotation(p.der)))
    return p


def _arbol_ejemplo():
    """Construye el árbol del notebook: insert(20), insert(40), insert(80), insert(10)."""
    a = Nodoe()
    for v in [20, 40, 80, 10]:
        a = _avl_insert_simple(a, v)
    return a


# ---------- Generador de pasos para una inserción AVL ----------
def _pasos_avl_insert(root, x):
    pasos = []
    current = [copy.deepcopy(root)]  # contenedor mutable

    # Árbol vacío
    if es_ext(current[0]):
        pasos.append({
            "msg": f"El árbol está vacío. Insertamos {x} como nueva raíz (altura 1).",
            "highlights": {"": "target"},
            "tree": current[0],
        })
        final = Nodoi(Nodoe(), x, Nodoe())
        pasos.append({
            "msg": f"Listo: {x} es la raíz. La condición AVL se cumple trivialmente.",
            "highlights": {"": "inserted"},
            "tree": final,
        })
        return pasos, final

    # Verificar duplicado
    n = current[0]
    while not es_ext(n):
        if x == n.info:
            pasos.append({
                "msg": (f"{x} ya existe en el árbol. La implementación del notebook usa "
                        f"<code>assert x != self.info</code>, por lo que no se permite "
                        f"insertar duplicados."),
                "highlights": {"": "visiting"},
                "tree": current[0],
            })
            return pasos, copy.deepcopy(root)
        n = n.izq if x < n.info else n.der

    pasos.append({
        "msg": (f"<b>Algoritmo AVL recursivo:</b> primero descendemos hasta donde insertar {x} "
                f"(igual que en un ABB normal). Luego, en el <b>ascenso recursivo</b>, en cada "
                f"nivel verificamos la condición de balance "
                f"|h(izq) − h(der)| ≤ 1 y aplicamos rotaciones si se rompe."),
        "highlights": {"": "visiting"},
        "tree": current[0],
    })

    def rec(subtree_path, visited):
        node = node_at(current[0], subtree_path)

        if es_ext(node):
            new_node = Nodoi(Nodoe(), x, Nodoe())
            current[0] = _replace_at_avl(current[0], subtree_path, new_node)
            pasos.append({
                "msg": f"Llegamos a una hoja externa. Insertamos {x} como nodo interno de "
                       f"altura 1.",
                "highlights": {**visited, subtree_path: "inserted"},
                "tree": current[0],
            })
            return

        new_visited = {**visited, subtree_path: "trail"}

        if x < node.info:
            pasos.append({
                "msg": f"<b>Descenso:</b> en {node.info}, {x} &lt; {node.info}, "
                       f"bajamos por la IZQUIERDA.",
                "highlights": {**visited, subtree_path: "visiting"},
                "tree": current[0],
            })
            rec(subtree_path + "L", new_visited)

            node = node_at(current[0], subtree_path)
            h_izq, h_der = height(node.izq), height(node.der)

            if h_izq > h_der + 1:
                left_child = node.izq
                if x < left_child.info:
                    pasos.append({
                        "msg": (f"<b>Ascenso en {node.info}:</b> h(izq)={h_izq}, "
                                f"h(der)={h_der}. ¡La condición AVL se rompe! "
                                f"{x} &lt; {left_child.info}: fue por IZQUIERDA-IZQUIERDA → "
                                f"<b>inserción exterior (LL, zig-zig)</b>. "
                                f"Aplicamos una <b>rotación DERECHA simple</b> en {node.info}."),
                        "highlights": {subtree_path: "imbalance",
                                       subtree_path + "L": "pivot"},
                        "tree": current[0],
                    })
                    rotated = right_rotation(node)
                    current[0] = _replace_at_avl(current[0], subtree_path, rotated)
                    pasos.append({
                        "msg": (f"Después de la rotación derecha, {left_child.info} sube y "
                                f"{node.info} baja. La condición AVL vuelve a cumplirse en "
                                f"este subárbol, y su altura no aumentó respecto de antes de "
                                f"la inserción, así que no hay más desbalances que arreglar."),
                        "highlights": {subtree_path: "balanced"},
                        "tree": current[0],
                    })
                else:
                    pasos.append({
                        "msg": (f"<b>Ascenso en {node.info}:</b> h(izq)={h_izq}, "
                                f"h(der)={h_der}. ¡La condición AVL se rompe! "
                                f"{x} &gt; {left_child.info}: fue por IZQUIERDA-DERECHA → "
                                f"<b>inserción interior (LR, zig-zag)</b>. "
                                f"Necesitamos una <b>rotación DOBLE</b>: primero IZQUIERDA en "
                                f"{left_child.info}, luego DERECHA en {node.info}."),
                        "highlights": {subtree_path: "imbalance",
                                       subtree_path + "L": "pivot_parent"},
                        "tree": current[0],
                    })
                    rotated_left = left_rotation(left_child)
                    intermediate = Nodoi(rotated_left, node.info, node.der)
                    current[0] = _replace_at_avl(current[0], subtree_path, intermediate)
                    pasos.append({
                        "msg": (f"<b>Paso 1 de 2:</b> rotación IZQUIERDA en el hijo izquierdo "
                                f"({left_child.info}). El subárbol completo aún está "
                                f"desbalanceado en {node.info}; esta rotación interna preparó "
                                f"el terreno para la siguiente."),
                        "highlights": {subtree_path: "imbalance",
                                       subtree_path + "L": "pivot"},
                        "tree": current[0],
                    })
                    intermediate_node = node_at(current[0], subtree_path)
                    rotated_final = right_rotation(intermediate_node)
                    current[0] = _replace_at_avl(current[0], subtree_path, rotated_final)
                    pasos.append({
                        "msg": (f"<b>Paso 2 de 2:</b> rotación DERECHA en el subárbol completo. "
                                f"Ahora todos los nodos cumplen la condición AVL."),
                        "highlights": {subtree_path: "balanced"},
                        "tree": current[0],
                    })
            else:
                pasos.append({
                    "msg": (f"<b>Ascenso en {node.info}:</b> h(izq)={h_izq}, h(der)={h_der}, "
                            f"|diferencia| ≤ 1. La condición AVL se mantiene; no se necesita "
                            f"rotación aquí."),
                    "highlights": {subtree_path: "balanced"},
                    "tree": current[0],
                })

        else:  # x > node.info
            pasos.append({
                "msg": f"<b>Descenso:</b> en {node.info}, {x} &gt; {node.info}, "
                       f"bajamos por la DERECHA.",
                "highlights": {**visited, subtree_path: "visiting"},
                "tree": current[0],
            })
            rec(subtree_path + "R", new_visited)

            node = node_at(current[0], subtree_path)
            h_izq, h_der = height(node.izq), height(node.der)

            if h_der > h_izq + 1:
                right_child = node.der
                if x > right_child.info:
                    pasos.append({
                        "msg": (f"<b>Ascenso en {node.info}:</b> h(izq)={h_izq}, "
                                f"h(der)={h_der}. ¡La condición AVL se rompe! "
                                f"{x} &gt; {right_child.info}: fue por DERECHA-DERECHA → "
                                f"<b>inserción exterior (RR, zag-zag)</b>. "
                                f"Aplicamos una <b>rotación IZQUIERDA simple</b>."),
                        "highlights": {subtree_path: "imbalance",
                                       subtree_path + "R": "pivot"},
                        "tree": current[0],
                    })
                    rotated = left_rotation(node)
                    current[0] = _replace_at_avl(current[0], subtree_path, rotated)
                    pasos.append({
                        "msg": (f"Después de la rotación izquierda, {right_child.info} sube y "
                                f"{node.info} baja. AVL restaurado."),
                        "highlights": {subtree_path: "balanced"},
                        "tree": current[0],
                    })
                else:
                    pasos.append({
                        "msg": (f"<b>Ascenso en {node.info}:</b> h(izq)={h_izq}, "
                                f"h(der)={h_der}. ¡La condición AVL se rompe! "
                                f"{x} &lt; {right_child.info}: fue por DERECHA-IZQUIERDA → "
                                f"<b>inserción interior (RL, zag-zig)</b>. "
                                f"<b>Rotación DOBLE</b>: primero DERECHA en "
                                f"{right_child.info}, luego IZQUIERDA en {node.info}."),
                        "highlights": {subtree_path: "imbalance",
                                       subtree_path + "R": "pivot_parent"},
                        "tree": current[0],
                    })
                    rotated_right = right_rotation(right_child)
                    intermediate = Nodoi(node.izq, node.info, rotated_right)
                    current[0] = _replace_at_avl(current[0], subtree_path, intermediate)
                    pasos.append({
                        "msg": (f"<b>Paso 1 de 2:</b> rotación DERECHA en el hijo derecho "
                                f"({right_child.info})."),
                        "highlights": {subtree_path: "imbalance",
                                       subtree_path + "R": "pivot"},
                        "tree": current[0],
                    })
                    intermediate_node = node_at(current[0], subtree_path)
                    rotated_final = left_rotation(intermediate_node)
                    current[0] = _replace_at_avl(current[0], subtree_path, rotated_final)
                    pasos.append({
                        "msg": (f"<b>Paso 2 de 2:</b> rotación IZQUIERDA en el subárbol "
                                f"completo. AVL restaurado."),
                        "highlights": {subtree_path: "balanced"},
                        "tree": current[0],
                    })
            else:
                pasos.append({
                    "msg": (f"<b>Ascenso en {node.info}:</b> h(izq)={h_izq}, h(der)={h_der}, "
                            f"|diferencia| ≤ 1. La condición AVL se mantiene; no se necesita "
                            f"rotación aquí."),
                    "highlights": {subtree_path: "balanced"},
                    "tree": current[0],
                })

    rec("", {})

    pasos.append({
        "msg": f"¡Listo! {x} se insertó manteniendo la propiedad AVL en todo el árbol.",
        "highlights": {"": "inserted"},
        "tree": current[0],
    })
    return pasos, current[0]


# ---------- App ----------
class _AVLApp:
    def __init__(self, arbol_inicial=None):
        if arbol_inicial is None:
            self.tree = _arbol_ejemplo()
        else:
            self.tree = convertir(arbol_inicial)
        self.op = None
        self.idx = 0
        self._build_ui()
        self._redibujar()

    def _build_ui(self):
        self.entrada = widgets.IntText(value=15, description="Llave:",
                                       layout=widgets.Layout(width="170px"))
        self.btn_ins = widgets.Button(description="Insertar (AVL)", icon="plus",
                                      button_style="success")
        self.btn_ej = widgets.Button(description="Árbol ejemplo", icon="refresh")
        self.btn_vac = widgets.Button(description="Vaciar")
        self.btn_ins.on_click(lambda _: self._iniciar())
        self.btn_ej.on_click(lambda _: self._cargar(_arbol_ejemplo()))
        self.btn_vac.on_click(lambda _: self._cargar(Nodoe()))

        self.btn_prev = widgets.Button(description="Anterior", icon="chevron-left")
        self.btn_next = widgets.Button(description="Siguiente", icon="chevron-right")
        self.btn_apl = widgets.Button(description="Aplicar", icon="check",
                                      button_style="success")
        self.btn_can = widgets.Button(description="Cancelar")
        self.btn_prev.on_click(lambda _: self._mover(-1))
        self.btn_next.on_click(lambda _: self._mover(+1))
        self.btn_apl.on_click(lambda _: self._aplicar())
        self.btn_can.on_click(lambda _: self._cancelar())

        self.lbl_paso = widgets.HTML()
        self.lbl_msg = widgets.HTML()
        self.out = widgets.Output()

        controles = widgets.HBox([self.entrada, self.btn_ins,
                                  self.btn_ej, self.btn_vac])
        nav = widgets.HBox([self.btn_prev, self.btn_next,
                            self.btn_apl, self.btn_can])
        self.caja_pasos = widgets.VBox([self.lbl_paso, self.lbl_msg, nav])
        self.caja_pasos.layout.display = "none"

        leyenda = widgets.HTML(
            '<div style="font-size:11px;color:#64748b;margin-top:6px;line-height:1.8">'
            '<span style="background:#fbbf24;padding:1px 6px;border-radius:3px">visitando</span> '
            '<span style="background:#34d399;padding:1px 6px;border-radius:3px">insertado</span> '
            '<span style="background:#bae6fd;padding:1px 6px;border-radius:3px">AVL OK</span> '
            '<span style="background:#fb923c;padding:1px 6px;border-radius:3px">desbalance</span> '
            '<span style="background:#c4b5fd;padding:1px 6px;border-radius:3px">pivote (sube)</span> '
            '<span style="background:#fda4af;padding:1px 6px;border-radius:3px">baja / prepara</span>'
            '<br><i style="color:#0369a1">el número en azul junto a cada nodo es su altura</i>'
            '</div>')

        self.ui = widgets.VBox([
            widgets.HTML(
                '<h3 style="margin:4px 0">Árboles AVL — tutorial paso a paso</h3>'),
            widgets.HTML(
                '<div style="font-size:12px;color:#475569;margin-bottom:6px">'
                'Inserción recursiva con rebalanceo: tras descender e insertar como en un ABB '
                'normal, el algoritmo verifica la condición |h(izq) − h(der)| ≤ 1 en cada nivel '
                'del ascenso y aplica rotaciones simples (LL, RR) o dobles (LR, RL) si se rompe. '
                'A lo más se necesita una rotación (simple o doble) por inserción.</div>'),
            controles, self.out, self.caja_pasos, leyenda,
        ])

    def show(self):
        display(self.ui)

    def _cargar(self, arbol):
        self._cancelar()
        self.tree = arbol
        self._redibujar()

    def _iniciar(self):
        x = self.entrada.value
        pasos, final = _pasos_avl_insert(copy.deepcopy(self.tree), x)
        self.op = {"valor": x, "pasos": pasos, "final": final}
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
            self.lbl_paso.value = (
                f"<b>Inserción AVL de {self.op['valor']}</b> · "
                f"paso {self.idx + 1} / {len(self.op['pasos'])}")
            self.lbl_msg.value = (
                f"<div style='background:#f8fafc;border:1px solid #e2e8f0;"
                f"padding:8px;border-radius:6px;font-size:13px;line-height:1.5'>"
                f"{paso['msg']}</div>")
        else:
            arbol, hl = self.tree, {}
        with self.out:
            clear_output(wait=True)
            fig, ax = plt.subplots(figsize=(8, 4.8))
            dibujar(ax, arbol, hl, mostrar_alturas=True)
            plt.tight_layout()
            plt.show()


# ---------- Punto de entrada público ----------
def demo_avl(arbol=None):
    """Lanza el tutorial interactivo de inserción en árboles AVL.

    Parámetros
    ----------
    arbol : Arbol | Nodoi | Nodoe | None, opcional
        Árbol inicial a mostrar. Si se omite, construye el ejemplo del notebook
        insertando 20, 40, 80, 10.

    Ejemplos
    --------
    >>> import aed_utilities as aed
    >>> aed.demo_avl()
    >>> aed.demo_avl(mi_arbol)
    """
    _AVLApp(arbol).show()