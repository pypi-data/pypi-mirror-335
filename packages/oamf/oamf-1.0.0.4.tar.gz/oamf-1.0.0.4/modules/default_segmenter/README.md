

# Default BERT Textual Entailment Service Documentation

## Introduction
This application provides an implementation of BART fine-tuned on NLI dataset for indetifying argument relations. It serves as a default AMF component designed for detecting argument relations between propositions. Entailemtnt relation is mapped to support relation,  conflicts, and non-relations between propositions.
- It can be integrated into the argument mining pipeline alongside other AMF components for further analysis and processing.


## Brief Overview of the Architecture/Method
Brief overview of the architecture/method used.

- **Dataset**: [Link to datasets](#)
- **Model ID**: [facebook/bart-large-mnli](https://huggingface.co/facebook/bart-large-mnli)
- **Repository**: [GitHub repository](https://github.com/arg-tech/bert-te)
- **Paper**: [Link to published paper](https://arxiv.org/abs/1909.00161)

## Endpoints

### /bert-te

#### Description
- **Methods**: `GET`, `POST`
  - **GET**: Returns information about the BERT Textual Entailment Service and its usage.
  - **POST**: Expects a file upload (`file` parameter) in the xAIF format. The Flask route processes the uploaded file identify argument relation between I-nodes and update the xAIF node to represent the argument relations and returns the updated xAIF as a json file. 

#### Details
- **URL**: `/bert-te`
- **Methods**: `GET`, `POST`
- **Input**:
  - **GET**: No parameters.
  - **POST**: Expects a file upload (`file` parameter) in the xAIF format.
- **Output**:
  - **Response**: The inferred argument structure in xAIF json file format, containing nodes, edges, locutions, and other relevant information.
  - **Example Response**: Example JSON response.

## Input and Output Formats

### Input Format
- **Text File**: xAIF format input ([xAIF format details](https://wiki.arg.tech/books/amf/page/xaif)).

### Output Format
The inferred argument structure is returned in the xAIF format, containing nodes, edges, locutions, and other relevant information. In the xAIF:
- Argument units are specified as type "I" nodes.
- Argument relations are represented as "RA" type for support and "CA" type for attack relations.
- The relations between the "I" nodes and argument relation nodes are presented as edges.

## Installation

### Requirements for Installation
torch
numpy
transformers
xaif_eval==0.0.9
amf-fast-inference==0.0.3
markdown2


### Installation Setup

#### Using Docker Container

To set up the BERT Textual Entailment Service using Docker, follow these steps:

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/arg-tech/bert-te.git
   ```

2. **Navigate to the Project Root Directory:**
   ```sh
   cd bert-te
   ```

3. **Make Required Changes:**
   - Edit the `Dockerfile`, `main.py`, and `docker-compose.yml` files to specify the container name, port number, and other settings as needed.

4. **Build and Run the Docker Container:**
   ```sh
   docker-compose up
   ```

#### From Source Without Docker

If you prefer to install without Docker:

1. **Install Dependencies:**
   - Ensure Python and necessary libraries are installed.

2. **Configure and Run:**
   - Configure the environment variables and settings in `main.py`.
   - Run the application using Python:
     ```sh
     python main.py
     ```



## Usage

### Using Programming Interface

#### Example Python Code Snippet

```python
import requests
import json

url = 'http://your-server-url/bert-te'
input_file_path = 'example_xAIF.json'

with open(input_file_path, 'r', encoding='utf-8') as file:
    files = {'file': (input_file_path, file, 'application/json')}

response = requests.post(url, files=files)

if response.status_code == 200:
    output_file_path = 'output_xAIF.json'
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(response.json(), output_file, ensure_ascii=False, indent=4)
    print(f'Response saved to {output_file_path}')
else:
    print(f'Failed to make a POST request. Status code: {response.status_code}')
    print(response.text)

```

### Using cURL

- **Example Request**:

```bash
curl -X POST \
  -F "file=@example_xAIF.json" \
  http://your-server-url/bert-te
```



### Using Web Interface

The service can also be used to create a pipeline on our n8n interface. Simply create an HTTP node, configure the node including the URL of the service and the parameter name of the file (`file`).




<div style="text-align:center;">
    <img src="img/n8n_screnshot.png" alt="Image Description" width="100%">
</div>

