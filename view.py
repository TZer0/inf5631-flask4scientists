from model import getForm
from flask import Flask, render_template, request
from compute import compute_gamma as compute
import sys, os, inspect

app = Flask(__name__)

def testFunc(x = 1):
    return ((x * 2, "y"),)

func_paths = {
        'vib3_ext' : compute,
        'test' : testFunc
}

@app.route('/vib3_ext', methods=['GET', 'POST'])
@app.route('/test', methods=['GET', 'POST'])
def index():
    func = func_paths[request.path.strip('/')]
    formClass, arg_names, defaults = getForm(func)
    form = formClass(request.form)
    result = None

    if request.method == 'POST':
        arg_names = inspect.getargspec(func).args
        # Run eval on the text
        # Note that form.name.label is <label for="A">(list)</label>
        kwargs = {name: getattr(form, name).data
                  for name in arg_names if hasattr(form, name)}
        
        if arg_names:
            for name in kwargs:
                if hasattr(form, name) and \
                       hasattr(getattr(form, name), 'label'):
                    label = str(getattr(form, name).label)
                    for tp in ('list', 'tuple', 'nd.array'):
                        if tp in label:
                            kwargs[name] = eval(kwargs[name])

            if form.validate():
                result = func(**kwargs)

    # Concatenate view_forms.html and view_results.html
    return render_template('view.html',
                           form=form, result=result, funcs=func_paths)
