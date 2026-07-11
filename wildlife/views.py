from django.shortcuts import render
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import (
    Species,
    Category,
    Habitat,
)


def home(request):

    featured_species = (
    Species.objects.filter(
        is_featured=True,
        is_verified=True,
    )
    .select_related(
        "category",
        "conservation_status",
    )
    .prefetch_related(
        "habitats",
        "images",
    )
    .order_by("featured_priority")[:6])

    context = {

        "featured_species": featured_species,
        "species_count": Species.objects.count(),
        "category_count": Category.objects.count(),
        "habitat_count": Habitat.objects.count(),
        "national_park_count": 0,  # Placeholder for future implementation
        "categories": Category.objects.all(),
        "habitats": Habitat.objects.all(),
    }

    return render(
        request,
        "wildlife/home.html",
        context,
    )

def species_list(request):

    species = (
        Species.objects.select_related(
            "category",
            "conservation_status"
        )
        .prefetch_related(
            "habitats",
            "images"
        )
        .filter(
            is_verified=True
        )
        .order_by("common_name")
    )

    paginator = Paginator(species, 9)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {

        "page_obj": page_obj,

    }

    return render(
        request,
        "wildlife/species_list.html",
        context,
    )

def species_detail(request, slug):

    species = get_object_or_404(
        Species.objects.select_related(
            "category",
            "conservation_status",
        ).prefetch_related(
            "habitats",
            "images",
            "sounds",
            "distributions",
        ),
        slug=slug,
        is_verified=True,
    )

    related_species = (
        Species.objects.filter(
            category=species.category,
            is_verified=True,
        )
        .exclude(id=species.id)
        .order_by("?")[:3]
    )

    context = {

        "species": species,

        "related_species": related_species,

    }

    return render(
        request,
        "wildlife/species_detail.html",
        context,
    )

def search_species(request):

    query = request.GET.get("q", "")
    category = request.GET.get("category")
    habitat = request.GET.get("habitat")

    species = (
        Species.objects.filter(
            is_verified=True
        )
        .select_related(
            "category",
            "conservation_status"
        )
        .prefetch_related(
            "images",
            "habitats"
        )
    )

    # Search by common/scientific name

    if query:

        species = species.filter(

            Q(common_name__icontains=query) |

            Q(scientific_name__icontains=query)

        )

    # Filter by category

    if category:

        species = species.filter(
            category_id=category
        )

    # Filter by habitat

    if habitat:

        species = species.filter(
            habitats__id=habitat
        )

    species = species.distinct().order_by("common_name")

    context = {

        "species": species,

        "query": query,

        "selected_category": category,

        "selected_habitat": habitat,

    }

    return render(
        request,
        "wildlife/search_results.html",
        context,
    )