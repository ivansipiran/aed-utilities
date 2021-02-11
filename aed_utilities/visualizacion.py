from graphviz import Source
from IPython.display import display_svg, SVG,display

class Visualizacion:
  @staticmethod
  def dibujar_lista(lista):
    listStr = ""
    p=lista.primero
    while p is not None:
      listStr = listStr + str(p.info)
      if p.sgte is not None:
        listStr = listStr + ' -> '
      p=p.sgte
  
    src = Source('digraph "Lista" { rankdir=LR; ' + listStr +' }')
    src.render('lista.gv', view=True)
    display(SVG(src.pipe(format='svg')))

  @staticmethod
  def dibujar_lista_doble_enlace(lista):
    listStrAsc = ""
    listaAsc = [x for x in lista.ascendente()]
    for i, x in enumerate(listaAsc):
      listStrAsc = listStrAsc + str(x)
      if i < len(listaAsc) - 1:
        listStrAsc = listStrAsc + ' -> '
  
    listStrDesc = ""

    listaDesc = [x for x in lista.descendente()]
    for i, x in enumerate(listaDesc):
      listStrDesc = listStrDesc + str(x)
      if i < len(listaDesc) - 1:
        listStrDesc = listStrDesc + ' -> '
  
    src = Source('digraph "Lista" { rankdir=LR; ' + listStrAsc + ' ' + listStrDesc +' }')
    src.render('lista.gv', view=True)
    display(SVG(src.pipe(format='svg')))