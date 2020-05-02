#! /usr/bin/python3.6

import pyverilog.vparser.ast as ast
from pyverilog.vparser.parser import parse as rtl_parse
import re
import autopilot_parser
from assign_slr import *

class Edge:
  def __init__(self, name:str):
    self.src : Vertex = None
    self.dst : Vertex = None
    self.width = -1
    self.name = name
    self.mark = False

class Vertex:
  def __init__(self, type:str, name : str):
    self.in_edges = [] # stores Edge objects
    self.out_edges = []
    self.type = type
    self.name = name
    self.upstream = [] # marked edges in the upstream
    self.downstream = []
    self.area = autopilot_parser.Area(-1, -1, -1, -1)
    self.slr_loc = -1

  def add_in(self, edge : Edge):
    self.out_edges.append(edge)

  def add_out(self, edge : Edge):
    self.in_edges.append(edge)

class Graph:
  fifo_type = ['fifo', 'relay_station']

  def __init__(self, rtl_addrs : list, rpt_path : str, DDR_loc):
    self.rpt_path = rpt_path
    ast, directives = rtl_parse(rtl_addrs)

    self.vertices = {} # name -> Vertex
    self.edges = {} # name -> Edge
    self.edge_to_vertex = {} # edge name -> Vertex

    self.dfs(ast, set(), self.init_vertices)
    self.dfs(ast, set(), self.init_edges)

    self.DDR_loc = DDR_loc

    assign_slr(self.vertices.values(), self.edges.values(), self.DDR_loc)

  def show_vertices(self):
    for v in self.vertices.values():
      print(f'{v.name}: {v.area}')
      for e in v.in_edges:
        print(f'  <- {e.name}')
      for e in v.out_edges:
        print(f'  -> {e.name}')

  def show_edges(self):
    for e in self.edges.values():
      print(f'{e.name}: {e.src.name} -> {e.dst.name}')

  #
  # traverse the rtl and apply a function
  #
  def dfs(self, node, visited, func):
    if(node not in visited):
      visited.add(node)
    else:
      return
    
    func(node)

    for c in node.children():
      self.dfs(c, visited, func)

  #
  # for each instance create a Vertex
  #
  def init_vertices(self, node):  
    if (not isinstance(node, ast.Instance)):
      return 
    if (node.module in Graph.fifo_type):
      return 

    v = Vertex(node.module, node.name)
    
    # get connection
    for portarg in node.portlist:
      if(not isinstance(portarg.argname, ast.Identifier)):
        continue

      formal = portarg.portname
      actual = portarg.argname.name

      if ('_dout' in formal and '_dout' in actual):
        edge_name = re.search('([^ ]+)_dout', actual).group(1)
        self.edge_to_vertex[actual] = v

      elif ('_din' in formal and '_din' in actual):
        edge_name = re.search('([^ ]+)_din', actual).group(1)
        self.edge_to_vertex[actual] = v

    # get area
    v.area = autopilot_parser.getAreaFromReport(v.name, self.rpt_path)

    self.vertices[node.name] = v

  #
  # for each FIFO or relay station create an Edge
  #
  def init_edges(self, node):
    # only considers fifo/rs instances
    if (not isinstance(node, ast.Instance)):
      return 
    if (node.module not in Graph.fifo_type):
      return 

    e = Edge(node.name)

    # extract width
    for paramarg in node.parameterlist:
      formal = paramarg.paramname
      actual = paramarg.argname.value
      if( 'DATA_WIDTH' in formal):
        e.width = int(actual)

    # extract wire name
    for portarg in node.portlist:
      if(not isinstance(portarg.argname, ast.Identifier)):
        continue

      formal = portarg.portname
      actual = portarg.argname.name

      if ('_dout' in actual and '_dout' in formal):
        e.dst = self.edge_to_vertex[actual]
        e.dst.add_in(e)

      elif ('_din' in actual and '_din' in formal):
        e.src = self.edge_to_vertex[actual]
        e.src.add_out(e)
        
    self.edges[node.name] = e


def main():
  
  tlp_path = '/home/einsx7/pr/application/PageRank/HBM_try1/PageRank.xilinx_u280_xdma_201920_3.hw.xo.tlp'
  top_name = 'PageRank'
  top_rtl_path = f'{tlp_path}/hdl/{top_name}_{top_name}.v'
  rpt_path = f'{tlp_path}/report'

  DDR_loc = collections.defaultdict(dict)

  DDR_loc['UpdateMem_0'] = 0
  DDR_loc['UpdateMem_1'] = 0
  DDR_loc['UpdateMem_2'] = 0
  DDR_loc['UpdateMem_3'] = 0
  DDR_loc['UpdateMem_4'] = 0
  DDR_loc['UpdateMem_5'] = 0
  DDR_loc['UpdateMem_6'] = 0
  DDR_loc['UpdateMem_7'] = 0
  DDR_loc['EdgeMem_0'] = 0
  DDR_loc['EdgeMem_1'] = 0
  DDR_loc['EdgeMem_2'] = 0
  DDR_loc['EdgeMem_3'] = 0
  DDR_loc['EdgeMem_4'] = 0
  DDR_loc['EdgeMem_5'] = 0
  DDR_loc['EdgeMem_6'] = 0
  DDR_loc['EdgeMem_7'] = 0
  DDR_loc['VertexMem_0'] = 0
  DDR_loc['PageRank_control_s_axi_U'] = 0
  DDR_loc['edges_0__m_axi'] = 0
  DDR_loc['edges_1__m_axi'] = 0
  DDR_loc['edges_2__m_axi'] = 0
  DDR_loc['edges_3__m_axi'] = 0
  DDR_loc['edges_4__m_axi'] = 0
  DDR_loc['edges_5__m_axi'] = 0
  DDR_loc['edges_6__m_axi'] = 0
  DDR_loc['edges_7__m_axi'] = 0
  DDR_loc['updates_0__m_axi'] = 0
  DDR_loc['updates_1__m_axi'] = 0
  DDR_loc['updates_2__m_axi'] = 0
  DDR_loc['updates_3__m_axi'] = 0
  DDR_loc['updates_4__m_axi'] = 0
  DDR_loc['updates_5__m_axi'] = 0
  DDR_loc['updates_6__m_axi'] = 0
  DDR_loc['updates_7__m_axi'] = 0
  DDR_loc['degrees__m_axi'] = 0
  DDR_loc['rankings__m_axi'] = 0
  DDR_loc['tmps__m_axi'] = 0

  g = Graph([top_rtl_path], rpt_path, DDR_loc)
    
if __name__ == '__main__':
  main()
