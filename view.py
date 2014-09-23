from model import getForm
from flask import Flask, render_template, request
from compute import compute_gamma as vib3compute
from vib1 import compute as vib1compute
from numpy import sin
import sys, os, inspect

app = Flask(__name__)

def testFunc(x = 1.):
    return ((x * 2, "y"),)

def sinFunc(x=0.):
    return ((sin(x), "y"),)

def surfaceFunc(x=0., y=0.):
    return ((sin(x) + sin(y)*sin(x+y), "z"),)

func_paths = (
        # Uses customized view to display results
        ('vib3_ext', vib3compute, "view_alt.html"),
        # Uses the default result-view
        ('vib3_ext_default', vib3compute, False),
        ('vib1', vib1compute, False),
        ('test', testFunc, False),
        ('sin', sinFunc, False),
        ('surface', surfaceFunc, False),
)

@app.route('/', methods=['GET', 'POST'])
@app.route('/<funcName>', methods=['GET', 'POST'])
def index(funcName=""):

    # Find the right function
    func = None
    result_alt = False
    for path in func_paths:
        if path[0] == funcName:
            func = path[1]
            view_alt = path[2]

    # If not found, default to first function    
    if not func:
        func = func_paths[0][1]
        view_alt = func_paths[0][2]

    # Retrieve the appropriate form-class for the function
    formClass, arg_names, defaults = getForm(func)
    form = formClass(request.form)

    result = None

    if request.method == 'POST':
        # Run eval on the text
        # Note that form.name.label is <label for="A">(list)</label>
        kwargs = {name: getattr(form, name).data
                  for name in arg_names if hasattr(form, name)}
        
        for name in kwargs:
            if hasattr(form, name) and \
                   hasattr(getattr(form, name), 'label'):
                label = str(getattr(form, name).label)
                for tp in ('list', 'tuple', 'nd.array'):
                    if tp in label:
                        kwargs[name] = eval(kwargs[name])

        if form.validate():
            result = func(**kwargs)

    # If a different result-render is specified, render this first
    # and insert it into the main template, else use the default-render
    # to display the results
    if view_alt:
        result_alt=render_template(view_alt, result=result)
        result = None
    return render_template('view.html',
        form=form, result=result, result_alt=result_alt, funcs=[path[0] for path in func_paths])
