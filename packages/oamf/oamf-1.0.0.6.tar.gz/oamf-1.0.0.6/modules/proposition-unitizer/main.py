from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
from src.data import Data, AIF
from src.propositionalizer import  Propositionalizer 
from src.utility import get_file,handle_errors
import logging
logging.basicConfig(datefmt='%H:%M:%S',
                    level=logging.DEBUG)



app = Flask(__name__)
metrics = PrometheusMetrics(app)
@app.route('/propositionUnitizer-01', methods = ['GET', 'POST'])
@metrics.summary('requests_by_status', 'Request latencies by status',
                 labels={'status': lambda r: r.status_code})
@metrics.histogram('requests_by_status_and_path', 'Request latencies by status and path',
                   labels={'status': lambda r: r.status_code, 'path': lambda: request.path})
@handle_errors
def propositionalizer_defult():
	if request.method == 'POST':
		file_obj = request.files['file']
		propositionaliser = Propositionalizer(file_obj)
		result=propositionaliser.propositionalizer_default()
		return result
	if request.method == 'GET':
		info = """PropositionUnitizer is an AMF component that performs preprocessing steps on propositions. 
		These steps include converting reported speeches and questions, resolving co-references, and creating 'I' nodes for every 'L' node. 
		This implementation serves as the default PropositionUnitizer, which injects 'I' nodes for every 'L' node. It accepts input and returns xIAF format. 
		The component can be connected to Turninator to inject 'I' nodes into the output of Turninator, as most AMF components process the 'I' nodes."""
		return info
	
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5004"), debug=False)	  
