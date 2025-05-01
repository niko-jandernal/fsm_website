# mywebsite/templatetags/disc_extras.py
from django import template
from ..models import DiscussionTopic

register = template.Library()

@register.filter
def get_by_id(topics, id):
    return topics.filter(id=id).first()
