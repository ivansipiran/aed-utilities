from graphviz import Source
from IPython.display import display_svg, SVG,display

class LinkedListDrawer:
  def __init__(self, strHeader = "", fieldHeader="", fieldData="", fieldLink="", fieldReverseLink=None):
    self.strHeader = strHeader
    self.fieldLink = fieldLink
    self.fieldHeader = fieldHeader
    self.fieldData = fieldData
    self.fieldReverseLink = fieldReverseLink
  
  def draw_linked_list(self, nList):
    if self.strHeader!="":
      listStr = 'node[shape=plaintext];'+self.strHeader+'; node[shape=square]; ""; node[shape=circle]; '+ self.strHeader + '-> '
    else:
      listStr = 'node[shape=square]; ""; node[shape=circle]; '

    p = getattr(nList, self.fieldHeader)
    while p is not None:
      listStr += str(getattr(p, self.fieldData))+ ' -> '
      p = getattr(p, self.fieldLink)
    listStr += '"";'
  
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
  def __init__(self, fieldData, fieldLeft, fieldRight, classNone=None, drawNull = False):
    self.nameInfo = fieldData
    self.nameLeft = fieldLeft
    self.nameRight = fieldRight
    self.offset = 0.35
    self.classNone = classNone
    self.drawNull = drawNull
    self.counterNull = 0
    self.counterNodes = 0
    
  def gen_code(self):
    code = "node" + str(self.counterNodes)
    self.counterNodes = self.counterNodes + 1
    return code

  def copy_tree(self, node):
    if self.classNone is not None:
      if isinstance(node, self.classNone):
        if not hasattr(node, "info"):
          if not self.drawNull:
            return None
          else:
            newNode = PositionNode(None, "", None, "null", "null" + str(self.counterNull))
            self.counterNull = self.counterNull + 1
            return newNode
        else:
          if not self.drawNull:
            return PositionNode(None, getattr(node, self.nameInfo), None, "notnull", self.gen_code())
          else:
            newNode1 = PositionNode(None, "", None, "null", "null" + str(self.counterNull))
            self.counterNull = self.counterNull + 1
            newNode2 = PositionNode(None, "", None, "null", "null" + str(self.counterNull))
            self.counterNull = self.counterNull + 1
            return PositionNode(newNode1, getattr(node, self.nameInfo), newNode2, "notnull", self.gen_code())
    else:
      if node is None:
        if not self.drawNull:
          return None
        else:
          newNode = PositionNode(None, "", None, "null", "null" + str(self.counterNull))
          self.counterNull = self.counterNull + 1
          return newNode
  
    newLeft = self.copy_tree(getattr(node, self.nameLeft))
    newRight = self.copy_tree(getattr(node, self.nameRight))

    return PositionNode(newLeft, getattr(node, self.nameInfo), newRight, "notnull", self.gen_code())

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
      L.append((node.info, node.x, node.y, node.code))
      self.inorden(node.right, L)

  def encode_nodes(self,node):
    L = []
    self.inorden(node, L)
    
    listStr = ""

    for item in L:
      if "null" in str(item[3]):
        listStr = listStr + ' ' + str(item[3])+ '[pos="' + str(item[1]) + ',' + str(item[2]) + '!" shape=square label="'+str(item[0])+'" width="0.2"] '  
      else:
        listStr = listStr + '"' + str(item[3])+ '"' + '[pos="' + str(item[1]) + ',' + str(item[2]) + '!" label="'+str(item[0])+'" shape=circle] '
  
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
  
    src = Source('graph "Arbol" { rankdir=TB; ' + listNodes + ' node[shape=circle] ' + listStr +' }')
    src.engine="neato"
    src.render('lista.gv', view=True)
    display(SVG(src.pipe(format='svg')))

class NumpyArrayDrawer:
  def __init__(self):
    pass

  def drawNumpy1DArray(self, array, showIndex=False, layout="row"):
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
  
    src = Source('graph "Array" { node [fontsize=15, shape=plaintext]; a0 [label=< <TABLE border="0" cellspacing="0" cellpadding="3">' + strArray + '</TABLE> >] }')
    src.render('lista.gv', view=True)
    display(SVG(src.pipe(format='svg')))
  
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
      strArray = strArray + '<TR><TD border="0" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'">' + str(i)+ '</TD>'
      for j in range(array.shape[1]):
        strArray = strArray + '<TD border="1" fixedsize="true" width="'+str(size)+'" height="'+str(size)+'">' + str(array[i][j]) +'</TD>'
      strArray = strArray + "</TR>"

    src = Source('graph "Array" { node [fontsize=15, shape=plaintext]; a0 [label=< <TABLE border="0" cellspacing="0" cellpadding="3">' + strArray + '</TABLE> >] }')
    src.render('lista.gv', view=True)
    display(SVG(src.pipe(format='svg')))