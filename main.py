# app.py
from flask import Flask, request, jsonify
from src.llm_am import LLMArgumentStructure
from src.llm_segmenter import LLMSegmenter
import json

app = Flask(__name__)

@app.route('/segmenter', methods=['POST'])
def segmenter():
    """Segments an argumentative paragraph into discourse units."""

    file_obj = request.files['file']
    Segmenter = LLMSegmenter(file_obj)
    result=Segmenter.segmenter_default()
    return result

@app.route('/relation_identifier', methods=['POST'])
def relation_identifier():
    """Classifies the relationship between two discourse units."""
    file_obj = request.files['file']
    result = LLMArgumentStructure(file_obj).get_argument_structure()

    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5030)
