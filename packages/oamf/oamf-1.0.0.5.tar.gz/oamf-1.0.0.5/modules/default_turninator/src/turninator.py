import re
from flask import json
import logging
# Explicitly import JSONDecodeError for better clarity
from json.decoder import JSONDecodeError
from xaif_eval import xaif

logging.basicConfig(datefmt='%H:%M:%S', level=logging.DEBUG)

from src.data import AIF
from src.templates import TurninatorOutput






class Turninator():
    def __init__(self,file_obj):
        self.file_obj = file_obj
        self.f_name = file_obj.filename
        self.file_obj.save(self.f_name)
        file = open(self.f_name,'r')
    
    def dialog_turns_old(self, text: str):
        '''Extract dialog turns from input text using regex.'''
        text = re.sub('<.*?>', '', text, flags=re.DOTALL)
        return re.findall(r'([A-Za-z ]+):((?:.|\n)*?)(?=(?:^[A-Za-z ]+:)|\Z)', text)
    
    def dialog_turns(self, text: str):
            '''Extract dialog turns from input text using regex.'''
            # Remove any HTML tags
            text = re.sub('<.*?>', '', text, flags=re.DOTALL)
            # Regular expression to capture speaker and their corresponding text
            return re.findall(r'([A-Za-z0-9_ -]+)\s*:\s*((?:.|\n)*?)(?=\n[A-Za-z0-9_ -]+\s*:\s*|\Z)', text)

    def monolog_text(self, text: str) -> str:
        '''Extract the entire text if monolog.'''
        return re.sub('<.*?>', '', text, flags=re.DOTALL)
    
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
    ###

    def get_aif(self, format='xAIF'):
        try:
            # Open and read the file content
            with open(self.f_name, 'r') as file:
                data = file.read()  # Read the raw content
                
                print(f"Raw data read from file: {data}")  # Debugging step
                
                # Convert to Python dictionary (or JSON object)
                x_aif = json.loads(data)  # Parse JSON string
                
                # If 'AIF' exists and is a string, convert it to a dictionary
                if 'AIF' in x_aif and isinstance(x_aif['AIF'], str):
                    try:
                        x_aif['AIF'] = json.loads(x_aif['AIF'])  # Parse 'AIF' value
                    except json.JSONDecodeError:
                        print("Warning: 'AIF' value is not valid JSON.")
                
                print(f"Parsed JSON object with 'AIF' as JSON: {x_aif}")  # Debugging step
                
                # Return the modified dictionary
                return x_aif
        
        except json.JSONDecodeError as e:
            # Handle JSON errors gracefully
            print(f"Error decoding JSON: {e}")
            return None
        except Exception as e:
            # Handle other exceptions
            print(f"An unexpected error occurred: {e}")
            return None


    def turninator_default(self,):
        # Get the file path from the path object

        AIF_obj = AIF()

        extended_json_aif = {}
        if self.f_name.endswith("json"):

            xAIF_input = self.get_aif()
            #logging.info(f"xAIF data:  {xAIF_input}, {self.file_obj}")  
            xaif_obj = xaif.AIF(xAIF_input)
            
            is_json_file = self.is_valid_json()
            
            if is_json_file:				
                nodes, edges, locutions = [], [], []
                extended_json_aif = xaif_obj.xaif
                logging.info(f"extended_json_aif:  {extended_json_aif}")  
                if 'AIF' in extended_json_aif and 'text' in extended_json_aif:
                    json_dict = extended_json_aif['AIF'] 
                    dialog = extended_json_aif.get('dialog', False)
                    OVA = extended_json_aif.get('OVA', [])
                    # Handle the case where 'json_dict' is a string
                    if isinstance(json_dict, str):
                        if json_dict.startswith('"'):
                            json_dict = json_dict.replace("\"", "")
                            json_dict = dict(json_dict)
                            logging.info(f'processing monolog text in json extenssion')
                    if not isinstance(json_dict, dict):
                        json_dict = json.loads(json_dict)
                    # Extract values associated with specific keys from the AIF section
                    schemefulfillments, descriptorfulfillments = AIF_obj.get_xAIF_arrays(aif_section=json_dict,
                                                                                     xaif_elements=['schemefulfillments', 'descriptorfulfillments'])
                    logging.info(f"xAIF valid:  {is_json_file}")  
                    participants = json_dict.get("participants", [])
                    if isinstance(extended_json_aif['text'], dict):
                        text = extended_json_aif['text']['txt']
                        logging.info(f'text with dict')
                    else:
                        text = extended_json_aif['text']  # gets the text
                        text = text + "\n"
                        logging.info(f'text without dict')
                        #logging.info(f'text :{text}')
                    if isinstance(text, str):
                        json_object = json.dumps(text)
                        json_object = json.loads(json_object) 
                        logging.info(f'text dumped')                   
                    is_dialog = extended_json_aif.get('dialog')
                    text_with_span = ""
                    node_id, person_id = 0, 0
                    # Extract dialog turns if it's a dialog, otherwise extract monolog text
                    logging.info(f'text : {text}')
                    logging.info(f'is dialog : {is_dialog}')
                    speakers_and_turns = self.dialog_turns(text) if is_dialog and len(self.dialog_turns(text)) else self.monolog_text(text)
                    #logging.info(f'speakers_and_turns : {speakers_and_turns}')
                    logging.info(f'length if turns ====================== : {len(self.dialog_turns(text)) }')
                    if is_dialog and len(self.dialog_turns(text)):
                        logging.info(f'processing dialog text from text format')
                        speakers_and_turns = self.dialog_turns(text)
                        nodes, locutions, participants, text_with_span, node_id, person_id = AIF_obj.create_turn_entry(
                            nodes, node_id, person_id, text_with_span, speakers_and_turns, locutions, participants, is_dialog)
                    else:
                        logging.info(f'====== Something else')
                        if not is_dialog:
                            logging.info(f'processing monolog text since not dialog')
                            speakers_and_turns = self.monolog_text(text)
                            nodes, locutions, participants, text_with_span, node_id, person_id = AIF_obj.create_turn_entry(
                                nodes, node_id, person_id, text_with_span, speakers_and_turns, locutions, participants, is_dialog)
                    return TurninatorOutput.format_output(nodes, edges, locutions, 
                                                          schemefulfillments, descriptorfulfillments, participants, 
                                                          OVA, text_with_span, dialog, json_dict, extended_json_aif)
                else:
                    if 'text' in extended_json_aif:
                        node_id, person_id = 0, 0
                        if isinstance(extended_json_aif['text'], dict):
                            text = extended_json_aif['text']['txt']
                        else:
                            text = extended_json_aif['text'] + "\n"
                        
                        aif, json_aif, OVA = {}, {}, {}      
                        text_with_span = ""
                        nodes, edges, schemefulfillments, descriptorfulfillments, participants, locutions = [], [], [], [], [], []
                        speakers_and_turns = self.monolog_text(text)                   
                        nodes, locutions, participants, text_with_span, node_id, person_id = AIF_obj.create_turn_entry(
                            nodes, node_id, person_id, text_with_span, speakers_and_turns, locutions, participants, False)
                        return TurninatorOutput.format_output(nodes, edges, locutions, schemefulfillments, descriptorfulfillments, participants, OVA, text_with_span, aif, extended_json_aif)
            else:
                logging.info(f'the file is not in a correct json format')
                return "Invalid json"
        else:
            # Non-json data is treated as monolog
            node_id, person_id = 0, 0
            with open(self.f_name, 'r') as file:
                data = file.read() + "\n"              
            aif, json_aif, OVA = {}, {}, {}       
            text_with_span = ""
            nodes, edges, schemefulfillments, descriptorfulfillments, participants, locutions = [], [], [], [], [], []
            speakers_and_turns = self.monolog_text(data)                    
            nodes, locutions, participants, text_with_span, node_id, person_id = AIF_obj.create_turn_entry(
                nodes, node_id, person_id, text_with_span, speakers_and_turns, locutions, participants, False)
            return TurninatorOutput.format_output(nodes, edges, locutions, schemefulfillments, descriptorfulfillments, participants, OVA, text_with_span,aif, json_aif)



