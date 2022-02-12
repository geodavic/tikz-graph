""" Classes that control the style of nodes and lines.

TODO: selfloop size should be node scale not line scale
"""

class NodeStyle:
    """Node style object for tikz graph. Consists of the style with wich
    each node is drawn.
    """

    def __init__(self,shape="circle", fill_color="black", line_color="black", scale=0.1, outer_sep=None):
        self.shape = shape
        self.fill_color = fill_color
        self.line_color = line_color
        self.scale = scale
        self.outer_sep = outer_sep

    def render_node(self, node, pos, label):
        """ Tikz code for a named node.
        """
        node_str = f"\\node ({node}) at ({pos[0]},{pos[1]}) {{ {label} }};\n"
        return node_str

    def scope(self,nodestr,outer_sep=None):
        """ The scope wrapper for all nodes in the drawing.
        """
        if self.outer_sep is None:
            outer_sep = min(0.2,0.1/self.scale)
        else:   
            outer_sep = self.outer_sep
        rval = f"\\begin{{scope}}[every node/.style={{ shape={self.shape},draw={self.line_color},fill={self.fill_color},scale={self.scale},outer sep={outer_sep}cm }}]\n"
        rval += nodestr + "\n\\end{scope}\n\n"
        return rval

    def header(self):
        """ Any required settings/macros outside of tikzpicture environment.
        """
        return ""


class LineStyle:
    """Line style object for the tikz graph. Consists of several options for the edges
    of the tikz graph.
    """

    def __init__(self, color="black", directed=True, arrow_mark_location=0.65, line_width=0.1, selfloop_size=1,arrow_tip=">"):
        self.color = color
        self.directed = directed
        self.arrow_mark_location = arrow_mark_location
        self.line_width = line_width
        self.selfloop_size = selfloop_size
        self.arrow_tip = arrow_tip

    def render_line(self, node1, node2, bend=None):
        """ Tikz code for a line between two named nodes.
        """
        if not self.directed:
            arrow_style = ""
        elif self.arrow_mark_location == 1:
            arrow_style = f"[-{self.arrow_tip}]"
        else:
            arrow_style = "[ar]"

        bend_str = ""
        if bend is not None:
            if bend == "left":
                bend_str = "[bend left=30]"
            elif bend == "right":
                bend_str = "[bend right=30]"
            else:
                pass

        linestr = f"\\draw [line width={self.line_width}, {self.color}] {arrow_style} ({node1}) to {bend_str} ({node2});\n"
        return linestr

    def render_selfloop(self, node, angle, num_neighbors=2):
        """ Tikz code for a self loop on a named node.
        """
        distance = self.selfloop_size * 9
        angle_width = min(40, 360 / num_neighbors)
        in_ = angle + angle_width
        out_ = angle - angle_width
        line_str = f"\\draw [line width={self.line_width}, {self.color}] ({node}) edge[out={out_},in={in_},distance={distance}mm] ({node});\n"
        return line_str

    def scope(self,nodestr):
        """ The scope wrapper for all lines in the drawing.
        """
        #rval = "\\begin{scope}\n "+nodestr+"\n\\end{scope}\n"
        return nodestr

    def header(self):
        """ Any required settings/macros outside of tikzpicture environment.
        """
        if not self.directed:
            return ""
        elif self.arrow_mark_location == 1:
            return "\\usetikzlibrary{arrows.meta}\n"
        else:
            header = "\\usetikzlibrary{decorations.markings}\n"
            header += "\\usetikzlibrary{arrows.meta}\n"
            header += f"\\tikzset{{ar/.style={{decoration={{markings,mark=at position {self.arrow_mark_location} with {{\\arrow{{{self.arrow_tip}}}}}}},postaction={{decorate}}}}}}\n"
            return header


