from django.http import HttpResponse, HttpResponseRedirect
import uuid as uuid_type
from api_handler.utils import *

from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action

from api_handler.models import PlatformUser, Project, Company
from api_handler.serializers import PlatformUserSerializer, ProjectSerializer, CompanySerializer

procore = Procore()


class PlatformUserViewSet(viewsets.ModelViewSet):
    queryset = PlatformUser.objects.all()
    serializer_class = PlatformUserSerializer
    lookup_field = 'uuid'

    def get_object(self):
        return get_object_or_404(PlatformUser, uuid=self.kwargs['uuid'])

    # methods for procore api calls
    @action(detail=True, methods=['get'])
    def redirect_to_authorization(self, request, uuid):
        return HttpResponseRedirect(redirect_to=procore.get_authorization_url(uuid))

    @action(detail=False, methods=['get'])
    def receive_authorization(self, request):
        code = request.query_params['code']
        uuid = request.query_params['state']

        # uuid = uuid_type.UUID(uuid)
        token_data = procore.get_access_token(code)

        self.create_or_update_user(uuid, token_data)

        return Response('authorization successful', status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def get_procore_companies(self, request, uuid):
        user = self.get_user_with_valid_token(uuid)

        return Response(procore.get_companies(user), status=status.HTTP_200_OK, content_type='application/json')


    @action(detail=True, methods=['get'])
    def get_procore_projects(self, request, uuid):
        user = self.get_user_with_valid_token(uuid)

        try:
            return Response(procore.get_projects(user), status=status.HTTP_200_OK, content_type='application/json')

        except ValueError as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)

    # methods to modify database
    @action(detail=True, methods=['post'])
    def create_or_link_company(self, request, uuid):
        data = request.data
        company_uuid = data['company_uuid']
        company_name = data['company_name']
        procore_company_id = data['procore_company_id']
        user_uuid = uuid

        try:
            user = PlatformUser.objects.get(uuid=user_uuid)
            try:
                company = Company.objects.get(uuid=company_uuid)
                user.company = company
                user.save()
                return Response('Company successfully linked', status=status.HTTP_200_OK)
            except Company.DoesNotExist:
                company = Company.objects.create(uuid=company_uuid,
                                                 name=company_name,
                                                 procore_company_id=procore_company_id)
                user.company = company
                user.save()
                return Response('Company successfully created and linked', status=status.HTTP_200_OK)

        except PlatformUser.DoesNotExist:
            return Response('User not found', status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def create_and_link_projects(self, request, uuid):
        data = request.data
        projects = data['projects']
        user_uuid = uuid
        try:
            user = PlatformUser.objects.get(uuid=user_uuid)
            company = user.company
            if company is None:
                return Response('A company has not been linked to this user yet', status=status.HTTP_400_BAD_REQUEST)
            for project in projects:
                try:
                    Project.objects.get(uuid=project['project_uuid'])
                except Project.DoesNotExist:
                    Project.objects.create(uuid=project['project_uuid'],
                                           name=project['project_name'],
                                           procore_project_id=project['procore_project_id'],
                                           company=company)

            return Response('Projects successfully created and linked', status=status.HTTP_200_OK)

        except PlatformUser.DoesNotExist:
            return Response('User not found', status=status.HTTP_400_BAD_REQUEST)

    # helper methods
    @staticmethod
    def create_or_update_user(uuid, token_data):
        access_token = token_data['access_token']
        expires_in = token_data['expires_in']
        refresh_token = token_data['refresh_token']
        created_at = token_data['created_at']

        try:
            user = PlatformUser.objects.get(uuid=uuid)
            user.access_token = access_token
            user.access_token_expires_in = expires_in
            user.refresh_token = refresh_token
            user.access_token_created_at = created_at
            user.save()

        except PlatformUser.DoesNotExist:
            user_info = procore.get_user_info(access_token)
            procore_id = user_info['id']
            PlatformUser.objects.create(uuid=uuid,
                                        access_token=access_token,
                                        access_token_expires_in=expires_in,
                                        refresh_token=refresh_token,
                                        access_token_created_at=created_at,
                                        procore_user_id=procore_id)
        return

    @staticmethod
    def get_user_with_valid_token(uuid):
        try:
            user = PlatformUser.objects.get(uuid=uuid)
            if procore.access_token_expired(user):
                token_data = procore.refresh_access_token(user)
                __class__.create_or_update_user(uuid, token_data)
                user.refresh_from_db()
            return user

        except PlatformUser.DoesNotExist:
            return HttpResponseRedirect(redirect_to=procore.get_authorization_url(uuid))


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    lookup_field = 'uuid'

    def get_object(self):
        return get_object_or_404(Company, uuid=self.kwargs['uuid'])


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'uuid'

    def get_object(self):
        return get_object_or_404(Project, uuid=self.kwargs['uuid'])

    @action(detail=True, methods=['get'])
    def get_procore_project(self, request, uuid):
        user_uuid = request.query_params['user_uuid']
        user = PlatformUserViewSet.get_user_with_valid_token(user_uuid)
        project = self.get_object()
        procore.get_project(user, project)
        return Response(procore.get_project(user, project), status=status.HTTP_200_OK, content_type='application/json')





































