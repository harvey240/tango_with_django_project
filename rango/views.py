from django.shortcuts import render, redirect
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


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

@login_required
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
            return redirect(reverse('rango:index'))
        else:
            #supplied form had errors so print to terminal
            print(form.errors)
    
    #handle bad form, new form, or no form supplied cases
    #render the form with error messages (if any)       
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    if category is None:
        return redirect(reverse('rango:index'))
    
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


def register(request):
    #boolean to tell template whether the registration worked
    #set false initially, change to true when successful
    registered = False
    
    #if its a HTTP POST, we wanna process the form data
    if request.method == 'POST':
        #try grab info from form, use both UserForm AND UserProfileForm
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        #if two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            #save users form data to database
            user = user_form.save()
            
            #Now we hash the password with the set method and update user object
            user.set_password(user.password)
            user.save()
            
            #now sort out UserProfile instance
            #need to set the user attribute ourselves
            #so set commit = False to delay saving the model until ready, for integrity
            profile = profile_form.save(commit=False)
            profile.user = user
            
            #Did user give a pic? if so then need to get it from form
            #and put it in UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            #now save UserProfile model instance
            profile.save()
            
            #update variable to show successful registration in template
            registered = True
            
        else:
            #invalid form(s) mistakes or otherwise? print problems
            print(user_form.errors, profile_form.errors)
            
    else:
        #Not a HTTP POST, so render form using 2 ModelForm instances.
        #These forms will be blank & ready for input
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    return render(request, 
                  'rango/register.html',
                  context = {'user_form': user_form,
                             'profile_form': profile_form,
                             'registered': registered})
            
    
    
def user_login(request):
    #if HTTP POST, try pull relevant info
    if request.method == 'POST':
        #Gather username & password from login form
        #We use request.POST.get('<variable>') instead of request.POST['<variable>']
        #because the former returns None if the value doesn't exist and the latter raises an error
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        #use djangos machinery to see if username/password combo is valid
        #returns a user object if it is
        user = authenticate(username=username, password=password)
        
        #if we have user object-details are correct
        #if None, no user with credentials was found
        if user:
            #is account still active?
            if user.is_active:
                #if account is valid and active, log in and send to homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                #inactive account - no log in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            #bad login details - no log in!
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    
    #no POST request so display login form.
    #this scenario would most likely be a HTTP GET
    else:
        #no context vars to pass
        return render(request, 'rango/login.html')
  
    
@login_required    
def restricted(request):
    return render(request, 'rango/restricted.html')


#User login_required() to ensure only those logged in can access
@login_required
def user_logout(request):
    #since we know user is logged in, we can log them out.
    logout(request)
    return redirect(reverse('rango:index'))