"""
Example on generic model.py file which defines a function
which takes another function as an argument and generates
the appropriate form
"""

import wtforms
from math import pi
import numpy as np
import inspect

def get_type_as_str(obj):
    return str(type(obj)).split("'")[1]

def getForm(func):

    # This class will be returned once the fields have been added to it.
    class InputForm(wtforms.Form):
        pass

    # Fetch arguments and default arguments from the function
    arg_names = inspect.getargspec(func).args
    defaults  = inspect.getargspec(func).defaults

    # Augment defaults with None elements for the positional
    # arguments
    defaults = [None]*(len(arg_names)-len(defaults)) + list(defaults)

    # Map type of default to right form field
    type2form = {type(1.0): wtforms.FloatField,
                 type(1):   wtforms.IntegerField,
                 type(''):  wtforms.TextField,
                 type([]):  wtforms.TextField,
                 type(()):  wtforms.TextField,
                 type(np.array([1,2.])):  wtforms.TextField,
                 }

    # Create a form-class containing argument-list of the function
    for name, value in zip(arg_names, defaults):
        if value is None:
            setattr(InputForm, name, wtforms.FloatField(
                validators=[wtforms.validators.InputRequired()]))
        else:
            if type(value) in type2form:
                setattr(InputForm, name, type2form[type(value)](
                    default=value,
                    label='%s' % get_type_as_str(value),
                    validators=[wtforms.validators.InputRequired()]))
            else:
                raise TypeError('argument %s %s not supported' %
                                name, type(value))
    return InputForm, arg_names, defaults

if __name__ == '__main__':
    """ This tests the function on compute_gamma """
    from compute import compute_gamma as compute
    form, args, default = getForm(compute)
    for item in dir(form):
        if item in args:
            print item, getattr(form, item)
