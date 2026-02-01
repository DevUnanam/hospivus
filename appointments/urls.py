from django.urls import path
from appointments import views

app_name = "appointments"

urlpatterns = [
    path('appointments/', views.AppointmentsView.as_view(), name='appointments'),
    path('doctors/', views.FindDoctorView.as_view(), name='doctors'),
    path('manage/appointments/', views.ManageAppointmentsView.as_view(), name='manage_schedule'),
    # path('manage/appointments/<int:appointment_id>/', views.ManageAppointmentDetailView.as_view(), name='manage_appointment_detail'),
    # path('book/appointment/<int:doctor_id>/', views.BookAppointmentView.as_view(), name='book_appointment'),
    # path('cancel/appointment/<int:appointment_id>/', views.CancelAppointmentView.as_view(), name='cancel_appointment'),
    # path('reschedule/appointment/<int:appointment_id>/', views.RescheduleAppointmentView.as_view(), name='reschedule_appointment'),
]