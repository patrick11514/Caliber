from django.middleware.csrf import get_token
from django.shortcuts import render


def index(request):
	get_token(request)
	return render(request, "core/index.html")
