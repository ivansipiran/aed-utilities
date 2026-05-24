"""Tutorial interactivo de Árboles de Búsqueda Binaria para Jupyter.

Uso desde un notebook:

    import aed_utilities as aed
    aed.demo_abb()
"""

import copy
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

from ._common import (
    Nodoi, Nodoe, es_ext, convertir, replace_at, dibujar,
)

__all__ = ["demo_abb"]


# ---------- Generadores de pasos ----------
def _trail(d):
    return dict(d)


def _set_info(root, path, info):
    """Modifica in-place la llave del nodo en `path`. Asume que `root` ya es copia."""
    n = root
    for d in path:
        n = n.izq if d == "L" else n.der
    n.info = info


def _pasos_insert(root, x):
    pasos, visited = [], {}
    if es_ext(root):
        pasos.append({
            "msg": f"El árbol está vacío (hoja externa ☐). Se reemplaza directamente por un "
                   f"nodo interno con la llave {x}.",
            "highlights": {"": "target"},
        })
        nuevo = Nodoi(Nodoe(), x, Nodoe())
        pasos.append({
            "msg": f"Listo. La hoja externa pasó a ser un nodo interno con llave {x} y dos "
                   f"nuevas hojas externas como hijos.",
            "highlights": {"": "inserted"}, "tree": nuevo,
        })
        return pasos, nuevo

    n, path = root, ""
    pasos.append({
        "msg": f"Para insertar se hace una búsqueda que debe ser infructuosa. Empezamos en la "
               f"raíz (llave {n.info}).",
        "highlights": {"": "visiting"},
    })

    while not es_ext(n):
        if x == n.info:
            pasos.append({
                "msg": f"{x} = {n.info}: la llave ya existe. Un ABB no admite duplicados, no se "
                       f"inserta nada.",
                "highlights": {**_trail(visited), path: "duplicate"},
            })
            return pasos, copy.deepcopy(root)
        if x < n.info:
            pasos.append({
                "msg": f"Comparamos: {x} < {n.info}. Bajamos hacia el subárbol IZQUIERDO.",
                "highlights": {**_trail(visited), path: "visiting"},
            })
            visited[path] = "trail"; path += "L"; n = n.izq
        else:
            pasos.append({
                "msg": f"Comparamos: {x} > {n.info}. Bajamos hacia el subárbol DERECHO.",
                "highlights": {**_trail(visited), path: "visiting"},
            })
            visited[path] = "trail"; path += "R"; n = n.der

    pasos.append({
        "msg": f"Llegamos a una hoja externa (☐). La búsqueda terminó infructuosa, confirmando "
               f"que {x} no estaba.",
        "highlights": {**_trail(visited), path: "target"},
    })
    nuevo_root = replace_at(root, path, Nodoi(Nodoe(), x, Nodoe()))
    pasos.append({
        "msg": f"La hoja externa se reemplaza por un nodo interno con la llave {x} y dos nuevas "
               f"hojas externas.",
        "highlights": {**_trail(visited), path: "inserted"}, "tree": nuevo_root,
    })
    return pasos, nuevo_root


def _pasos_search(root, x):
    pasos, visited = [], {}
    if es_ext(root):
        pasos.append({"msg": f"El árbol está vacío. La llave {x} no está.",
                      "highlights": {"": "notfound"}})
        return pasos, copy.deepcopy(root)

    n, path = root, ""
    pasos.append({"msg": f"Comenzamos la búsqueda de {x} en la raíz (llave {n.info}).",
                  "highlights": {"": "visiting"}})
    while not es_ext(n):
        if x == n.info:
            pasos.append({"msg": f"{x} = {n.info}. ¡Búsqueda exitosa! La llave fue encontrada.",
                          "highlights": {**_trail(visited), path: "found"}})
            return pasos, copy.deepcopy(root)
        if x < n.info:
            pasos.append({"msg": f"{x} < {n.info}: la llave, si existe, está a la IZQUIERDA.",
                          "highlights": {**_trail(visited), path: "visiting"}})
            visited[path] = "trail"; path += "L"; n = n.izq
        else:
            pasos.append({"msg": f"{x} > {n.info}: la llave, si existe, está a la DERECHA.",
                          "highlights": {**_trail(visited), path: "visiting"}})
            visited[path] = "trail"; path += "R"; n = n.der
    pasos.append({"msg": f"Llegamos a una hoja externa. La búsqueda concluye infructuosa: {x} "
                         f"NO está en el árbol.",
                  "highlights": {**_trail(visited), path: "notfound"}})
    return pasos, copy.deepcopy(root)


def _pasos_delete(root, x):
    pasos, visited = [], {}
    if es_ext(root):
        pasos.append({"msg": "El árbol está vacío: no hay nada que eliminar.",
                      "highlights": {"": "notfound"}})
        return pasos, copy.deepcopy(root)

    n, path = root, ""
    pasos.append({"msg": f"Primero buscamos la llave {x}, empezando en la raíz (llave {n.info}).",
                  "highlights": {"": "visiting"}})
    while not es_ext(n) and n.info != x:
        if x < n.info:
            pasos.append({"msg": f"{x} < {n.info}: seguimos por el subárbol izquierdo.",
                          "highlights": {**_trail(visited), path: "visiting"}})
            visited[path] = "trail"; path += "L"; n = n.izq
        else:
            pasos.append({"msg": f"{x} > {n.info}: seguimos por el subárbol derecho.",
                          "highlights": {**_trail(visited), path: "visiting"}})
            visited[path] = "trail"; path += "R"; n = n.der

    if es_ext(n):
        pasos.append({"msg": f"Llegamos a una hoja externa: {x} no está en el árbol. No se hace "
                             f"ningún cambio.",
                      "highlights": {**_trail(visited), path: "notfound"}})
        return pasos, copy.deepcopy(root)

    izq_int, der_int = not es_ext(n.izq), not es_ext(n.der)

    # Caso A: nodo sin hijos internos
    if not izq_int and not der_int:
        pasos.append({"msg": f"Encontramos {x}. Ambos hijos son hojas externas: caso más simple.",
                      "highlights": {**_trail(visited), path: "toDelete"}})
        nuevo = replace_at(root, path, Nodoe())
        pasos.append({"msg": "El nodo desaparece y en su lugar queda una hoja externa (☐).",
                      "highlights": {**_trail(visited), path: "target"}, "tree": nuevo})
        return pasos, nuevo

    # Caso B: exactamente un hijo interno
    if izq_int != der_int:
        lado = "izquierdo" if izq_int else "derecho"
        child_path = path + ("L" if izq_int else "R")
        pasos.append({"msg": f"Encontramos {x}. Tiene un único hijo interno (subárbol {lado}).",
                      "highlights": {**_trail(visited), path: "toDelete", child_path: "successor"}})
        hijo = copy.deepcopy(n.izq if izq_int else n.der)
        nuevo = replace_at(root, path, hijo)
        pasos.append({"msg": f"El padre de {x} pasa a apuntar directamente al único hijo de {x}.",
                      "highlights": {**_trail(visited), path: "inserted"}, "tree": nuevo})
        return pasos, nuevo

    # Caso C: dos hijos internos -> sucesor
    pasos.append({"msg": f"Encontramos {x}. Tiene DOS hijos internos: buscaremos su sucesor "
                         f"(mínimo del subárbol derecho).",
                  "highlights": {**_trail(visited), path: "toDelete"}})
    succ, succ_path = n.der, path + "R"
    pasos.append({"msg": "Damos un paso a la DERECHA para entrar al subárbol derecho.",
                  "highlights": {**_trail(visited), path: "toDelete", succ_path: "visiting"}})
    while not es_ext(succ.izq):
        succ = succ.izq; succ_path += "L"
        pasos.append({"msg": "Bajamos por la IZQUIERDA mientras haya hijo izquierdo interno.",
                      "highlights": {**_trail(visited), path: "toDelete", succ_path: "visiting"}})
    succ_val = succ.info
    pasos.append({"msg": f"El sucesor es {succ_val}: no tiene hijo izquierdo interno, así que "
                         f"es fácil de quitar.",
                  "highlights": {**_trail(visited), path: "toDelete", succ_path: "successor"}})
    t1 = replace_at(root, succ_path, copy.deepcopy(succ.der))
    pasos.append({"msg": f"Quitamos el nodo sucesor {succ_val}: en su lugar queda su hijo derecho.",
                  "highlights": {**_trail(visited), path: "toDelete"}, "tree": t1})
    t2 = copy.deepcopy(t1)
    _set_info(t2, path, succ_val)
    pasos.append({"msg": f"Finalmente escribimos el valor del sucesor ({succ_val}) en lugar de "
                         f"{x}. El ABB queda ordenado.",
                  "highlights": {**_trail(visited), path: "inserted"}, "tree": t2})
    return pasos, t2


# ---------- Árbol de ejemplo (del notebook) ----------
def _arbol_ejemplo():
    return Nodoi(
        Nodoi(Nodoi(Nodoe(), 15, Nodoe()),
              20,
              Nodoi(Nodoi(Nodoe(), 30, Nodoe()), 35, Nodoe())),
        42,
        Nodoi(Nodoi(Nodoi(Nodoi(Nodoe(), 65, Nodoe()),
                          72,
                          Nodoi(Nodoe(), 81, Nodoe())),
                    90, Nodoe()),
              95, Nodoe()))


# ---------- App ----------
class _ABBApp:
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
        self.entrada = widgets.IntText(value=50, description="Llave:",
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
        self.btn_vac.on_click(lambda _: self._cargar(Nodoe()))

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
            '🔴 a eliminar / no está · ⬜ hoja externa (Nodoe)</div>')

        self.ui = widgets.VBox([
            widgets.HTML(
                '<h3 style="margin:4px 0">Árboles de Búsqueda Binaria — '
                'tutorial paso a paso</h3>'),
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
        pasos, final = gen(copy.deepcopy(self.tree), x)
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
            nombres = {"insert": "Inserción", "search": "Búsqueda", "delete": "Eliminación"}
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
            dibujar(ax, arbol, hl)
            plt.tight_layout()
            plt.show()


# ---------- Punto de entrada público ----------
def demo_abb(arbol=None):
    """Lanza el tutorial interactivo de ABB en una celda del notebook.

    Parámetros
    ----------
    arbol : Arbol | Nodoi | Nodoe | None, opcional
        Árbol inicial a mostrar. Si se omite, usa un árbol de ejemplo.

    Ejemplos
    --------
    >>> import aed_utilities as aed
    >>> aed.demo_abb()
    >>> aed.demo_abb(mi_arbol)
    """
    _ABBApp(arbol).show()