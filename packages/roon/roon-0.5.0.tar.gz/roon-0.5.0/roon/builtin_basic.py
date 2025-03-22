import uproot
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import awkward as ak
import os
from io import StringIO
from roon.global_store import result as result
matplotlib.use("svg")  # Use a non-interactive backend

def mpl_figure( dpi:int=100 ) -> plt.Figure:
    # Create a new figure
    fig = plt.figure()
    # Set the figure size
    # size = (8, 6)  # Width, Height in inches
    fig.set_size_inches(18, 16)
    # Set the figure background color
    fig.patch.set_facecolor("white")
    # Set the DPI (dots per inch)
    fig.set_dpi(100)
    # Set the figure title
    fig.suptitle("Matplotlib Figure")
    return fig

def fig_svg_data(fig:plt.Figure) -> str:
    svg_io = StringIO()
    plt.savefig(svg_io, format='svg')
    svg_data = svg_io.getvalue()
    svg_io.close()
    if "mpl" not in result:
        result["mpl"] = []
    result["mpl"].append( {"data": svg_data, "type": "svg"} )
    return svg_data

def get_gcf() -> plt.Figure:
    # Get the current figure
    fig = plt.gcf()
    # Check if the figure is None
    if fig is None:
        raise ValueError("No figure found")
    return fig

def example_plot( fig:plt.Figure=None, color:str="red", size:int=10, title:str="Example Plot") -> plt.Figure:
    with plt.xkcd():
        if fig is None:
            fig = mpl_figure()
        
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        plt.plot(x, y, color=color, marker='o', markersize=size)
        plt.title(title)
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        # plt.show()
        plt.savefig('example_plot.svg')
        print( os.getcwd() )
        print("Plot saved as example_plot.svg")
        svg_io = StringIO()
        plt.savefig(svg_io, format='svg')

    return fig

def gen_get( fromObj:any, key:any) -> any:
    return fromObj[key]

def plot_from_tree( branch:any, leaf_name:str, nbins:int=-1, range:tuple[float,float]=None):
    leaf = branch.arrays( [leaf_name], library="ak")
    all_leaf = ak.flatten(leaf[leaf_name]).to_numpy()
    calcnbins = smartBinning(all_leaf)
    if nbins == -1:
        nbins = calcnbins
    plt.hist( all_leaf , bins=nbins, range=range)
    plt.xlabel(leaf_name)
    plt.ylabel("Counts")
    plt.title(leaf_name)

    # set log y if difference between max and min is large
    
    if np.max(all_leaf) / max( np.min(all_leaf), 0.01 ) > 100:
        plt.yscale('log')

    plt.show()

def filterLeaves( leafs:any, filter:str) -> any:
    leafs = [ x for x in leafs if filter in x]
    return leafs

def excludeFilter( leafs:any, filter:str) -> any:
    leafs = [ x for x in leafs if filter not in x]
    return leafs

# leafs = filterLeaves( fwdTracks.keys(), "FwdTracks")
# leafs = excludeFilter( leafs, "MatchIndex")
# print(leafs)

def smartBinning( array, reduced=10. ) -> int:
    # if all values are integers then return the number of unique values
    if np.all( array == np.round(array) ):
        # something weird happening with types
        minmax = int(np.max(array)) - int(np.min(array))
        minmax = minmax + 1
        lenb = len( np.unique(array) )
        
        n = max(minmax, lenb );
        n = max( n, 500 ) #dont allow more than 500 bins
        return 
        # return len( np.unique(array) )
    return len( np.unique(array) / reduced )  

def plot_foreach( branch:any, leafs:any, range:any=None):
    for leaf in leafs:
        plot_from_tree( branch, leaf, range=range)

# for leaf in leafs:
#     plot_from_tree( fwdTracks, leaf, range=None)


# print(fwdTracks["FwdTracks.mNumberOfSeedPoints"].reshape(-1))



def let( v ):
    return v

def print_pass( v:any, format_string:str="" ) -> any:
    try:
        if format_string and format_string != "" and format_string != "None":
            print(format_string % v)
        else:
            print(v)
    except Exception as e:
        print(e)

    return v
    
def bootrstrap( v, source:str = ""  ):
    exec(source)
    return v