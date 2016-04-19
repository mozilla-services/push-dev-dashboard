from django.test import TestCase

from push.templatetags.timetags import print_api_timestamp


class PrintAPITimestampTestCase(TestCase):
    def test_e_notation_values(self):
        timestamp = 1461082276312460000
        printed_datetime = print_api_timestamp(timestamp)
        self.assertEqual((2016, 4, 19), (printed_datetime.year,
                                         printed_datetime.month,
                                         printed_datetime.day))
