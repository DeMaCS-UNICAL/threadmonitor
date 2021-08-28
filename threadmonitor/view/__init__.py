"""
TODO Insert view module description here
"""

from . import tk

activeViews = []

def view_init():
    
    activeViews.append( tk.setup() )
    print('view initialized')