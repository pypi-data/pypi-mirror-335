# Default Segmenter

It provides a default implementation of Segmenter, an AMF component that segments arguments into propositions. It utilises simple regular expressions for text segmentation.

## Endpoints

### /segmenter-01

- **Methods**: GET, POST
- **Description**: 
  - **GET**: Returns information about the Segmenter component and its usage.
  - **POST**: Expects a file upload containing text data to segment. Parses the input and returns the segmented output in xIAF format.

## Usage

- Use the `/segmenter-01` endpoint to interact with the Segmenter:
   - For GET requests, visit the endpoint URL to get information about Segmenter usage.
   - For POST requests, upload a file containing text data to segment and receive the segmented output.

## Input Format

The Segmenter accepts input in  xIAF formats:

- **xIAF**: It segements the texts in the L-nodes.

## Output Format

The processed output is returned in xIAF format, containing segmented nodes, edges, locutions, and keeps the rest as they are.

## Notes

- This app serves as a basic segmenter using regular expressions for text segmentation.
- It can be connected to other components in an argument mining pipeline for further analysis.
