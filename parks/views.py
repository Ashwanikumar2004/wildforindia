from django.shortcuts import get_object_or_404, render

from .models import NationalPark, State

from django.db.models import Q
from django.core.paginator import Paginator


def parks_list(request):

    parks = (
        NationalPark.objects
        .select_related("state")
        .prefetch_related(
            "images",
            "facilities",
            "species",
        )
        .filter(is_active=True)
    )

    # ------------------------
    # Search
    # ------------------------

    query = request.GET.get("q")

    if query:

        parks = parks.filter(

            Q(name__icontains=query) |
            Q(description__icontains=query)

        )

    # ------------------------
    # State Filter
    # ------------------------

    state = request.GET.get("state")

    if state:

        parks = parks.filter(

            state__id=state

        )

    # ------------------------
    # Safari Filter
    # ------------------------

    safari = request.GET.get("safari")

    if safari == "yes":

        parks = parks.filter(

            safari_available=True

        )

    # ------------------------
    # Featured Filter
    # ------------------------

    featured = request.GET.get("featured")

    if featured == "yes":

        parks = parks.filter(

            is_featured=True

        )

    # ------------------------
    # Sorting
    # ------------------------

    sort = request.GET.get("sort")

    if sort == "area":

        parks = parks.order_by("-area")

    elif sort == "name":

        parks = parks.order_by("name")

    else:

        parks = parks.order_by(

            "-is_featured",
            "featured_priority",
            "name",

        )

    paginator = Paginator(parks, 9)

    page = request.GET.get("page")

    parks = paginator.get_page(page)

    context = {

        "parks": parks,

        "states": State.objects.all(),

        "selected_state": state,

    }

    return render(

        request,

        "parks/parks_list.html",

        context,

    )


def park_detail(request, slug):

    park = get_object_or_404(

        NationalPark.objects
        .select_related("state")
        .prefetch_related(
            "images",
            "facilities",
            "species",
            "reviews",
            "routes",
        ),

        slug=slug,

    )
    related_parks = (
    NationalPark.objects
    .filter(
        state=park.state,
        is_active=True
    )
    .exclude(id=park.id)[:3]
    )


    context = {

        "park": park,
        "related_parks": related_parks,
    }

    return render(
        request,
        "parks/park_detail.html",
        context,
    )