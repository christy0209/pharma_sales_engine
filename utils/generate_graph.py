import pandas as pd

def create_nodes_edges(input_file, nodes_file, edges_file):
    # Load dataset
    df = pd.read_csv(input_file)
    
    # Extract unique nodes
    medicines = df[['id', 'name']].rename(columns={'id': 'node_id', 'name': 'label'})
    medicines['category'] = 'medicine'
    manufacturers = df[['manufacturer_name']].drop_duplicates().reset_index(drop=True)
    manufacturers['node_id'] = range(len(medicines)+1, len(medicines)+1+len(manufacturers))
    manufacturers = manufacturers.rename(columns={'manufacturer_name': 'label'})
    manufacturers['category'] = 'manufacturer'
    
    ingredients = pd.concat([df['short_composition1'], df['short_composition2']], ignore_index=True).dropna().drop_duplicates().reset_index(drop=True)
    ingredients = pd.DataFrame({'label': ingredients, 'node_id': range(len(medicines) + len(manufacturers) + 1, len(medicines) + len(manufacturers) + 1 + len(ingredients)), 'category': 'ingredient'})
    
    # Combine all nodes
    nodes = pd.concat([medicines, manufacturers, ingredients], ignore_index=True)
    
    # Create edges: Medicine -> Manufacturer
    medicine_manufacturer_edges = df[['id', 'manufacturer_name']].merge(manufacturers, left_on='manufacturer_name', right_on='label')[['id', 'node_id']]
    medicine_manufacturer_edges = medicine_manufacturer_edges.rename(columns={'id': 'source', 'node_id': 'target'})
    medicine_manufacturer_edges['relationship'] = 'manufactured_by'
    
    # Create edges: Medicine -> Ingredients
    medicine_ingredient_edges1 = df[['id', 'short_composition1']].merge(ingredients, left_on='short_composition1', right_on='label')[['id', 'node_id']]
    medicine_ingredient_edges2 = df[['id', 'short_composition2']].merge(ingredients, left_on='short_composition2', right_on='label')[['id', 'node_id']]
    medicine_ingredient_edges = pd.concat([medicine_ingredient_edges1, medicine_ingredient_edges2], ignore_index=True).dropna()
    medicine_ingredient_edges = medicine_ingredient_edges.rename(columns={'id': 'source', 'node_id': 'target'})
    medicine_ingredient_edges['relationship'] = 'contains'
    
    # Combine all edges
    edges = pd.concat([medicine_manufacturer_edges, medicine_ingredient_edges], ignore_index=True)
    
    # Save to CSV
    nodes.to_csv(nodes_file, index=False)
    edges.to_csv(edges_file, index=False)
    
    print(f"Nodes and edges saved to {nodes_file} and {edges_file}")

# Example usage
input_csv = "data/A_Z_medicines_dataset_of_India.csv"
nodes_output = "data/nodes.csv"
edges_output = "data/edges.csv"
create_nodes_edges(input_csv, nodes_output, edges_output)