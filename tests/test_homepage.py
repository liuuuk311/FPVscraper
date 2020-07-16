import unittest

from tests.functional import FunctionalTestCase


class HomePageTestCase(FunctionalTestCase):

    def test_search_item_and_show_prices_from_different_stores(self):
        # A user has heard about a new FPV website.

        # He loads up the homepage
        self.browser.get('http://localhost:8000')

        # And he notices the page title and header mention FPV Shopping list
        self.assertIn('FPV Shopping list', self.browser.title)

        # He is invited to search for an item on the search box

        # He types "Fatshark HDO V2" into the search box

        # When he hit enter, he get redirected in the comparison page

        # Here he can see 3 columns, one for each online store: GetFPV.com, RaceDayQuad.com and Banggood.com

        # Each column displays a product that matched the query.

        # Each item has a name, a description, a price and a link

        # By clicking the link the user should be redirected in a new tab to the store

        # The product with the lowest price is highlighted

        # Now he knows which shop has the lowest price


if __name__ == '__main__':
    unittest.main()
