from uuid import UUID
from urllib.parse import urlencode

from django.db.models import F, Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.db.models import Prefetch
from wildlife.catalogue import catalogue_profile
from wildlife.models import Species
from .forms import ParkReviewForm

from .models import NationalPark, State, ParkReview


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

    query = request.GET.get("q", "").strip()

    if query:

        parks = parks.filter(

            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(state__name__icontains=query)

        )

    # ------------------------
    # State Filter
    # ------------------------

    state = request.GET.get("state", "")

    try:
        UUID(state)
    except (ValueError, AttributeError):
        state = ""

    if state:

        parks = parks.filter(

            state__id=state

        )

    # ------------------------
    # Protected area type
    # ------------------------

    area_type = request.GET.get("type", "")
    valid_types = {choice[0] for choice in NationalPark.AREA_TYPE_CHOICES}
    if area_type in valid_types:
        parks = parks.filter(protected_area_type=area_type)

    # ------------------------
    # Safari Filter
    # ------------------------

    safari = request.GET.get("safari")

    if safari == "yes":

        parks = parks.filter(

            safari_available=True

        )
    elif safari == "no":
        parks = parks.filter(safari_available=False)
    elif safari == "unknown":
        parks = parks.filter(safari_available__isnull=True)

    # ------------------------
    # Featured Filter
    # ------------------------

    featured = request.GET.get("featured")

    if featured == "yes":

        parks = parks.filter(

            is_featured=True

        )
    elif featured == "no":
        parks = parks.filter(is_featured=False)

    # ------------------------
    # Sorting
    # ------------------------

    sort = request.GET.get("sort")

    if sort == "area":

        parks = parks.order_by(F("area").desc(nulls_last=True), "name")

    elif sort == "name":

        parks = parks.order_by("name")

    else:

        parks = parks.order_by(

            "-is_featured",
            "featured_priority",
            "name",

        )

    filtered_count = parks.count()
    total_count = NationalPark.objects.filter(is_active=True).count()
    paginator = Paginator(parks, 12)

    page = request.GET.get("page")

    parks = paginator.get_page(page)

    pagination_params = request.GET.copy()
    pagination_params.pop("page", None)

    context = {

        "parks": parks,

        "states": State.objects.all(),

        "selected_state": state,
        "selected_type": area_type,
        "selected_safari": safari,
        "selected_featured": featured,
        "selected_sort": sort,
        "area_types": (
            ("national_park", "National Parks"),
            ("wildlife_sanctuary", "Wildlife Sanctuaries"),
        ),
        "filtered_count": filtered_count,
        "query": query,
        "total_count": total_count,
        "pagination_query": pagination_params.urlencode(),
        "pagination_pages": paginator.get_elided_page_range(
            number=parks.number,
            on_each_side=1,
            on_ends=1,
        ),
        "pagination_ellipsis": Paginator.ELLIPSIS,

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
            Prefetch("species", queryset=Species.objects.filter(is_verified=True).select_related("conservation_status", "category").prefetch_related("images")),
            Prefetch("reviews", queryset=ParkReview.objects.filter(is_verified=True), to_attr="published_reviews"),
            "routes",
        ),

        slug=slug,
        is_active=True,

    )
    related_parks = (
    NationalPark.objects
    .filter(
        state=park.state,
        is_active=True
    )
    .exclude(id=park.id).select_related("state").prefetch_related("images")[:3]
    )

    own_review = ParkReview.objects.filter(park=park, user=request.user).first() if request.user.is_authenticated else None
    form = ParkReviewForm(request.POST if request.method == "POST" else None, instance=own_review)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.path)
        if form.is_valid():
            ParkReview.objects.update_or_create(park=park, user=request.user, defaults={**form.cleaned_data, "reviewer_name": request.user.username[:100], "is_verified": False})
            messages.success(request, "Your review was saved. It will appear after it has been checked by a moderator.")
            return redirect("park_detail", slug=park.slug)


    context = {

        "park": park,
        "related_parks": related_parks,
        "profile": catalogue_profile(park),
        "review_form": form,
        "own_review": own_review,
        "map_search_url": "https://www.google.com/maps/search/?" + urlencode({"api": 1, "query": f"{park.name}, {park.state.name}, India"}),
    }

    return render(
        request,
        "parks/park_detail.html",
        context,
    )
