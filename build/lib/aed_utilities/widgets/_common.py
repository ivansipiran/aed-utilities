# aed_utilities/widgets/_common.py
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import ipywidgets as widgets
from IPython.display import display, clear_output


class Nodoe:
    __slots__ = ("height",)
    def __init__(self): self.height = 0


class Nodoi:
    __slots__ = ("izq", "info", "der", "height")
    def __init__(self, izq, info, der):
        self.izq, self.info, self.der = izq, info, der
        self.height = 1 + max(height(izq), height(der))


def es_ext(n): return isinstance(n, Nodoe)


def height(n):
    if es_ext(n): return 0
    if hasattr(n, "height") and n.height is not None: return n.height
    return 1 + max(height(n.izq), height(n.der))


def convertir(obj):
    if obj is None: return Nodoe()
    if hasattr(obj, "raiz"): return convertir(obj.raiz)
    if hasattr(obj, "info") and hasattr(obj, "izq") and hasattr(obj, "der"):
        return Nodoi(convertir(obj.izq), obj.info, convertir(obj.der))
    return Nodoe()


def node_at(root, path):
    n = root
    for d in path: n = n.izq if d == "L" else n.der
    return n


def replace_at(root, path, new_subtree):
    if path == "": return new_subtree
    new_root = copy.deepcopy(root)
    parent = new_root
    for d in path[:-1]: parent = parent.izq if d == "L" else parent.der
    if path[-1] == "L": parent.izq = new_subtree
    else: parent.der = new_subtree
    return new_root


def right_rotation(n):
    return Nodoi(n.izq.izq, n.izq.info, Nodoi(n.izq.der, n.info, n.der))


def left_rotation(n):
    return Nodoi(Nodoi(n.izq, n.info, n.der.izq), n.der.info, n.der.der)


COLOR_MAP = {
    "visiting":     ("#fbbf24", "#b45309"),
    "trail":        ("#fde68a", "#d97706"),
    "found":        ("#34d399", "#047857"),
    "target":       ("#a7f3d0", "#059669"),
    "inserted":     ("#34d399", "#047857"),
    "notfound":     ("#f87171", "#b91c1c"),
    "toDelete":     ("#f87171", "#b91c1c"),
    "duplicate":    ("#f87171", "#b91c1c"),
    "successor":    ("#c4b5fd", "#6d28d9"),
    "pivot":        ("#c4b5fd", "#6d28d9"),
    "pivot_parent": ("#fda4af", "#be123c"),
    "balanced":     ("#bae6fd", "#0284c7"),
    "imbalance":    ("#fb923c", "#c2410c"),
}


def layout(root):
    nodes, edges = [], []
    counter = [0]
    def rec(n, depth, path):
        if es_ext(n):
            x = counter[0]; counter[0] += 1
            nodes.append({"id": path, "x": x, "y": -depth, "external": True})
            return x
        xl = rec(n.izq, depth + 1, path + "L")
        x = counter[0]; counter[0] += 1
        xr = rec(n.der, depth + 1, path + "R")
        nodes.append({
            "id": path, "x": x, "y": -depth, "external": False,
            "info": n.info, "height": height(n),
        })
        edges.append((x, -depth, xl, -depth - 1))
        edges.append((x, -depth, xr, -depth - 1))
        return x
    rec(root, 0, "")
    return nodes, edges


def dibujar(ax, root, highlights, mostrar_alturas=False):
    ax.clear(); ax.set_axis_off()
    nodes, edges = layout(root)
    for x1, y1, x2, y2 in edges:
        ax.plot([x1, x2], [y1, y2], color="#cbd5e1", lw=1.6, zorder=1)
    for nd in nodes:
        st = highlights.get(nd["id"])
        if nd["external"]:
            fc, ec = COLOR_MAP.get(st, ("#e2e8f0", "#94a3b8"))
            ax.add_patch(mpatches.Rectangle(
                (nd["x"] - 0.18, nd["y"] - 0.12), 0.36, 0.24,
                facecolor=fc, edgecolor=ec, lw=2.2 if st else 1.2, zorder=2))
        else:
            fc, ec = COLOR_MAP.get(st, ("#ffffff", "#475569"))
            ax.add_patch(mpatches.Circle(
                (nd["x"], nd["y"]), 0.32,
                facecolor=fc, edgecolor=ec, lw=2.6 if st else 1.6, zorder=2))
            ax.text(nd["x"], nd["y"], str(nd["info"]),
                    ha="center", va="center", fontsize=10, fontweight="bold", zorder=3)
            if mostrar_alturas:
                ax.text(nd["x"] + 0.34, nd["y"] + 0.34, str(nd["height"]),
                        ha="left", va="bottom", fontsize=8, color="#0369a1",
                        style="italic", fontweight="bold", zorder=3)
    if nodes:
        xs = [n["x"] for n in nodes]; ys = [n["y"] for n in nodes]
        ax.set_xlim(min(xs) - 0.9, max(xs) + 0.9)
        ax.set_ylim(min(ys) - 0.7, max(ys) + 0.8)
    ax.set_aspect("equal")