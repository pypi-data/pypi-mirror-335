"""inspectk  -- view variables & help docs like so:

import inspectk
inspectk.go()


It's that simple.
"""

import liontk
import inspect
import textwrap
import contextlib
from io import StringIO

# Module-level global
g = {"FIRSTRUN": False, "FRAMELOCALS": None}

setup_tcl_commands = """
wm withdraw .
option add *tearOff 0

ttk::style theme use clam

ttk::style configure Treeview \
    -background "#1e1e1e" \
    -foreground "#dddddd" \
    -fieldbackground "#1e1e1e"

ttk::style map Treeview \
    -background {selected "#444444"} \
    -foreground {selected "#ffffff"}
"""

def poke1(s):
    "Poke a string into $poked1"
    liontk.poke("poked1", s)

def poke2(s):
    "Poke a string into $poked2"
    liontk.poke("poked2", s)

def create_debug_window():
    "Create the debug window"
    liontk.tclexec('toplevel .debugwin')
    liontk.tclexec('wm title .debugwin "Inspectk Debugger Window"')
    liontk.tclexec('wm geometry .debugwin 1200x600')

    # Configure grid
    liontk.tclexec('grid columnconfigure .debugwin 0 -weight 1')
    liontk.tclexec('grid columnconfigure .debugwin 1 -weight 0')
    liontk.tclexec('grid columnconfigure .debugwin 2 -weight 0')
    liontk.tclexec('grid rowconfigure .debugwin 0 -weight 1')

    # Tree widget with two columns: name and repr
    liontk.tclexec('ttk::treeview .debugwin.tree -columns {name repr} -show headings')
    liontk.tclexec('.debugwin.tree heading name -text "name"')
    liontk.tclexec('.debugwin.tree heading repr -text "repr"')
    liontk.tclexec('.debugwin.tree column name -width 150 -anchor w -stretch 0')
    liontk.tclexec('.debugwin.tree column repr -width 400 -anchor w -stretch 1')
    liontk.tclexec('grid .debugwin.tree -row 0 -column 0 -sticky nsew')

    # Vertical scrollbar
    liontk.tclexec('ttk::scrollbar .debugwin.vscroll -orient vertical -command ".debugwin.tree yview"')
    liontk.tclexec('.debugwin.tree configure -yscrollcommand ".debugwin.vscroll set"')
    liontk.tclexec('grid .debugwin.vscroll -row 0 -column 1 -sticky ns')

    # Text widget for documentation
    liontk.tclexec('text .debugwin.doc -wrap word -state normal')
    liontk.tclexec('grid .debugwin.doc -row 0 -column 2 -sticky nsew')
    
    # Styling (dark mode)
    liontk.tclexec('ttk::style configure Vertical.TScrollbar -background "#2e2e2e"')
    liontk.tclexec('.debugwin.doc configure -background "#1e1e1e" -foreground "#dddddd" -insertbackground "#ffffff"')
    liontk.tclexec('.debugwin.doc configure -font {Courier 10}')

def populate_tree_from_frame():
    "Populate the base of the tree from the specified frame"
    for key, value in g["FRAMELOCALS"].items():
        value_repr = repr(value)[:100].replace('"', '\"')
        poke1(key)  # use the plain key as the node ID
        poke2(value_repr)
        liontk.tclexec(f'.debugwin.tree insert "" end -id $poked1 -values [list "{key}" $poked2]')
        poke2(key + ".__tree$dummy")
        liontk.tclexec(f'.debugwin.tree insert $poked1 end -id "$poked2" -values [list "" ""]')

def bind_tree_events():
    "Bind tree events for opening entries on"
    liontk.tclexec('bind .debugwin.tree <<TreeviewOpen>> py_on_treeview_open')
    liontk.tclexec('bind .debugwin.tree <<TreeviewSelect>> py_on_treeview_select')


def read_tcl_list(s):
    "Tcl lists can be 'a' or '{a}' or '{a b c}'"
    if s.startswith("{") and s.startswith("}"):
        return s[1:-1].split()
    else:
        return s.split()

def on_treeview_open():
    "When a treeview entry is opened... (populate the children)"
    node = liontk.tclexec('.debugwin.tree focus')
    try:
        children = read_tcl_list(liontk.tclexec(f'.debugwin.tree children "{node}"'))
        for child_id in children:
            poke1(child_id)
            liontk.tclexec(".debugwin.tree delete $poked1")

        obj = g["FRAMELOCALS"]
        for attr in node.split('.'):
            obj = getattr(obj, attr) if hasattr(obj, attr) else obj[attr]

        children = dir(obj)
        for child in children:
            child_full_name = f"{node}.{child}"
            child_repr = repr(getattr(obj, child))[:100].replace('"', '\"')
            depth = child_full_name.count(".")
            indent = '    ' * depth
            display_name = f"{indent}{child}"
            poke1(child_full_name)
            poke2(child_repr)
            liontk.tclexec(
                f'.debugwin.tree insert "{node}" end -id $poked1 -values [list "{display_name}" $poked2]'
            )
            poke2(child_full_name + ".__tree$dummy")
            liontk.tclexec(f'.debugwin.tree insert $poked1 end -id "$poked2" -values [list "" ""]')

    except Exception as e:
        print(f"Error expanding node {node}: {e}")

def on_treeview_select():
    "When a treeview entry is selected... (show help)"
    node = liontk.tclexec('.debugwin.tree focus')
    try:
        obj = g["FRAMELOCALS"]
        for attr in node.split('.'):
            obj = getattr(obj, attr) if hasattr(obj, attr) else obj[attr]

        with StringIO() as buf, contextlib.redirect_stdout(buf):
            help(obj)
            doc_text = buf.getvalue()

        poke1(doc_text)
        liontk.tclexec('.debugwin.doc delete 1.0 end')
        liontk.tclexec(f'.debugwin.doc insert end $poked1')
        
        # update selection
        current_selection = liontk.tclexec(".debugwin.tree selection")
        if node not in read_tcl_list(current_selection):
            poke1(node)
            liontk.tclexec(f'.debugwin.tree selection set $poked1')

    except Exception as e:
        print(f"Error displaying doc for node {node}: {e}")


# The entry-point function
def go():
    "Entry-point function"
    # Record calling stack frame
    caller_frame = inspect.currentframe().f_back
    g["FRAMELOCALS"] = caller_frame.f_locals

    # Initialize, if this is the first run
    if not g["FIRSTRUN"]:
        liontk.init.setup()
        liontk.tclexec(setup_tcl_commands)
        liontk.mkcmd('py_on_treeview_open', on_treeview_open)
        liontk.mkcmd('py_on_treeview_select', on_treeview_select)
        g["FIRSTRUN"] = True

    # Build the window
    create_debug_window()
    populate_tree_from_frame()
    bind_tree_events()
  
    liontk.tclexec('wm deiconify .debugwin')

