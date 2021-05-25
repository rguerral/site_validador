from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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
	min_products_category_level = models.IntegerField(
		validators=[
            MaxValueValidator(4),
            MinValueValidator(1)
        ])
	min_products_n = models.IntegerField(
		validators=[
            MaxValueValidator(20),
            MinValueValidator(0)
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

class Category(models.Model):
	name = models.CharField(max_length = 200, unique = True)
	tree_name = models.CharField(max_length = 200, unique = True)
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
		self.name = self.name.strip()
		parent = self.parent
		self.update_position()
		self.update_tree_name()
		super(Category,self).save(*args, **kwargs)

	def update_tree_name(self):
		tab = "---"
		if self.level == 0:
			self.tree_name = "ROOT"
		else:
			self.tree_name = (self.level-1)*tab +" "+ self.position + " " + self.name
		
	def get_brothers_position(self):
		if self.level == 1:
			brothers = Category.objects.filter(level = 1)
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
		if self.fixed == "SI" and self.attribute_type == "NOMINAL":
			return ['nf_{}_value'.format(self.name)]
		elif self.fixed == "SI" and self.attribute_type == "RATIO":
			return ['rf_{}_value'.format(self.name)]
		elif self.fixed == "NO" and self.attribute_type == "NOMINAL":
			return ['nuf_{}_values'.format(self.name), 'nuf_{}_others'.format(self.name)]
		elif self.fixed == "NO" and self.attribute_type == "RATIO":
			return ['ruf_{}_min'.format(self.name),
					'ruf_{}_max'.format(self.name),
					'ruf_{}_integer'.format(self.name)]
		else:
			raise ValueError()

class FixedNominalValue(models.Model):
	value = models.CharField(max_length = 64)
	attribute = models.ForeignKey(Attribute, on_delete = models.CASCADE)
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
	product = models.ForeignKey(
		Product,
		on_delete = models.CASCADE,
		related_name = 'fixed_ratio_values')

	def __str__(self):
		return str(self.value)

class NominalConfig(models.Model):
	accept_others = models.BooleanField()
	attribute = models.ForeignKey(Attribute, on_delete = models.CASCADE)
	product = models.ForeignKey(
		Product,
		on_delete = models.CASCADE,
		related_name = 'nominal_configs'
		)

	def get_values_str(self):
		return "; ".join([str(x) for x in self.nominal_values.all()]).strip()

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

class RatioConfig(models.Model):
	minval = models.FloatField()
	maxval = models.FloatField()
	integer = models.BooleanField()
	attribute = models.ForeignKey(Attribute, on_delete = models.CASCADE)
	product = models.ForeignKey(Product,
								on_delete = models.CASCADE,
								related_name = 'ratio_configs')
	def __str__(self):
		unit = self.attribute.unit
		return "{}-{}({})".format(self.minval,self.maxval,unit)
