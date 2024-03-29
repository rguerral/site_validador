from django import forms
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from catalog.models import Attribute, Product, Bid, Category, Unit, Dimension, BidAttribute, BidAttributeLevel
from .widgets import ClearableMultipleFilesInput
from .fields import MultipleFilesField

class BidForm(forms.Form):
	name = forms.CharField(label= "Nombre del convenio")
	max_category_level = forms.IntegerField(min_value = 1, max_value = 4, label="Niveles de categoría")
	zones = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 35}), label="Zonas", required = False)
	max_products_alternatives = forms.IntegerField(min_value = 1, label="Número de alternativas de producto")

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
		if len(zones) == 1 and zones[0]=="":
			return ["NACIONAL"]
		if len(zones) != len(set(zones)):
			raise ValidationError(
				"Hay una zona duplicada"
			)
		return zones

class BidAttributeForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.bid = kwargs.pop('bid')
		super(BidAttributeForm, self).__init__(*args, **kwargs)
		self.fields["name"] = forms.CharField(label = "Nombre atributo")
		self.fields["zone_or_global"] = forms.ChoiceField(
			choices = [
				["ZONA", "ZONA"],
				["NACIONAL", "NACIONAL"],
			],
			label = "¿Se oferta a nivel nacional o por zona?"
			)
		self.fields["unit"] = forms.ModelChoiceField(queryset=Unit.objects.filter(
			dimension = Dimension.objects.get(name = "MONEDA")),
			label = "Unidad")
	def clean(self):
		cleaned_data = super().clean()
		zone_or_global = cleaned_data.get("zone_or_global")
		name = cleaned_data.get("name")

		if BidAttribute.objects.filter(bid = self.bid, name = name):
			raise ValidationError(
				"Ya existe un atributo con ese nombre"
			)
		return cleaned_data

class BidAttributeLevelForm(forms.Form):

	def __init__(self, *args, **kwargs):
		self.bidattribute = kwargs.pop('bidattribute')
		self.zones = kwargs.pop('zones')
		self.form_auxdata = kwargs.pop('form_auxdata')
		super(BidAttributeLevelForm, self).__init__(*args, **kwargs)
		self.fields["name"] = forms.CharField(label = "Nombre nivel")

		if self.bidattribute.zone_or_global == "NACIONAL":
			self.fields["global_minprice"] = forms.IntegerField(min_value = 0, label = "Mínimo")
			self.fields["global_maxprice"] = forms.IntegerField(min_value = 0, label = "Máximo")
		elif self.bidattribute.zone_or_global == "ZONA":
			for zone in self.zones:
				self.fields['{}_minprice'.format(zone)] = forms.IntegerField(min_value = 0, label = "Mínimo")
				self.fields['{}_maxprice'.format(zone)] = forms.IntegerField(min_value = 0, label = "Máximo")

	def clean(self):
		cleaned_data = super().clean()
		zone_or_global = self.bidattribute.zone_or_global
		name = cleaned_data.get("name")

		if BidAttributeLevel.objects.filter(bidattribute = self.bidattribute, name = name):
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
	name = forms.CharField(label = "Nombre")

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
		fields = ['name', 'attribute_type', 'zone_or_global', 'fixed', 'unit', 'accept_others', "only_integers"]
		labels = {
        	"name": "Nombre atributo",
        	"attribute_type": "Tipo de atributo",
        	"zone_or_global": "Restricciones a nivel nacional o por zona",
        	"fixed": "¿Valor fijo?",
        	"unit": "Unidad",
        	"accept_others": "¿Acepta otros valores?",
        	"only_integers": "¿Solo valores enteros?"
    	}
	def clean_name(self):
		# Reemplazar _
		cleaned_data = self.cleaned_data
		name = cleaned_data.get("name")
		return name.replace("_", " ")

	def clean_unit(self):
		cleaned_data = self.cleaned_data
		attribute_type = cleaned_data.get("attribute_type")
		unit = cleaned_data.get("unit")
		if attribute_type == "NOMINAL":
			return None
		else:
			return unit

	def clean_accept_others(self):
		cleaned_data = self.cleaned_data
		attribute_type = cleaned_data.get("attribute_type")
		accept_others = cleaned_data.get("accept_others")
		fixed = cleaned_data.get("fixed")
		if attribute_type == "RATIO" or fixed==True:
			return None
		else:
			return accept_others

	def clean_only_integers(self):
		cleaned_data = self.cleaned_data
		attribute_type = cleaned_data.get("attribute_type")
		only_integers = cleaned_data.get("only_integers")
		fixed = cleaned_data.get("fixed")
		if attribute_type == "NOMINAL" or fixed==True:
			return None
		else:
			return only_integers

	def clean(self):
		cleaned_data = super().clean()
		attribute_type = cleaned_data.get("attribute_type")
		unit = cleaned_data.get("unit")
		fixed = cleaned_data.get("fixed")
		# Atributo ratio sin unit
		if attribute_type == "RATIO" and not unit:
			raise ValidationError(
					"Debe definir el campo unit"
				)
		# Only_integers
		if attribute_type == "RATIO" and fixed==False:
			raise ValidationError(
					"Debe definir el campo only_integers"
				)
		# accept_others
		if attribute_type == "NOMINAL" and fixed==False:
			raise ValidationError(
					"Debe definir el campo accept_others"
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
		self.zones = kwargs.pop('zones')
		super(ProductForm, self).__init__(*args, **kwargs)
		# name
		self.fields["name"] = forms.CharField(label = "Modelo")
		#NomFix
		for att in self.attributes["nom_fix"]:
			if att.zone_or_global == "NACIONAL":
				self.fields['nf_{}_global_value'.format(att)] = forms.CharField(
					label = str("Valor"))
			elif att.zone_or_global == "ZONA":
				for zone in self.zones:
					self.fields['nf_{}_{}_value'.format(att,zone)] = forms.CharField(
						label = str("Valor"))
		#RatFix
		for att in self.attributes["rat_fix"]:
			if att.zone_or_global == "NACIONAL":
				self.fields['rf_{}_global_value'.format(att)] = forms.FloatField(
				label = str("Valor"))


			elif att.zone_or_global == "ZONA":
				for zone in self.zones:
					self.fields['rf_{}_{}_value'.format(att,zone)] = forms.FloatField(
					label = str("Valor"))

		#NomUnfixed
		for att in self.attributes["nom_unfix"]:
			if att.zone_or_global == "NACIONAL":
				self.fields['nuf_{}_global_values'.format(att)] = forms.CharField(
					label = str("Valores"),
					widget=forms.Textarea(attrs={'rows': 5,
												 'cols': 25}))

			elif att.zone_or_global == "ZONA":
				for zone in self.zones:
					self.fields['nuf_{}_{}_values'.format(att,zone)] = forms.CharField(
						label = str("Valores"),
						widget=forms.Textarea(attrs={'rows': 5,
													 'cols': 25}))

		#RatUnfixed
		for att in self.attributes["rat_unfix"]:
			if att.zone_or_global == "NACIONAL":
				self.fields['ruf_{}_global_min'.format(att)] = forms.FloatField(
					label = str("Valor minimo"))
				self.fields['ruf_{}_global_max'.format(att)] = forms.FloatField(
					label = str("Valor maximo"))

			elif att.zone_or_global == "ZONA":
				for zone in self.zones:
					self.fields['ruf_{}_{}_min'.format(att,zone)] = forms.FloatField(
						label = str("Valor minimo"))
					self.fields['ruf_{}_{}_max'.format(att,zone)] = forms.FloatField(
						label = str("Valor maximo"))

	def clean_name(self):
		# Reemplazar _
		cleaned_data = self.cleaned_data
		name = cleaned_data.get("name")
		return name.upper().strip()

class SimulateForm(forms.Form):
	nsims = forms.IntegerField(min_value = 1, max_value = 500, label ="NSIMS")
	p_field_error = forms.FloatField(min_value = 0, max_value = 1, label = "P_FIELD_ERROR")
	p_empty = forms.FloatField(min_value = 0, max_value = 1, label = "P_EMPTY")
	p_edit_field = forms.FloatField(min_value = 0, max_value = 1, label = "P_EDIT_FIELD")
	
class ValidateForm(forms.Form):
	content = MultipleFilesField(
		widget=ClearableMultipleFilesInput(
			attrs={'multiple': True}),
		label = "Archivos")
							
	def clean(self):
		cleaned_data = super().clean()
		for file in cleaned_data["content"]:
			CONTENT_TYPES = [
				'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' #xlsx
				]
			MAX_UPLOAD_SIZE = 5242880 # 5mb
			if file.content_type in CONTENT_TYPES:
				if file.size > MAX_UPLOAD_SIZE:
					raise forms.ValidationError('El archivo %s pesa más de %s (%s)') % (file, filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(content.size))
			else:
				raise forms.ValidationError('El archivo %s no es de un formato soportado' % (file))
