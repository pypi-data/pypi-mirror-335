import logging

from django.conf import settings
from django.http import Http404
from django.views.generic import UpdateView

from rdmo.core.views import ObjectPermissionMixin, RedirectViewMixin
from rdmo.questions.models import Catalog
from rdmo.tasks.models import Task
from rdmo.views.models import View

from ..forms import (
    ProjectForm,
    ProjectUpdateCatalogForm,
    ProjectUpdateInformationForm,
    ProjectUpdateParentForm,
    ProjectUpdateTasksForm,
    ProjectUpdateViewsForm,
    ProjectUpdateVisibilityForm,
)
from ..mixins import ProjectImportMixin
from ..models import Project

logger = logging.getLogger(__name__)


class ProjectUpdateView(ObjectPermissionMixin, RedirectViewMixin, UpdateView):
    model = Project
    queryset = Project.objects.all()
    form_class = ProjectForm
    permission_required = 'projects.change_project_object'

    def get_form_kwargs(self):
        catalogs = Catalog.objects.filter_current_site() \
                                  .filter_group(self.request.user) \
                                  .filter_availability(self.request.user)
        projects = Project.objects.filter_user(self.request.user)

        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({
            'catalogs': catalogs,
            'projects': projects
        })
        return form_kwargs


class ProjectUpdateInformationView(ObjectPermissionMixin, RedirectViewMixin, UpdateView):
    model = Project
    queryset = Project.objects.all()
    form_class = ProjectUpdateInformationForm
    permission_required = 'projects.change_project_object'


class ProjectUpdateVisibilityView(ObjectPermissionMixin, RedirectViewMixin, UpdateView):
    model = Project
    queryset = Project.objects.all()
    form_class = ProjectUpdateVisibilityForm
    permission_required = 'projects.change_visibility_object'
    template_name = 'projects/project_form_visibility.html'


class ProjectUpdateCatalogView(ObjectPermissionMixin, RedirectViewMixin, UpdateView):
    model = Project
    queryset = Project.objects.all()
    form_class = ProjectUpdateCatalogForm
    permission_required = 'projects.change_project_object'

    def get_form_kwargs(self):
        catalogs = Catalog.objects.filter_current_site() \
                                  .filter_group(self.request.user) \
                                  .filter_availability(self.request.user)

        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({
            'catalogs': catalogs
        })
        return form_kwargs


class ProjectUpdateTasksView(ObjectPermissionMixin, RedirectViewMixin, UpdateView):
    model = Project
    queryset = Project.objects.all()
    form_class = ProjectUpdateTasksForm
    permission_required = 'projects.change_project_object'

    def dispatch(self, request, *args, **kwargs):
        if settings.PROJECT_TASKS_SYNC:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        tasks = Task.objects.filter_for_project(self.object).filter_availability(self.request.user)
        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({
            'tasks': tasks
        })
        return form_kwargs

    def get_success_url(self):
        return self.get_object().get_absolute_url()


class ProjectUpdateViewsView(ObjectPermissionMixin, RedirectViewMixin, UpdateView):
    model = Project
    queryset = Project.objects.all()
    form_class = ProjectUpdateViewsForm
    permission_required = 'projects.change_project_object'

    def dispatch(self, request, *args, **kwargs):
        if settings.PROJECT_VIEWS_SYNC:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        views = View.objects.filter_for_project(self.object).filter_availability(self.request.user)
        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({
            'views': views
        })
        return form_kwargs

    def get_success_url(self):
        return self.get_object().get_absolute_url()


class ProjectUpdateParentView(ObjectPermissionMixin, RedirectViewMixin, UpdateView):
    model = Project
    queryset = Project.objects.all()
    form_class = ProjectUpdateParentForm
    permission_required = 'projects.change_project_object'

    def get_form_kwargs(self):
        projects = Project.objects.filter_user(self.request.user)

        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({
            'projects': projects
        })
        return form_kwargs


class ProjectUpdateImportView(ProjectImportMixin, ObjectPermissionMixin, RedirectViewMixin, UpdateView):
    model = Project
    queryset = Project.objects.all()
    permission_required = 'projects.import_project_object'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if kwargs.get('format') is None:
            return self.import_form()
        else:
            return self.get_import_plugin(self.kwargs.get('format'), self.object).render()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        method = request.POST.get('method')
        if method in ['upload_file', 'import_file', 'import_project']:
            return getattr(self, method)()
        else:
            return self.get_import_plugin(self.kwargs.get('format'), self.object).submit()
