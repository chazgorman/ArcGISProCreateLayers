This project includes a python script that can be run in the ArcGIS Pro python window to generate layers based on layer definitions defined in JSON.

From the layer definition JSON, the script generates:
- Field domains, both CODED and RANGE
- Feature class layers
- Fields for feature class layers
- Editor tracking on layers
- Layer symbology for 'Simple Renderer' and for single group 'Unique Value Renderer'
- Layer aliases

Usage:
1. Create a new ArcGIS Pro Project
2. Add a map to the project, keeping the default name of 'Map'
3. Update layer definition JSON file location in code: layer_file = open("C:\\yourdir\\LayerDefinition.json", "r")
4. From the Python window in ArcGIS Pro, right-click and select "Load Code"
5. Navigate to and select your ArcGISPro_CreateLayers.py script
6. In the ArcGIS Pro python window, ensure the cursor is at the very end of the script
7. Press Enter three times to run the script
8. Sit back and relax

TODO:
1. Add labelling
2. More docs on the layer definition JSON

![Alt text](/docs/Demo.png?raw=true "Screenshot of Script Execution")

