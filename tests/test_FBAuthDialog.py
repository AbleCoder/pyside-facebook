import sys
import unittest

from PySide.QtGui import QApplication
from PySide.QtGui import QWidget

from pyside_facebook import DEFAULT_REDIRECT_URI
from pyside_facebook import FBAuthDialog
from pyside_facebook import FBAuthDialogInvalidParamException
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
        fbad = FBAuthDialog()

        self.assertIsNone(fbad.parentWidget())
        self.assertIsNone(fbad.oauth_params['app_id'])
        self.helper_test_oauth_params(fbad.oauth_params)

        fbad.destroy(True, True)
        fbad = None

        # test widget with only parent and no app_id
        fbad = FBAuthDialog(parentWidget)

        self.assertIs(parentWidget, fbad.parentWidget())
        self.assertIsNone(fbad.oauth_params['app_id'])

        fbad.destroy(True, True)
        fbad = None

        # test widget with parent and app_id
        fbad = FBAuthDialog(parentWidget, "12345")

        self.assertIs(parentWidget, fbad.parentWidget())
        self.assertEqual("12345", fbad.oauth_params['app_id'])

        fbad.destroy(True, True)
        fbad = None

    # -------------------------------------------------------------------------

    def test_oauth_url(self):
        # setup widget to run tests on
        fbad = FBAuthDialog(FBAuthDialogTestCase.parentWidget)

        # test default oauth_params WITH OUT app_id
        oauth_params = DEFAULT_OAUTH_PARAMS.copy()

        with self.assertRaises(FBAuthDialogInvalidParamException):
            fbad.oauth_url(**oauth_params)

        # test default oauth_params
        oauth_params = DEFAULT_OAUTH_PARAMS.copy()
        oauth_params['app_id'] = "TEST_APP_ID"

        fbad_oauth_url = str(fbad.oauth_url(**oauth_params))
        test_oauth_url = "%s?%s" % (OAUTH_URL, "&".join([
            "client_id=TEST_APP_ID",
            "redirect_uri=http://www.facebook.com/connect/login_success.html",
            "response_type=token",
            "display=page"]))

        self.assertEqual(test_oauth_url, fbad_oauth_url)

        # test default oauth_params w/ scope
        oauth_params = DEFAULT_OAUTH_PARAMS.copy()
        oauth_params['app_id'] = "TEST_APP_ID-1"
        oauth_params['scope'] = ["test_perm1", "test_permABC"]

        fbad_oauth_url = str(fbad.oauth_url(**oauth_params))
        test_oauth_url = "%s?%s" % (OAUTH_URL, "&".join([
            "client_id=TEST_APP_ID-1",
            "redirect_uri=http://www.facebook.com/connect/login_success.html",
            "response_type=token",
            "display=page",
            "scope=test_perm1,test_permABC"]))

        # test default oauth_params w/ state
        oauth_params = DEFAULT_OAUTH_PARAMS.copy()
        oauth_params['app_id'] = "TEST_APP_ID-2"
        oauth_params['state'] = "test_state"

        fbad_oauth_url = str(fbad.oauth_url(**oauth_params))
        test_oauth_url = "%s?%s" % (OAUTH_URL, "&".join([
            "client_id=TEST_APP_ID-2",
            "redirect_uri=http://www.facebook.com/connect/login_success.html",
            "response_type=token",
            "display=page",
            "state=test_state"]))

        # test default oauth_params w/ scope and state
        oauth_params = DEFAULT_OAUTH_PARAMS.copy()
        oauth_params['app_id'] = "TEST_APP_ID-3"
        oauth_params['scope'] = ["test_perm1", "test_permABC"]
        oauth_params['state'] = "test_state"

        fbad_oauth_url = str(fbad.oauth_url(**oauth_params))
        test_oauth_url = "%s?%s" % (OAUTH_URL, "&".join([
            "client_id=TEST_APP_ID-3",
            "redirect_uri=http://www.facebook.com/connect/login_success.html",
            "response_type=token",
            "display=page",
            "scope=test_perm1,test_permABC",
            "state=test_state"]))

        self.assertEqual(test_oauth_url, fbad_oauth_url)

if __name__ == '__main__':
    unittest.main()
