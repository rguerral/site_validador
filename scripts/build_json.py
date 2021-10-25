from catalog.models import *
def build_json(bid):
	# BidAttributes
	json_bidattributes = {}
	bidattributes = BidAttribute.objects.filter(bid = bid)
	for bidattribute in bidattributes:
		json_bidattributes.setdefault(bidattribute.name,{})["config"] = {
			"type": bidattribute.zone_or_global,
			"unit": {"full": bidattribute.unit.name, "abb": bidattribute.unit.abbreviation}}
		if bidattribute.zone_or_global == "NACIONAL":
			aux = {}
			bidattributelevels = BidAttributeLevel.objects.filter(
				bidattribute = bidattribute)
			for x in bidattributelevels:
				aux.setdefault(x.name, {})["NACIONAL"] = {"minprice": x.minprice, "maxprice": x.maxprice}
			json_bidattributes[bidattribute.name]["values"] = aux
		else:
			aux = {}
			for zone in bid.zones.all():
				bidattributelevels = BidAttributeLevel.objects.filter(
					bidattribute = bidattribute,
					zone = zone)
				for x in bidattributelevels:
					aux.setdefault(x.name, {})[zone.name] = {"minprice": x.minprice, "maxprice": x.maxprice}
			json_bidattributes[bidattribute.name]["values"] = aux

	# Categories
	max_level = bid.max_category_level
	lvl1_categories = Category.objects.filter(bid = bid, level = 1)
	if max_level == 1:
		json_categories = [str(x) for x in lvl1_categories]
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
	leaf_categories = Category.objects.filter(level = max_level, bid = bid)
	for category in leaf_categories:
		attributes = category.attributes.all()
		products = category.products.all()
		zones = bid.zones.all()
		product_dict = {}
		for product in products:
			zones_dict = {}
			for zone in zones:
				attributes_dict = {}
				for attribute in attributes:
					if attribute.zone_or_global == "NACIONAL":
						zone_query = None
					else:
						zone_query = zone
					# Fixed nominal
					if attribute.fixed == "SI" and attribute.attribute_type == "NOMINAL":
						fixed_nominal_value = FixedNominalValue.objects.get(
							attribute = attribute,
							product = product,
							zone = zone_query)
						attributes_dict.setdefault("attributes_defined", {})[fixed_nominal_value.attribute.full_str()] = fixed_nominal_value.value
					# Fixed ratio
					elif attribute.fixed=="SI" and attribute.attribute_type=="RATIO":
						fixed_ratio_value = FixedRatioValue.objects.get(
							attribute = attribute,
							product = product,
							zone = zone_query)
						attributes_dict.setdefault("attributes_defined", {})[fixed_ratio_value.attribute.full_str()] = fixed_ratio_value.value
					elif attribute.fixed =="NO" and attribute.attribute_type=="NOMINAL":
						nominal_config = NominalConfig.objects.get(
							attribute = attribute,
							product = product,
							zone = zone_query)
						aux = {}
						if attribute.accept_others==True:
							aux["type"] = "list_others"
						else:
							aux["type"]= "list"
						aux["list"] = [str(x) for x in nominal_config.nominal_values.all()]
						attributes_dict.setdefault("attributes_asked", {})[nominal_config.attribute.full_str()] = aux
					else:
						ratio_config = RatioConfig.objects.get(
							attribute = attribute,
							product = product,
							zone = zone_query)
						aux = {}
						if attribute.only_integers==True:
							aux["type"] = "integer"
						else:
							aux["type"] = "float"
						aux["range"] = [ratio_config.minval, ratio_config.maxval]
						attributes_dict.setdefault("attributes_asked", {})[ratio_config.attribute.full_str()] = aux
				zones_dict[str(zone)] = attributes_dict
			json_products.setdefault(str(category),{})[product.name] = zones_dict

	# Zones
	json_zones = [str(x) for x in bid.zones.all()]

	# Conditions
	json_conditions = {}
	json_conditions["max_products_alternatives"] = bid.max_products_alternatives

	full_json = {
		"zones" : json_zones,
		"conditions": json_conditions,
		"bidattributes": json_bidattributes,
		"categories": json_categories,
		"products": json_products,
	}
	return full_json