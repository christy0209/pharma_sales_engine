import pandas as pd
from groq import Groq
import random
import json
from dotenv import load_dotenv
import os
import io

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
    
def filter_json(json_data):
    data = json.loads(json_data)

    # Filter the dictionary
    filtered_data = {}
    for key, details in data.items():
        # Get the list of comparisons, defaulting to an empty list if not present
        comparisons = details.get('Comparisons', [])
        # Filter comparisons where "Alternative Uses" is "Yes"
        filtered_comparisons = [comp for comp in comparisons if comp.get('Alternative Uses', '').lower() == 'yes']
        if filtered_comparisons:
            filtered_data[key] = {'Comparisons': filtered_comparisons}

    return filtered_data




def generate_prompt(medicine_name,medicine_list):
    
    prompt = f"""Given the medicine '{medicine_name}', compare it with the following medicines'{medicine_list}'
    Comparison Criteria:
    1. Manufactured By – Identify and compare the manufacturer of '{medicine_name}' with the medicines listed above; if different, include the actual manufacturer value from the medicine in the list.
    2. Active Ingredients – Identify and compare the active components of '{medicine_name}' with those of the medicines listed above; if they differ, include the actual active ingredients of the medicine from the list.
    3. Uses and Indications – Determine if the listed medicines serve similar medical purposes as '{medicine_name}'; if not, include the actual uses and indications of the medicine from the list.
    4. Dosage Forms – Highlight any differences in dosage forms (e.g., tablet, suspension, injection); if different, include the actual dosage forms of the medicine from the list.
    5. Strength and Composition – Analyze variations in strength and composition; if they differ, include the actual strength and composition details of the medicine from the list.
    6. Side Effects & Contraindications – Compare potential side effects and contraindications; if different, include the actual side effects and contraindications of the medicine from the list.
    7. Prescription Use – Specify whether the medicines are over-the-counter or prescription-based; if different, include the actual prescription use details of the medicine from the list.
    8. Alternative Uses – If applicable, suggest cases where the listed medicines may serve as an alternative to '{medicine_name}' and include the actual alternative use details from the medicine in the list.

    sample output format
               
               'Medicine': 'Zenflox-OZ Tablet',
               'Manufactured By': 'Mankind Pharma Ltd',
               'Active Ingredients': 'ammoxillin',
               'Uses and Indications': 'Muscle relaxation and pain relie',
               'Dosage Forms': 'Injection',
               'Strength and Composition': 'Ofloxacin (200mg) + Ornidazole (500mg)',
               'Side Effects & Contraindications': 'Nausea,Dizziness',
               'Prescription Use': 'Swallow it as a whole. Do not chew, crush or break it',
               'Alternative Uses': 'Yes' - if an alternative for {medicine_name}
           ,

    Return the result in JSON format."""


    return prompt


def LLM_GROQ(medicine_name):
    nodes_file = "data/nodes.csv"
    edges_file = "data/edges.csv"
    medicine_list = find_similar_medicines(medicine_name, nodes_file, edges_file)
    prompt = generate_prompt(medicine_name,medicine_list)
    
    model = "llama3-70b-8192"
    # Get the Groq API key and create a Groq client
    load_dotenv(".env")
    groq_api_key = os.getenv("groq_api_key")
    client = Groq(
    api_key=groq_api_key
    )
    # Get the AI's response. Call with '{"type": "json_object"}' to use JSON mode
    llm_response = chat_with_groq(client, prompt, model, {"type": "json_object"})
    llm_response = convert_to_readable_json(llm_response)
    return llm_response

def generate_df(str_data):
    data_dict = json.loads(str_data)
    first_value = next(iter(data_dict.values()))
    df = pd.DataFrame(first_value)
    df = df[df['Alternative Uses']=='Yes']
    df = df.reset_index(drop=True)
    return df