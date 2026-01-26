from django.shortcuts import render, redirect
import markdown2
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": markdown2.markdown(content)
    })


def search(request):
    return render(request, "encyclopedia/error.html", {
        "message": "Search not implemented yet."
    })


def new_page(request):
    return render(request, "encyclopedia/error.html", {
        "message": "New Page not implemented yet."
    })


def edit_page(request, title):
    return render(request, "encyclopedia/error.html", {
        "message": "Edit Page not implemented yet."
    })


def random_page(request):
    return render(request, "encyclopedia/error.html", {
        "message": "Random Page not implemented yet."
    })
