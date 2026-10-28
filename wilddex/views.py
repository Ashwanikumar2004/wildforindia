import uuid
import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render

from ai_identifier.models import Identification, IdentificationResult
from wildlife.models import Species, Category

from .models import WildDexEntry
from .forms import JournalForm


@login_required
def wilddex_home(request):
    entries = {
        entry.species_id: entry
        for entry in WildDexEntry.objects.filter(
            user=request.user,
            species__is_verified=True,
        ).select_related("species")
    }
    species_rows = (
        Species.objects.filter(is_verified=True)
        .select_related("category", "conservation_status")
        .prefetch_related("images")
        .order_by("common_name")
    )
    collection = [
        {"species": species, "entry": entries.get(species.pk)}
        for species in species_rows
    ]
    total_xp = sum(
        row["species"].xp_reward
        for row in collection
        if row["entry"] is not None
    )
    level = 1 + (total_xp // 500)
    xp_to_next_level = 500 - (total_xp % 500)
    query = request.GET.get("q", "").strip()[:200]
    category = request.GET.get("category", "")
    status = request.GET.get("status", "all")
    sort = request.GET.get("sort", "name")
    total_species = len(collection)
    if query:
        collection = [row for row in collection if query.casefold() in (row["species"].common_name + " " + row["species"].scientific_name).casefold()]
    if category:
        collection = [row for row in collection if row["species"].category.slug == category]
    if status in {"discovered", "undiscovered"}:
        collection = [row for row in collection if bool(row["entry"]) == (status == "discovered")]
    if sort == "recent":
        collection.sort(key=lambda row: row["entry"].discovered_at.timestamp() if row["entry"] else 0, reverse=True)
    elif sort == "xp":
        collection.sort(key=lambda row: row["species"].xp_reward, reverse=True)
    paginator = Paginator(collection, 12)
    page = paginator.get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)

    context = {
        "species_collection": page,
        "page_obj": page,
        "pagination_query": params.urlencode(),
        "pagination_pages": paginator.get_elided_page_range(page.number, on_each_side=1, on_ends=1),
        "pagination_ellipsis": Paginator.ELLIPSIS,
        "categories": Category.objects.filter(species__is_verified=True).distinct(),
        "query": query, "selected_category": category, "selected_status": status, "selected_sort": sort,
        "total_species": total_species,
        "completion_percent": round(100 * len(entries) / total_species) if total_species else 0,
        "experience_points": total_xp,
        "explorer_level": level,
        "discovery_count": len(entries),
        "xp_to_next_level": xp_to_next_level,
    }
    return render(request, "wilddex/home.html", context)


@login_required
def add_discovery(request, identification_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Use the confirmation form to add a discovery.")

    identification = get_object_or_404(
        Identification,
        pk=identification_id,
        user=request.user,
    )
    try:
        species_id = uuid.UUID(request.POST.get("species_id", ""))
    except (AttributeError, TypeError, ValueError):
        return HttpResponseBadRequest("Choose a valid species suggestion.")
    result = IdentificationResult.objects.select_related("species").filter(
        identification=identification,
        species_id=species_id,
        species__is_verified=True,
    ).first()
    if not result:
        return HttpResponseBadRequest("Choose a verified species suggested for this photo.")

    if float(result.score) < float(result.species.confidence_threshold):
        return HttpResponseBadRequest(
            "This result did not meet the species confidence threshold. "
            "Please make a new identification with a clearer photo."
        )

    entry, created = WildDexEntry.objects.get_or_create(
        user=request.user,
        species=result.species,
        defaults={"source_identification": identification},
    )
    if created:
        messages.success(request, f"{result.species.common_name} was added to your WildDex.")
    else:
        messages.info(request, f"{result.species.common_name} is already in your WildDex.")
    return redirect("wilddex")


@login_required
def entry_detail(request, entry_id):
    entry = get_object_or_404(WildDexEntry.objects.select_related("species__category", "species__conservation_status", "source_identification").prefetch_related("species__images"), pk=entry_id, user=request.user)
    form = JournalForm(request.POST if request.method == "POST" else None, instance=entry)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Journal entry saved.")
        return redirect("wilddex_entry", entry_id=entry.pk)
    return render(request, "wilddex/entry.html", {"entry": entry, "form": form})


@login_required
@require_POST
def remove_entry(request, entry_id):
    entry = get_object_or_404(WildDexEntry, pk=entry_id, user=request.user)
    entry.delete()
    messages.success(request, "Discovery removed from your journal. Your identification history is still available.")
    return redirect("wilddex")


@login_required
def export_journal(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="my-wilddex.csv"'
    response["Cache-Control"] = "private, no-store"
    writer = csv.writer(response)
    writer.writerow(["Species", "Scientific name", "Added", "Observed", "Location", "Notes"])
    def safe_cell(value):
        text = str(value or "")
        return "'" + text if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else text
    for entry in WildDexEntry.objects.filter(user=request.user).select_related("species"):
        writer.writerow([safe_cell(value) for value in [entry.species.common_name, entry.species.scientific_name, entry.discovered_at.date(), entry.observed_on, entry.location, entry.notes]])
    return response
