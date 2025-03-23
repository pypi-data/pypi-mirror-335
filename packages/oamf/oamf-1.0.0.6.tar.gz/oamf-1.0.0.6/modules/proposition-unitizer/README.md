# Default PropositionUnitizer

This app provides a default implementation of PropositionUnitizer, an AMF component that performs preprocessing steps on propositions. 
It is designed to convert reported speeches and questions, resolve co-references, and create 'I' nodes for every 'L' node. 
The app accepts input in various formats and returns data in xIAF format.

## Endpoints

### /propositionUnitizer-01

- **Methods**: GET, POST
- **Description**: 
  - **GET**: Returns information about the PropositionUnitizer component and its usage.
  - **POST**: Expects a file upload containing propositions data. Performs preprocessing steps and returns the processed output in xIAF format.

## Usage

- Use the `/propositionUnitizer-01` endpoint to interact with the PropositionUnitizer:
   - For GET requests, visit the endpoint URL to get information about PropositionUnitizer usage.
   - For POST requests, upload a file containing propositions data to preprocess and receive the processed output.

## Input Format

- **JSON (xIAF)**: Input can be provided in the xIAF format.

## Output Format

The processed output is returned in xIAF format, containing preprocessed nodes, edges, locutions, and other relevant information.

## Notes

- This app serves as a default PropositionUnitizer implementation, injecting 'I' nodes for every 'L' node in the input.
- It can be connected to other AMF components, such as Turninator, to preprocess their output before further analysis.
