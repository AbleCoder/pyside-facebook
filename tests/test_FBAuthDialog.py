import sys
import unittest

from PySide.QtGui import QApplication
from PySide.QtGui import QWidget

from pyside_facebook import DEFAULT_REDIRECT_URI
from pyside_facebook import FBAuthDialog
from pyside_facebook import OAUTH_URL


# -------------------------------------------------------------------------
# CONSTANTS
# -------------------------------------------------------------------------

DEFAULT_OAUTH_PARAMS = {
    "app_id": None,
    "redirect_uri": DEFAULT_REDIRECT_URI,
    "scope": [],
    "state": None,
    "response_type": "token",
    "display": "page",
}


# -----------------------------------------------------------------------------
# TEST CASES
# -----------------------------------------------------------------------------

class FBAuthDialogTestCase(unittest.TestCase):

    # -------------------------------------------------------------------------
    # FIXTURES
    # -------------------------------------------------------------------------

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

        cls.parentWidget = QWidget()

    @classmethod
    def tearDownClass(cls):
        cls.parentWidget.destroy(True, True)
        cls.parentWidget = None

    # -------------------------------------------------------------------------
    # TEST HELPERS
    # -------------------------------------------------------------------------

    def helper_test_oauth_params(self, oauth_params, app_id=None,
            redirect_uri=DEFAULT_REDIRECT_URI, scope=[], state=None,
            response_type="token", display="page"):
        """
        Assert oauth_params dict matches kwarg values.

        @param (dict) oauth_params
        @param (str)  [app_id]
        @param (str)  [redirect_uri]
        @param (list) [scope]
        @param (str)  [state]
        @param (str)  [response_type]
        @param (str)  [display]
        """

        oauth_keys = ['app_id', 'redirect_uri', 'scope', 'state',
                      'response_type', 'display']

        # build dict of individual oauth param kwargs
        oauth_vals = {k: v for k, v in locals().iteritems() if k in oauth_keys}

        for k in oauth_keys:
            self.assertTrue(k in oauth_keys)
            self.assertEqual(oauth_params[k], oauth_vals[k])

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def test__instantiation(self):
        parentWidget = FBAuthDialogTestCase.parentWidget

        # test widget without parent or app_id
        fbAuthWidget = FBAuthDialog()

        self.assertIsNone(fbAuthWidget.parentWidget())
        self.assertIsNone(fbAuthWidget.oauth_params['app_id'])
        self.helper_test_oauth_params(fbAuthWidget.oauth_params)

        fbAuthWidget.destroy(True, True)
        fbAuthWidget = None

        # test widget with only parent and no app_id
        fbAuthWidget = FBAuthDialog(parentWidget)

        self.assertIs(parentWidget, fbAuthWidget.parentWidget())
        self.assertIsNone(fbAuthWidget.oauth_params['app_id'])

        fbAuthWidget.destroy(True, True)
        fbAuthWidget = None

        # test widget with parent and app_id
        fbAuthWidget = FBAuthDialog(parentWidget, "12345")

        self.assertIs(parentWidget, fbAuthWidget.parentWidget())
        self.assertEqual("12345", fbAuthWidget.oauth_params['app_id'])

        fbAuthWidget.destroy(True, True)
        fbAuthWidget = None

    # -------------------------------------------------------------------------

    def test_oauth_url(self):
        # setup widget to run tests on
        fbAuthWidget = FBAuthDialog(FBAuthDialogTestCase.parentWidget)

        self.assertEqual(DEFAULT_OAUTH_PARAMS, fbAuthWidget.oauth_params)




    """
    def test_default_size(self):
        self.assertEqual(self.widget.size(), (50,50),
                         'incorrect default size')

    def test_resize(self):
        self.widget.resize(100,150)
        self.assertEqual(self.widget.size(), (100,150),
                         'wrong size after resize')
    """

if __name__ == '__main__':
    unittest.main()
