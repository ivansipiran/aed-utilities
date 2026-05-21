from graphviz import Source
from IPython.display import display_svg, SVG,display
import numpy as np

class SegmentationFault(Exception):
    pass

class LinkedListDrawer:
  def __init__(self, **kwargs):
    self.strHeader = kwargs.get('strHeader', '')
    self.fieldLink = kwargs.get('fieldLink', '')
    self.fieldHeader = kwargs.get('fieldHeader', '')
    self.fieldData = kwargs.get('fieldData', '')
    self.fieldReverseLink = kwargs.get('fieldReverseLink', None)
    self.pointers = kwargs.get('pointers', {}) # dict of [int] -> [str]
  
  def draw_linked_list(self, nList):
    listStr = ''

    if self.strHeader!="":
      listStr = f'HEAD [shape=plaintext label="{self.strHeader}"];\n'
    listStr += 'NULL [shape=square label=""];\n'

    for position, label in self.pointers.items():
      listStr += f'_label_pos{position} [shape=plaintext label="{label}"];\n'

    listStr += 'node[shape=circle];\n'
    if self.strHeader != "":
      listStr += 'HEAD -> '

    p = getattr(nList, self.fieldHeader)
    position = 0
    pointedNodes = []
    while p is not None:
      nodeData = str(getattr(p, self.fieldData))
      p = getattr(p, self.fieldLink)
    
      if position in self.pointers:
        listStr += f'_nodo_pos{position} -> '
        pointedNodes.append(f'_nodo_pos{position} [shape=circle label="{nodeData}"];\n'
                                    f'_label_pos{position} -> _nodo_pos{position};\n'
                                    f'{{ rank="same"; _label_pos{position}; _nodo_pos{position} }};')
      else:
        listStr += f'{nodeData} -> '
      position+=1
  
    listStr += 'NULL;\n'

    listStr += '\n'.join(pointedNodes)
    if position in self.pointers: # Last position is NULL
      listStr += f'''
        _label_pos{position} -> NULL;
        {{ rank="same"; _label_pos{position}; NULL }} '''

    if len(self.pointers) > 1 and max(self.pointers) > position:
      raise SegmentationFault(f'Tried to draw a pointer to node {max(self.pointers)}, but list length is {position}.')

    src = Source('digraph "Lista" { rankdir=LR; ' + listStr +' }')
    src.render('lista.gv', view=True)
    display(SVG(src.pipe(format='svg')))
  
  def ascending_list(self, nList):
    p = getattr(getattr(nList, self.fieldHeader), self.fieldLink)
    while p is not getattr(nList, self.fieldHeader):
      yield getattr(p, self.fieldData)
      p = getattr(p, self.fieldLink)

  def descending_list(self, nList):
    p = getattr(getattr(nList, self.fieldHeader), self.fieldReverseLink)
    while p is not getattr(nList, self.fieldHeader):
      yield getattr(p, self.fieldData)
      p = getattr(p, self.fieldReverseLink)

  def draw_double_linked_list(self, nList):
    listStrAsc = "node[shape=circle]; "
    listaAsc = [x for x in self.ascending_list(nList)]
    for i, x in enumerate(listaAsc):
      listStrAsc = listStrAsc + str(x)
      if i < len(listaAsc) - 1:
        listStrAsc = listStrAsc + ' -> '
  
    listStrDesc = ""

    listaDesc = [x for x in self.descending_list(nList)]
    for i, x in enumerate(listaDesc):
      listStrDesc = listStrDesc + str(x)
      if i < len(listaDesc) - 1:
        listStrDesc = listStrDesc + ' -> '
  
    src = Source('digraph "Lista" { rankdir=LR; ' + listStrAsc + ' ' + listStrDesc +' }')
    src.render('lista.gv', view=True)
    display(SVG(src.pipe(format='svg')))


class PositionNode:
  def __init__(self, left, info, right, nodetype, code):
        self.left=left
        self.info=info
        self.right=right
        self.x = 0.0
        self.y = 0.0
        self.nodetype = nodetype
        self.code = code

class BinaryTreeDrawer:
  def __init__(self, fieldData, fieldLeft, fieldRight, classNone=None, drawNull = False, shapeInternal='circle'):
    self.nameInfo = fieldData
    self.nameLeft = fieldLeft
    self.nameRight = fieldRight
    self.offset = 0.35
    self.classNone = classNone
    self.drawNull = drawNull
    self.counterNull = 0
    self.counterNodes = 0
    self.shapeInternal = shapeInternal
    
  def gen_code(self):
    code = "node" + str(self.counterNodes)
    self.counterNodes = self.counterNodes + 1
    return code

  def copy_tree(self, node):
    if self.classNone is not None:
      if isinstance(node, self.classNone):
        if not hasattr(node, self.nameInfo):
          if not self.drawNull:
            return None
          else:
            newNode = PositionNode(None, "", None, "square", "null" + str(self.counterNull))
            self.counterNull = self.counterNull + 1
            return newNode
        else:
          if not self.drawNull:
            return PositionNode(None, getattr(node, self.nameInfo), None, "square", self.gen_code())
          else:
            newNode1 = PositionNode(None, "", None, "square", "null" + str(self.counterNull))
            self.counterNull = self.counterNull + 1
            newNode2 = PositionNode(None, "", None, "square", "null" + str(self.counterNull))
            self.counterNull = self.counterNull + 1
            return PositionNode(newNode1, getattr(node, self.nameInfo), newNode2, self.shapeInternal, self.gen_code())
    else:
      if node is None:
        if not self.drawNull:
          return None
        else:
          newNode = PositionNode(None, "", None, "square", "null" + str(self.counterNull))
          self.counterNull = self.counterNull + 1
          return newNode
  
    newLeft = self.copy_tree(getattr(node, self.nameLeft))
    newRight = self.copy_tree(getattr(node, self.nameRight))

    return PositionNode(newLeft, getattr(node, self.nameInfo), newRight, self.shapeInternal, self.gen_code())

  def update_position(self, node, shiftX, shiftY):
    if node is not None:
      self.update_position(node.left, shiftX, shiftY)
      self.update_position(node.right, shiftX, shiftY)
      node.x = node.x + shiftX
      node.y = node.y + shiftY

  def compute_position(self, node):
    if node.left is None and node.right is None:
      return 0.0,-self.offset/3,self.offset/3
  
    if node.left is not None:
      center1, min1, max1 = self.compute_position(node.left)
    else:
      min1 = 0.0
      max1 = 0.0

    if node.right is not None:  
      center2, min2, max2 = self.compute_position(node.right)
    else:
      min2 = 0.0
      max2 = 0.0

    self.update_position(node.left, -(max1 + self.offset), -0.6)
    self.update_position(node.right,-(min2 - self.offset), -0.6)

    return 0.0, min1 - (max1 + self.offset), max2 - (min2 - self.offset)

  def inorden(self, node, L):
    if node is not None:
      self.inorden(node.left, L)
      L.append((node.info, node.x, node.y, node.code, node.nodetype))
      self.inorden(node.right, L)

  def encode_nodes(self,node):
    L = []
    self.inorden(node, L)
    
    listStr = ""

    for item in L:
      data = item[0]
      if data == np.inf:
        data='+&infin;'

      if "null" in str(item[3]):
        listStr = listStr + ' ' + str(item[3])+ '[pos="' + str(item[1]) + ',' + str(item[2]) + '!" shape=square label="'+str(data)+'" width="0.2"] '  
      else:
        listStr = listStr + '"' + str(item[3])+ '"' + '[pos="' + str(item[1]) + ',' + str(item[2]) + '!" label="'+str(data)+'" shape='+str(item[4])+' margin=0] '
  
    return listStr

  def encode_edges(self, node):
    listStr = ""

    if node.left is not None:
      listStr = listStr + " " + str(node.code) + "--" + str(node.left.code)
      listStr = listStr + self.encode_edges(node.left) + " "
 
    if node.right is not None:
      listStr = listStr + " " + str(node.code) + "--" + str(node.right.code)
      listStr = listStr + self.encode_edges(node.right) + " "
 
    return listStr

  def draw_tree(self, tree, root):
    self.counterNull = 0
    self.counterNodes = 0
    
    B = self.copy_tree(getattr(tree, root))
    x,y,z=self.compute_position(B)

    listNodes = self.encode_nodes(B)
    listStr = self.encode_edges(B)
  
    src = Source('graph "Arbol" { rankdir=TB; ' + listNodes + ' node[shape='+ self.shapeInternal +'] ' + listStr +' }')
    src.engine="neato"
    src.render('lista.gv', view=True)
    display(SVG(src.pipe(format='svg')))

class GraphDrawer:
  def __init__(self):
    pass

  def draw_graph(self, graph):
    listStr = ""

    if graph.dirigido:
      head = 'digraph'
      connector = '->'
    else:
      head = 'graph'
      connector = '--'

    for e in graph.E:
      listStr = listStr + '"' + str(e[0]) + '"' + connector + '"' + str(e[1]) + '"'
      if len(e) == 3:
        listStr = listStr + '[label = ' + str(e[2]) + ']'
      listStr = listStr + ';'

    final_str = head + ' "Grafo" {' + listStr + '}'
    
    src = Source(final_str)
    src.engine="neato"
    src.render('lista.gv', view=True)
    display(SVG(src.pipe(format='svg')))

class NumpyArrayDrawer:
  def __init__(self, animation = False):
    self.animation = animation

  def drawNumpy1DArray(self, array, showIndex=False, layout="row", ):
    maxLen = 0
    for i in range(array.shape[0]):
      val = str(array[i])
      if len(val) > maxLen:
        maxLen = len(val)

    size = 20 + 7*maxLen
    if layout=="row":
      strArray = "<TR>"
      for i in range(array.shape[0]):
        strArray = strArray + '<TD border="1" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'">' + str(array[i]) +'</TD>'
      strArray = strArray + '</TR>'
      if showIndex:
        strArray = strArray + "<TR>"
        for i in range(array.shape[0]):
          strArray = strArray + '<TD border="0" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'">' + str(i) +'</TD>'
        strArray = strArray + '</TR>'
    elif layout=="column":
      strArray = ""
      for i in range(array.shape[0]):
        if not showIndex:
          strArray = strArray + '<TR><TD border="1" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'">' + str(array[i]) +'</TD></TR>'
        else:
          strArray = strArray + '<TR><TD border="0" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'">' + str(i) +'</TD><TD border="1" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'">' + str(array[i]) +'</TD></TR>'
  
    if not self.animation:
      src = Source('graph "Array" { node [fontsize=15, shape=plaintext]; a0 [label=< <TABLE border="0" cellspacing="0" cellpadding="3">' + strArray + '</TABLE> >] }')
      src.render('lista.gv', view=True)
      display(SVG(src.pipe(format='svg')))
      return None
    else:
      src = Source('graph "Array" { node [fontsize=15, shape=plaintext]; a0 [label=< <TABLE border="0" cellspacing="0" cellpadding="3">' + strArray + '</TABLE> >] }', format='png')
      return src
  
  def drawNumpy2DArray(self, array, showIndex=False):
    maxLen = 0
    for i in range(array.shape[0]):
      for j in range(array.shape[1]):
        val = str(array[i][j])
        if len(val) > maxLen:
          maxLen = len(val)

    size = 20 + 7*maxLen
    strArray=""

    if showIndex:
      strArray = strArray + '<TR><TD border="0" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'"></TD>'
      for j in range(array.shape[1]):
        strArray = strArray + '<TD border="0" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'">' + str(j) +'</TD>'
      strArray = strArray + '</TR>'

    for i in range(array.shape[0]):
      if showIndex:
        strArray = strArray + '<TR><TD border="0" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'">' + str(i)+ '</TD>'
      else:
        strArray = strArray + '<TR>'
      for j in range(array.shape[1]):
        strArray = strArray + '<TD border="1" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'">' + str(array[i][j]) +'</TD>'
      strArray = strArray + "</TR>"

    src = Source('graph "Array" { node [fontsize=15, shape=plaintext]; a0 [label=< <TABLE border="0" cellspacing="0" cellpadding="3">' + strArray + '</TABLE> >] }')
    src.render('lista.gv', view=True)
    if not self.animation:
      display(SVG(src.pipe(format='svg')))
    else:
      return src

class PositionNode23:
    def __init__(self, children, labels, nodetype, code):
        self.children = children     # lista de PositionNode23
        self.labels = labels         # lista de strings: 1 para Nodo2, 2 para Nodo3, [] para Nodoe
        self.x = 0.0
        self.y = 0.0
        self.nodetype = nodetype     # 'circle', 'Mrecord', 'square'
        self.code = code


class Tree23Drawer:
    """
    Visualizador de árboles 2-3, en el mismo estilo de BinaryTreeDrawer.

    Uso típico (con las clases Nodo2/Nodo3/Nodoe/Arbol23):
        drawer = Tree23Drawer(Nodo2, Nodo3, Nodoe)
        drawer.draw_tree(mi_arbol)

    Parámetros principales:
      - classNode2/classNode3/classEmpty: las tres clases del árbol 2-3.
      - fields2:  tupla (izq, info, der) con los nombres de atributos de Nodo2.
      - fields3:  tupla (izq, info1, med, info2, der) para Nodo3.
      - fieldRoot: nombre del atributo raíz en el Arbol23 ('raiz' por defecto).
      - shape2/shape3: shapes de Graphviz para 2-nodos y 3-nodos.
      - drawEmpty: si True, dibuja también los Nodoe como cuadraditos.
    """

    def __init__(self, classNode2, classNode3, classEmpty,
                 fields2=('izq', 'info', 'der'),
                 fields3=('izq', 'info1', 'med', 'info2', 'der'),
                 fieldRoot='raiz',
                 shape2='circle',
                 shape3='Mrecord',
                 drawEmpty=False):
        self.classNode2 = classNode2
        self.classNode3 = classNode3
        self.classEmpty = classEmpty
        self.fields2 = fields2
        self.fields3 = fields3
        self.fieldRoot = fieldRoot
        self.shape2 = shape2
        self.shape3 = shape3
        self.drawEmpty = drawEmpty
        self.offset = 0.5      # separación horizontal entre subárboles hermanos
        self.vgap   = 0.8      # separación vertical entre niveles
        self.counterNodes = 0
        self.counterEmpty = 0

    # ---------- utilidades ----------
    def _gen_code(self):
        code = "node" + str(self.counterNodes)
        self.counterNodes += 1
        return code

    def _gen_empty_code(self):
        code = "empty" + str(self.counterEmpty)
        self.counterEmpty += 1
        return code

    def _fmt(self, v):
        if isinstance(v, float) and v == np.inf:
            return '+&infin;'
        return str(v)

    def _half_width(self, n_labels):
        # Ancho visual aproximado del nodo (Nodo3 es el doble que Nodo2)
        if n_labels == 0:
            return self.offset / 4.0  # Nodoe
        return self.offset / 3.0 * n_labels

    # ---------- conversión del árbol a la estructura de posicionamiento ----------
    def copy_tree(self, node):
        if isinstance(node, self.classEmpty):
            if not self.drawEmpty:
                return None
            return PositionNode23([], [], "square", self._gen_empty_code())

        if isinstance(node, self.classNode2):
            f_left, f_info, f_right = self.fields2
            izq = self.copy_tree(getattr(node, f_left))
            der = self.copy_tree(getattr(node, f_right))
            children = [c for c in [izq, der] if c is not None]
            labels = [self._fmt(getattr(node, f_info))]
            return PositionNode23(children, labels, self.shape2, self._gen_code())

        if isinstance(node, self.classNode3):
            f_left, f_info1, f_med, f_info2, f_right = self.fields3
            izq = self.copy_tree(getattr(node, f_left))
            med = self.copy_tree(getattr(node, f_med))
            der = self.copy_tree(getattr(node, f_right))
            children = [c for c in [izq, med, der] if c is not None]
            labels = [self._fmt(getattr(node, f_info1)),
                      self._fmt(getattr(node, f_info2))]
            return PositionNode23(children, labels, self.shape3, self._gen_code())

        return None

    # ---------- layout ----------
    def update_position(self, node, shiftX, shiftY):
        if node is None:
            return
        for child in node.children:
            self.update_position(child, shiftX, shiftY)
        node.x += shiftX
        node.y += shiftY

    def compute_position(self, node):
        """Devuelve (centro, min_x, max_x) del subárbol. El nodo raíz queda en x=0."""
        half_w = self._half_width(len(node.labels))

        if not node.children:
            return 0.0, -half_w, half_w

        # Calcula extensiones de cada subárbol hijo
        children_info = []
        for child in node.children:
            _, mn, mx = self.compute_position(child)
            children_info.append((mn, mx, child))

        # Coloca los hijos uno al lado del otro, partiendo desde cursor=0
        positions = []
        cursor = 0.0
        for mn, mx, _ in children_info:
            center_pos = cursor - mn          # el borde izquierdo del hijo queda en cursor
            positions.append(center_pos)
            cursor += (mx - mn) + self.offset

        total_used = cursor - self.offset

        # Centra horizontalmente para que el bounding box quede simétrico al padre
        shift = -(total_used / 2.0)
        for i, (mn, mx, ch) in enumerate(children_info):
            final_pos = positions[i] + shift
            self.update_position(ch, final_pos, -self.vgap)
            positions[i] = final_pos

        new_min = positions[0]  + children_info[0][0]
        new_max = positions[-1] + children_info[-1][1]

        # Asegura que el ancho del propio nodo también esté incluido
        new_min = min(new_min, -half_w)
        new_max = max(new_max,  half_w)

        return 0.0, new_min, new_max

    # ---------- generación del DOT ----------
    def _collect(self, node, L):
        if node is None:
            return
        L.append(node)
        for ch in node.children:
            self._collect(ch, L)

    def encode_nodes(self, root):
        L = []
        self._collect(root, L)
        out = ""
        for n in L:
            if n.code.startswith("empty"):
                out += (f' {n.code}[pos="{n.x},{n.y}!" shape=square '
                        f'label="" width="0.2" height="0.2"] ')
            else:
                if n.nodetype in ("record", "Mrecord"):
                    label = " | ".join(n.labels)
                else:
                    label = n.labels[0] if n.labels else ""
                out += (f' "{n.code}"[pos="{n.x},{n.y}!" '
                        f'label="{label}" shape={n.nodetype} margin=0.05] ')
        return out

    def encode_edges(self, node):
        if node is None:
            return ""
        out = ""
        for child in node.children:
            out += f' "{node.code}"--"{child.code}" '
            out += self.encode_edges(child)
        return out

    # ---------- API pública ----------
    def draw_tree(self, tree):
        self.counterNodes = 0
        self.counterEmpty = 0

        root = getattr(tree, self.fieldRoot)
        B = self.copy_tree(root)

        if B is None:
            # Árbol vacío
            src = Source('graph "Arbol23" { vacio [shape=square label="" '
                         'width="0.2" height="0.2"] }')
            src.render('arbol23.gv', view=True)
            display(SVG(src.pipe(format='svg')))
            return

        self.compute_position(B)
        listNodes = self.encode_nodes(B)
        listEdges = self.encode_edges(B)

        src = Source('graph "Arbol23" { ' + listNodes + ' ' + listEdges + ' }')
        src.engine = "neato"
        src.render('arbol23.gv', view=True)
        display(SVG(src.pipe(format='svg')))