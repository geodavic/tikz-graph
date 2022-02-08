import numpy as np
import csv
from io import StringIO

SUPPORTED_FORMATS = ['csv']

def read_adj_mat_txt(txt,fmt='csv',symmetric=False):
    """ Read adjacency matrix from a given text format.

    TODO: error handling when can't be parsed, binarize matrix, assert symmetric
    """
    assert fmt in SUPPORTED_FORMATS, f"Unrecognized matrix format {fmt}."

    if fmt == 'csv':
        f = StringIO(txt)
        data = np.array(list(csv.reader(f, delimiter=',')),dtype=np.int64)

    return data

def parse_style(kwargs, defaults):
    """ Parse the nodestyle kwargs, setting default values where nothing
    passed and cleaning values.
    """
    for k,v in defaults.items():
        if k not in kwargs or not kwargs[k]:
            kwargs[k] = v[0]
        else:
            kwargs[k] = v[1](kwargs[k])
    return kwargs


def svg_to_html(svg_b64):
    s = f"""<html><p style='text-align:center;'><img src='data:image/svg+xml;base64, {svg_b64}' width="60%" height="auto"/></p></html>"""
    return s
