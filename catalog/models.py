from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

class Bid(models.Model):
	name = models.CharField(max_length = 256, unique = True)
	max_category_level = models.IntegerField(
		validators=[
            MaxValueValidator(4),
            MinValueValidator(1)
        ])
	max_products_alternatives = models.IntegerField(
		validators=[
            MaxValueValidator(20),
            MinValueValidator(1)
        ])

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.name = self.name.strip().upper()
		super(Bid,self).save(*args, **kwargs)
 
class Zone(models.Model):
	name = models.CharField(max_length = 256)
	bid = models.ForeignKey(Bid, related_name = 'zones', on_delete = models.CASCADE)

	def __str__(self):
		return self.name

	class Meta:
		unique_together = [['name', 'bid']]

	def save(self, *args, **kwargs):
		self.name = self.name.strip().upper()
		super(Zone,self).save(*args, **kwargs)

class Dimension(models.Model):
	name = models.CharField(max_length = 64, unique = True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.name = self.name.upper()
		super(Dimension,self).save(*args, **kwargs)

class Unit(models.Model):
	name = models.CharField(max_length = 64, unique = True)
	abbreviation = models.CharField(max_length = 8, unique = True)
	is_base = models.BooleanField()
	to_base = models.FloatField()
	currency = models.BooleanField(default = False)
	dimension = models.ForeignKey(Dimension, 
								on_delete = models.CASCADE,
								related_name = 'units'
		)
	# syn = ...
	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.name = self.name.upper()
		super(Unit,self).save(*args, **kwargs)

class BidAttribute(models.Model):
	name = models.CharField(max_length = 64, unique = True)
	bid = models.ForeignKey(Bid, related_name = 'attributes', on_delete = models.CASCADE)
	zone_or_global = models.CharField(max_length = 8,
									choices = [("ZONA", "ZONA"),
												("NACIONAL", "NACIONAL")])
	unit = models.ForeignKey(
		Unit,
		on_delete = models.CASCADE,
		limit_choices_to={'currency': True}
		)

	def __str__(self):
		return str(self.bid) + "-" + str(self.name)

	class Meta:
		unique_together = [['name', 'bid']]

	def save(self, *args, **kwargs):
		self.name = self.name.upper().strip()
		super(BidAttribute, self).save(*args, **kwargs)

class BidAttributeLevel(models.Model):
	bidattribute = models.ForeignKey(BidAttribute, related_name = "levels", on_delete = models.CASCADE)
	zone = models.ForeignKey(Zone, on_delete = models.CASCADE, blank = True, null = True)
	name = models.CharField(max_length = 128)
	minprice = models.IntegerField()
	maxprice = models.IntegerField()

	def __str__(self):
		return str(self.bidattribute) + "-" + self.name + "-" + str(self.zone)

	class Meta:
		unique_together = [['bidattribute', 'zone', 'name']]

	def save(self, *args, **kwargs):
		self.name = self.name.upper().strip()
		if self.minprice >= self.maxprice:
			raise ValidationError("El valor mínimo debe ser mayor al valor máximo")
		super(BidAttributeLevel,self).save(*args, **kwargs)

class Category(models.Model):
	name = models.CharField(max_length = 200)
	tree_name = models.CharField(max_length = 200)
	position = models.CharField(max_length = 16, null = True)
	level = models.IntegerField()
	parent = models.ForeignKey('self',
								null = True,
								blank = True,
								related_name = 'children',
								on_delete = models.CASCADE)
	bid = models.ForeignKey(Bid,
							on_delete = models.CASCADE)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	def __str__(self):
		return self.name

	class Meta:
		unique_together = [['name', 'bid']]

	def save(self, *args, **kwargs):
		self.name = self.name.upper().strip()
		self.update_position()
		self.update_tree_name()
		super(Category,self).save(*args, **kwargs)

	def update_tree_name(self):
		tab = "–––––"
		if self.level == 0:
			self.tree_name = "ROOT"
		else:
			self.tree_name = (self.level-1)*tab +" "+ self.position + ". " + self.name
		
	def get_brothers_position(self):
		if self.level == 1:
			brothers = Category.objects.filter(level = 1, bid = self.bid)
		else:
			brothers = self.parent.children.all().order_by('created_at')
		try:
			position = list(brothers).index(self)+1
		except:
			position = len(brothers) +1
		return position

	def update_position(self):
		if self.level == 0:
			self.position = str(0)
		elif self.level == 1:
			self.position = str(self.get_brothers_position())
		else:
			self.position = str(self.parent.position) + "." + str(self.get_brothers_position())

	def get_branch(self):
		branch = []
		node = self
		while True:
			branch = [node] + branch
			node = node.parent
			if node == None:
				break
		return branch

class Product(models.Model):
	name = models.CharField(max_length = 200)
	category = models.ForeignKey(Category,
								 on_delete = models.CASCADE,
								 related_name = "products")

	def get_fixednominal_dict(self):
		d = {}
		attributes = self.category.attributes.filter(
			attribute_type = "NOMINAL",
			fixed = "SI")
		for att in attributes:
			fixed_nominal_value = FixedNominalValue.objects.get(
				product = self,
				attribute = att)
			d[att] = str(fixed_nominal_value)
		return d

	class Meta:
		unique_together = [['name', 'category']]

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.name = self.name.upper()
		super(Product,self).save(*args, **kwargs)

class Attribute(models.Model):
	name = models.CharField(max_length = 64)
	category = models.ForeignKey(Category,
								on_delete = models.CASCADE,
								related_name = "attributes")
	attribute_type = models.CharField(max_length = 8,
									choices = [("NOMINAL", "NOMINAL"),
												("RATIO", "RATIO")])
	fixed = models.CharField(max_length = 2,
							choices = [("NO", "NO"),
										("SI", "SI")])
	unit = models.ForeignKey(Unit, 
								on_delete = models.PROTECT,
								null = True,
								blank = True)

	zone_or_global = models.CharField(max_length = 8,
									choices = [("ZONA", "ZONA"),
												("NACIONAL", "NACIONAL")])

	CHOICES = (
	    (None, "-------"),
	    (True, "SI"),
	    (False, "NO")
	)
	# only_integers: atributo para los type RATIO. Si es True, restringe los valores a enteros
	only_integers = models.BooleanField(null = True, blank = True, choices = CHOICES)
	# accept_others: atributo para los type NOMINAL. Si es True, permite al proveedor ingresar nuevos valores
	accept_others = models.BooleanField(null = True, blank = True, choices = CHOICES)


	class Meta:
		unique_together = [['name', 'category']]

	def __str__(self):
		return self.name

	def full_str(self):
		if self.attribute_type == "NOMINAL":
			return self.name
		else:
			return self.name + " (" + self.unit.abbreviation +")"

	def save(self, *args, **kwargs):
		self.name = self.name.upper()
		if self.attribute_type == "NOMINAL":
			self.unit = None
		super(Attribute,self).save(*args, **kwargs)

	def get_form_fields(self):
		# nominal fixed
		if self.fixed == "SI" and self.attribute_type == "NOMINAL":
			if self.zone_or_global == "NACIONAL":
				return [{
						"zone": None,
						"fields": ['nf_{}_global_value'.format(self.name)]
						}]
			else:
				aux = []
				for zone in self.category.bid.zones.all():
					aux.append({
						"zone": zone,
						"fields": ['nf_{}_{}_value'.format(self.name, zone.name)]
						})
				return aux
		elif self.fixed == "SI" and self.attribute_type == "RATIO":
			if self.zone_or_global == "NACIONAL":
				return [{
						"zone": None,
						"fields": ['rf_{}_global_value'.format(self.name)]
						}]
			else:
				aux = []
				for zone in self.category.bid.zones.all():
					aux.append({
						"zone": zone,
						"fields": ['rf_{}_{}_value'.format(self.name, zone.name)]
						})
				return aux
		elif self.fixed == "NO" and self.attribute_type == "NOMINAL":
			if self.zone_or_global == "NACIONAL":
				return [{
						"zone": None,
						"fields": [
							'nuf_{}_global_values'.format(self.name),
							'nuf_{}_global_others'.format(self.name)
							]
						}]
			else:
				aux = []
				for zone in self.category.bid.zones.all():
					aux.append({
						"zone": zone,
						"fields": [
							'nuf_{}_{}_values'.format(self.name, zone.name),
							'nuf_{}_{}_others'.format(self.name, zone.name)
							]
						})
				return aux

			return ['nuf_{}_values'.format(self.name), 'nuf_{}_others'.format(self.name)]
		elif self.fixed == "NO" and self.attribute_type == "RATIO":

			if self.zone_or_global == "NACIONAL":
				return [{
					"zone": None,
					"fields": [
						'ruf_{}_global_min'.format(self.name),
						'ruf_{}_global_max'.format(self.name),
						'ruf_{}_global_integer'.format(self.name)
						]
					}]
			else:
				aux = []
				for zone in self.category.bid.zones.all():
					aux.append({
					"zone": zone,
					"fields": [
						'ruf_{}_{}_min'.format(self.name, zone.name),
						'ruf_{}_{}_max'.format(self.name, zone.name),
						'ruf_{}_{}_integer'.format(self.name, zone.name)
						]
					})
				return aux
		else:
			raise ValidationError()

class FixedNominalValue(models.Model):
	value = models.CharField(max_length = 64)
	attribute = models.ForeignKey(Attribute, on_delete = models.CASCADE)
	zone = models.ForeignKey(Zone, on_delete = models.CASCADE, blank = True, null = True)
	product = models.ForeignKey(
		Product,
	 	on_delete = models.CASCADE,
	 	related_name = 'fixed_nominal_values')

	def __str__(self):
		return self.value

	def save(self, *args, **kwargs):
		self.value = self.value.upper()
		super(FixedNominalValue,self).save(*args, **kwargs)

class FixedRatioValue(models.Model):
	value = models.FloatField()
	attribute = models.ForeignKey(Attribute, on_delete = models.CASCADE)
	zone = models.ForeignKey(Zone, on_delete = models.CASCADE, blank = True, null = True)
	product = models.ForeignKey(
		Product,
		on_delete = models.CASCADE,
		related_name = 'fixed_ratio_values')

	def __str__(self):
		return str(self.value)

class NominalConfig(models.Model):
	attribute = models.ForeignKey(Attribute, on_delete = models.CASCADE)
	zone = models.ForeignKey(Zone, on_delete = models.CASCADE, blank = True, null = True)
	product = models.ForeignKey(
		Product,
		on_delete = models.CASCADE,
		related_name = 'nominal_configs'
		)

	def get_values_str(self):
		return "; ".join([str(x) for x in self.nominal_values.all()]).strip()

class RatioConfig(models.Model):
	minval = models.FloatField()
	maxval = models.FloatField()
	
	attribute = models.ForeignKey(Attribute, on_delete = models.CASCADE)
	product = models.ForeignKey(Product,
								on_delete = models.CASCADE,
								related_name = 'ratio_configs')
	zone = models.ForeignKey(Zone, on_delete = models.CASCADE, blank = True, null = True)
	def __str__(self):
		unit = self.attribute.unit
		return "{}-{}({})".format(self.minval,self.maxval,unit)

	def save(self, *args, **kwargs):
		if self.minval >= self.maxval:
			raise ValidationError("El valor mínimo debe ser mayor al valor máximo")
		super(RatioConfig,self).save(*args, **kwargs)


class NominalValue(models.Model):
	value = models.CharField(max_length = 64)
	nominal_config = models.ForeignKey(
		NominalConfig,
		on_delete = models.CASCADE,
		related_name = 'nominal_values')
	def __str__(self):
		return str(self.value)

	def save(self, *args, **kwargs):
		self.value = self.value.upper()
		super(NominalValue,self).save(*args, **kwargs)