from django.shortcuts import render
from django.views import View
from .models import Genre, Book
from .forms import SearchForm, BookForm
from google.cloud import recaptchaenterprise_v1
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/credentials.json"

class Catalog(View):

    def get(self, request):
        books = Book.objects.all()
        genres = Genre.objects.all()
        form = SearchForm()
        return render(request, 'home.html', {'books': books, 'genres': genres, 'search_form': form})

class CreateBook(View):

    def get(self, request):
        form = BookForm()
        return render(request, 'create_book.html', {'form': form})

    def post(self, request):
        form = BookForm(request.POST)

        recaptcha_key = 'ваш_ключ_recaptcha'
        token = request.POST.get('g-recaptcha-response', '') 
        recaptcha_action = 'create_book'

        if not is_valid_recaptcha(recaptcha_key, token, recaptcha_action):
            form.add_error(None, 'reCAPTCHA verification failed. Please try again.')
            return render(request, 'create_book.html', {'form': form})

        if form.is_valid():
            form.save()
            return render(request, 'catalog/success.html')
        return render(request, 'create_book.html', {'form': form})

class DetailBook(View):

    def get(self, request, id):
        book = Book.objects.get(pk=id)
        return render(request, 'book.html', {'book': book})

def is_valid_recaptcha(recaptcha_key, token, recaptcha_action):
    client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()

    event = recaptchaenterprise_v1.Event()

    event.site_key = recaptcha_key
    event.token = token

    assessment = recaptchaenterprise_v1.Assessment()
    assessment.event = event

    project_id = '6Lcx5BApAAAAAAqVQs_9uk_zzOA2EXmDapzNG2HQ'  

    project_name = f"projects/{project_id}"

    request = recaptchaenterprise_v1.CreateAssessmentRequest()
    request.assessment = assessment
    request.parent = project_name

    try:
        response = client.create_assessment(request)

        if not response.token_properties.valid:
            print(
                "The CreateAssessment call failed because the token was "
                + "invalid for the following reasons: "
                + str(response.token_properties.invalid_reason)
            )
            return False

        if response.token_properties.action != recaptcha_action:
            print(
                "The action attribute in your reCAPTCHA tag does"
                + "not match the action you are expecting to score"
            )
            return False
        
        for reason in response.risk_analysis.reasons:
            print(reason)
        print(
            "The reCAPTCHA score for this token is: "
            + str(response.risk_analysis.score)
        )
        assessment_name = client.parse_assessment_path(response.name).get("assessment")
        print(f"Assessment name: {assessment_name}")

        return True

    except Exception as e:
        print(f"An error occurred during reCAPTCHA verification: {e}")
        return False