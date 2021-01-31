from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from django.shortcuts import redirect
from django.urls import reverse


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

def add_category(request):
    form = CategoryForm()
    
    #A HTTP POST????
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        #Have we been provided with a valid form??
        if form.is_valid():
            #save new category to database
            form.save(commit=True)
            #now cat is saved we could confirm this
            #for now just redirect user back to index
            return redirect('/rango/')
        else:
            #supplied form had errors so print to terminal
            print(form.errors)
    
    #handle bad form, new form, or no form supplied cases
    #render the form with error messages (if any)       
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                
                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug':
                                            category_name_slug}))
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)