from django import template
from django.templatetags.static import static

from wildlife.catalogue import catalogue_profile

register = template.Library()


@register.simple_tag
def catalogue_media(obj):
    return catalogue_profile(obj)


@register.simple_tag
def catalogue_image(obj):
    if obj._meta.model_name == "species":
        primary = obj.primary_image
        if primary and primary.image:
            return primary.image.url
        illustrated_species = {"bengal-tiger", "asian-elephant", "gharial", "indian-peafowl", "indian-leopard", "great-hornbill"}
        fallback = f"images/species/{obj.slug}.svg" if obj.slug in illustrated_species else "images/species/default_species.svg"
    else:
        if obj.hero_image:
            return obj.hero_image.url
        images = list(obj.images.all())
        if images and images[0].image:
            return images[0].image.url
        fallback = "images/species/default_park.svg"
    return static(catalogue_profile(obj).get("path", fallback))
