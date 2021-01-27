from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page


def index(request):
    
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to the template engine
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    
    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {'name': 'Harvey Russell'}
    
    return render(request, 'rango/about.html', context=context_dict)
    #return HttpResponse('<a href="/rango/">Index</a>' + "Rango says here is the about page.")
    
def show_category(request, category_name_slug):
    #create context dict to pass into the template rendering engine
    context_dict = {}
    
    try:
        #trys to find a category name slug with the given name
        #if cant the .get() method raises a DoesNotExist exception
        #The .get() method returns one model instance OR raises an exception
        category  = Category.objects.get(slug=category_name_slug)
        
        #Retrieve all associated pages, the filter() will return a list of page objects or empty list
        pages = Page.objects.filter(category=category)
        
        #adds results list to template context under name pages
        context_dict['pages'] = pages
        #We also add the category object from the database to the context_dict
        #We us this in template to verigy the category exists
        context_dict['category'] = category
        
    except Category.DoesNotExist:
        #We get here if didnt find the specified category
        #Don't do anything-- template will display the "no category" message for us
        context_dict['category'] = None
        context_dict['pages'] = None
        
    
        
    #Go render response and return it to the client
    return render(request, 'rango/category.html', context=context_dict)