#Import system modules
import arcpy
import json
import os
 
try:
	layer_file = open("D:\\dev\\ArcGISProCreateLayers\\LayerDefinition.json", "r")	
	layer_json = json.load(layer_file)
	gdb = arcpy.env.workspace
	
	# Create spatial reference to apply to the layers
	spatialRef = arcpy.SpatialReference("WGS 1984 Web Mercator (auxiliary sphere)")
	
	p = arcpy.mp.ArcGISProject('current')	
	m = p.listMaps("Map")[0]
	
	# Get the domains from the JSON
	domains = layer_json["domains"]	
	
	print("Creating Domains")
	
	for domain in domains:
		try:
			arcpy.CreateDomain_management(gdb, domain["name"], domain["description"], domain["field_type"], domain["domain_type"])
			
			if domain["domain_type"] == "CODED":
				domainValuesDict = domain["values"]
				
				# Loop through all the domain codes in the dictionary and add them to the domain
				for code in domainValuesDict:        
					arcpy.AddCodedValueToDomain_management(gdb, domain["name"], code, domainValuesDict[code])
			elif domain["domain_type"] == "RANGE":
				# Set the min and max values for a range domain
				arcpy.SetValueForRangeDomain_management(gdb, domain["name"], domain["min"], domain["max"])
			else:
				print("Unknown type of domain: " + domain["domain_type"])
		except Exception as domEx:
			print(domEx)
	
	# Create the layers
	layerList = layer_json["layers"]
	
	# Create dictionary object to populate with symbols and alias for the layers
	layerSymbolDict = {}
	layerAliasDict = {}
	
	for layer in layerList:
		print("Creating layer: " + layer["name"])
		
		# Create the feature class layer
		arcpy.CreateFeatureclass_management(gdb, layer["name"], layer["geometry_type"], spatial_reference=spatialRef)
		
		# Create empty fields array to populate
		fields = []
		
		try:
			# If layer has specific layer fields, combine them with the layer fields that will be applied to all layers
			if "fields" in layer:
				fields = layer_json["fields"] + layer["fields"]
			# Otherwise just use the layer fields that will be applied to all layers
			else:
				fields = layer_json["fields"]

			# Populate layer symbol dictionary for later use while looping through JSON layers
			layerSymbolDict[layer["name"]] = layer["symbology"]
			
			# Populate layer alias dictionary for later use while looping through JSON layers
			layerAliasDict[layer["name"]] = layer["alias"]
			
			# Loop through the fields and add them to the layer
			for field in fields:
				if field["field_domain"] != "None" and "length" in field:
					arcpy.AddField_management(layer["name"], field["name"], field["type"], field_length=field["length"], field_is_nullable=field["nullable"], field_alias=field["alias"], field_domain=field["field_domain"])
				elif field["type"] == "DATE":
					arcpy.AddField_management(layer["name"], field["name"], field["type"], field_is_nullable=field["nullable"], field_alias=field["alias"])					
				elif field["type"] == "FLOAT" or field["type"] == "SHORT":
					arcpy.AddField_management(layer["name"], field["name"], field["type"], field_is_nullable=field["nullable"], field_alias=field["alias"])	
				else:
					arcpy.AddField_management(layer["name"], field["name"], field["type"], field_length=field["length"], field_is_nullable=field["nullable"], field_alias=field["alias"])
		except Exception as flderr:
			print(flderr.args[0])
			
	print("Enabling Editor Tracking on Layers")
	
	# Retrieve all the tables and feature classes added
	dataList = arcpy.ListTables() + arcpy.ListFeatureClasses()

	# Loop through dataset list and enable editor tracking
	for dataset in dataList:
		arcpy.EnableEditorTracking_management(dataset,"created_user","created_date","last_edited_user","last_edited_date","ADD_FIELDS","UTC")
	
	# Begin apply symbology
	print("Applying symbology")
	
	# Retrieve all layers in the map
	layers = m.listLayers()

	# Loop through layers to apply symbology
	for lyr in layers:
		try:
			print("Applying symbology to " + lyr.name)
			sym = None 
			
			# Only apply symbology to feature layers
			if lyr.isFeatureLayer == False:
				continue
			
			# Retrive symbology definition for layer
			symbologyDef = layerSymbolDict[lyr.name]
			
			if symbologyDef['renderer'] == 'SimpleRenderer':
				sym = lyr.symbology
				symbolName = symbologyDef['symbol']['SymbolName']
				symbolIndex = symbologyDef['symbol']['Index']
				sym.renderer.symbol.applySymbolFromGallery(symbolName, symbolIndex)
				lyr.symbology = sym
				continue
			elif symbologyDef['renderer'] == 'UniqueValueRenderer':
				sym = lyr.symbology
				sym.updateRenderer(symbologyDef['renderer'])
				sym.renderer.fields = [ symbologyDef['field'] ]
				
				items = sym.renderer.groups[0].items

				itemSymbolDict = symbologyDef["groups"][0]
								
				for item in items:				
					symbolName = itemSymbolDict[item.label]["SymbolName"]
					symbolIndex = itemSymbolDict[item.label]["Index"]
					item.symbol.applySymbolFromGallery(symbolName, symbolIndex)
					
				lyr.symbology = sym
				continue

		except Exception as symEx:
			print(symEx)
			
	p.save()
	
	for lyr in layers:
		print("Applying alias name to " + lyr.name)
		
		if lyr.isFeatureLayer == False:
			continue
			
		lyr.name = layerAliasDict[lyr.name]
	
	print("Setting up Labels")
	
	for layer in layerList:
		lyrName = layerAliasDict[layer["name"]]
		try:
			print("Setting up label for " + lyrName)
			if layer["enableLabel"] == True:
				mapLyr = m.listLayers(lyrName)[0]
				if mapLyr.supports("SHOWLABELS"):
					labelClass = mapLyr.listLabelClasses('*')[0]
					labelClass.visible = True
					labelClass.expression = layer['labelProperties']['expression']
		except Exception as labelEx:
			print(labelEx)
			print(labelEx.args[0])
			print("Exception applying label to " + layer["name"])
			
	print("Turning on Labels")
	
	for layer in layerList:
		lyrName = layerAliasDict[layer["name"]]
		
		print("Turning on Labels for " + lyrName)
		if layer["enableLabel"] == True:
			mapLyr = m.listLayers(lyrName)[0]
			mapLyr.showLabels = True
			
except Exception as err:
	print(err)
	print(err.args[0])