from catalog.models import Dimension, Unit

def run():
	data = {
		"MONEDA":{
			"PESO CHILENO":{
				"abbreviation": "CLP",
				"is_base": True,
				"to_base": 1,
				"synonyms": [],
				"currency": True
			},
			"DOLAR":{
				"abbreviation": "DOLAR",
				"is_base": True,
				"to_base": 1,
				"synonyms": [],
				"currency": True
			}
		},
		"TAMAÑO DATO":{
			"GIGABYTE":{
				"abbreviation": "GB",
				"is_base": True,
				"to_base": 1,
				"synoyms": [],
				"currency": False
			},
			"TERABYTE":{
				"abbreviation": "TB",
				"is_base": False,
				"to_base": 1000,
				"synoyms": [],
				"currency": False
			},
			"MEGABYTE":{
				"abbreviation": "MB",
				"is_base": False,
				"to_base": 0.001,
				"synoyms": [],
				"currency": False
			},
			"KILOBYTE":{
				"abbreviation": "KB",
				"is_base": False,
				"to_base": 1e-6,
				"synoyms": [],
				"currency": False
			}
		},
		"LONGITUD":{
			"METRO":{
				"abbreviation": "M",
				"is_base": True,
				"to_base": 1,
				"synonyms": [],
				"currency": False
			},
			"KILOMETRO":{
				"abbreviation": "KM",
				"is_base": False,
				"to_base": 1000,
				"synonyms": [],
				"currency": False

			},
			"CENTIMETRO":{
				"abbreviation": "CM",
				"is_base": False,
				"to_base": 0.01,
				"synonyms": [],
				"currency": False
			},
			"MILIMETRO":{
				"abbreviation": "MM",
				"is_base": False,
				"to_base": 0.001,
				"synonyms": [],
				"currency": False
			},
			"PULGADA":{
				"abbreviation": '"',
				"is_base": False,
				"to_base": 0.0254,
				"synonyms": [],
				"currency": False
			}				
		},
		"MASA":{
			"GRAMO":{
				"abbreviation": "GR",
				"is_base": True,
				"to_base": 1,
				"synonyms": [],
				"currency": False
			},
			"KILOGRAMO":{
				"abbreviation": "KG",
				"is_base": False,
				"to_base": 1000,
				"synonyms": [],
				"currency": False
			},
			"MILIGRAMO":{
				"abbreviation": "MG",
				"is_base": False,
				"to_base": 0.001,
				"synonyms": [],
				"currency": False
			}
		},
		"VOLUMEN":{
			"LITRO":{
				"abbreviation": "L",
				"is_base": True,
				"to_base": 1,
				"synonyms": [],
				"currency": False
			},
			"MILILITRO":{
				"abbreviation": "ML",
				"is_base": False,
				"to_base": 0.001,
				"synonyms": [],
				"currency": False
			},
			"METRO CÚBICO":{
				"abbreviation": "M3",
				"is_base": False,
				"to_base": 1000,
				"synonyms": [],
				"currency": False
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
				dimension = dimension,
				currency = unit_dict["currency"]
				)
