import pandas as pd
from groq import Groq
import random
import json

def chat_with_groq(client, prompt, model, response_format):
  completion = client.chat.completions.create(
  model=model,
  messages=[
      {
          "role": "user",
          "content": prompt
      }
  ],
  response_format=response_format
  )

  return completion.choices[0].message.content

def find_similar_medicines(medicine_name, nodes_file, edges_file):
    # Load the data
    nodes_df = pd.read_csv(nodes_file)
    edges_df = pd.read_csv(edges_file)
    
    # Find the node_id for the given medicine
    medicine_node = nodes_df[nodes_df['label'] == medicine_name]
    if medicine_node.empty:
        return f"Medicine '{medicine_name}' not found."
    
    medicine_id = medicine_node['node_id'].values[0]

    
    # Find elements connected to this medicine
    elements = edges_df[edges_df['source'] == medicine_id]['target'].unique()
    
    # Find other medicines containing the same elements
    related_medicines = edges_df[edges_df['target'].isin(elements)]['source'].unique().tolist()

    related_medicines = random.sample(related_medicines, min(20, len(related_medicines)))
    
    
    # Get medicine names and their manufacturers excluding the searched one
    similar_meds_df = nodes_df[nodes_df['node_id'].isin(related_medicines) & (nodes_df['node_id'] != medicine_id)]
    similar_meds = []
    
    for _, row in similar_meds_df.iterrows():
        medicine_id = row['node_id']
        medicine_name = row['label']
        manufacturer = edges_df[(edges_df['source'] == medicine_id) & (edges_df['relationship'] == 'manufactured_by')]['target'].values
        manufacturer_name = nodes_df[nodes_df['node_id'].isin(manufacturer)]['label'].tolist()
        similar_meds.append((medicine_name, manufacturer_name))
    return similar_meds if similar_meds else "No similar medicines found."

def convert_to_readable_json(raw_json_string):
    try:
        # Convert the raw JSON string to a Python dictionary
        formatted_json = json.loads(raw_json_string)
        
        # Convert back to a properly formatted JSON string
        readable_json = json.dumps(formatted_json, indent=4)
        
        return readable_json
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {e}"


def generate_prompt(medicine_name,medicine_list):
    
    prompt =  f"""Given the medicine '{medicine_name}', compare it with the following medicines, which are all manufactured by Glaxo SmithKline Pharmaceuticals Ltd:
    
    {medicine_list}
    
    Comparison Criteria:
    Manufactured By – Identify and compare the manufacturer of '{medicine_name}' with the medicines listed above; if different, list the manufacturer of the medicine from the list.
    Active Ingredients – Identify and compare the active components of '{medicine_name}' with the medicines listed above; if different, list the Ingredients of the medicine from the list.
    Uses and Indications – Determine if the listed medicines serve similar medical purposes as '{medicine_name}',if different, list the usage and indications of the medicine from the list.
    Dosage Forms – Highlight any differences in dosage forms (e.g., tablet, suspension, injection),if different, list the dosage forms of the medicine from the list.
    Strength and Composition – Analyze variations in strength and composition, if different, list the strength and composition of the medicine from the list.
    Side Effects & Contraindications – Compare potential side effects and contraindications; if different, list the side effects of the medicine from the list.
    Prescription Use – Specify whether they are over-the-counter or prescription-based,if different, list the prescription use of the medicine from the list.
    Alternative Uses – If applicable, suggest cases where the listed medicines may serve as an alternative to '{medicine_name}' return the result in json."""

    return prompt


def LLM_GROQ(medicine_name):
    nodes_file = "data/nodes.csv"
    edges_file = "data/edges.csv"
    medicine_list = find_similar_medicines(medicine_name, nodes_file, edges_file)
    prompt = generate_prompt(medicine_name,medicine_list)
    
    model = "llama3-70b-8192"
    # Get the Groq API key and create a Groq client
    #groq_api_key = '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'
    groq_api_key = "Token"
    client = Groq(
    api_key=groq_api_key
    )
    # Get the AI's response. Call with '{"type": "json_object"}' to use JSON mode
    llm_response = chat_with_groq(client, prompt, model, {"type": "json_object"})
    llm_response = convert_to_readable_json(llm_response)
    return llm_response