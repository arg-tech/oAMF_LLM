import ollama
import json
from xaif_eval import xaif
from itertools import combinations


class LLMArgumentStructure:
    def __init__(self,file_obj):
        self.file_obj = file_obj

        self.file_obj = file_obj
        self.f_name = file_obj.filename
        self.file_obj.save(self.f_name)
        file = open(self.f_name,'r')

        xAIF_input = self.get_aif()  
        self.aif_obj = xaif.AIF(xAIF_input)

    def llm_model(self, prompt, model_name="deepseek-r1:1.5b"):
        """Run deepseek-r1:7b model with a given prompt using Ollama API."""
        response = ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'].strip()

    def is_valid_json(self):
        ''' check if the file is valid json
		'''

        try:
            json.loads(open(self.f_name).read())
        except ValueError as e:			
            return False

        return True
    def is_valid_json_aif(sel,aif_nodes):
        if 'nodes' in aif_nodes and 'locutions' in aif_nodes and 'edges' in aif_nodes:
            return True
        return False

    def get_aif(self, format='xAIF'):
        if self.is_valid_json():
            with open(self.f_name) as file:
                data = file.read()
                x_aif = json.loads(data)
                if format == "xAIF":
                    return x_aif
                else:
                    aif = x_aif.get('AIF')
                    return json.dumps(aif)
        else:
            return "Invalid json"



    def get_argument_structure(self):
        """Retrieve the argument structure from the input data."""
        data = self.get_aif()
        if not data:
            return "Invalid input"
        
        x_aif = self.aif_obj.xaif
        aif =  self.aif_obj.aif
        if not self.is_valid_aif(aif):
            return "Invalid json-aif"

        propositions_id_pairs = self.get_propositions_id_pairs(aif)
        self.update_node_edge_with_relations(propositions_id_pairs)

        return x_aif


    def is_valid_aif(self, aif):
        """Check if the AIF data is valid."""
        return 'nodes' in aif and 'edges' in aif

    def get_propositions_id_pairs(self, aif):
        """Extract proposition ID pairs from the AIF data."""
        propositions_id_pairs = {}
        for node in aif.get('nodes', []):
            if node.get('type') == "I":
                proposition = node.get('text', '').strip()
                if proposition:
                    node_id = node.get('nodeID')
                    propositions_id_pairs[node_id] = proposition
        return propositions_id_pairs
    
    def update_node_edge_with_relations(self, propositions_id_pairs):
        """
        Update the nodes and edges in the AIF structure to reflect the new relations between propositions.
        """
        checked_pairs = set()
        for prop1_node_id, prop1 in propositions_id_pairs.items():
            for prop2_node_id, prop2 in propositions_id_pairs.items():
                if prop1_node_id != prop2_node_id:
                    pair1 = (prop1_node_id, prop2_node_id)
                    pair2 = (prop2_node_id, prop1_node_id)
                    if pair1 not in checked_pairs and pair2 not in checked_pairs:
                        checked_pairs.add(pair1)
                        checked_pairs.add(pair2)
                        prompt = f"""
                            Given the two argumentative texts:
                            1. {pair1}
                            2. {pair2}
                            
                            Classify their relationship as one of the following: 'Support', 'Attack', 'Rephrase', or 'None'.
                            Provide the classification as a JSON object in the format {{"relation": label}}.
                            """
                        
                        response = self.llm_model(prompt)
                        print(response)
                        
                        
                        try:
                            relation = json.loads(response).get("relation", "Unknown")
                        except ValueError as e:
                            relation = response
                        if relation =='Support':
                            predictions = "RA"
                        elif relation == 'Attack':
                            predictions = "CA"
                        elif relation == 'Rephrase':
                            predictions = "MA"
                        else:
                            predictions = "None"

                        for prediction in predictions:
                            if prediction in ['RA','MA','CA']:
                                self.aif_obj.add_component("argument_relation", prediction, prop1_node_id, prop2_node_id)
                            



    def update_node_edge_with_relations__(self, propositions_id_pairs, batch_size=4):
        """
        Update the nodes and edges in the AIF structure to reflect the new relations between propositions.
        """
        pairs_to_predict = []
        pair_ids = []

        # Use combinations to create pairs without redundant checking
        for (prop1_node_id, prop1), (prop2_node_id, prop2) in combinations(propositions_id_pairs.items(), 2):
            pairs_to_predict.append(prop1+ "" + prop2)
            pair_ids.append((prop1_node_id, prop2_node_id))

        # Process pairs in batches
        for i in range(0, len(pairs_to_predict), batch_size):
            batch_pairs = pairs_to_predict[i:i+batch_size]
            batch_pair_ids = pair_ids[i:i+batch_size]
            
            # Assuming `self.model.predict` can handle batches of inputs
            #predictions = self.model.predict(batch_pairs)
            predictions = self.llm_model(batch_pairs)
            
            for (prop1_node_id, prop2_node_id), prediction in zip(batch_pair_ids, predictions):
                if prediction in ['RA', 'MA', 'CA']:
                    self.aif_obj.add_component("argument_relation", prediction, prop1_node_id, prop2_node_id)
                    
