import ollama
import json
from xaif_eval import xaif
from itertools import combinations
import re




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



    def get_segments(self, prompt, model_name="deepseek-r1:1.5b"):
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

                        # Refined prompt to DeepSeek
                        prompt = f"""
                        Segment the following text into argumentative discourse units (ADUs). Each ADU represents a distinct argumentative claim or premise within the text. Do not include explanations or thinking steps. Only provide the final list of argumentative discourse units as a 1D JSON array. So no dictionary.
                        If if the input text is already small segement, just return the original text without segmenting. 

                        Input text: {node_text}

                        Ensure that each segment is a complete argumentative claim, or premise. Do not rephrase, or summarise, you have to segment the existing text as it is. Do not also add any text other than what is provided.
                    
                        """

                        response = self.get_segments(prompt)
                        logging.info(f"xAIF data:  {response}, {response}")  
                        response_cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    
                        try:
                            segments = json.loads(response_cleaned)  # Expecting JSON list
                        except ValueError as e:
                            logging.info(f"Error data ---------------:  {response_cleaned}, {response_cleaned}")  
                            segments = response_cleaned.split("\n")
                        if len(segments) > 1:	
                            segments = [seg.strip() for seg in segments if len(seg.strip()) > 0]
                            for segement in segments:
                                if 	len(segement) > 1:					
                                    xaif_obj.add_component("segment", node_id, segement)										


                return xaif_obj.xaif
            else:
                return("Invalid json-aif")
        else:
            return("Invalid input")




