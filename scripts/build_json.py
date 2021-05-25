from catalog.models import *
def build_json(bid):

	# Categories
	max_level = bid.max_category_level
	lvl1_categories = Category.objects.filter(bid = bid, level = 1)
	if max_level == 1:
		json_categories = [x for x in lvl1_categories]
	elif max_level == 2:
		json_categories = {}
		for c1 in lvl1_categories:
			lvl2_categories = c1.children.all()
			for c2 in lvl2_categories:
				json_categories.setdefault(str(c1), []).append(str(c2))
	elif max_level == 3:
		json_categories = {}
		for c1 in lvl1_categories:
			lvl2_categories = c1.children.all()
			for c2 in lvl2_categories:
				lvl3_categories = c2.children.all()
				for c3 in lvl3_categories:
					json_categories.setdefault(str(c1), {}).setdefault(str(c2), []).append(str(c3))
	elif max_level == 4:
		json_categories = {}
		for c1 in lvl1_categories:
			lvl2_categories = c1.children.all()
			for c2 in lvl2_categories:
				lvl3_categories = c2.children.all()
				for c3 in lvl3_categories:
					lvl4_categories = c3.children.all()
					for c4 in lvl4_categories:
						json_categories.setdefault(str(c1), {}).setdefault(str(c2), {}).setdefault(str(c3), []).append(str(c4))
	else:
		raise ValueError("Error bid.max_category_level>4")

	# Products
	json_products = {}
	leaf_categories = Category.objects.filter(level = max_level)
	for category in leaf_categories:
		products = category.products.all()
		for product in products:
			product_dict = {}
			fixed_nominal_values = product.fixed_nominal_values.all()
			fixed_ratio_values = product.fixed_ratio_values.all()
			nominal_configs = product.nominal_configs.all()
			ratio_configs = product.ratio_configs.all()
			for fixed_value in list(fixed_nominal_values) + list(fixed_ratio_values):
				product_dict.setdefault("attributes_defined", {})[fixed_value.attribute.full_str()] = fixed_value.value
			for config in nominal_configs:
				aux = {}
				if config.accept_others:
					aux["type"] = "list_others"
				else:
					aux["type"]= "list"
				aux["list"] = [str(x) for x in config.nominal_values.all()]
				product_dict.setdefault("attributes_asked", {})[config.attribute.full_str()] = aux
			for config in ratio_configs:
				aux = {}
				if config.integer:
					aux["type"] = "integer"
				else:
					aux["type"] = "float"
				aux["range"] = [config.minval, config.maxval]
				product_dict.setdefault("attributes_asked", {})[config.attribute.full_str()] = aux
			json_products.setdefault(str(category),{})[product.name] = product_dict

	# Zones
	json_zones = [str(x) for x in bid.zones.all()]

	# Conditions
	json_conditions = {}
	json_conditions["max_products_alternatives"] = bid.max_products_alternatives
	json_conditions["min_products_category_level"] = bid.min_products_category_level
	json_conditions["min_products_n"] = bid.min_products_n

	full_json = {
		"zones" : json_zones,
		"conditions": json_conditions,
		"categories": json_categories,
		"products": json_products,
	}
	return full_json