import json

from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase

from . import querybuilder
from .models import Author


class EndpointTest(TestCase):

    def setUp(self):
        self.view = querybuilder.Endpoint.as_view()
        self.factory = RequestFactory()

    def test_no_filter(self):
        Author.objects.create(name='name', birth_date='2016-05-23')
        request = self.factory.post('myurl', {'widget_id': 'author-table'})
        response = self.view(request)
        content = json.loads(response.content.decode())
        self.assertEqual(content['status'], 'OK')
        self.assertEqual(len(content['data']), 1)
        row = content['data'][0]
        self.assertEqual(row['0'], 'name')
        self.assertEqual(row['1'], '2016-05-23')

    def test_no_widget(self):
        request = self.factory.post('myurl',
                                    {'widget_id': 'non-existing-table'})
        response = self.view(request)
        content = json.loads(response.content.decode())
        self.assertEqual(content['status'], 'WIDGET_NOT_FOUND')

    def test_endpoint_forbidden(self):
        class ForbiddenTable(querybuilder.Table):
            name = "forbidden"

            def is_accessible(self, request):
                return False

        querybuilder.Endpoint.register(ForbiddenTable)

        response = self.client.post(reverse("example-endpoint"),
                                    data={"widget_id": "forbidden"})
        self.assertEqual(response.status_code, 403)
