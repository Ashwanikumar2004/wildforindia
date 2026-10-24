from django.shortcuts import render


def identifier_home(request):
    return render(request, "ai_identifier/home.html")   
