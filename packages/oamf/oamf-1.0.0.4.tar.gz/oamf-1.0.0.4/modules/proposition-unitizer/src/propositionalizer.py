

import logging
from src.utility import get_next_max_id
import json

from src.templates import PropositionalizerOutput




import logging
from src.data import Data
from xaif_eval import xaif

logging.basicConfig(datefmt='%H:%M:%S',
                    level=logging.DEBUG)



class Propositionalizer():
	def __init__(self,file_obj):
		self.file_obj = file_obj
		self.f_name = file_obj.filename
		self.file_obj.save(self.f_name)
		file = open(self.f_name,'r')


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


	def propositionalizer(self,):
		xAIF_input = self.get_aif()
		logging.info(f"xAIF data:  {xAIF_input}, {self.file_obj}")  
		xaif_obj = xaif.AIF(xAIF_input)
		is_json_file = self.is_valid_json()
		if is_json_file:				
			json_dict = xaif_obj.aif
			if self.is_valid_json_aif(json_dict):
				nodes = json_dict['nodes']		
				nodes, edges  = json_dict['nodes'], json_dict['edges']				
				original_nodes = nodes.copy()			
				i_nodes_lis = []
				for nodes_entry in original_nodes:
					propositions = nodes_entry['text']
					node_id = nodes_entry['nodeID'] 
					if propositions not in i_nodes_lis:
						if nodes_entry['type'] == "L":						
							inode_id = get_next_max_id(nodes, "nodeID")
							nodes.append({'text': propositions, 'type':'I','nodeID': inode_id})
							i_nodes_lis.append(propositions)
							y_id = get_next_max_id(nodes, "nodeID")
							nodes.append({'text': 'Default Illocuting', 'type':'YA','nodeID': y_id})
							if edges:	
								edge_id = get_next_max_id(edges, "edgeID")
							else:
								edge_id = 0
							edges.append({'toID': y_id, 'fromID':node_id,'edgeID': edge_id})
							edge_id = get_next_max_id(edges, "edgeID")
							edges.append({'toID': inode_id, 'fromID':y_id,'edgeID': edge_id})

				return xaif_obj.xaif
			else:
				return("Incorrect json-aif format")
		else:
			return("Incorrect input format")



	####################
	def propositionalizer_default(self,):	
		json_aif = self.propositionalizer() 	
		return json_aif


