from catalog.models import Dimension, Unit

def run():
	data = {
		"MONEDA":{
			"PESO CHILENO":{
				"abbreviation": "CLP",
				"is_base": True,
				"to_base": 1,
				"synonyms": []
			}
		},
		"TAMAÑO DATO":{
			"GIGABYTE":{
				"abbreviation": "GB",
				"is_base": True,
				"to_base": 1,
				"synoyms": []
			}
		},
		"LONGITUD":{
			"METRO":{
				"abbreviation": "M",
				"is_base": True,
				"to_base": 1,
				"synonyms": []
			},
			"CENTIMETRO":{
				"abbreviation": "CM",
				"is_base": False,
				"to_base": 0.01,
				"synonyms": []
			}
		},
		"MASA":{
			"GRAMO":{
				"abbreviation": "GR",
				"is_base": True,
				"to_base": 1,
				"synonyms": []
			},
			"KILOGRAMO":{
				"abbreviation": "KG",
				"is_base": False,
				"to_base": 1000,
				"synonyms": []
			}
		}
	}

	for dim_name, units_dict in data.items():
		dimension, created = Dimension.objects.get_or_create(
			name = dim_name.upper()
			)
		for unit_name, unit_dict in units_dict.items():
			unit, _ = Unit.objects.get_or_create(
				name = unit_name.upper(),
				abbreviation = unit_dict["abbreviation"],
				is_base = unit_dict["is_base"],
				to_base = unit_dict["to_base"],
				dimension = dimension
				)
