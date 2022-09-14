from django.test import TestCase
from django.shortcuts import reverse


class LandingPageTest(TestCase):

    def test_get(self):
        response = self.client.get(reverse("landing-page"))
        self.assertEqual(response.status_code,
                         200)  # check 'response.status_code' is equal is 200, if it is not it got an error
        self.assertTemplateUsed(response, "landing_page.html")  # check the name of the template is equal to response


class LeadListPageTest(TestCase):

    def test(self):
        response = self.client.get(reverse("leads:lead-list"))
        self.assertEqual(response.status_code,
                         201)  # check 'response.status_code' is equal is 200, if it is not it got an error
        self.assertTemplateUsed(response, "leads/lead_list.html")