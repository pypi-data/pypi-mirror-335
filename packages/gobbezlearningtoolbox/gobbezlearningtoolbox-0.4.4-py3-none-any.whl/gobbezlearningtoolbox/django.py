from .print_fonts import PrintFonts


class Django():
    def help(self):
        """Get all methods with descriptions"""
        pf = PrintFonts()
        text = f"""
        ## DJANGO
        ! Here you can find how to quickly setup your own Django backend

        # Imports:
        -imports_project() = Most common imports for your main project
        -imports_application() = Find the most common imports to use in your applications 

        # Configuration Examples:
        -example_main_urls() = Example of Urls of the main project
        -example_model() = Example of Model for your application
        -example_view() = Example of View for your application
        -example_urls() = Example of Urls for your application
        
        # Settings and Commands:
        -settings() = Django settings file explanations
        -commands() = Most important Django commands
        """
        pf.format(text)

    def imports_project(self):
        """Write main project imports"""
        pf = PrintFonts()

        text = f"""
        ## MOST USED IMPORTS FOR THE MAIN DJANGO PROJECT

        ## Urls
        from django.contrib import admin
        from django.urls import path, include
        """
        pf.format(text)

    def imports_application(self):
        """Write applications imports"""
        pf = PrintFonts()

        text = f"""
        ## MOST USED IMPORTS FOR YOUR DJANGO APPLICATIONS

        ## Models
        from django.db import models
        
        ## Views
        from django.http import JsonResponse
        from django.views import View
        from django.utils.decorators import method_decorator
        from django.views.decorators.csrf import csrf_exempt
        from .models import ExampleModel
        import json
        
        ## Urls
        from django.urls import path
        from .views import ExampleView
        """
        pf.format(text)

    def example_model(self):
        """Example code for your Model application"""
        pf = PrintFonts()

        text = """  
        ## EXAMPLE MODEL FOR YOUR APPLICATION

        from django.db import models

        # Example table model
        class ExampleModel(models.Model):
            text = models.CharField(max_length=30)
            number = models.IntegerField()
        
            class Meta:
                # Create unique constraints
                constraints = [
                    models.UniqueConstraint(fields=['text', 'number'], name='unique_text_number')
                ]
        """
        pf.format(text)

    def example_view(self):
        """Example code for your View application"""
        pf = PrintFonts()

        text = """  
        ## EXAMPLE VIEW FOR YOUR APPLICATION

        from django.http import JsonResponse
        from django.views import View
        from django.utils.decorators import method_decorator
        from django.views.decorators.csrf import csrf_exempt
        from .models import Example
        import json
        
        class ExampleView(View):
            @method_decorator(csrf_exempt)
            def dispatch(self, *args, **kwargs):
                # Use csrf_exampt to enable post methods from other sources
                return super().dispatch(*args, **kwargs)
        
            def get(self, request):
                # This method is used to select all or one row(s)
                data = json.loads(request.body.decode('utf-8'))
                input_id = data.get('input_id')
        
                if input_id is None:
                    # Select all records
                    all_records = Example.objects.values()
                    return JsonResponse({"Example table results": list(all_records)})
                else:
                    # Select one record
                    try:
                        one_record = Example.objects.get(id=input_id)
                        return JsonResponse(
                            {"Example": {"id": one_record.id, "text": one_record.text, "number": one_record.number}})
                    except Example.DoesNotExist:
                        return JsonResponse({"error": "Record not found"}, status=404)
        
            @csrf_exempt
            def post(self, request):
                # This method (requires csrf_exempt to enable different origins of calls) is used to add a new row in the table (Postman is fine)
                try:
                    data = json.loads(request.body.decode('utf-8'))
                    input_text = data.get("text")
                    input_number = data.get("number")
        
                    if not input_text or input_number is None:
                        return JsonResponse({"error": "Missing fields"}, status=400)
        
                    Example.objects.create(text=input_text, number=input_number)
                    return JsonResponse({"success": "You have added a new row in the Example table!"}, status=200)
                except json.JSONDecodeError:
                    return JsonResponse({"error": f"Invalid JSON, {request}"}, status=400)
                except Exception as e:
                    return JsonResponse({"error": f"Failed to add a new row: {str(e)}"}, status=500)
        
            @csrf_exempt
            def put(self, request):
                # This method is called to update a row
                try:
                    data = json.loads(request.body.decode('utf-8'))
                    input_id = data.get("input_id")
                    input_text = data.get("text")
                    input_number = data.get("number")
                    one_record = Example.objects.get(id=input_id)
        
                    if input_text == None and input_number == None:
                        return JsonResponse({"error": f"Invalid JSON, {request}"}, status=400)
                    if input_text:
                        one_record.text = input_text
                        one_record.save()
                    if input_number:
                        one_record.number = input_number
                        one_record.save()
                    return JsonResponse({"success": "You have updated a row in the Example table!"}, status=200)
                except Exception as e:
                    return JsonResponse({"error": f"Failed to update a row: {str(e)}"}, status=500)
        
            @csrf_exempt
            def delete(self, request):
                # This method is used to delete a row in the table
                try:
                    data = json.loads(request.body.decode('utf-8'))
                    input_id = data.get("input_id")
                    one_record = Example.objects.get(id=input_id)
                    one_record.delete()
                    return JsonResponse({"success": "You have deleted a row in the Example table!"}, status=200)
                except Exception as e:
                    return JsonResponse({"error": f"Failed to delete a row: {str(e)}"}, status=500)
        """
        pf.format(text)

    def example_urls(self):
        """Example code for your Urls application"""
        pf = PrintFonts()

        text = """  
        ## EXAMPLE URLS FOR YOUR APPLICATION

        from django.urls import path
        from .views import ExampleView
        
        urlpatterns = [
            path('exampleselect/', ExampleView.as_view(), name='select'),
            path('examplecreate/', ExampleView.as_view(), name='create'),
            path('exampleupdate/', ExampleView.as_view(), name='update'),
            path('exampledelete/', ExampleView.as_view(), name='delete'),
        ]
        """
        pf.format(text)

    def example_main_urls(self):
        """Example code for main project Urls"""
        pf = PrintFonts()

        text = """  
        ## EXAMPLE URLS FOR MAIN PROJECT

        from django.contrib import admin
        from django.urls import path, include
        
        urlpatterns = [
            path('admin/', admin.site.urls),
            path('', include('exampleapplication.urls')),
        ]
        """
        pf.format(text)

    def settings(self):
        """Example code for Django settings file"""
        pf = PrintFonts()

        text = """  
        ## DESCRIPTIONS FOR SETTINGS FILE

        ## SECRET_KEY
        # Store the Django secret key in another file and don't push it on Github!
        from YourMainProject import secretkeys
        SECRET_KEY = secretkeys.SECRET_KEY
        
        ## INSTALLED_APPS
        # Add all your applications below
        INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'exampleapplication',
        ]
        """
        pf.format(text)

    def commands(self):
        """Most important Django commands"""
        pf = PrintFonts()

        text = """  
        ## MOST IMPORTANT DJANGO SHELL COMMANDS

        ## CREATE MAIN PROJECT
        # Create the main folders of your Django project, where you can run the server and configurations
        ! Run this from the (venv) Python shell, in the folder that you want to use  
        $ django-admin startproject exampleproject
        
        ## CREATE APPLICATION(S)
        # Create your applications to modify models, views, templates and logic
        ! Run this from the (venv) Python shell, in the folder of the manage.py (after the project has been created)
        $ python manage.py startapp exampleapplication
        
        ## RUN SERVER  
        # Run the backend server
        ! Run this from the (venv) Python shell, in the folder of the manage.py (after the project has been created)
        $ python manage.py runserver
        
        ## CREATE MIGRATIONS
        # Create Database table(s)
        ! Run this from the (venv) Python shell, in the folder of the manage.py (after you have created a table in your application(s) and added it in the settings.py file)
        $ python manage.py makemigrations
        $ python manage.py migrate
        """
        pf.format(text)