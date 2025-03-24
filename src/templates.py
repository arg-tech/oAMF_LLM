import json

class SegmenterOutput:
    @staticmethod
    def format_output(nodes, edges, locutions, aif, x_aif):
        aif['nodes'] =  nodes
        aif['edges'] =  edges
        aif['locutions'] =  locutions
        x_aif['AIF'] = aif
        return json.dumps(x_aif)
