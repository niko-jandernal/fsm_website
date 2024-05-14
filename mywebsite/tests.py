# tests.py
from django.test import TestCase, Client
from django.urls import reverse
from .models import Poll
from .forms import PollForm
from .views import home, create_poll, news
from django.urls import resolve


class SimpleTest(TestCase):
    def setUp(self):
        # Setup run before every test method.
        self.client = Client()


class ModelTestCase(TestCase):
    def test_model_creation(self):
        # Assuming you have a model named Poll with a title field
        poll = Poll.objects.create(title="Sample Poll")
        self.assertIsInstance(poll, Poll)
        self.assertEqual(poll.question, "Sample Poll")


class ViewTestCase(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_poll_creation_page(self):
        response = self.client.get(reverse('create_poll'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(response, 'create_poll.html')

    def test_news_page(self):
        response = self.client.get(reverse('news'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news.html')


class FormTestCase(TestCase):
    def test_valid_form(self):
        data = {'name': 'Test Poll', 'choices': ['Option 1', 'Option 2']}
        form = PollForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = PollForm(data={})
        self.assertFalse(form.is_valid())


class URLTestCase(TestCase):
    def test_url_resolves(self):
        resolver = resolve('/news')
        self.assertEqual(resolver.view_name, 'news')

class PollModelTest(TestCase):
    def setUp(self):
        Poll.objects.create(title="Sample Poll")

    def test_poll_creation(self):
        poll = Poll.objects.get(title="Sample Poll")
        self.assertTrue(isinstance(poll, Poll))
        self.assertEqual(poll.title, "Sample Poll")