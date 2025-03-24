import ollama
import json
from xaif_eval import xaif
from itertools import combinations




"""This file provides a simple segmenter that splits texts based on regex. 
The default segmenter takes xAIF, segments the texts in each L-node, 
introduces new L-node entries for each of the new segments, and deletes the old L-node entries.
"""

import re
from flask import json
import logging


from src.data import Data
from xaif_eval import xaif
from src.templates import SegmenterOutput
logging.basicConfig(datefmt='%H:%M:%S',
                    level=logging.DEBUG)

class LLMSegmenter():
    def __init__(self,file_obj):
        self.file_obj = file_obj
        self.f_name = file_obj.filename
        self.file_obj.save(self.f_name)
        file = open(self.f_name,'r')

    def llm_model(self, prompt, model_name="deepseek-r1:1.5b"):
        """Run deepseek-r1:7b model with a given prompt using Ollama API."""
        response = ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'].strip()



    def get_segments(self, prompt, model_name="deepseek-r1:7b"):
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
    def is_valid_json_aif(self,aif_nodes):
        if 'nodes' in aif_nodes and 'locutions' in aif_nodes and 'edges' in aif_nodes:
            return True
        return False
        

    def get_aif(self, format='xAIF'):

        with open(self.f_name) as file:
            data = file.read()
            x_aif = json.loads(data)
            if format == "xAIF":
                return x_aif
            else:
                aif = x_aif.get('AIF')
                return json.dumps(aif)


    def segmenter_default(self,):
        """The default segmenter takes xAIF, segments the texts in each L-nodes,
        introduce new L-node entries for each of the new segements and delete the old L-node entries
        """
        xAIF_input = self.get_aif()
        logging.info(f"xAIF data:  {xAIF_input}, {self.file_obj}")  
        xaif_obj = xaif.AIF(xAIF_input)
        is_json_file = self.is_valid_json()
        if is_json_file:				
            json_dict = xaif_obj.aif
            if self.is_valid_json_aif(json_dict):
                nodes = json_dict['nodes']		
                for nodes_entry in nodes:
                    node_id = nodes_entry['nodeID']
                    node_text = nodes_entry['text']
                    type = nodes_entry['type']
                    if type == "L":
                        prompt = f"""
                        Segment the following paragraph into discourse units. 
                        Provide the result as a JSON list of segments. Do not provide any explanations.
                        
                        Paragraph: {node_text}
                        """
                        response = self.get_segments(prompt)
                        logging.info(f"xAIF data:  {response}, {response}")  
    
                        try:
                            segments = json.loads(response)  # Expecting JSON list
                        except ValueError as e:
                            segments = response.split("\n")
                        segments = [seg.strip() for seg in segments if len(seg.strip()) > 0]
                        if len(segments) > 1:							
                            xaif_obj.add_component("segment", node_id, segments)										


                return xaif_obj.xaif
            else:
                return("Invalid json-aif")
        else:
            return("Invalid input")




