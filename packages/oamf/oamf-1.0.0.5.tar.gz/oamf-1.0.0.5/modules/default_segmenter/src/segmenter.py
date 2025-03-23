"""This file provides a simple segmenter that splits texts based on regex. 
The default segmenter takes xAIF, segments the texts in each L-node, 
introduces new L-node entries for each of the new segments, and deletes the old L-node entries.
"""

import re
from flask import json
import logging
import spacy

# Load the pre-trained spaCy model for English
nlp = spacy.load("en_core_web_sm")
from src.data import Data
from xaif_eval import xaif
from src.templates import SegmenterOutput
logging.basicConfig(datefmt='%H:%M:%S',
                    level=logging.DEBUG)

class Segmenter():
	def __init__(self,file_obj):
		self.file_obj = file_obj
		self.f_name = file_obj.filename
		self.file_obj.save(self.f_name)
		file = open(self.f_name,'r')

	def get_segments(self, input_text):
		"""Split input text into sentences using spaCy's sentence segmentation."""
		doc = nlp(input_text)  # Process the input text using spaCy
		return [sent.text.strip() for sent in doc.sents]  # Return sentences, stripping any extra spaces

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
						segments = self.get_segments(node_text)
						segments = [seg.strip() for seg in segments if len(seg.strip()) > 1]
						if len(segments) > 1:
							for segment in segments:								
								if segment != "":	
									xaif_obj.add_component("segment", node_id, segment)										


				return xaif_obj.xaif
			else:
				return("Invalid json-aif")
		else:
			return("Invalid input")
	

'''
{"AIF":{"edges":[{"edgeID":"1","formEdgeID":"None","fromID":"247603","toID":"247602"},{"edgeID":"2","formEdgeID":"None","fromID":"247604","toID":"247603"}],"locutions":[],
"nodes":[{"nodeID":"1","text":"THANK YOU","timestamp":"2016-10-31 17:17:34","type":"I"},{"nodeID":"2","text":"COOPER : THANK YOU","timestamp":"2016-11-10 18:34:23","type":"L"},
{"nodeID":"3","text":"You are well come","timestamp":"2016-10-31 17:17:34","type":"I"},{"nodeID":"4","text":"Bob : You are well come","timestamp":"2016-11-10 18:34:23","type":"L"},
{"nodeID":"5","text":"does or doesn't Jeane Freeman think the SNP is divided with what is going on","timestamp":"","type":"I"},
{"nodeID":"6","text":"the SNP is a big party","timestamp":"","type":"I"},{"nodeID":"7","text":"would or wouldn't Jeane Freeman describe the SNP as united","timestamp":"","type":"I"},
{"nodeID":"8","text":"the SNP has disagreements","timestamp":"","type":"I"},{"nodeID":"9","text":"the SNP has disagreements","timestamp":"","type":"I"},
{"nodeID":"10","text":"Michael Forsyth belongs to a party that has disagreements","timestamp":"","type":"I"},
{"nodeID":"11","text":"one disagreement of Michael Forsyth's party is currently about their Scottish leader","timestamp":"","type":"I"},
{"nodeID":"12","text":"Iain Murray has had disagreements with his party","timestamp":"","type":"I"},
{"nodeID":"13","text":"it's not uncommon for there to be disagreements between party members","timestamp":"","type":"I"},
{"nodeID":"14","text":"disagreements between party members are entirely to be expected","timestamp":"","type":"I"},
{"nodeID":"15","text":"what isn't acceptable is any disagreements are conducted that is disrespectful of other points of view","timestamp":"","type":"I"},
{"nodeID":"16","text":"Jeanne Freeman wants to be in a political party and a country where different viewpoints. and different arguments, Donald Dyer famously said, are conducted with respect and without abuse","timestamp":"","type":"I"},{"nodeID":"17","text":"who does or doesn't Jeanne Freeman think is being disrespectful then","timestamp":"","type":"I"},{"nodeID":"18","text":"people feel, when they have been voicing opinions on different matters, that they have been not listened to","timestamp":"","type":"I"},
{"nodeID":"19","text":"people feel that they have been treated disrespectfully on all sides of the different arguments and disputes going on","timestamp":"","type":"I"}],"participants":[]}}




{"aif":{"edges":[{"edgeID":"1","formEdgeID":"None","fromID":"1","toID":"20"},{"edgeID":"2","formEdgeID":"None","fromID":"20","toID":"3"}],"locutions":[],
"nodes":[{"nodeID":"1","text":"THANK YOU","timestamp":"2016-10-31 17:17:34","type":"I"},
{"nodeID":"2","text":"COOPER : THANK YOU","timestamp":"2016-11-10 18:34:23","type":"L"},
{"nodeID":"3","text":"You are well come","timestamp":"2016-10-31 17:17:34","type":"I"},
{"nodeID":"4","text":"Bob : You are well come","timestamp":"2016-11-10 18:34:23","type":"L"},
{"nodeID":"5","text":"does or doesn't Jeane Freeman think the SNP is divided with what is going on","timestamp":"","type":"I"},
{"nodeID":"6","text":"the SNP is a big party","timestamp":"","type":"I"},{"nodeID":"20","text":"Default Inference","timestamp":"","type":"RA"},
{"nodeID":"7","text":"would or wouldn't Jeane Freeman describe the SNP as united","timestamp":"","type":"I"},
{"nodeID":"8","text":"the SNP has disagreements","timestamp":"","type":"I"},{"nodeID":"9","text":"the SNP has disagreements","timestamp":"","type":"I"},
{"nodeID":"10","text":"Michael Forsyth belongs to a party that has disagreements","timestamp":"","type":"I"},
{"nodeID":"11","text":"one disagreement of Michael Forsyth's party is currently about their Scottish leader","timestamp":"","type":"I"},
{"nodeID":"12","text":"Iain Murray has had disagreements with his party","timestamp":"","type":"I"},
{"nodeID":"13","text":"it's not uncommon for there to be disagreements between party members","timestamp":"","type":"I"},
{"nodeID":"14","text":"disagreements between party members are entirely to be expected","timestamp":"","type":"I"},
{"nodeID":"15","text":"what isn't acceptable is any disagreements are conducted that is disrespectful of other points of view","timestamp":"","type":"I"},
{"nodeID":"16","text":"Jeanne Freeman wants to be in a political party and a country where different viewpoints and different arguments, Donald Dyer famously said, are conducted with respect and without abuse","timestamp":"","type":"I"},
{"nodeID":"17","text":"who does or doesn't Jeanne Freeman think is being disrespectful then","timestamp":"","type":"I"},
{"nodeID":"18","text":"people feel, when they have been voicing opinions on different matters, that they have been not listened to","timestamp":"","type":"I"},
{"nodeID":"19","text":"people feel that they have been treated disrespectfully. on all sides of the different arguments and disputes going on","timestamp":"","type":"I"}],"participants":[]}}
'''




  
