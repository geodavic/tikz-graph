from flask import Flask, request
import werkzeug
import os
import json
import subprocess
from graph import TikzGrapher
from utils.style import LineStyle,NodeStyle
from utils.parse import read_adj_mat_txt,svg_to_html,parse_style
import subprocess
import base64
import io

app = Flask(__name__)

str_to_bool = lambda s : True if s=="True" else False

LINE_DEFAULTS = {
    'color':('black',str),
    'directed':(True,str_to_bool),
    'arrow_mark_location':(1,float),
    'line_width':(0.5,float),
    'selfloop_size':(0.5,float)
}
NODE_DEFAULTS = {
    'shape':('circle',str),
    'line_color':('black',str),
    'fill_color':('black',str),
    'scale':(0.3,float)
}
LAYOUT_DEFAULTS = {
    'align_angle':90,
    'seed':1,
    'loops_are_nodes':False,
    'labels':None
}

def serialize_body(body):
    rdict = {"nodestyle":{},"linestyle":{}}
    for k,v in body.items():
        if "." in k:
            rdict[k.split(".")[0]][k.split(".")[1]] = v
        else:
            rdict[k] = v
    return rdict

def get_tikz_from_body(body,full_doc=False):
    """ Get the tikz graph string from the payload.
    """
    # read adjacency matrix text field
    print(body,flush=True)
    fmt = body.pop("adj_mat_fmt")
    adj_mat = read_adj_mat_txt(body.pop("adj_mat_txt"),fmt=fmt)

    # separate linestye and nodestyle kwargs
    body = serialize_body(body)
    print(body,flush=True)
  
    # read line and node style kwargs
    linekwargs = parse_style(body.pop("linestyle",{}),LINE_DEFAULTS)
    nodekwargs = parse_style(body.pop("nodestyle",{}),NODE_DEFAULTS)

    # get tikz string
    linestyle = LineStyle(**linekwargs)
    nodestyle = NodeStyle(**nodekwargs)
    tikz = TikzGrapher(nodestyle,linestyle)
    if full_doc:
        rval = tikz.to_doc(adj_mat,**body)
    else:
        rval = tikz.to_tikz(adj_mat,**body)

    return rval

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route("/tikz",methods=["POST"])
def tikz():
    """ Return the tikz string from a data request.
    """
    
    body = json.loads(request.data.decode("utf-8"))
    rval = get_tikz_from_body(body)

    return rval


@app.route("/tikz_html",methods=["POST"])
def tikz_html():
    """ Return the tikz string as html from a form request.
    """
    
    body = dict(request.form)    
    rval = get_tikz_from_body(body,html=True)

    return rval

@app.route("/tikz_svg",methods=["POST"])
def tikz_svg():
    """ Return a pdf of the graph from a form request.
    """
    body = dict(request.form)    
    tikz_str = get_tikz_from_body(body,full_doc=True)

    filename = str(abs(hash(tikz_str)))
    with open(filename+".tex","w") as fp:
        fp.write(tikz_str)

    # compile latex and convert to svg
    # TODO: catch exit codes
    proc = subprocess.Popen(['pdflatex',filename+".tex",'>','/dev/null'])
    out = proc.communicate()[0]
    proc = subprocess.Popen(['pdf2svg',filename+".pdf",filename+".svg"])
    out = proc.communicate()[0]

    # put a try except here
    svg = open(filename+".svg","rb").read()
    svg_encoded = base64.b64encode(svg).decode("utf-8")

    # delete all files (todo)
    return svg_to_html(svg_encoded)
         



if __name__ == "__main__":
    app.run(host='0.0.0.0')
