from django.shortcuts import render
from catalog.models import Bid, Zone, Category, Attribute, Product, NominalConfig, RatioConfig, NominalValue, FixedNominalValue, FixedRatioValue, BidAttribute, PriceBidAttributeZone
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, FormView,TemplateView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from catalog.forms import AttributeForm, ProductForm, SimulateForm, BidForm, CategoryForm, BidAttributeForm
from scripts.build_json import build_json
from scripts.bid_excel_template import bid_excel_template
from scripts.simulate_bids import simulate_bids
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
		min_products_category_level = form.cleaned_data.get('min_products_category_level')
		min_products_n = form.cleaned_data.get('min_products_n')
		bid = Bid(
			name = name,
			max_category_level = max_category_level,
			max_products_alternatives = max_products_alternatives,
			min_products_category_level = min_products_category_level,
			min_products_n = min_products_n)
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

class BidDetail(ListView):
	model = Bid
	template_name = "catalog/bid_detail.html"

	def get(self, request, pk):
		bid = get_object_or_404(Bid, pk=pk)
		category_list = Category.objects.filter(bid=bid, level__gt = 0)
		root_category = Category.objects.get(bid=bid, level = 0)
		for category in category_list:
			category.update_tree_name()
			category.save()
		bidattribute_list = BidAttribute.objects.filter(bid = bid)
		context = {"category_list": category_list,
					"root_category": root_category,
					"bidattribute_list": bidattribute_list,
					"bid" : bid}
		return render(request, self.template_name, context)

class BidAttributeCreate(FormView):
	form_class = BidAttributeForm
	template_name = "catalog/bidattribute_form.html"

	def get_form_kwargs(self):
		kwargs = super(BidAttributeCreate, self).get_form_kwargs()
		bid = get_object_or_404(Bid, pk=self.kwargs['pk'])
		zones = bid.zones.all()
		kwargs["bid"] = bid
		kwargs["zones"] = zones
		form_auxdata = [{"name": x,
						"min_price_field": '{}_minprice'.format(str(x)),
						"max_price_field": '{}_maxprice'.format(str(x)) } for x in zones]
		kwargs["form_auxdata"] = form_auxdata
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(BidAttributeCreate, self).get_context_data()
		kwargs = self.get_form_kwargs()
		context['bid'] = kwargs['bid']
		context['zones'] = kwargs['zones']
		context['form_auxdata'] = kwargs['form_auxdata']
		return context

	def get_success_url(self, **kwargs):
		bid = self.get_form_kwargs()["bid"]
		return reverse('catalog:categories', kwargs={'pk':bid.id})

	def form_valid(self, form):
		kwargs = self.get_form_kwargs()
		bid = kwargs["bid"]
		zones = kwargs["zones"]
		name = form.cleaned_data.get('name')
		zone_or_global = form.cleaned_data.get('zone_or_global')
		unit = form.cleaned_data.get('unit')
		if zone_or_global == "NACIONAL":
			global_minprice = form.cleaned_data.get('global_minprice')
			global_maxprice = form.cleaned_data.get('global_maxprice')
			BidAttribute(
				bid = bid,
				name = name,
				zone_or_global = zone_or_global,
				unit = unit,
				global_minprice = global_minprice,
				global_maxprice = global_maxprice
				).save()

		else:
			bidattribute = BidAttribute(
				bid = bid,
				name = name,
				zone_or_global = zone_or_global,
				unit = unit)
			bidattribute.save()
			for zone in zones:
				minprice = form.cleaned_data.get('{}_minprice'.format(zone))
				maxprice = form.cleaned_data.get('{}_maxprice'.format(zone))
				PriceBidAttributeZone(
					bidattribute = bidattribute,
					zone = zone,
					minprice = minprice,
					maxprice = maxprice).save()
		return super(BidAttributeCreate, self).form_valid(form)

class BidAttributeUpdate(FormView):
	form_class = BidAttributeForm
	template_name = "catalog/bidattribute_form.html"

	def get_form_kwargs(self):
		kwargs = super(BidAttributeUpdate, self).get_form_kwargs()
		bidattribute = get_object_or_404(BidAttribute, pk=self.kwargs['pk'])
		bid = bidattribute.bid
		zones = bid.zones.all()
		kwargs["bid"] = bid
		kwargs["zones"] = zones
		form_auxdata = [{"name": x,
						"min_price_field": '{}_minprice'.format(str(x)),
						"max_price_field": '{}_maxprice'.format(str(x)) } for x in zones]
		kwargs["form_auxdata"] = form_auxdata
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(BidAttributeUpdate, self).get_context_data()
		kwargs = self.get_form_kwargs()
		bidattribute = get_object_or_404(BidAttribute, pk=self.kwargs['pk'])
		context['bidattribute'] = bidattribute
		context['bid'] = kwargs['bid']
		context['zones'] = kwargs['zones']
		context['form_auxdata'] = kwargs['form_auxdata']

		# Prefill form
		if bidattribute.zone_or_global == "NACIONAL":
			prefilled_form = BidAttributeForm(
				initial = {
					'name': bidattribute.name,
					'zone_or_global': bidattribute.zone_or_global,
					'unit': bidattribute.unit,
					'global_minprice': bidattribute.global_minprice,
					'global_maxprice': bidattribute.global_maxprice,
				},
				bid = kwargs['bid'],
				zones = kwargs["zones"],
				form_auxdata = kwargs["form_auxdata"]
			)
			context["form"] = prefilled_form

		else:
			price_zones = bidattribute.price_zones.all()
			initial_dict = {}
			for price_zone in price_zones:
				initial_dict["{}_minprice".format(price_zone.zone)] = price_zone.minprice
				initial_dict["{}_maxprice".format(price_zone.zone)] = price_zone.maxprice
			initial_dict['name'] = bidattribute.name
			initial_dict['zone_or_global'] = bidattribute.zone_or_global
			initial_dict['unit'] = bidattribute.unit

			prefilled_form = BidAttributeForm(
				initial = initial_dict,
				bid = kwargs['bid'],
				zones = kwargs["zones"],
				form_auxdata = kwargs["form_auxdata"]
			)
			context["form"] = prefilled_form
		return context

	def get_success_url(self, **kwargs):
		bidattribute = get_object_or_404(BidAttribute, pk=self.kwargs['pk'])
		return reverse('catalog:categories', kwargs={'pk':bidattribute.bid.id})

	def form_valid(self, form):
		print("aaaaaabbb")
		return super(BidAttributeUpdate, self).form_valid(form)

class BidAttributeDelete(DeleteView):
	model = BidAttribute
	template_name = "catalog/bidattribute_confirm_delete.html"

	def get_success_url(self, **kwargs):
		bidattribute = get_object_or_404(BidAttribute, pk=self.kwargs['pk'])
		return reverse('catalog:categories', kwargs={'pk':bidattribute.bid.id})

class CategoryDetail(DetailView):
	model = Category
	template_name = "catalog/category_detail.html"

	def get(self, request, pk):
		category = Category.objects.get(id = pk)
		bid = category.bid
		products = category.products.all()
		branch = category.get_branch()[1:-1]
		
		# product table data
		table_data = []
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
		for product in products:
			row_data = []
			for attribute in nom_fix:
				obj = FixedNominalValue.objects.get(
					product = product,
					attribute = attribute)
				row_data.append({"value":obj})
			for attribute in rat_fix:
				obj = FixedRatioValue.objects.get(
					product = product,
					attribute = attribute)
				row_data.append({"value":obj})
			for attribute in nom_unfix:
				obj = NominalConfig.objects.get(
					product = product,
					attribute = attribute)
				row_data.append({"value": obj.get_values_str(), "others": obj.accept_others})
			for attribute in rat_unfix:
				obj = RatioConfig.objects.get(
					product = product,
					attribute = attribute)
				row_data.append({"value": str(obj.minval) + " - " + str(obj.maxval), "integer":obj.integer})
			table_data.append({"product": product, "attributes": row_data})


		context = {'category': category,
					'bid': bid,
					#'products': products,
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
		return reverse('catalog:categories', kwargs={'pk':bid.id})

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
		return reverse('catalog:categories', kwargs={'pk':bid.id})

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
		form.instance.category = get_object_or_404(Category, pk=self.kwargs['pk'])
		return super(AttributeCreate, self).form_valid(form)

	def get_success_url(self, **kwargs):
		return reverse('catalog:category_detail', kwargs={'pk':self.kwargs['pk']})

class AttributeUpdate(UpdateView):
	model = Attribute
	form_class = AttributeForm

	def get_context_data(self, **kwargs):
		context = super(AttributeUpdate, self).get_context_data(**kwargs)
		category = get_object_or_404(Category, pk=self.kwargs['pk'])
		context['category'] = category
		context['branch'] = category.get_branch()
		return context

	def form_valid(self, form):
		form.instance.category = get_object_or_404(Category, pk=self.kwargs['pk'])
		return super(AttributeUpdate, self).form_valid(form)

	def get_success_url(self, **kwargs):
		return reverse('catalog:category_detail', kwargs={'pk':self.kwargs['pk']})

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
			value = form.cleaned_data.get('nf_{}_value'.format(att.name))
			nom_fix_value = FixedNominalValue(
				value = value,
				attribute = att,
				product = product)
			to_save.append(nom_fix_value)
		#ratfix
		for att in attributes["rat_fix"]:
			value = form.cleaned_data.get('rf_{}_value'.format(att.name))
			rat_fix_value = FixedRatioValue(
				value = value,
				attribute = att,
				product = product)
			to_save.append(rat_fix_value)
		#nom_unfix
		for att in attributes["nom_unfix"]:
			values = form.cleaned_data.get('nuf_{}_values'.format(att.name))
			values = [x.strip("\r") for x in values.split("\n")]
			others = form.cleaned_data.get('nuf_{}_others'.format(att.name))
			nominal_config = NominalConfig(
				attribute = att,
				product = product,
				accept_others = others)
			to_save.append(nominal_config)
			for value in values:
				nom_value = NominalValue(
					value = value,
					nominal_config = nominal_config)
				to_save.append(nom_value)
		for att in attributes["rat_unfix"]:
			minval = form.cleaned_data.get('ruf_{}_min'.format(att.name))
			maxval = form.cleaned_data.get('ruf_{}_max'.format(att.name))
			integer = form.cleaned_data.get('ruf_{}_integer'.format(att.name))
			ratio_config = RatioConfig(
				attribute = att,
				product = product,
				minval = minval,
				maxval = maxval,
				integer = integer)
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
		bid = product.category.bid
		return reverse('catalog:category_detail', kwargs={'pk':bid.id})

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
							P_EMPTY = p_empty)
		filename = 'simulacion_{}.zip'.format(str(bid))
		response = HttpResponse(
					zip_file,
					content_type='application/zip'
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


