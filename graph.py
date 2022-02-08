import numpy as np
import csv
from utils.layout import SpringLayout
from utils.style import LineStyle,NodeStyle


class TikzGrapher:
    """Main class to deal with rendering the whole TikZ graph."""

    def __init__(self, nodestyle, linestyle):
        self.nodestyle = nodestyle
        self.linestyle = linestyle

    def to_tikz(self, adj_matrix, labels=None, **layout_kwargs):
        """ Render graph to a tikz string.
        """

        # compute the layout of the nodes
        layout_tool = SpringLayout(**layout_kwargs)
        layout = layout_tool.get_layout(adj_matrix)
        node_layout = layout['nodes']
        edge_layout = layout['loops']

        # any required macros or headers
        header = self.nodestyle.header() + self.linestyle.header()

        tikzstr = "\\begin{tikzpicture}\n" 

        # draw edges of graph
        tikzstr += self.node_block(node_layout, adj_matrix, labels)

        # draw lines of graph
        tikzstr += self.line_block(edge_layout, adj_matrix)

        tikzstr += "\n\\end{tikzpicture}\n"
        return header+tikzstr

    def to_doc(self, adj_matrix, labels=None, **layout_kwargs):
        docstart = "\\documentclass[tikz]{standalone}\n\\begin{document}" 
        docend = "\\end{document}\n"
        tikz = self.to_tikz(adj_matrix,labels=labels,**layout_kwargs)
        return docstart+tikz+docend

    def node_block(self, node_layout, adj_matrix, labels):
        # get labels 
        if labels is None:
            labels = [""]*len(adj_matrix)
        elif labels == "numbered":
            labels = range(len(adj_matrix))

        # draw nodes of graph
        nodestr = ""
        for node,label in zip(range(len(adj_matrix)),labels):
            nodestr += self.nodestyle.render_node(node,node_layout[node],label)
        nodestr = self.nodestyle.scope(nodestr)
        return nodestr

    def line_block(self, edge_layout, adj_matrix):
        linestr = ""
        
        symmetrized = adj_matrix - adj_matrix.T
        asym_idx = np.where(symmetrized > 0)  # unidirectional edges
        sym_idx = np.nonzero(
            np.triu(adj_matrix * adj_matrix.T)
        )  # bidirectional edges (or self-loops)

        # draw unidirectional edges
        for edge_out, edge_in in zip(*asym_idx):
            linestr += self.linestyle.render_line(edge_out,edge_in)

        # draw bidirectional edges
        for edge_out, edge_in in zip(*sym_idx):
            if edge_out != edge_in:
                if self.linestyle.directed:
                    linestr += self.linestyle.render_line(edge_out,edge_in,bend="left")
                    linestr += self.linestyle.render_line(edge_in,edge_out,bend="left")
                else:
                    linestr += self.linestyle.render_line(edge_out,edge_in)
            else:
                # draw self-loops
                num_neighbors = len(np.nonzero(symmetrized[edge_out,:])[0])
                linestr += self.linestyle.render_selfloop(edge_out,edge_layout[edge_out],num_neighbors=num_neighbors)

        linestr = self.linestyle.scope(linestr)
        return linestr


if __name__=="__main__":
    import sys 
    with open(sys.argv[1],"r") as fp:
        data = list(csv.reader(fp))
    adj_mat = np.array(data,dtype=np.int64) 


    scale = 1.5
    linestyle = LineStyle(color='black',directed=True,arrow_mark_location=1,scale=scale)
    nodestyle = NodeStyle(shape='circle',line_color='black',fill_color='white',scale=0.7)
    tikz = TikzGrapher(nodestyle,linestyle)

    s=tikz.to_doc(adj_mat,align_angle=90,seed=1,scale=scale,loops_are_nodes=False,labels="numbered")
    print(s)
