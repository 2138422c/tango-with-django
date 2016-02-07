from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

def encode_url(str):
    return str.replace(' ', '_').lower()
    return str.replace(' ', '_')

def decode_url(str):
    return str.replace('_',' ').capitalize()
    return str.replace('_',' ')

def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}

    # Render the response and send it back!
    return render(request, 'rango/index.html', context_dict)

def about(request):
    context_dict = {'italicsmessage': "Tango with Django!"}
    return render(request, 'rango/about.html', context_dict)

def category(request, category_name_slug):

    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_url):

     category_name = decode_url(category_name_url)
     if request.method == 'POST':
         form = PageForm(request.POST)

         if form.is_valid():
             # This time we cannot commit straight away.
             # Not all fields are automatically populated!
             page = form.save(commit=False)

             # Retrieve the associated Category object so we can add it.
             cat = Category.objects.get(name=category_name)
             page.category = cat

             # Also, create a default value for the number of views.
             page.views = 0

             # With this, we can then save our new model instance.
             page.save()

             # Now that the page is saved, display the category instead.
             return category(request, category_name)
         else:
             print form.errors
     else:
         form = PageForm()

     return render_to_response( 'rango/add_page.html',
             {'category_name_url': category_name_url,
              'category_name': category_name, 'form': form},
              context)
