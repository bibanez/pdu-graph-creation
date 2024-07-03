import argparse
import sys
import os
import graph_tool.all as gt
import opendbpy as odb
from tqdm import tqdm

def build_graph(design, undirected=False):
    """
    Input: design is an OpenDB representation of the chip
    Returns: graph-tool Graph
    """
    instances = design.getBlock().getInsts()
    pins = design.getBlock().getBTerms()

    # initialize graph
    g = gt.Graph(directed=not undirected)

    # graph-tool can use string vertex properties, so we don't need a separate mapping
    v_name = g.new_vertex_property("string")
    g.vertex_properties["name"] = v_name
    v_color = g.new_vertex_property("string")
    g.vertex_properties["color"] = v_color
    v_inst = g.new_vertex_property("boolean")
    g.vertex_properties["is_inst"] = v_inst
    v_width = g.new_vertex_property("float")
    g.vertex_properties["width"] = v_width
    v_height = g.new_vertex_property("float")
    g.vertex_properties["height"] = v_height
    
    # Add vertices
    print("Reading Instances...")
    for inst in instances:
        v = g.add_vertex()
        v_name[v] = inst.getName()
        v_color[v] = "#007dff"
        v_inst[v] = True
        v_width[v] = inst.getMaster().getWidth()
        v_height[v] = inst.getMaster().getHeight()

    print("Reading Pins...")
    for pin in pins:
        v = g.add_vertex()
        v_name[v] = pin.getName()
        v_color[v] = "#ff7c44"
        v_inst[v] = False
        v_width[v] = 0
        v_height[v] = 0

    nets = design.getBlock().getNets()
    for net in tqdm(nets, total=len(nets), desc="Processing nets"):
        # exclude power nets
        if net.isSpecial():
            continue

        iterms = net.getITerms()
        bterms = net.getBTerms()

        # given a net, figure out the driving cell and the loads
        driving_cell = None
        loads = []

        # if iterm, then it needs to have direction output to be a driving cell
        for iterm in iterms:
            if iterm.getIoType() == 'OUTPUT':
                driving_cell = iterm.getInst().getName()
            else:
                loads.append(iterm.getInst().getName())
        
        # if bterm, then it needs to have direction input to be a driving cell
        for bterm in bterms:
            if bterm.getIoType() == 'INPUT':
                assert (driving_cell == None), "Something is wrong with the directions!"
                driving_cell = bterm.getName()
            else:
                loads.append(bterm.getName())

        assert (driving_cell != None), "Unconnected Network"
        
        # add edges
        src = g.vertex(list(v_name).index(driving_cell))
        for load in loads:
            dst = g.vertex(list(v_name).index(load))
            g.add_edge(src, dst)

    return g

def read_netlist(lef_file, def_file):
    # intialize the database
    db = odb.dbDatabase.create()

    # load the lef file
    try:
        odb.read_lef(db, lef_file)
    except Exception as e:
        print("Problem loading the tech file!")
        return None

    # load the def file
    try:
        odb.read_def(db, def_file)
    except Exception as e:
        print("Problem loading the design!")
        return None

    # parse the design into a graph-tool graph
    design = db.getChip()
    G = build_graph(design)

    print(str.format('Built a graph with %s nodes' % str(G.num_vertices())))
    print(str.format('.... Added %s edges' % str(G.num_edges())))

    return G

def process_files(lef_file, def_file, gt_file):
    # Read netlist from LEF/DEF files
    print("Reading netlist...")
    G = read_netlist(lef_file, def_file)
    
    # Save the graph
    G.save(gt_file)
    print(f"Graph saved to: {gt_file}")

def main():
    parser = argparse.ArgumentParser(description="Convert LEF and DEF files to graph-tool (.gt) format")
    parser.add_argument("lef_input", help="Input LEF file")
    parser.add_argument("def_input", help="Input DEF file")
    parser.add_argument("gt_output", help="Output GT file")
    args = parser.parse_args()

    # Check if input files exist
    if not os.path.isfile(args.lef_input):
        print(f"Error: LEF input file '{args.lef_input}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isfile(args.def_input):
        print(f"Error: DEF input file '{args.def_input}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    # Check if output directory exists
    output_dir = os.path.dirname(args.gt_output)
    if output_dir and not os.path.isdir(output_dir):
        print(f"Error: Output directory '{output_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        process_files(args.lef_input, args.def_input, args.gt_output)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()