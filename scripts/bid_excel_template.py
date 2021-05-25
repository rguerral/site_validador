import xlsxwriter
import io

def bid_excel_template(data):
	output = io.BytesIO()

	# Crear planilla output
	workbook  = xlsxwriter.Workbook(output)

	# Formatos excel
	## celdas restringidas
	locked = workbook.add_format()
	locked.set_locked(True)
	locked.set_bg_color('#999999')
	## celdas a llenar
	unlocked = workbook.add_format()
	unlocked.set_locked(False)
	def set_format(security, border):
		# security
		if security == "locked":
			## celdas restringidas
			the_format = workbook.add_format()
			the_format.set_locked(True)
			the_format.set_bg_color('#999999')   
		elif security == "locked_white":
			the_format = workbook.add_format()
			the_format.set_locked(True)
		elif security == "unlocked":
			## celdas a llenar
			the_format = workbook.add_format()
			the_format.set_locked(False)
		# border 
		if border == None:
			pass
		elif border == "thick_left":
			the_format.set_left(5)
		elif border == "thick_right":
			the_format.set_right(5)
		elif border == "thick_bottom":
			the_format.set_bottom(5)
		elif border == "thick_left_bottom":
			the_format.set_left(5)
			the_format.set_bottom(5)
		elif border == "thick_right_bottom":
			the_format.set_right(5)
			the_format.set_bottom(5)
		elif border == "thick_left_top":
			the_format.set_left(5)
			the_format.set_bottom(5)
		elif border == "thick_right_top":
			the_format.set_right(5)
			the_format.set_top(5)
		elif border == "thick_top":
			the_format.set_top(5)
		elif border == "top":
			the_format.set_top(1)
		return the_format

	# Variables
	zones = data["zones"]
	n_alternatives = data["conditions"]["max_products_alternatives"]
	data_tps = data["products"]

	# Crear sheets de la planilla output
	for tp, data_tp in data_tps.items():

		ws = workbook.add_worksheet(tp)
		ws.protect()
		
		for model, data_model in data_tp.items():
			attributes = []
			try:
				attributes += list(data_model["attributes_defined"].keys())
			except:
				pass
			try:
				attributes += list(data_model["attributes_asked"].keys())
			except:
				pass
				
		# Cambiar width columnas
		ws.set_column(0, len(attributes) +2 , 18)

		# Columnas Zona y Modelo
		## heads
		ws.write(0,0, "Zona", set_format("locked", "thick_left_top"))
		ws.write(0,1, "Modelo", set_format("locked", "thick_top"))
		ws.write(0,2, "Alternativa", set_format("locked", "thick_top"))
		## rows
		row = 1
		for zone in zones:
			first_row_zone = True
			for model, data_model in data_tp.items():
				first_row_model = True
				for alternative in range(n_alternatives):
					if first_row_zone:
						border = "thick_top"
					elif first_row_model:
						border = "top"
					else:
						border = None
					ws.write(row, 0, zone, set_format("locked", border))
					ws.write(row, 1, model, set_format("locked", border))
					ws.write(row, 2, alternative + 1, set_format("locked", border))
					row += 1
					first_row_zone = False
					first_row_model = False

		# Columnas atributos
		j = 0
		base_column = 3
		for attribute in attributes:
			if j == len(attributes)-1:
				ws.write(0, base_column + j, attribute, set_format("locked", "thick_right_top"))
			else:
				ws.write(0, base_column + j, attribute, set_format("locked", "thick_top"))
			j += 1
			 
		# rows atributos fixed
		base_column = 3
		row = 1
		for zone in zones:
			first_row_zone = True
			for model, data_model in data_tp.items():
				first_row_model = True
				for alternative in range(n_alternatives):
					for attribute, value in data_model["attributes_defined"].items():
						if first_row_zone:
							border = "thick_top"
						elif first_row_model:
							border = "top"
						else:
							border = None
						column = base_column + attributes.index(attribute)
						ws.write(row, column, value, set_format("locked", border))
					row += 1
					first_row_zone = False
					first_row_model = False
						
		# Validaciones atributos asked
		base_column = column + 1
		row = 1
		## rows
		for zone in zones:
			first_row_zone = True
			for model, data_model in data_tp.items():
				first_row_model = True
				for alternative in range(n_alternatives):
					## border format
					if first_row_zone:
						border = "thick_top"
					elif first_row_model:
						border = "top"
					else:
						border = None
					# loop through attributes
					column = base_column
					for attribute, data_val in data_model["attributes_asked"].items():
						ws.write(row,column,None, set_format("unlocked", border))
						if data_val["type"] == "integer":
							range_min = data_val["range"][0]
							range_max = data_val["range"][1]
							ws.data_validation(row, column, row, column,
								{'validate': 'integer',
								'criteria': 'between',
								'minimum': range_min,
								'maximum': range_max,
								'input_title': 'Ingrese un valor sin decimales',
								'input_message': 'entre {} y {}'.format(range_min, range_max),
								'error_title': 'Error',
								'error_message': 'Ingrese un valor de acuerdo a las restricciones'
								})
						elif data_val["type"] == "list_others":
							values = data_val["list"] 
							ws.data_validation(row, column, row, column,
									{'validate': 'list',
									 'source': values,
									 'error_type': 'warning',
									 'input_title': 'Seleccione un valor de la lista',
									 'input_message': 'Puede agregar valores nuevos',
									 'error_title': 'Confirmar nuevo valor',
									 'error_message': 'Confirme que su valor no aparece en la lista'
									 })
						elif data_val["type"] == "list":
							values = data_val["list"] 
							ws.data_validation(row, column, row, column,
									{'validate': 'list',
									 'source': values,
									 'input_title': 'Seleccione un valor de la lista',
									 'input_message': 'No puedo agregar valores nuevo',
									 'error_title': 'Error',
									 'error_message': 'Ingrese un valor de acuerdo a las restricciones'
									 })
						column += 1
					row += 1
					first_row_zone = False
					first_row_model = False

		# Cerrar bordes tabla
		last_column = 3 + len(attributes)
		last_row = 1 + len(zones) * n_alternatives * len(data_tp)
		for i in range(last_row):
			ws.write(i, last_column, None, set_format("locked_white", "thick_left"))
		for j in range(last_column):
			ws.write(last_row, j, None, set_format("locked_white", "thick_top"))
		del attributes

	workbook.close()
	output.seek(0)

	return output
