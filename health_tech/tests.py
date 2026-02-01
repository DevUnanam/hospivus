from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import MedicalCondition

User = get_user_model()


class MedicalConditionModelTest(TestCase):
    """Test cases for the MedicalCondition model"""
    
    def setUp(self):
        self.condition = MedicalCondition.objects.create(
            name='Test Condition',
            overview='Test overview',
            symptoms='Test symptoms',
            causes='Test causes',
            treatments='Test treatments',
            department='cardiology'
        )
    
    def test_string_representation(self):
        """Test the string representation of the model"""
        self.assertEqual(str(self.condition), 'Test Condition')
    
    def test_slug_generation(self):
        """Test that slug is automatically generated"""
        self.assertEqual(self.condition.slug, 'test-condition')
    
    def test_first_letter_property(self):
        """Test the first_letter property"""
        self.assertEqual(self.condition.first_letter, 'T')
    
    def test_absolute_url(self):
        """Test get_absolute_url method"""
        expected_url = reverse('health_tech:condition_detail', kwargs={'slug': self.condition.slug})
        self.assertEqual(self.condition.get_absolute_url(), expected_url)
    
    def test_department_display(self):
        """Test department display property"""
        self.assertEqual(self.condition.department_display, 'Cardiology')


class HealthTechViewsTest(TestCase):
    """Test cases for health_tech views"""
    
    def setUp(self):
        self.client = Client()
        self.condition = MedicalCondition.objects.create(
            name='Asthma',
            overview='A respiratory condition',
            symptoms='Shortness of breath, wheezing',
            causes='Allergies, genetics',
            treatments='Inhalers, medications',
            department='pulmonology'
        )
    
    def test_conditions_index_view(self):
        """Test the A-Z conditions index view"""
        response = self.client.get(reverse('health_tech:conditions_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Medical Conditions A-Z Index')
        self.assertContains(response, 'A')  # Should contain letters
    
    def test_conditions_by_letter_view(self):
        """Test the conditions by letter view"""
        response = self.client.get(reverse('health_tech:conditions_by_letter', kwargs={'letter': 'a'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Asthma')
    
    def test_condition_detail_view(self):
        """Test the condition detail view"""
        response = self.client.get(
            reverse('health_tech:condition_detail', kwargs={'slug': self.condition.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Asthma')
        self.assertContains(response, 'A respiratory condition')
    
    def test_search_conditions_view(self):
        """Test the search conditions view"""
        response = self.client.get(reverse('health_tech:search_conditions'), {'q': 'asthma'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Asthma')
    
    def test_invalid_letter_404(self):
        """Test that invalid letters return 404"""
        response = self.client.get(reverse('health_tech:conditions_by_letter', kwargs={'letter': '1'}))
        self.assertEqual(response.status_code, 404)