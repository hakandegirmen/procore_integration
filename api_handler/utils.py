import requests
import json
from api_handler.models import PlatformUser
import time
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import status
from rest_framework.response import Response
import os


class Procore:
    base_urls = {
        'sandbox': "https://sandbox.procore.com",
        'app': 'https://app.procore.com'
    }

    base_url = base_urls['sandbox']

    client_id = 'fe61a88b5b137142c87f8a347228a413a7e5e931fc786c071457e7a6bb239acc'
    client_secret = 'f5b4d12d53d1fa699933e8967f07262a586724e2c3ca6a19234f97c9656317e2'


    environment = os.environ.get('PLATFORM', 'local')

    api_server_uris = {'local': 'http://127.0.0.1:8002',
                       'heroku': 'https://procore-integration-1.herokuapp.com'}

    api_server_uri = api_server_uris[environment]

    def get_authorization_url(self, user_uuid):
        # TODO: find another way to get user uuid (or another identifier)
        path = '/oauth/authorize?response_type=code&client_id=' + self.client_id + '&redirect_uri=http://' + self.api_server_uri + '/platform_users/receive_authorization/&state=' + user_uuid
        url = self.base_url + path

        print(url)

        return url

    def get_access_token(self, authorization_code):
        path = '/oauth/token'
        url = self.base_url + path

        data = {'code': authorization_code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.api_server_uri + '/platform_users/receive_authorization/'}

        headers = {'content-type': 'application/x-www-form-urlencoded'}

        response = requests.post(url,
                                 data=data,
                                 headers=headers)

        return json.loads(str(response.content, 'utf-8'))

    def refresh_access_token(self, user):
        refresh_token = user.refresh_token

        path = '/oauth/token'
        url = self.base_url + path

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }

        headers = {'content-type': 'application/x-www-form-urlencoded'}

        response = requests.post(url,
                                 data=data,
                                 headers=headers)

        return json.loads(str(response.content, 'utf-8'))

    def get_user_info(self, access_token):
        path = '/vapid/me'
        url = self.base_url + path

        headers = {'Authorization': 'Bearer ' + access_token,
                   'content-type': 'application/json'}

        response = requests.get(url,
                                headers=headers)

        return json.loads(str(response.content, 'utf-8'))

    def get_companies(self, user):
        path = '/vapid/companies'
        url = self.base_url + path

        headers = {'Authorization': 'Bearer ' + user.access_token,
                   'content-type': 'application/json'}

        response = requests.get(url,
                                headers=headers)

        return json.loads(str(response.content, 'utf-8'))

    def get_projects(self, user):
        company = user.company

        if company is None:
            raise ValueError('A company has not been linked for this user yet')

        company_id = company.procore_company_id
        path = '/vapid/projects?company_id=' + str(company_id)
        url = self.base_url + path

        headers = {'Authorization': 'Bearer ' + user.access_token,
                   'content-type': 'application/json'}

        response = requests.get(url,
                                headers=headers)
        return json.loads(str(response.content, 'utf-8'))

    def get_project(self, user, project):
        path = '/vapid/projects/{}?company_id={}'.format(project.procore_project_id, user.company.procore_company_id)
        url = self.base_url + path
        headers = {'Authorization': 'Bearer ' + user.access_token,
                   'content-type': 'application/json'}

        response = requests.get(url,
                                headers=headers)
        return json.loads(str(response.content, 'utf-8'))

    def access_token_expired(self, user):
        current_timestamp = int(time.time())

        if current_timestamp - user.access_token_created_at > user.access_token_expires_in:
            return True

        return False
