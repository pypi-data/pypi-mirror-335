
from transformers import BartTokenizer


from transformers import pipeline
from amf_fast_inference import model
import logging
import json

logging.basicConfig(datefmt='%H:%M:%S', level=logging.DEBUG)
#

class Model:
    def __init__(self, model_path):
        self.model_path = model_path
        self.tokenizer = BartTokenizer.from_pretrained(model_path)
        #tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        #self.model = BartForSequenceClassification.from_pretrained(model_path)
        loader = model.ModelLoader(model_path)
        pruned_model = loader.load_model()
        self.pipe = pipeline("text-classification", model=pruned_model, tokenizer=self.tokenizer )
        self.RA_TRESHOLD = 80
        self.CA_TRESHOLD = 10

    def predict(self, proposition_pair):
        #proposition1, proposition2 = proposition_pair
        outputs = self.pipe(proposition_pair)
        logging.info(f"xAIF data:  {outputs}") 
        relations = [output['label'] for output in outputs]
        #return self._post_process(proposition1, proposition2)
        return self._post_process(relations)

    def _get_prob(self, text1, text2):
        input_ids = self.tokenizer.encode(text1, text2, return_tensors='pt')
        #logits = self.model(input_ids)[0]
        #[{'label': 'neutral', 'score': 0.796902596950531}]
        logits = self.pipe(text1+ " [SEP] " +text2)
        #logging.info(f"xAIF data:  {logits}")  
        logits = self.pipe(text1+ " [SEP] " +text2)[0]
        entail_contradiction_logits = logits[:, [0, 2]]
        probs = entail_contradiction_logits.softmax(dim=1)
        true_prob = probs[:, 1].item() * 100
        return true_prob

    def _post_process_(self, text1, text2):
        true_prob, arg_rel = 0.0, "None"
        true_prob1 = self._get_prob(text1, text2)
        true_prob2 = self._get_prob(text2, text1)
        true_prob = max(true_prob1, true_prob2)
        
        if true_prob > self.RA_TRESHOLD:
            arg_rel = "RA"
        elif true_prob < self.CA_TRESHOLD:
            arg_rel = "CA"
        else:
            arg_rel = "None"

        return arg_rel
    
    def _post_process(self, results):  
        arg_rels = []  
        arg_rel = "None" 
        for result in results:  
            if result == 'entailment':
                arg_rel = "RA"
            elif result ==  'contradiction':
                arg_rel = "CA"
            else:
                arg_rel = "None"
            arg_rels.append(arg_rel)

        return arg_rels

