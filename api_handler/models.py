from django.db import models


# Create your models here.

class Company(models.Model):
    class Meta:
        verbose_name_plural = 'Companies'

    uuid = models.UUIDField(unique=True)
    name = models.CharField(max_length=64, null=True)

    # procore properties
    procore_company_id = models.CharField(max_length=20, null=True)

    def __str__(self):
        return str(self.name)


class Project(models.Model):
    class Meta:
        verbose_name_plural = 'Projects'

    uuid = models.UUIDField(unique=True)
    name = models.CharField(max_length=64, null=True)
    active = models.BooleanField(default=True)

    # procore properties
    procore_project_id = models.CharField(max_length=20)

    # foreign keys
    company = models.ForeignKey(Company, related_name='projects', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.name)


class PlatformUser(models.Model):
    class Meta:
        verbose_name_plural = 'PlatformUsers'

    uuid = models.UUIDField(unique=True)
    name = models.CharField(max_length=64, null=True)

    # procore properties
    procore_user_id = models.CharField(max_length=20, null=True)

    access_token = models.CharField(max_length=500, null=True)
    refresh_token = models.CharField(max_length=500, null=True)
    access_token_expires_in = models.IntegerField(null=True)
    access_token_created_at = models.IntegerField(null=True)

    # foreign keys
    company = models.ForeignKey(Company, related_name='platformusers', on_delete=models.CASCADE, null=True)
    projects = models.ManyToManyField(Project)

    def __str__(self):
        return str(self.name)


class Report(models.Model):
    class Meta:
        verbose_name_plural = 'Reports'

    procore_id = models.CharField(max_length=20, null=True)
    sensor_uuid = models.UUIDField(null=True)
    url = models.URLField(null=True)

    # foreign keys
    project = models.ForeignKey(Project, related_name='reports', on_delete=models.CASCADE, null=True)