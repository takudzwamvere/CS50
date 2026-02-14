from django.shortcuts import render, redirect
from django import forms

from . import util

import random
import markdown2

# The index page`s simple logic
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# Logic for an entry page
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

class EditEntryForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}))

# edit page function
def edit_page(request, title):
    # check if user submitted the form
    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect('encyclo:entry', title=title)
        else:
            return render(request, "encyclopedia/edit_page.html", {
                "form": form,
                "title": title
            })
    
    if request.method == "GET":
        content = util.get_entry(title)
        if content == None:
            # show error if not found
            return render(request, "encyclopedia/error.html", {
                "message": "The requested page was not found."
            })
        else:
            # create form with existing content
            form = EditEntryForm(initial={'content': content})
            return render(request, "encyclopedia/edit_page.html", {
                "form": form,
                "title": title
            })

def search(request):
    query = request.GET.get('q')
    
    if query:
        entries = util.list_entries()
        
        # check for exact match
        for entry in entries:
            if query.lower() == entry.lower():
                return redirect('encyclo:entry', title=entry)

        # check for substring match
        results = []
        for entry in entries:
            if query.lower() in entry.lower():
                results.append(entry)
        
        return render(request, "encyclopedia/search.html", {
            "results": results,
            "query": query
        })
            
    # if there is no query, go to index page
    return redirect('encyclo:index')

#new page form
class NewEntryForm(forms.Form):
    title = forms.CharField(label="Entry Title")
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}))
    
#creating a new entry page
def new_page(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(title):
                return render(request, "encyclopedia/new_page.html", {
                    "form": form,
                    "error": "Entry with this title already exists."
                })
            util.save_entry(title, content)
            return redirect('encyclo:entry', title=title)
        else:
            return render(request, "encyclopedia/new_page.html", {
                "form": form
            })
    return render(request, "encyclopedia/new_page.html", {
        "form": NewEntryForm()
    })

#random page
def random_page(request):
    entries = util.list_entries()
    if entries:
        random_entry = random.choice(entries)
        return redirect('encyclo:entry', title=random_entry)
    else:
        return redirect('encyclo:index')
