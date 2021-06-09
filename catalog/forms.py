from django import forms
from django.core.exceptions import ValidationError
from catalog.models import Attribute, Product, Bid, Category, Unit, Dimension, BidAttribute

class BidForm(forms.Form):
	name = forms.CharField()
	max_category_level = forms.IntegerField(min_value = 1, max_value = 4)
	zones = forms.CharField(widget=forms.Textarea)
	max_products_alternatives = forms.IntegerField(min_value = 1)
	min_products_category_level = forms.ChoiceField(
		choices = [
			[1, "Categoria Nivel 1"],
			[2, "Categoria Nivel 2"],
			[3, "Categoria Nivel 3"],
			[4, "Categoria Nivel 4"]
		]
		)
	min_products_n = forms.IntegerField()

	def clean_name(self):
		cleaned_data = self.cleaned_data
		name = cleaned_data.get("name").strip()
		name = name.upper()
		if len(Bid.objects.filter(name=name))>0:
			raise ValidationError(
				"Ya existe un convenio con ese nombre"
			)
		return name

	def clean_zones(self):
		cleaned_data = self.cleaned_data
		zones = cleaned_data.get("zones")
		zones = [x.strip("\r") for x in zones.split("\n")]
		if len(zones) != len(set(zones)):
			raise ValidationError(
				"Hay una zona duplicada"
			)
		return zones

	def clean_min_products_category_level(self):
		cleaned_data = self.cleaned_data
		min_products_category_level = cleaned_data.get("min_products_category_level")
		return int(min_products_category_level)

	def clean(self):
		cleaned_data = super().clean()
		min_products_category_level = cleaned_data.get("min_products_category_level")
		max_category_level = cleaned_data.get("max_category_level")
		if min_products_category_level > max_category_level:
			raise ValidationError(
					"No se cumple min_products_category_level <= max_category_level"
				)

class BidAttributeForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.bid = kwargs.pop('bid')
		self.zones = kwargs.pop('zones')
		self.form_auxdata = kwargs.pop('form_auxdata')
		super(BidAttributeForm, self).__init__(*args, **kwargs)
		self.fields["name"] = forms.CharField()
		self.fields["zone_or_global"] = forms.ChoiceField(
			choices = [
				["ZONA", "ZONA"],
				["NACIONAL", "NACIONAL"],
			]
			)
		self.fields["unit"] = forms.ModelChoiceField(queryset=Unit.objects.filter(dimension = Dimension.objects.get(name = "MONEDA")))
		self.fields["global_minprice"] = forms.IntegerField(min_value = 0, required = False)
		self.fields["global_maxprice"] = forms.IntegerField(min_value = 0, required = False)


		for zone in self.zones:
			self.fields['{}_minprice'.format(zone)] = forms.IntegerField(min_value = 0, required = False, label = "Precio minimo")
			self.fields['{}_maxprice'.format(zone)] = forms.IntegerField(min_value = 0, required = False, label = "Precio maximo")

	def clean(self):
		cleaned_data = super().clean()
		zone_or_global = cleaned_data.get("zone_or_global")
		name = cleaned_data.get("name")

		if BidAttribute.objects.filter(bid = self.bid, name = name):
			raise ValidationError(
				"Ya existe un atributo con ese nombre"
			)

		if zone_or_global == "NACIONAL":
			global_minprice = cleaned_data.get("global_minprice")
			global_maxprice = cleaned_data.get("global_maxprice")
			if global_minprice >= global_maxprice:
				raise ValidationError(
					"global_minprice >= global_maxprice"
				)
		elif zone_or_global == "ZONA":
			for zone in self.zones:
				minprice = cleaned_data.get("{}_minprice".format(zone))
				maxprice = cleaned_data.get("{}_maxprice".format(zone))
				if minprice >= maxprice:
					raise ValidationError(
						"{}_minprice >= {}_maxprice".format(zone,zone)
					)
		else:
			print(zone_or_global)
			raise ValidationError(
				"Campo zone_or_global debería ser 'NACIONAL' o 'ZONA'"
			)
		return cleaned_data

class CategoryForm(forms.Form):
	name = forms.CharField()

	def __init__(self, *args, **kwargs):
		self.bid = kwargs.pop('bid')
		self.parent = kwargs.pop('parent')
		super(CategoryForm, self).__init__(*args, **kwargs)

	def clean_name(self):
		cleaned_data = self.cleaned_data
		name = cleaned_data.get("name")
		return name.upper().strip()

	def clean(self):
		cleaned_data = super().clean()
		name = cleaned_data.get("name")
		if len(Category.objects.filter(bid = self.bid, name = name))>0:
			raise ValidationError(
				"Ya existe una categoría con ese nombre"
			)

class AttributeForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		self.category = kwargs.pop('category', None)
		super().__init__(*args, **kwargs)

	class Meta:
		model = Attribute
		fields = ['name', 'attribute_type', 'fixed', 'unit']
	
	def clean_name(self):
		# Reemplazar _
		cleaned_data = self.cleaned_data
		name = cleaned_data.get("name")
		return name.replace("_", " ")

	def clean(self):
		cleaned_data = super().clean()
		attribute_type = cleaned_data.get("attribute_type")
		unit = cleaned_data.get("unit")
		# Atributo ratio sin unit
		if attribute_type == "RATIO" and not unit:
			raise ValidationError(
					"Los atributos ratio deben tener una unidad"
				)
		# Atributo ya existe
		name = cleaned_data.get("name").upper()
		if len(Attribute.objects.filter(name = name, category = self.category))>0:
			raise ValidationError(
					"Ya existe un atributo con ese nombre"
				)

class ProductForm(forms.Form):

	def __init__(self, *args, **kwargs):
		self.category = kwargs.pop('category')
		self.bid = kwargs.pop('bid')
		self.attributes = kwargs.pop('attributes')
		super(ProductForm, self).__init__(*args, **kwargs)
		# name
		self.fields["name"] = forms.CharField(label = "Nombre")
		#NomFix
		for att in self.attributes["nom_fix"]:
			self.fields['nf_{}_value'.format(att)] = forms.CharField(
				label = str("Valor"))
		#RatFix
		for att in self.attributes["rat_fix"]:
			self.fields['rf_{}_value'.format(att)] = forms.FloatField(
				label = str("Valor"))
		#NomUnfixed
		for att in self.attributes["nom_unfix"]:
			self.fields['nuf_{}_values'.format(att)] = forms.CharField(
				label = str("Valores"),
				widget=forms.Textarea)
			self.fields['nuf_{}_others'.format(att)] = forms.BooleanField(
				label = str("Acepta otros"),
				initial = False,
				required = False)
		#RatUnfixed
		for att in self.attributes["rat_unfix"]:
			self.fields['ruf_{}_min'.format(att)] = forms.FloatField(
				label = str("Valor minimo"))
			self.fields['ruf_{}_max'.format(att)] = forms.FloatField(
				label = str("Valor maximo"))
			self.fields['ruf_{}_integer'.format(att)] = forms.BooleanField(
				label = str("Solo numeros enteros"),
				initial = False,
				required = False)

	def clean_name(self):
		# Reemplazar _
		cleaned_data = self.cleaned_data
		name = cleaned_data.get("name")
		return name.upper().strip()

class SimulateForm(forms.Form):
	nsims = forms.IntegerField(min_value = 1, max_value = 500)
	p_field_error = forms.FloatField(min_value = 0, max_value = 1)
	p_empty = forms.FloatField(min_value = 0, max_value = 1)
	p_edit_field = forms.FloatField(min_value = 0, max_value = 1)
	