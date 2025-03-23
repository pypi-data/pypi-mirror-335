from flask import Flask, request,render_template_string
from prometheus_flask_exporter import PrometheusMetrics
import markdown2
from flask_cors import CORS

from src.segmenter import Segmenter
from src.data import Data
from src.utility import handle_errors

import logging
logging.basicConfig(datefmt='%H:%M:%S',
                    level=logging.DEBUG)

app = Flask(__name__)



CORS(app, resources={r"/*": {"origins": "https://arg-tech.github.io"}})
metrics = PrometheusMetrics(app)
	
@app.route('/segmenter-01', methods = ['GET', 'POST'])
@metrics.summary('requests_by_status', 'Request latencies by status',
                 labels={'status': lambda r: r.status_code})
@metrics.histogram('requests_by_status_and_path', 'Request latencies by status and path',
                   labels={'status': lambda r: r.status_code, 'path': lambda: request.path})
@handle_errors  
def segmenter_defult():
	if request.method == 'POST':
		file_obj = request.files['file']
		segmenter = Segmenter(file_obj)
		result=segmenter.segmenter_default()
		return result
	if request.method == 'GET':
		# Read the markdown file
		with open('README.md', 'r') as file:
			md_content = file.read()

		# Convert to HTML
		html_content = markdown2.markdown(md_content)

		# Add CSS link
		css_link = '<link rel="stylesheet" href="https://example.com/path/to/your/styles.css">'
		html_with_css = f"<html><head>{css_link}</head><body>{html_content}</body></html>"

		# Render the HTML content as a template
		return render_template_string(html_with_css)

	
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5005"), debug=False)	  
