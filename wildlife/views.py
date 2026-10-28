from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from parks.models import NationalPark, State
from .catalogue import catalogue_profile, media_manifest, species_sources
from .models import Species, Category, Habitat


def catalogue_species():
    return Species.objects.filter(is_verified=True).select_related(
        "category", "conservation_status"
    ).prefetch_related("habitats", "images")


def filter_options():
    return {
        "categories": Category.objects.filter(is_active=True, species__is_verified=True).distinct(),
        "habitats": Habitat.objects.filter(is_active=True, species__is_verified=True).distinct(),
        "states": State.objects.filter(
            is_active=True, species_distributions__species__is_verified=True,
            species_distributions__is_native=True,
        ).distinct(),
    }


def pagination_context(request, rows, size=12):
    paginator = Paginator(rows, size)
    page = paginator.get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return {
        "page_obj": page,
        "pagination_query": params.urlencode(),
        "pagination_pages": paginator.get_elided_page_range(page.number, on_each_side=1, on_ends=1),
        "pagination_ellipsis": Paginator.ELLIPSIS,
    }


def home(request):
    context = filter_options()
    context.update({
        "featured_species": catalogue_species().filter(is_featured=True).order_by("featured_priority", "common_name")[:6],
        "featured_parks": NationalPark.objects.filter(is_active=True, is_featured=True).select_related("state").prefetch_related("images").order_by("featured_priority", "name")[:3],
        "species_count": Species.objects.filter(is_verified=True).count(),
        "category_count": context["categories"].count(),
        "habitat_count": context["habitats"].count(),
        "national_park_count": NationalPark.objects.filter(protected_area_type="national_park", is_active=True).count(),
    })
    return render(request, "wildlife/home.html", context)


def species_list(request):
    return search_species(request)


def species_detail(request, slug):
    species = get_object_or_404(
        catalogue_species().prefetch_related("sounds", "distributions__state"),
        slug=slug,
    )
    journal_entry = None
    if request.user.is_authenticated:
        journal_entry = request.user.wilddex_entries.filter(species=species).first()
    return render(request, "wildlife/species_detail.html", {
        "species": species,
        "profile": catalogue_profile(species),
        "profile_sources": species_sources().get(species.scientific_name, []),
        "related_species": catalogue_species().filter(category=species.category).exclude(pk=species.pk).order_by("common_name")[:3],
        "known_parks": species.national_parks.filter(is_active=True).select_related("state").prefetch_related("images").order_by("-is_featured", "name")[:6],
        "journal_entry": journal_entry,
    })


def search_species(request):
    query = request.GET.get("q", "").strip()[:200]
    category = request.GET.get("category", "").strip()
    habitat = request.GET.get("habitat", "").strip()
    state = request.GET.get("state", "").strip()
    species = catalogue_species()
    if query:
        species = species.filter(
            Q(common_name__icontains=query) | Q(scientific_name__icontains=query) |
            Q(short_description__icontains=query) | Q(description__icontains=query) |
            Q(category__name__icontains=query) | Q(habitats__name__icontains=query) |
            Q(distributions__state__name__icontains=query)
        )
    if category:
        species = species.filter(category__slug=category)
    if habitat:
        species = species.filter(habitats__slug=habitat)
    if state:
        species = species.filter(distributions__state__slug=state, distributions__is_native=True)
    species = species.distinct().order_by("common_name")
    context = filter_options()
    context.update(pagination_context(request, species))
    context.update({
        "species": context["page_obj"], "query": query,
        "selected_category": category, "selected_habitat": habitat,
        "selected_state": state, "result_count": context["page_obj"].paginator.count,
    })
    return render(request, "wildlife/search_results.html", context)


def wildlife_map(request):
    species_rows = catalogue_species().order_by("common_name")
    parks = NationalPark.objects.filter(is_active=True).select_related("state").prefetch_related(
        Prefetch("species", queryset=species_rows)
    )
    def species_payload(species):
        return {
            "id": str(species.pk), "name": species.common_name,
            "scientificName": species.scientific_name, "summary": species.short_description,
            "status": species.conservation_status.name, "category": species.category.name,
            "url": reverse("species_detail", args=[species.slug]),
        }
    locations = []
    mapped_species = {}
    for park in parks:
        profile = catalogue_profile(park)
        latitude = park.latitude if park.latitude is not None else profile.get("latitude")
        longitude = park.longitude if park.longitude is not None else profile.get("longitude")
        if latitude is None or longitude is None:
            continue
        if not (6 <= float(latitude) <= 38 and 67 <= float(longitude) <= 98):
            continue
        linked_species = [species_payload(s) for s in park.species.all()]
        for species in linked_species:
            mapped_species[species["id"]] = species
        locations.append({
            "id": f"park-{park.pk}", "name": park.name, "state": park.state.name,
            "latitude": float(latitude), "longitude": float(longitude),
            "summary": profile.get("summary", park.description)[:300],
            "url": reverse("park_detail", args=[park.slug]), "demo": False,
            "species": linked_species,
        })
    return render(request, "wildlife/map.html", {
        "map_locations": locations,
        "species_catalogue": sorted(mapped_species.values(), key=lambda row: row["name"]),
        "using_demo_regions": False,
    })


def about(request):
    credits = [
        {"name": key.split("|")[-1], **entry}
        for group in media_manifest().values()
        for key, entry in group.items() if entry.get("path")
    ]
    credits.sort(key=lambda item: item["name"])
    context = pagination_context(request, credits, size=24)
    context.update({
        "photo_count": len(credits),
        "species_count": Species.objects.filter(is_verified=True).count(),
        "park_count": NationalPark.objects.filter(is_active=True).count(),
    })
    return render(request, "wildlife/about.html", context)
