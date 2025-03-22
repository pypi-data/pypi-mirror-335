import json

class PropositionalizerOutput:
    @staticmethod
    def format_output(nodes, edges, aif, x_aif):
        aif['nodes'] = nodes
        aif['edges'] =  edges        
        x_aif['AIF'] = aif
        return json.dumps(x_aif)
