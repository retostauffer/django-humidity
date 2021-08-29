



from django.shortcuts import render

def home(request):

    context = dict(author = "reto")

    return render(request, "index.html", context)
