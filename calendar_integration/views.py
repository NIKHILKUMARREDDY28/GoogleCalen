from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_calendar_integration.settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

# Step 1: GoogleCalendarInitView
class GoogleCalendarInitView(View):
    def get(self, request):
        # Set up OAuth2 flow
        flow = Flow.from_client_secrets_file(
            'path/to/client_secrets.json',  # Replace with the path to your client_secrets.json file
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri(reverse('google-calendar-redirect'))
        )

        # Generate the authorization URL
        authorization_url, _ = flow.authorization_url(prompt='consent')

        # Store the OAuth2 state in the session for security
        request.session['google_auth_state'] = flow.authorization_response['state']
        request.session.modified = True

        # Redirect the user to the Google authentication page
        return HttpResponseRedirect(authorization_url)


# Step 2: GoogleCalendarRedirectView
class GoogleCalendarRedirectView(View):
    def get(self, request):
        # Retrieve the OAuth2 state from the session for security validation
        stored_state = request.session.pop('google_auth_state', None)
        if stored_state is None or stored_state != request.GET.get('state'):
            return HttpResponseRedirect(reverse('google-calendar-init'))

        # Set up OAuth2 flow
        flow = Flow.from_client_secrets_file(
            'path/to/client_secrets.json',  # Replace with the path to your client_secrets.json file
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri(reverse('google-calendar-redirect'))
        )

        # Exchange the authorization code for an access token
        flow.fetch_token(
            authorization_response=request.build_absolute_uri(),
            client_secret=GOOGLE_CLIENT_SECRET
        )

        # Create credentials from the access token
        credentials = flow.credentials

        # Create a service object for the Google Calendar API
        service = build('calendar', 'v3', credentials=credentials)

        # Retrieve the list of events from the user's calendar
        events = service.events().list(calendarId='primary').execute()

        

        return ...
