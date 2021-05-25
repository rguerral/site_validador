from django import template

register = template.Library()

@register.filter
def get_obj_attr(form, field):
	return [form[field].errors, form[field].label_tag, form[field]]