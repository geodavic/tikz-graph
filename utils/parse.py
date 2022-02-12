import numpy as np
import csv
from io import StringIO

SUPPORTED_FORMATS = ['csv','mathematica','python']

def read_adj_mat_txt(txt,fmt='csv',directed=True):
    """ Read adjacency matrix from a given text format.
    """
    assert fmt in SUPPORTED_FORMATS, f"Unrecognized matrix format {fmt}."

    if fmt == 'csv':
        f = StringIO(txt)
        data = np.array(list(csv.reader(f, delimiter=',')),dtype=np.int64)
        data = process_matrix(data,directed=directed)
        return data 

    if fmt == 'mathematica':
        txt = txt.replace("{",'[').replace("}","]")

    list_txt = txt[1:-1].split(',')
    list_txt = [i
        .replace(']','')
        .replace('[','')
        .replace('"','')
        .strip() for i in list_txt
    ]

    data = np.array(list_txt,dtype=np.float64)
    size = int(np.sqrt(len(data)))
    data = np.reshape(data,(size,len(data)//size))
    
    data = process_matrix(data,directed=directed)
    return data

def process_matrix(mat,directed=True):
    """ Apply post-processing steps to matrix (binarize, assert symmetric, have at least two nodes,etc)
    """
    mat = (mat != 0).astype(np.int_)
    assert mat.shape[0] == mat.shape[1],"Adjacency matrix must be square."
    """ Decided to take this check out
    if not directed:
        assert ((mat.T - mat) == np.zeros_like(mat)).all(),"Non-directed graphs must have a symmetric matrix."
    """
    assert len(mat) > 1, "Graph must have at least two nodes"

    return mat

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


def svg_to_html(svg_b64,tikz=None):
    s = f"""<html><h3 style="text-align:center">Preview:</h3><p style='text-align:center;'><img style='max-height:400px' src='data:image/svg+xml;base64, {svg_b64}' width="60%" height="auto"/></p>"""
    if tikz is not None:
        s+='<h3 style="text-align:center; margin-top:60">TikZ code:</h3>'+tikz_to_html(tikz)
    s+= "</html>"
    return s

def tikz_to_html(tikz):
    s = tikz.replace("\n","<br>")
    pad= 10
    html = f'<p style="border: 1px solid black;font-family:Courier New; font-size:12; padding-top: {pad}; padding-bottom:{pad}; padding-left: {pad}; padding-right: {pad}"> {s} </p>'
    html += '<h5><i>Tip: if your graph is too small after you paste into your document, adjust the "Scale" parameter under Line Style.</i></h5>'
    return html
