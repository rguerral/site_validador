from django.shortcuts import render
from catalog.models import Bid, Zone, Category, Attribute, Product, NominalConfig, RatioConfig, NominalValue, FixedNominalValue, FixedRatioValue, BidAttribute, BidAttributeLevel
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, FormView,TemplateView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from catalog.forms import AttributeForm, ProductForm, SimulateForm, BidForm, CategoryForm, BidAttributeForm, BidAttributeLevelForm, ValidateForm
from scripts.build_json import build_json
from scripts.bid_excel_template import bid_excel_template
from scripts.simulate_bids import simulate_bids
from scripts.validate_bids import validate_bids
from django.http import HttpResponseRedirect, Http404
import django_tables2 as tables
from django.http import JsonResponse, HttpResponse


class BidList(ListView):
	model = Bid
	template_name = "catalog/bid_list.html"

class BidCreate(FormView):
	form_class = BidForm
	template_name = "catalog/bid_form.html"
	success_url=reverse_lazy('catalog:bids')

	def form_valid(self, form):
		name = form.cleaned_data.get('name')
		zones = form.cleaned_data.get('zones')
		max_category_level = form.cleaned_data.get('max_category_level')
		max_products_alternatives = form.cleaned_data.get('max_products_alternatives')
		bid = Bid(
			name = name,
			max_category_level = max_category_level,
			max_products_alternatives = max_products_alternatives)
		bid.save()
		category = Category(name = "ROOT", parent = None, bid = bid, level = 0)
		category.save()
		for zone in zones:
			Zone(name = zone, bid = bid).save()
		return super(BidCreate, self).form_valid(form)

class BidUpdate(UpdateView):
	model = Bid
	template_name = "catalog/bid_form.html"
	fields = ['name']
	success_url=reverse_lazy('catalog:bids')

class BidDelete(DeleteView):
	model = Bid
	template_name = "catalog/bid_confirm_delete.html"
	success_url=reverse_lazy('catalog:bids')

class BidDetail(DetailView):
	model = Bid
	template_name = "catalog/bid_detail.html"

class BidAttributeList(ListView):
	model = BidAttribute
	template_name = "catalog/bidattribute_list.html"

	def get(self, request, pk):
		bid = get_object_or_404(Bid, pk=pk)
		bidattribute_list = BidAttribute.objects.filter(bid = bid)
		bidattribute_list2 = []
		for x in bidattribute_list:
			levels = list(set([y.name for y in x.levels.all()]))
			bidattribute_list2.append({"bidattribute": x, "bidattributelevels": levels})
		context = {	
					"bidattribute_list": bidattribute_list2,
					"bid" : bid
					}
		return render(request, self.template_name, context)

class BidAttributeCreate(FormView):
	form_class = BidAttributeForm
	template_name = "catalog/bidattribute_form.html"

	def get_form_kwargs(self):
		kwargs = super(BidAttributeCreate, self).get_form_kwargs()
		bid = get_object_or_404(Bid, pk=self.kwargs['pk'])
		zones = bid.zones.all()
		kwargs["bid"] = bid
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(BidAttributeCreate, self).get_context_data()
		kwargs = self.get_form_kwargs()
		context['bid'] = kwargs['bid']
		return context

	def get_success_url(self, **kwargs):
		bid = self.get_form_kwargs()["bid"]
		return reverse('catalog:bidattribute_list', kwargs={'pk':bid.id})

	def form_valid(self, form):
		kwargs = self.get_form_kwargs()
		bid = kwargs["bid"]
		name = form.cleaned_data.get('name')
		zone_or_global = form.cleaned_data.get('zone_or_global')
		unit = form.cleaned_data.get('unit')
		BidAttribute(
			bid = bid,
			name = name,
			zone_or_global = zone_or_global,
			unit = unit
			).save()
		return super(BidAttributeCreate, self).form_valid(form)

# No updatea si se cambia zona/nacional
class BidAttributeUpdate(FormView):
	form_class = BidAttributeForm
	template_name = "catalog/bidattribute_form.html"

	def get_form_kwargs(self):
		kwargs = super(BidAttributeUpdate, self).get_form_kwargs()
		bidattribute = get_object_or_404(BidAttribute, pk=self.kwargs['pk'])
		bid = bidattribute.bid
		kwargs["bid"] = bid
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(BidAttributeUpdate, self).get_context_data()
		kwargs = self.get_form_kwargs()
		bidattribute = get_object_or_404(BidAttribute, pk=self.kwargs['pk'])
		context['bidattribute'] = bidattribute
		context['bid'] = kwargs['bid']

		prefilled_form = BidAttributeForm(
			initial = {
				'name': bidattribute.name,
				'zone_or_global': bidattribute.zone_or_global,
				'unit': bidattribute.unit,
			},
			bid = kwargs['bid'],
		)
		context["form"] = prefilled_form
		return context

	def get_success_url(self, **kwargs):
		bidattribute = get_object_or_404(BidAttribute, pk=self.kwargs['pk'])
		return reverse('catalog:bidattribute_list', kwargs={'pk':bidattribute.bid.id})

	def form_valid(self, form):
		bidattribute = get_object_or_404(BidAttribute, pk=self.kwargs['pk'])
		name = form.cleaned_data.get('name')
		zone_or_global = form.cleaned_data.get('zone_or_global')
		unit = form.cleaned_data.get('unit')
		bidattribute.name = name
		bidattribute.zone_or_global = zone_or_global
		bidattribute.unit = unit
		bidattribute.save()
		return super(BidAttributeUpdate, self).form_valid(form)

class BidAttributeDelete(DeleteView):
	model = BidAttribute
	template_name = "catalog/bidattribute_confirm_delete.html"

	def get_success_url(self, **kwargs):
		bidattribute = get_object_or_404(BidAttribute, pk=self.kwargs['pk'])
		return reverse('catalog:bidattribute_list', kwargs={'pk':bidattribute.bid.id})

class BidAttributeDetail(DetailView):
	model = BidAttribute
	template_name = "catalog/bidattribute_detail.html"

	def get(self, request, pk):
		bidattribute = BidAttribute.objects.get(id = pk)
		bid = bidattribute.bid
		bidattributelevels = bidattribute.levels.all()
		table_content = {}
		if bidattribute.zone_or_global == "NACIONAL":
			unique_levels = list(set([x.name for x in bidattributelevels]))
			for x in unique_levels:
				prev_list = []
				obj = BidAttributeLevel.objects.get(
						bidattribute = bidattribute,
						name = x,
						zone = None)
				aux = {
					"bidattributelevel": obj, 
					"zone":"NACIONAL",
					"minprice": obj.minprice,
					"maxprice": obj.maxprice
					}
				prev_list.append(aux)
				table_content[x] = prev_list
		else:
			unique_levels = list(set([x.name for x in bidattributelevels]))
			zones = bid.zones.all()
			for x in unique_levels:
				prev_list = []
				for y in zones:
					obj = BidAttributeLevel.objects.get(
						bidattribute = bidattribute,
						name = x,
						zone = y)
					aux = {
						"bidattributelevel": obj, 						
						"zone": y,
						"minprice": obj.minprice,
						"maxprice": obj.maxprice
						}
					prev_list.append(aux)
				table_content[x] = prev_list
		
		context = {'bidattribute': bidattribute,
					'table_content': table_content,
					}
		return render(request, self.template_name, context)

class BidAttributeLevelCreate(FormView):
	form_class = BidAttributeLevelForm
	template_name = "catalog/bidattributelevel_form.html"

	def get_form_kwargs(self):
		kwargs = super(BidAttributeLevelCreate, self).get_form_kwargs()
		bidattribute = get_object_or_404(BidAttribute, pk=self.kwargs['pk'])
		bid = bidattribute.bid
		zones = bid.zones.all()
		kwargs["bidattribute"] = bidattribute
		kwargs["zones"] = zones
		form_auxdata = [{"name": x,
						"min_price_field": '{}_minprice'.format(str(x)),
						"max_price_field": '{}_maxprice'.format(str(x)) } for x in zones]
		kwargs["form_auxdata"] = form_auxdata
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(BidAttributeLevelCreate, self).get_context_data()
		kwargs = self.get_form_kwargs()
		context['bidattribute'] = kwargs['bidattribute']
		context['bid'] = kwargs['bidattribute'].bid
		context['zones'] = kwargs['zones']
		context["form_auxdata"] = kwargs["form_auxdata"]
		return context

	def get_success_url(self, **kwargs):
		bidattribute = self.get_form_kwargs()["bidattribute"]
		return reverse('catalog:bidattribute_detail', kwargs={'pk':bidattribute.id})

	def form_valid(self, form):
		kwargs = self.get_form_kwargs()
		bidattribute = kwargs["bidattribute"]
		zones = kwargs["zones"]
		zone_or_global = bidattribute.zone_or_global
		name = form.cleaned_data.get('name')
		if zone_or_global == "NACIONAL":
			global_minprice = form.cleaned_data.get('global_minprice')
			global_maxprice = form.cleaned_data.get('global_maxprice')
			BidAttributeLevel(
				bidattribute = bidattribute,
				name = name,
				minprice = global_minprice,
				maxprice = global_maxprice
				).save()
		else:
			for zone in zones:
				minprice = form.cleaned_data.get('{}_minprice'.format(zone))
				maxprice = form.cleaned_data.get('{}_maxprice'.format(zone))
				BidAttributeLevel(
					bidattribute = bidattribute,
					name = name,
					zone = zone,
					minprice = minprice,
					maxprice = maxprice
				).save()
		return super(BidAttributeLevelCreate, self).form_valid(form)

class BidAttributeLevelDelete(DeleteView):
	model = BidAttributeLevel
	template_name = "catalog/bidattributelevel_confirm_delete.html"

	def delete(self, request, *args, **kwargs):
		bidattributelevel = get_object_or_404(BidAttributeLevel, pk=self.kwargs['pk'])
		bidattributelevel_todelete = BidAttributeLevel.objects.filter(
			bidattribute = bidattributelevel.bidattribute,
			name = bidattributelevel.name)
		bidattributelevel_todelete.delete()
		response = super(BidAttributeLevelDelete, self).delete(request)
		return response

	def get_success_url(self, **kwargs):
		bidattributelevel = get_object_or_404(BidAttributeLevel, pk=self.kwargs['pk'])
		return reverse('catalog:bidattribute_list', kwargs={'pk':bidattribute.bid.id})

class CategoryList(ListView):
	model = Category
	template_name = "catalog/category_list.html"

	def get(self, request, pk):
		bid = get_object_or_404(Bid, pk=pk)
		category_list = Category.objects.filter(bid = bid, level__gt = 0)
		root_category = Category.objects.get(bid = bid, level = 0)
		for category in category_list:
			category.update_tree_name()
			category.save()
		category_list = category_list.order_by('position')
		context = {"category_list": category_list,
					"root_category": root_category,
					"bid" : bid}
		return render(request, self.template_name, context)

class CategoryDetail(DetailView):
	model = Category
	template_name = "catalog/category_detail.html"

	def get(self, request, pk):
		category = Category.objects.get(id = pk)
		bid = category.bid
		zones = bid.zones.all()
		branch = category.get_branch()[1:-1]
		
		# Atributos ordenados
		nom_fix = category.attributes.filter(
			attribute_type = "NOMINAL",
			fixed = "SI")
		rat_fix = category.attributes.filter(
			attribute_type = "RATIO",
			fixed = "SI")
		nom_unfix = category.attributes.filter(
			attribute_type = "NOMINAL",
			fixed = "NO")
		rat_unfix = category.attributes.filter(
			attribute_type = "RATIO",
			fixed = "NO")
		attributes = list(nom_fix) + list(rat_fix) + list(nom_unfix) + list(rat_unfix)

		# Datos de la tabla
		products = category.products.all()
		table_data = []
		for product in products:
			attributes_data = []
			# Nom fix
			for attribute in nom_fix:
				zone_data = []
				if attribute.zone_or_global == "NACIONAL":
					obj = FixedNominalValue.objects.get(
						product = product,
						attribute = attribute)
					zone_data.append(
						{"value":obj}
					)
				else:
					for zone in zones:
						obj = FixedNominalValue.objects.get(
							product = product,
							attribute = attribute,
							zone = zone)
						zone_data.append(
							{"value":obj}
						)
				attributes_data.append(zone_data)
			# Rat fix
			for attribute in rat_fix:
				zone_data = []
				if attribute.zone_or_global == "NACIONAL":
					obj = FixedRatioValue.objects.get(
						product = product,
						attribute = attribute)
					zone_data.append(
						{"value":obj}
					)
				else:
					for zone in zones:
						obj = FixedRatioValue.objects.get(
							product = product,
							attribute = attribute,
							zone = zone)
						zone_data.append(
							{"value":obj}
						)
				attributes_data.append(zone_data)
			# Nom unfix
			for attribute in nom_unfix:
				zone_data = []
				if attribute.zone_or_global == "NACIONAL":
					obj = NominalConfig.objects.get(
						product = product,
						attribute = attribute)
					zone_data.append(
						{"value": obj.get_values_str()}
					)
				else:
					for zone in zones:
						obj = NominalConfig.objects.get(
							product = product,
							attribute = attribute,
							zone = zone)
						zone_data.append(
							{"value": obj.get_values_str()}
						)
				attributes_data.append(zone_data)
			# Ratio unfix
			for attribute in rat_unfix:
				zone_data = []
				if attribute.zone_or_global == "NACIONAL":
					obj = RatioConfig.objects.get(
						product = product,
						attribute = attribute)
					zone_data.append(
						{"value": str(obj.minval) + " - " + str(obj.maxval)}
					)
				else:
					for zone in zones:
						obj = RatioConfig.objects.get(
							product = product,
							attribute = attribute,
							zone = zone)
						zone_data.append(
							{"value": str(obj.minval) + " - " + str(obj.maxval)}
						)
				attributes_data.append(zone_data)
			table_data.append({"product": product, "attributes_data": attributes_data})

		context = {'category': category,
					'bid': bid,
					'zones': zones,
					'branch': branch,
					'attributes': attributes,
					'table_data': table_data}
		return render(request, self.template_name, context)

class CategoryCreate(FormView):
	form_class = CategoryForm
	template_name = "catalog/category_form.html"

	def get_context_data(self, **kwargs):
		context = super(CategoryCreate, self).get_context_data()
		kwargs = self.get_form_kwargs()
		context['parent'] = kwargs["parent"]
		context['bid'] = kwargs["bid"]
		return context

	def get_form_kwargs(self):
		kwargs = super(CategoryCreate, self).get_form_kwargs()
		parent = get_object_or_404(Category, pk=self.kwargs['pk'])
		kwargs["parent"] = parent
		kwargs["bid"] = parent.bid
		return kwargs

	def form_valid(self, form):
		parent = get_object_or_404(Category, pk=self.kwargs['pk'])
		print(parent)
		bid = parent.bid
		name = form.cleaned_data.get('name')
		level = parent.level +1
		obj = Category(
				name = name,
				parent = parent,
				level = level,
				bid = bid)
		obj.save()
		return super(CategoryCreate, self).form_valid(form)

	def get_success_url(self, **kwargs):
		bid = self.get_form_kwargs()["bid"]
		return reverse('catalog:category_list', kwargs={'pk':bid.id})

class CategoryUpdate(UpdateView):
	model = Category
	fields = ['name', 'parent']

class CategoryDelete(DeleteView):
	model = Category

	def delete(self, request, *args, **kwargs):
		category = get_object_or_404(Category, pk=self.kwargs['pk'])
		bid = category.bid
		response = super(CategoryDelete, self).delete(request)
		# Update position on tree
		level = 1
		while True:
			categories = Category.objects.filter(level = level, bid = bid)
			if len(categories) == 0:
				break
			for category in categories:
				category.update_position()
			level += 1
		return response

	def get_success_url(self, **kwargs):
		category = get_object_or_404(Category, pk=self.kwargs['pk'])
		bid = category.bid
		return reverse('catalog:category_list', kwargs={'pk':bid.id})

class AttributeCreate(CreateView):
	template_name = "catalog/attribute_form.html"
	form_class = AttributeForm

	def get_context_data(self, **kwargs):
		context = super(AttributeCreate, self).get_context_data()
		category = get_object_or_404(Category, pk=self.kwargs['pk'])
		context['category'] = category
		context['bid'] = category.bid
		context['branch'] = category.get_branch()[1:]
		return context

	def get_form_kwargs(self):
		kwargs = super(AttributeCreate, self).get_form_kwargs()
		category = get_object_or_404(Category, pk=self.kwargs['pk'])
		kwargs["category"] = category
		return kwargs

	def form_valid(self, form):
		category = get_object_or_404(Category, pk=self.kwargs['pk'])
		category.products.all().delete()
		form.instance.category = category
		return super(AttributeCreate, self).form_valid(form)

	def get_success_url(self, **kwargs):
		return reverse('catalog:category_detail', kwargs={'pk':self.kwargs['pk']})

class AttributeUpdate(UpdateView):
	template_name = "catalog/attribute_form.html"
	model = Attribute
	form_class = AttributeForm

	def get_context_data(self, **kwargs):
		context = super(AttributeUpdate, self).get_context_data(**kwargs)
		attribute = get_object_or_404(Attribute, pk=self.kwargs['pk'])
		context['category'] = attribute.category
		context['attribute'] = attribute
		return context

	def get_success_url(self, **kwargs):
		attribute = get_object_or_404(Attribute, pk=self.kwargs['pk'])
		return reverse('catalog:category_detail', kwargs={'pk':attribute.category.id})

class AttributeDelete(DeleteView):
	model = Attribute

	def get_success_url(self, **kwargs):
		attribute = get_object_or_404(Attribute, pk=self.kwargs['pk'])
		category = attribute.category
		return reverse('catalog:category_detail', kwargs={'pk':category.id})

class ProductCreate(FormView):
	form_class = ProductForm
	template_name = "catalog/product_form.html"

	def get_form_kwargs(self):
		kwargs = super(ProductCreate, self).get_form_kwargs()
		category = get_object_or_404(Category, pk=self.kwargs['pk'])
		nom_fix = category.attributes.filter(
			attribute_type = "NOMINAL",
			fixed = "SI")
		rat_fix = category.attributes.filter(
			attribute_type = "RATIO",
			fixed = "SI")
		nom_unfix = category.attributes.filter(
			attribute_type = "NOMINAL",
			fixed = "NO")
		rat_unfix = category.attributes.filter(
			attribute_type = "RATIO",
			fixed = "NO")
		kwargs["category"] = category
		kwargs["bid"] = category.bid
		kwargs["zones"] = category.bid.zones.all()
		kwargs["attributes"] = {
			"nom_fix" : nom_fix,
			"rat_fix" : rat_fix,
			"nom_unfix" : nom_unfix ,
			"rat_unfix" : rat_unfix ,
		}
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(ProductCreate, self).get_context_data()
		kwargs = self.get_form_kwargs()
		context['category'] = kwargs['category']
		context['branch'] = kwargs['category'].get_branch()
		context['attributes'] = kwargs["attributes"]
		context['bid'] = kwargs["bid"]
		context['zones'] = kwargs["zones"]
		return context

	def get_success_url(self, **kwargs):
		category = self.get_form_kwargs()["category"]
		return reverse('catalog:category_detail', kwargs={'pk':category.id})

	def form_valid(self, form):
		kwargs = self.get_form_kwargs()
		attributes = kwargs["attributes"]
		category = kwargs["category"]
		to_save = []
		name = form.cleaned_data.get('name')
		product = Product(name = name, category = category)
		#nomfix
		for att in attributes["nom_fix"]:
			if att.zone_or_global == "NACIONAL":
				value = form.cleaned_data.get('nf_{}_global_value'.format(att.name))
				nom_fix_value = FixedNominalValue(
					value = value,
					attribute = att,
					product = product,
					zone = None)
				to_save.append(nom_fix_value)
			else:
				for zone in kwargs["zones"]:
					value = form.cleaned_data.get('nf_{}_{}_value'.format(att.name, zone.name))
					nom_fix_value = FixedNominalValue(
						value = value,
						attribute = att,
						product = product,
						zone = zone)
					to_save.append(nom_fix_value)

		#ratfix
		for att in attributes["rat_fix"]:
			if att.zone_or_global == "NACIONAL":
				value = form.cleaned_data.get('rf_{}_global_value'.format(att.name))
				rat_fix_value = FixedRatioValue(
					value = value,
					attribute = att,
					product = product,
					zone = None)
				to_save.append(rat_fix_value)
			else:
				for zone in kwargs["zones"]:
					value = form.cleaned_data.get('rf_{}_{}_value'.format(att.name, zone.name))
					rat_fix_value = FixedRatioValue(
						value = value,
						attribute = att,
						product = product,
						zone = zone)
					to_save.append(rat_fix_value)
		#nom_unfix
		for att in attributes["nom_unfix"]:
			if att.zone_or_global == "NACIONAL":
				values = form.cleaned_data.get('nuf_{}_global_values'.format(att.name))
				values = [x.strip("\r") for x in values.split("\n")]
				nominal_config = NominalConfig(
					attribute = att,
					product = product,
					zone = None)
				to_save.append(nominal_config)
				for value in values:
					nom_value = NominalValue(
						value = value,
						nominal_config = nominal_config)
					to_save.append(nom_value)
			else:
				for zone in kwargs["zones"]:
					values = form.cleaned_data.get('nuf_{}_{}_values'.format(att.name, zone))
					values = [x.strip("\r") for x in values.split("\n")]
					nominal_config = NominalConfig(
						attribute = att,
						product = product,
						zone = zone)
					to_save.append(nominal_config)
					for value in values:
						nom_value = NominalValue(
							value = value,
							nominal_config = nominal_config)
						to_save.append(nom_value)

		#rat_unfix
		for att in attributes["rat_unfix"]:
			if att.zone_or_global == "NACIONAL":
				minval = form.cleaned_data.get('ruf_{}_global_min'.format(att.name))
				maxval = form.cleaned_data.get('ruf_{}_global_max'.format(att.name))
				ratio_config = RatioConfig(
					attribute = att,
					product = product,
					minval = minval,
					maxval = maxval,
					zone = None)
				to_save.append(ratio_config)
			else:
				for zone in kwargs["zones"]:
					minval = form.cleaned_data.get('ruf_{}_{}_min'.format(att.name, zone))
					maxval = form.cleaned_data.get('ruf_{}_{}_max'.format(att.name, zone))
					ratio_config = RatioConfig(
						attribute = att,
						product = product,
						minval = minval,
						maxval = maxval,
						zone = zone)
					to_save.append(ratio_config)
		# Guardar
		product.save()
		for obj in to_save:
			obj.save()
		return super(ProductCreate, self).form_valid(form)

class ProductDelete(DeleteView):
	model = Product
	template_name = "catalog/product_confirm_delete.html"
	def get_success_url(self, **kwargs):
		product = get_object_or_404(Product, pk=self.kwargs['pk'])
		category = product.category
		return reverse('catalog:category_detail', kwargs={'pk':category.id})

class Algorithms(TemplateView):
	template_name = "catalog/algorithms.html"
	def get_context_data(self, **kwargs):
		context = super(Algorithms, self).get_context_data()
		bid = get_object_or_404(Bid, pk=self.kwargs['pk'])
		context["bid"] = bid
		return context

class Simulate(FormView):
	form_class = SimulateForm
	template_name = "catalog/simulate_form.html"

	def get_context_data(self, **kwargs):
		context = super(Simulate, self).get_context_data()
		bid = get_object_or_404(Bid, pk=self.kwargs['pk'])
		context["bid"] = bid
		return context

	def form_valid(self, form):
		#kwargs
		bid = get_object_or_404(Bid, pk=self.kwargs['pk'])
		# json & excel
		json = build_json(bid)
		bid_template = bid_excel_template(data = json)
		# form
		seed = form.cleaned_data.get('nsims')
		nsims = form.cleaned_data.get('nsims')
		p_field_error = form.cleaned_data.get('p_field_error')
		p_empty = form.cleaned_data.get('p_empty')
		p_edit_field = form.cleaned_data.get('p_edit_field')
		# simulate
		zip_file = simulate_bids(
							data = json,
							bid_template = bid_template,
							SEED = seed,
							NSIMS = nsims,
							P_FIELD_ERROR = p_field_error,
							P_EMPTY = p_empty,
							P_EDIT_FIELD = p_edit_field)
		filename = 'simulacion_{}.zip'.format(str(bid))
		response = HttpResponse(
					zip_file,
					content_type='application/zip'
				)
		response['Content-Disposition'] = 'attachment; filename=%s' % filename
		return response

class Validate(FormView):
	form_class = ValidateForm
	template_name = "catalog/validate_form.html"
	success_url = "catalog/bids"

	def get_context_data(self, **kwargs):
		context = super(Validate, self).get_context_data()
		bid = get_object_or_404(Bid, pk=self.kwargs['pk'])
		context["bid"] = bid
		return context

	def form_valid(self, form):
		bid = get_object_or_404(Bid, pk=self.kwargs['pk'])
		json = build_json(bid)
		excel_template = bid_excel_template(json)
		files = form.cleaned_data.get('content')
		excel_output = validate_bids(
			files = files,
			data = json,
			excel_template = excel_template)
		filename = 'VALIDACION_{}.xlsx'.format(str(bid))
		response = HttpResponse(
					excel_output,
					content_type='application/vnd.ms-excel'
				)
		response['Content-Disposition'] = 'attachment; filename=%s' % filename
		return response

def BuildJson(request, *args, **kwargs):
	bid = get_object_or_404(Bid, pk=kwargs['pk'])
	json = build_json(bid)
	return JsonResponse(json)
	#return HttpResponseRedirect(reverse('catalog:algorithms', kwargs={'pk':bid.id}))

def BuildTemplate(request, *args, **kwargs):
	bid = get_object_or_404(Bid, pk=kwargs['pk'])
	json = build_json(bid)
	bid_template = bid_excel_template(data = json)
	# Set up the Http response.
	filename = 'PLANILLA_{}.xlsx'.format(str(bid))
	response = HttpResponse(
		bid_template,
		content_type='application/vnd.ms-excel'
	)
	response['Content-Disposition'] = 'attachment; filename=%s' % filename

	return response
	#return JsonResponse(json)


