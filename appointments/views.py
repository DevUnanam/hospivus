from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class FindDoctorView(TemplateView):
    """Find doctor view for the app"""

    template_name = "find_doctor.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


@method_decorator(login_required, name='dispatch')
class AppointmentsView(TemplateView):
    """Appointments view for the app"""

    template_name = "appointments.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


@method_decorator(login_required, name='dispatch')
class ManageAppointmentsView(TemplateView):
    """Manage appointments view for the app"""

    template_name = "manage_appointments.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context
