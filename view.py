from model import getForm
from flask import Flask, render_template, request
from compute import compute_gamma as vib3compute
import sys, os, inspect

app = Flask(__name__)


@app.route('/vib3_ext', methods=['GET', 'POST'])
def index():
    # Retrieve the appropriate form-class for the function
    formClass, arg_names, defaults = getForm(vib3compute)
    form = formClass(request.form)

    result = None
    result_render = None

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
            result = vib3compute(**kwargs)

    # If there are results, render those, then insert them into the template.
    if result:
        result_render=render_template('view_alt.html', result=result)
    return render_template('view.html',
        form=form, result=result_render)
