import json
from collections import defaultdict, deque

preamble = """
# This provides a global data store for the script
import roon.global_store
result = roon.global_store.result
# Clear the plots
result["mpl"] = []

"""

# Dictionary mapping type names to type objects (all basic types supported by widgets)
type_map = {
    "int": int,
    "float": float,
    "str": str,
    "list": list,
    "tuple": tuple,
    "dict": dict,
    "bool": bool,
    "set": set,
    "<built-in function any>": any,
    # Add more types as needed
}

def check_type(v, type_str):
    
    # Get the type object from the string
    target_type = type_map.get(type_str)

    if type_str == "any" or target_type is any :
        return True
    
    if target_type is None:
        raise ValueError(f"Unknown type: {type_str}")
    return isinstance(v, target_type)

def module_import_star(module_path):
    return f"import {module_path}"
    

def normalize_module_path(module_path):
    if module_path.endswith(".py"):
        module_path = module_path[:-3]
    if module_path.startswith("./"):
        module_path = module_path[2:]
    return module_path.replace("/", ".")

def generate_python_script(json_data):
    nodes = json_data['nodes']
    connections = json_data['connections']
    node_dict = {node['id']: node for node in nodes}

    # Build dependency graph for topological sort
    adj_list = defaultdict(list)
    incoming_degree = {node['id']: 0 for node in nodes}
    for conn in connections:
        from_node = conn['from']['node']
        to_node = conn['to']['node']
        adj_list[from_node].append(to_node)
        incoming_degree[to_node] += 1

    # Topological sort
    queue = deque([nid for nid in incoming_degree if incoming_degree[nid] == 0])
    order = []
    while queue:
        node_id = queue.popleft()
        order.append(node_id)
        for neighbor in adj_list[node_id]:
            incoming_degree[neighbor] -= 1
            if incoming_degree[neighbor] == 0:
                queue.append(neighbor)
    if len(order) != len(nodes):
        raise ValueError("Cycle detected in the node graph")

    # Map connections: (to_node, input_name) → (from_node, output_name)
    connections_map = {
        (conn['to']['node'], conn['to']['input']): (conn['from']['node'], conn['from']['output'])
        for conn in connections
    }

    # Extract function definitions and module dependencies
    dependency_modules = set()
    function_defs = []
    for node in nodes:
        if 'module' in node and not node['module'] == "<source>":
            dependency_modules.add(normalize_module_path(node['module']))
            continue
        if 'source' not in node:
            continue
        function_defs.append(node['source'])

    # Generate execution lines
    execution_lines = []
    for node_id in order:
        node = node_dict[node_id]
        func_name = node['name']
        if 'module' in node:
            func_name = f"{normalize_module_path(node['module'])}.{func_name}"
            if node['module'] == "<source>":
                func_name = node['name']

        # Collect arguments
        args = []
        for input_spec in node['inputs']:
            input_name = input_spec['name']
            if (node_id, input_name) in connections_map:
                from_node, output_name = connections_map[(node_id, input_name)]
                if len(node_dict[from_node]['outputs']) == 1:
                    args.append(f"node_{from_node}_{output_name}")
                else:
                    args.append(f"node_{from_node}_result['{output_name}']")
            elif input_spec['default'] is not None:
                # default_value = repr(input_spec['default'])
                default_value = input_spec['default']
                # check the type on the default value
                if not check_type(default_value, input_spec['type']):
                    raise ValueError(f"Default value {default_value} for input '{input_name}' does not match type {input_spec['type']} in node {node_id}")

                # Check if the default value is a valid Python expression
                try:
                    eval(default_value)
                except (NameError, SyntaxError):
                    # If eval fails, treat it as a string
                    default_value = repr(input_spec['default'])
                # in the explicit case, just use repr
                # if isinstance(input_spec['default'], str):
                if input_spec['type'] == 'str':
                    default_value = repr(input_spec['default'])
                args.append(default_value)
            else:
                raise ValueError(f"Missing required input '{input_name}' for node {node_id}")
        arg_str = ', '.join(args)
        stdpre = f"print('{node['name']} [{node_id}]:')\n"
        call = f"{func_name}({arg_str})"

        # Assign return values based on output count
        if node['outputs']:
            if len(node['outputs']) == 1:
                output_name = node['outputs'][0]['name']
                output_var = f"node_{node_id}_{output_name}"
                execution_lines.append(f"{stdpre}{output_var} = {call}")
            else:
                output_var = f"node_{node_id}_result"
                execution_lines.append(f"{stdpre}{output_var} = {call}")
        else:
            execution_lines.append(f"{stdpre}{call}")

    # Assemble the script
    module_import_star_lines = [module_import_star(module) for module in dependency_modules]
    # function_defs = []
    script = (
        # "import sys\n\nsys.path.append('/Users/brandenburg.89/Development/rune/svelte/svelte-node-graph/nodes/')\n\n" +
        preamble +
        "\n\n".join(module_import_star_lines) + "\n\n" +
        "\n\n".join(function_defs) + "\n\n" +
        "\n".join(execution_lines)
    )
    with open('roon_graph.py', 'w') as f:
        f.write(script)
    with open('roon_graph.json', 'w') as f:
        json.dump(json_data, f, indent=4)
    return script