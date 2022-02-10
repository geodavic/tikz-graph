import numpy as np
import networkx as nx
import math

def rotation_matrix(angle):
    """ Rotation matrix in 2d.
    """
    cos = math.cos(angle)
    sin = math.sin(angle)
    return np.array([[cos, -sin], [sin, cos]])
   
class Layout:
    """Base class for any layout object."""

    def __init__(self, align_angle=0, seed=1, scale=1, loops_are_nodes=False):
        self.align_angle = 2*math.pi*((align_angle-45)/360)
        self.seed = seed
        self.scale = scale
        self.loops_are_nodes = loops_are_nodes

    def _get_layout(self, graph, num_nodes):
        """ The desired layout method. To be implemented by the child class.
        """
        raise NotImplementedError

    def get_layout(self, adj_mat):
        """Return the layout dictionary, which maps node number to
        position in the xy plane or a self loop to a xy position.
        """
        H = nx.from_numpy_array(adj_mat)

        # if treating loops as nodes, add a node for each one.
        if self.loops_are_nodes:
            for idx in np.nonzero(np.diag(adj_mat))[0]:
                H.remove_edge(idx, idx)
                H.add_edge(idx, len(adj_mat) + idx)

        # call base layout method
        layout = self._get_layout(H, len(adj_mat))

        # rotate to principal axes (this rotates to 45deg)
        rot = self.pca_rotation(list(layout.values()))

        # set alignment (if something other than 45 wanted)
        rot_align = rotation_matrix(self.align_angle) 
        trans = np.matmul(rot_align, rot)
        layout = {k: trans @ v for k, v in layout.items()}

        # if not treating loops as nodes, get their optimal angle
        # based on the node layout.
        if not self.loops_are_nodes:
            for idx in np.nonzero(np.diag(adj_mat))[0]:
                layout[len(adj_mat)+idx] = self._get_loop_pos(idx,layout,H)

        # convert loop layout positions to relative angles
        for k in layout.keys():
            if k>= len(adj_mat):
                layout[k] = self._compute_loop_angle(layout[k-len(adj_mat)],layout[k])

        rdict = {
            "nodes": {k: v for k, v in layout.items() if k < len(adj_mat)},
            "loops": {k-len(adj_mat): v for k, v in layout.items() if k >= len(adj_mat)},
        }
        return rdict

    def _get_loop_pos(self, idx, layout, H):
        """ Get optimal loop position for a self loop, given a layout.
        """

        # sort adjacent nodes by position around the circle (starting from angle 0)
        sort_fn = lambda v: (v[1] < 0, np.arccos(np.dot(v / np.linalg.norm(v), [1, 0])))
        adjacent_vecs = sorted(
            [layout[id_] - layout[idx] for id_ in H.neighbors(idx) if id_ != idx],
            key=sort_fn,
        )

        # special case when there is only one incident edge
        if len(adjacent_vecs) == 1:
            return -adjacent_vecs[0] + layout[idx]

        # easy case when there are two incident edges
        if len(adjacent_vecs) == 2:
            sum_ = adjacent_vecs[0] + adjacent_vecs[1]
            return -sum_ / 2 + layout[idx]

        # TODO: this could be bad if all edges are symetrically laid out
        if len(adjacent_vecs):
            pos = -sum(adjacent_vecs)/len(adjacent_vecs)
        else:
            pos = np.array([0,1])
        """
        # get angles between adjacent nodes
        angles = [np.arctan2(v[1], v[0]) for v in adjacent_vecs]
        for i in range(len(angles)):
            d = angles[i]
            if d < 0:
                angles[i] += 2 * math.pi
            if d > 2 * math.pi:
                angles[i] -= 2 * math.pi
        angle_diffs = [a - b for a, b in zip([angles[-1]] + angles[:-1], angles)]

        # get the biggest angle gap and rotate the starting vector
        # by half that to get the position.
        max_idx = np.argmax(angle_diffs)
        rot = rotation_matrix(angle_diffs[max_idx]/2)
        pos = rot @ adjacent_vecs[max_idx]
        """

        return pos + layout[idx]

    def _compute_loop_angle(self, node_pos, loop_pos):
        """ Compute angle at which a loop is positioned relative to its node.
        """
        angle_between = lambda v1, v2: np.arccos(
            np.dot(v1 / np.linalg.norm(v1), v2 / np.linalg.norm(v2))
        )
        angle_from_e1 = lambda v1: angle_between(v1, np.array([1, 0]))

        rel_pos = loop_pos - node_pos
        if rel_pos[1] < 0:
            angle = 2 * math.pi - angle_from_e1(rel_pos)
        else:
            angle = angle_from_e1(rel_pos)

        angle = 360 * (angle / (2 * math.pi))
        return angle


    def pca_rotation(self,points):
        """ Get the rotation matrix that aligns a set of points according
        to their PCA decomposition.
        """
        cov = np.cov(np.array(points).T)
        ev, eigv = np.linalg.eig(cov)

        max_idx = np.argmax(ev)
        [x, y] = eigv[:, max_idx]
        rot_mat = 0.7 * self.scale * np.array([[x + y, y - x], [x - y, x + y]])
        return rot_mat


class SpringLayout(Layout):
    """Spring layout method. This models the nodes as point charges and
    the edges as springs and runs a physics simulator.
    """

    def _get_layout(self, H, num_nodes):
        layout = nx.spring_layout(H, center=[0, 0], seed=self.seed)

        # translate to centroid of non-self-loop nodes
        centroid = sum([v for k, v in layout.items() if k < num_nodes]) / num_nodes
        layout = {k: v - centroid for k, v in layout.items()}

        # scale so it fits in unit circle
        sc = max([np.linalg.norm(v) for k, v in layout.items() if k < num_nodes])
        layout = {k: v / sc for k, v in layout.items()}

        return layout
