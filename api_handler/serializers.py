from rest_framework import serializers
from api_handler.models import Project, PlatformUser, Company


class PlatformUserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="platform_users-detail", lookup_field='uuid')
    company = serializers.HyperlinkedRelatedField(
        view_name='companies-detail',
        allow_null=True,
        queryset=Company.objects.all(),
        lookup_field='uuid')

    class Meta:
        model = PlatformUser
        fields = '__all__'


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="companies-detail", lookup_field='uuid')
    projects = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='projects-detail',
        allow_null=True,
        read_only=True,
        lookup_field='uuid')

    platformusers = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='platform_users-detail',
        allow_null=True,
        read_only=True,
        lookup_field='uuid')

    class Meta:
        model = Company
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="projects-detail", lookup_field='uuid')
    company = serializers.HyperlinkedRelatedField(
        view_name='companies-detail',
        allow_null=True,
        queryset=Company.objects.all(),
        lookup_field='uuid')

    class Meta:
        model = Project
        fields = '__all__'
