from django.shortcuts import render


def wilddex_home(request):
    demo_collection = [
        {
            "name": "Bengal Tiger",
            "scientific_name": "Panthera tigris tigris",
            "category": "Mammal",
            "status": "Endangered",
            "icon": "🐅",
            "discovered": True,
        },
        {
            "name": "Indian Elephant",
            "scientific_name": "Elephas maximus indicus",
            "category": "Mammal",
            "status": "Endangered",
            "icon": "🐘",
            "discovered": True,
        },
        {
            "name": "Indian Peafowl",
            "scientific_name": "Pavo cristatus",
            "category": "Bird",
            "status": "Least Concern",
            "icon": "🦚",
            "discovered": True,
        },
        {
            "name": "Gharial",
            "scientific_name": "Gavialis gangeticus",
            "category": "Reptile",
            "status": "Critically Endangered",
            "icon": "🐊",
            "discovered": False,
        },
    ]

    context = {
        "demo_collection": demo_collection,
        "demo_xp": 650,
        "demo_level": 4,
        "demo_discoveries": 3,
    }
    return render(request, "wilddex/home.html", context)
