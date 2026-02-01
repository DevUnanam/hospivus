from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from health_tech.models import MedicalCondition


class MedicalConditionModelTest(TestCase):
    """Test cases for the MedicalCondition model"""
    
    def setUp(self):
        self.condition = MedicalCondition.objects.create(
            name='Test Condition',
            department='cardiology',
            overview='This is a test condition overview.',
            symptoms='Test symptoms include fatigue and pain.',
            causes='Test causes include genetics and lifestyle.',
            treatments='Test treatments include medication and therapy.'
        )

    def test_condition_creation(self):
        """Test that a medical condition is created properly"""
        self.assertEqual(self.condition.name, 'Test Condition')
        self.assertEqual(self.condition.department, 'cardiology')
        self.assertTrue(self.condition.overview)
        self.assertTrue(self.condition.symptoms)
        self.assertTrue(self.condition.causes)
        self.assertTrue(self.condition.treatments)

    def test_slug_generation(self):
        """Test that slug is automatically generated"""
        self.assertEqual(self.condition.slug, 'test-condition')

    def test_first_letter_property(self):
        """Test the first_letter property"""
        self.assertEqual(self.condition.first_letter, 'T')

    def test_department_display_property(self):
        """Test the department_display property"""
        self.assertEqual(self.condition.department_display, 'Cardiology')

    def test_get_absolute_url(self):
        """Test the get_absolute_url method"""
        url = self.condition.get_absolute_url()
        expected_url = reverse('health_tech:condition_detail', kwargs={'slug': self.condition.slug})
        self.assertEqual(url, expected_url)

    def test_string_representation(self):
        """Test the __str__ method"""
        self.assertEqual(str(self.condition), 'Test Condition')

    def test_get_related_conditions(self):
        """Test the get_related_conditions method"""
        # Create another condition in the same department
        related_condition = MedicalCondition.objects.create(
            name='Related Test Condition',
            department='cardiology',
            overview='Related condition overview.',
            symptoms='Related symptoms.',
            causes='Related causes.',
            treatments='Related treatments.'
        )
        
        related = self.condition.get_related_conditions()
        self.assertIn(related_condition, related)
        self.assertNotIn(self.condition, related)


class ConditionsViewTest(TestCase):
    """Test cases for the conditions views"""
    
    def setUp(self):
        self.client = Client()
        self.condition = MedicalCondition.objects.create(
            name='Asthma',
            department='pulmonology',
            overview='Asthma is a respiratory condition.',
            symptoms='Wheezing, shortness of breath.',
            causes='Allergies, genetics.',
            treatments='Inhalers, medications.'
        )

    def test_conditions_index_view(self):
        """Test the conditions index page"""
        url = reverse('health_tech:conditions_index')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Medical Conditions A-Z Index')
        self.assertContains(response, 'A')  # Should show alphabet letters

    def test_conditions_by_letter_view(self):
        """Test the conditions by letter page"""
        url = reverse('health_tech:conditions_by_letter', kwargs={'letter': 'a'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Asthma')
        self.assertContains(response, 'Conditions Starting with "A"')

    def test_conditions_by_letter_invalid_letter(self):
        """Test invalid letter returns 404"""
        url = reverse('health_tech:conditions_by_letter', kwargs={'letter': '1'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)

    def test_condition_detail_view(self):
        """Test the condition detail page"""
        url = reverse('health_tech:condition_detail', kwargs={'slug': self.condition.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Asthma')
        self.assertContains(response, 'Overview')
        self.assertContains(response, 'Signs & Symptoms')
        self.assertContains(response, 'Causes & Risk Factors')
        self.assertContains(response, 'Treatment & Management')

    def test_condition_detail_not_found(self):
        """Test condition detail with invalid slug returns 404"""
        url = reverse('health_tech:condition_detail', kwargs={'slug': 'non-existent-condition'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)

    def test_search_conditions_view(self):
        """Test the search functionality"""
        url = reverse('health_tech:search_conditions')
        response = self.client.get(url, {'q': 'asthma'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Asthma')
        self.assertContains(response, 'Search Results')

    def test_search_conditions_empty_query(self):
        """Test search with empty query"""
        url = reverse('health_tech:search_conditions')
        response = self.client.get(url, {'q': ''})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search Medical Conditions')

    def test_search_no_results(self):
        """Test search with no matching results"""
        url = reverse('health_tech:search_conditions')
        response = self.client.get(url, {'q': 'nonexistentcondition'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No conditions found')