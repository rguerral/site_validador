import pandas as pd
import xlsxwriter
import io
import string

# Verifica que un valor sea numerico y entero
def is_integer(number):
	try:
		number = float(number)
	except:
		return False
	if number%1 == 0:
		return True
	else:
		return False

# Verifica formato de una hoja excel:
# * Las columnas del df_original estén en el df subido
# * Los campos no modificables no se hayan modificado
# Si una hoja (p.ej. TP1 - COMPUTADORES) falla la validación de formato, toda esa hoja queda invalidada
def check_sheet_format(
	sheet_name,
	df_original,
	df_uploaded):
	errors = []
	# Que no se hayan modificado las columnas
	for j, column in enumerate(df_original.columns):
		if column not in list(df_uploaded.columns):
			errors.append("ERROR: Se modificaron celdas grises: (.,{})".format(column))
			return errors
	# Que no se hayan modificado campos grises
	df_original_greycolumns = df_original.dropna(axis=1, how='all')
	for j,column in enumerate(df_original_greycolumns.columns):
		for i, row in enumerate(df_uploaded[column]):
			if row != df_original_greycolumns.loc[i,column]:
				errors.append("ERROR: Se modificaron celdas grises: ({},{})".format(i+1, column))
				return errors
	return errors

# Valida
def validate_bids(
	files,
	data,
	excel_template):

	bidattributes = list(data["bidattributes"].keys())
	data_bidattributes = data["bidattributes"]
	tps = list(data["products"].keys())
	data_tps = data["products"]


	excel_template = pd.ExcelFile(excel_template, engine='openpyxl')
	output_rows = []
	for file in files:
		bid_name = ".".join(file.name.split(".")[0:-1])
		excel_bid = pd.ExcelFile(file, engine='openpyxl')

		# Bidattributes 
		error_sheet_dontexist = False 
		for bidattribute in bidattributes:
			levels = list(data_bidattributes[bidattribute]["values"].keys())
			zones = list(data_bidattributes[bidattribute]["values"][levels[0]].keys())
			sheet_name = bidattribute

			# Check que exista la hoja
			if not sheet_name in excel_bid.sheet_names:
				for level in levels:
					for zone in zones:
						output_rows.append(
							{
							"bid_name":bid_name,
							"sheet_type": "bid_attribute",
							"sheet_name": sheet_name,
							"zone": zone,
							"level_or_model": level,
							"attribute": "PRECIO",
							"value": None,
							"status": "ERROR: No existe hoja"
							})
				continue

			# Load bid (existe)
			sheet_bid = pd.read_excel(excel_bid, sheet_name)
			# TEMPLATE: borrar ultima fila y ultima columna, estan full NAs.
			# quedan así al darles formato (borde superior y borde izquierdo)
			sheet_template = pd.read_excel(excel_template, sheet_name)
			sheet_template = sheet_template.iloc[:-1, :-1].copy()

			# Check que las celdas grises de la hoja no hayan sido modificadas
			errores_sheet_format = check_sheet_format(
				sheet_name = sheet_name,
				df_original = sheet_template,
				df_uploaded = sheet_bid)
			if len(errores_sheet_format) > 0:
				for level in levels:
					for zone in zones:
						output_rows.append(
							{
							"bid_name":bid_name,
							"sheet_type": "bid_attribute",
							"sheet_name": sheet_name,
							"zone": zone,
							"level_or_model": level,
							"alternative": None,
							"attribute": "PRECIO",
							"value": None,
							"status": "; ".join(errores_sheet_format)
							})
				continue

			# Check que los valores ingresados cumplan las restricciones
			## -> Celdas grises no han sido modificadas
			n_price_column = 2
			price_column = list(sheet_bid.columns)[n_price_column]
			for idx, row in sheet_bid.iterrows():
				zone = row["ZONA"]
				level = row["NIVEL"]
				attribute_data = data_bidattributes[bidattribute]["values"][level][zone]
				minprice = attribute_data["minprice"]
				maxprice = attribute_data["maxprice"]
				value = row[price_column]

				# Check que sea entero 
				if not is_integer(value):
					msg = "ERROR El precio no es entero: ({},{})".format(idx+2, price_column )
				# Check que esté dentro del rango
				elif not (value>=minprice and value<=maxprice):
					msg = "ERROR: No cumple con el rango de valores: ({},{})".format(idx+2, price_column )
				else:
					msg = "OK"

				output_rows.append(
					{
					"bid_name":bid_name,
					"sheet_type": "bid_attribute",
					"sheet_name": sheet_name,
					"zone": zone,
					"level_or_model": level,
					"alternative": None,
					"attribute": "PRECIO",
					"value": value,
					"status": msg
					})

		# TPs
		for n_tp, tp in enumerate(tps):
			n_tp = n_tp + 1 
			models = list(data_tps[tp].keys())
			zones = list(data_tps[tp][models[0]].keys())
			sheet_name = "TP{} - {}".format(n_tp, tp)

			# Check que exista la hoja
			if not sheet_name in excel_bid.sheet_names:
				for model in models:
					for zone in zones:
						for attribute in data_tps[tp][model][zone]["attributes_asked"]:
							for alternative in range(1, data_tps["condiciones_comerciales"]["max_products_alternatives"]+1):
								output_rows.append(
									{
									"bid_name":bid_name,
									"sheet_type": "tp",
									"sheet_name": sheet_name,
									"zone": zone,
									"level_or_model": model,
									"alternative": alternative,
									"attribute": attribute,
									"value": None,
									"status": "ERROR: No existe hoja"
									})
				continue

			# Load bid (comprobamos que existía)
			sheet_bid = pd.read_excel(excel_bid, sheet_name)
			# TEMPLATE: borrar ultima fila y ultima columna, estan full NAs.
			# quedan así al darles formato (borde superior y borde izquierdo)
			sheet_template = pd.read_excel(excel_template, sheet_name)
			sheet_template = sheet_template.iloc[:-1, :-1].copy()

			# Check que las celdas grises de la hoja no hayan sido modificadas
			errores_sheet_format = check_sheet_format(
				sheet_name = sheet_name,
				df_original = sheet_template,
				df_uploaded = sheet_bid)
			if len(errores_sheet_format) > 0:
				for model in models:
					for zone in zones:
						for attribute in data_tps[tp][model][zone]["attributes_asked"]:
							output_rows.append(
								{
								"bid_name":bid_name,
								"sheet_type": "tp",
								"sheet_name": sheet_name,
								"zone": zone,
								"level_or_model": model,
								"attribute": "attribute",
								"value": None,
								"status": "; ".join(errores_sheet_format)
								})
				continue

			# Check que los valores ingresados cumplan las restricciones
			## -> Celdas grises no han sido modificadas
			for idx, row in sheet_bid.iterrows():
				zone = row["ZONA"]
				model = row["MODELO"]
				alternative = row["ALTERNATIVA"] 
				for attribute, data_attribute in data_tps[tp][model][zone]["attributes_asked"].items():
					value = row[attribute]
					attribute_type = data_attribute["type"]

					# Enteros y floats
					if attribute_type in ["integer", "float"]:
						the_range = data_attribute["range"]
						if pd.isna(value):
							msg = "ERROR: Valor no cumple restricciones: ({},{})".format(idx+2, attribute)
						elif attribute_type == "integer" and not is_integer(value):
							msg = "ERROR: Valor no cumple restricciones: ({},{})".format(idx+2, attribute)
						elif not (value>=the_range[0] and value<=the_range[1]):
							msg = "ERROR: Valor no cumple restricciones: ({},{})".format(idx+2, attribute)
						else: 
							msg = "OK"
						output_rows.append(
							{
							"bid_name":bid_name,
							"sheet_type": "tp",
							"sheet_name": sheet_name,
							"zone": zone,
							"level_or_model": model,
							"alternative": alternative,
							"attribute": attribute,
							"value": value,
							"status": msg
							})

					elif attribute_type in ["list", "list_others"]:
						the_list = data_attribute["list"]
						if pd.isna(value):
							msg = "ERROR: Valor no cumple restricciones: ({},{})".format(idx+2, attribute)
						elif (attribute_type == "list") and (value not in the_list):
							msg = "ERROR: Valor no cumple restricciones: ({},{})".format(idx+2, attribute)
						else:
							msg = "OK"
						output_rows.append(
							{
							"bid_name":bid_name,
							"sheet_type": "tp",
							"sheet_name": sheet_name,
							"zone": zone,
							"level_or_model": model,
							"alternative": alternative,
							"attribute": attribute,
							"value": value,
							"status": msg
							})

					else:
						raise ValueError("Tipo de atributo desconocido: {}".format(attribute_type))


	# Planilla output_df
	output_excel = io.BytesIO()
	excel_output = pd.ExcelWriter(output_excel)
	df_output = pd.DataFrame(output_rows)
	df_output.to_excel(excel_output, "DETALLE ATRIBUTOS", index = False)
	excel_output.save()
	output_excel.seek(0)
	return output_excel