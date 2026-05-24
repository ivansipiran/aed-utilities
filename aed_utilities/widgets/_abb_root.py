"""Tutorial interactivo de INSERCIÓN EN LA RAÍZ para ABBs.

Uso desde un notebook:

    import aed_utilities as aed
    aed.demo_abb_root()
"""

import copy
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

from ._common import (
    Nodoi, Nodoe, es_ext, convertir, node_at, replace_at,
    right_rotation, left_rotation, dibujar,
)

__all__ = ["demo_abb_root"]


# ---------- Generador de pasos ----------
def _pasos_root_insert(root, x):
    pasos = []

    if es_ext(root):
        pasos.append({
            "msg": f"El árbol está vacío. Creamos directamente un nodo interno con la llave {x}, "
                   f"que pasa a ser la raíz.",
            "highlights": {"": "target"},
            "tree": root,
        })
        final = Nodoi(Nodoe(), x, Nodoe())
        pasos.append({
            "msg": f"Listo: {x} es la nueva raíz.",
            "highlights": {"": "inserted"},
            "tree": final,
        })
        return pasos, final

    pasos.append({
        "msg": (f"La inserción en la raíz tiene <b>dos fases</b>: "
                f"<b>(1)</b> descendemos como en una inserción normal hasta donde iría {x}; "
                f"<b>(2)</b> con una secuencia de rotaciones simples, hacemos subir el nuevo "
                f"nodo nivel por nivel hasta que quede en la raíz."),
        "highlights": {"": "visiting"},
        "tree": root,
    })

    # ---------- Fase 1: descenso ----------
    current = root
    path = ""
    visited = {}

    while not es_ext(current):
        if x == current.info:
            pasos.append({
                "msg": f"{x} ya existe en el árbol. No se admiten llaves duplicadas, así que la "
                       f"inserción no se realiza.",
                "highlights": {**visited, path: "duplicate"},
                "tree": root,
            })
            return pasos, copy.deepcopy(root)
        if x < current.info:
            pasos.append({
                "msg": f"<b>Fase 1 (descenso):</b> {x} &lt; {current.info}, bajamos por la "
                       f"IZQUIERDA.",
                "highlights": {**visited, path: "visiting"},
                "tree": root,
            })
            visited[path] = "trail"; path += "L"; current = current.izq
        else:
            pasos.append({
                "msg": f"<b>Fase 1 (descenso):</b> {x} &gt; {current.info}, bajamos por la "
                       f"DERECHA.",
                "highlights": {**visited, path: "visiting"},
                "tree": root,
            })
            visited[path] = "trail"; path += "R"; current = current.der

    # ---------- Fase 2: insertar en la hoja ----------
    leaf_path = path
    pasos.append({
        "msg": f"Llegamos a una hoja externa: confirmamos que {x} no estaba. Insertamos {x} aquí, "
               f"como un nodo hoja, igual que en la inserción tradicional.",
        "highlights": {**visited, leaf_path: "target"},
        "tree": root,
    })
    current_tree = replace_at(root, leaf_path, Nodoi(Nodoe(), x, Nodoe()))

    if leaf_path == "":
        pasos.append({
            "msg": f"Listo: {x} es la raíz.",
            "highlights": {"": "inserted"},
            "tree": current_tree,
        })
        return pasos, current_tree

    pasos.append({
        "msg": (f"{x} ya está insertado, pero como nodo hoja, no como raíz. "
                f"Ahora comienza la <b>fase 2</b>: aplicaremos rotaciones desde abajo hacia "
                f"arriba para que {x} vaya subiendo un nivel a la vez."),
        "highlights": {leaf_path: "inserted"},
        "tree": current_tree,
    })

    # ---------- Fase 3: rotaciones que suben x hasta la raíz ----------
    x_path = leaf_path
    n_rot = 0
    while x_path != "":
        n_rot += 1
        last_dir = x_path[-1]
        parent_path = x_path[:-1]
        parent_node = node_at(current_tree, parent_path)

        if last_dir == "L":
            msg = (
                f"<b>Rotación {n_rot} (DERECHA):</b> {x} es la raíz del subárbol izquierdo "
                f"de {parent_node.info}. "
                f"Aplicamos una rotación derecha:<br>"
                f"&nbsp;&nbsp;• {x} sube y reemplaza a {parent_node.info} como raíz del subárbol.<br>"
                f"&nbsp;&nbsp;• {parent_node.info} baja y queda como hijo derecho de {x}.<br>"
                f"&nbsp;&nbsp;• El antiguo hijo derecho de {x} (que en orden está entre {x} y "
                f"{parent_node.info}) pasa a ser el nuevo hijo izquierdo de {parent_node.info}."
            )
            rotated = right_rotation(parent_node)
        else:
            msg = (
                f"<b>Rotación {n_rot} (IZQUIERDA):</b> {x} es la raíz del subárbol derecho "
                f"de {parent_node.info}. "
                f"Aplicamos una rotación izquierda:<br>"
                f"&nbsp;&nbsp;• {x} sube y reemplaza a {parent_node.info} como raíz del subárbol.<br>"
                f"&nbsp;&nbsp;• {parent_node.info} baja y queda como hijo izquierdo de {x}.<br>"
                f"&nbsp;&nbsp;• El antiguo hijo izquierdo de {x} (que en orden está entre "
                f"{parent_node.info} y {x}) pasa a ser el nuevo hijo derecho de {parent_node.info}."
            )
            rotated = left_rotation(parent_node)

        pasos.append({
            "msg": msg,
            "highlights": {x_path: "pivot", parent_path: "pivot_parent"},
            "tree": current_tree,
        })

        current_tree = replace_at(current_tree, parent_path, rotated)
        x_path = parent_path

        if x_path == "":
            pasos.append({
                "msg": f"Después de esta rotación, {x} subió a la <b>RAÍZ</b> del árbol. "
                       f"El ABB sigue ordenado correctamente.",
                "highlights": {"": "inserted"},
                "tree": current_tree,
            })
        else:
            pasos.append({
                "msg": f"Después de esta rotación, {x} subió un nivel. Continuamos con la "
                       f"siguiente rotación.",
                "highlights": {x_path: "inserted"},
                "tree": current_tree,
            })

    pasos.append({
        "msg": f"¡Listo! {x} se insertó en la raíz mediante <b>{n_rot} rotación(es)</b>. "
               f"Las propiedades del ABB se mantuvieron en todo momento.",
        "highlights": {"": "inserted"},
        "tree": current_tree,
    })
    return pasos, current_tree


# ---------- Árbol de ejemplo ----------
def _arbol_ejemplo():
    return Nodoi(
        Nodoi(Nodoi(Nodoe(), 15, Nodoe()),
              25,
              Nodoi(Nodoe(), 40, Nodoe())),
        50,
        Nodoi(Nodoi(Nodoe(), 60, Nodoe()),
              75,
              Nodoi(Nodoe(), 90, Nodoe())))


# ---------- App ----------
class _RootInsertApp:
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
        self.entrada = widgets.IntText(value=55, description="Llave:",
                                       layout=widgets.Layout(width="170px"))
        self.btn_ins = widgets.Button(description="Insertar en raíz",
                                      icon="arrow-up", button_style="success")
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
            '<div style="font-size:11px;color:#64748b;margin-top:6px;line-height:1.6">'
            '<span style="background:#fbbf24;padding:1px 6px;border-radius:3px">nodo en revisión</span> · '
            '<span style="background:#34d399;padding:1px 6px;border-radius:3px">nuevo nodo / posición actual</span> · '
            '<span style="background:#c4b5fd;padding:1px 6px;border-radius:3px">pivote (sube)</span> · '
            '<span style="background:#fda4af;padding:1px 6px;border-radius:3px">nodo que baja</span> · '
            '<span style="background:#f87171;padding:1px 6px;border-radius:3px">ya existía</span> · '
            '<span style="background:#e2e8f0;padding:1px 6px;border-radius:3px;border:1px solid #94a3b8">☐ hoja externa</span>'
            '</div>')

        self.ui = widgets.VBox([
            widgets.HTML(
                '<h3 style="margin:4px 0">Inserción en la raíz — tutorial paso a paso</h3>'),
            widgets.HTML(
                '<div style="font-size:12px;color:#475569;margin-bottom:6px">'
                'Inserta una llave nueva y obsérvala subir hasta la raíz mediante '
                'una secuencia de rotaciones simples (derechas e izquierdas).</div>'),
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
        pasos, final = _pasos_root_insert(copy.deepcopy(self.tree), x)
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
                f"<b>Inserción en raíz de {self.op['valor']}</b> · "
                f"paso {self.idx + 1} / {len(self.op['pasos'])}")
            self.lbl_msg.value = (
                f"<div style='background:#f8fafc;border:1px solid #e2e8f0;"
                f"padding:8px;border-radius:6px;font-size:13px;line-height:1.5'>"
                f"{paso['msg']}</div>")
        else:
            arbol, hl = self.tree, {}
        with self.out:
            clear_output(wait=True)
            fig, ax = plt.subplots(figsize=(8, 4.5))
            dibujar(ax, arbol, hl)
            plt.tight_layout()
            plt.show()


# ---------- Punto de entrada público ----------
def demo_abb_root(arbol=None):
    """Lanza el tutorial interactivo de inserción en la raíz para ABBs.

    Parámetros
    ----------
    arbol : Arbol | Nodoi | Nodoe | None, opcional
        Árbol inicial a mostrar. Si se omite, usa un árbol de ejemplo.

    Ejemplos
    --------
    >>> import aed_utilities as aed
    >>> aed.demo_abb_root()
    >>> aed.demo_abb_root(mi_arbol)
    """
    _RootInsertApp(arbol).show()