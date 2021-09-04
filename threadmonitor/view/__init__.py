"""
TODO Insert view module description here
"""

from . import tk
#from . import logging

activeViews = []

def view_init():
    
    activeViews.append( tk.setup() )
#    activeViews.append( logging.setup() )




