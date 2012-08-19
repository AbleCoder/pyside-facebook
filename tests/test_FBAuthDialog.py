import sys
import time
import unittest

from PySide.QtGui import QApplication
from PySide.QtGui import QWidget

from pyside_facebook import FBAuthDialog
from pyside_facebook import FBAuthDialogInvalidParamException
from pyside_facebook import OAUTH_URL
from pyside_facebook import REDIRECT_URI


# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

DEFAULT_OAUTH_PARAMS = {
    "app_id": None,
    "redirect_uri": REDIRECT_URI,
    "scope": [],
    "state": None,
    "response_type": "token",
    "display": "popup",
}

# -----------------------------------------------------------------------------

FB_OAUTH_EXCEPTIONS = {
    "INVALID_APP_ID": {
        "code": 101,
        "message": "Error validating application. Invalid application ID.",
    },
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
            redirect_uri=REDIRECT_URI, scope=[], state=None,
            response_type="token", display="popup"):
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

    def test_get_oauth_url(self):
        # setup widget to run tests on
        fbad = FBAuthDialog(FBAuthDialogTestCase.parentWidget)

        # test default oauth_params WITH OUT app_id
        oauth_params = DEFAULT_OAUTH_PARAMS.copy()

        with self.assertRaises(FBAuthDialogInvalidParamException):
            fbad.get_oauth_url(**oauth_params)

        # test default oauth_params
        oauth_params = DEFAULT_OAUTH_PARAMS.copy()
        oauth_params['app_id'] = "TEST_APP_ID"

        fbad_oauth_url = fbad.get_oauth_url(**oauth_params)
        test_oauth_url = "%s?%s" % (OAUTH_URL, "&".join([
            "client_id=TEST_APP_ID",
            "redirect_uri=http://www.facebook.com/connect/login_success.html",
            "response_type=token",
            "display=popup"]))

        self.assertEqual(test_oauth_url, fbad_oauth_url)

        # test default oauth_params w/ scope
        oauth_params = DEFAULT_OAUTH_PARAMS.copy()
        oauth_params['app_id'] = "TEST_APP_ID-1"
        oauth_params['scope'] = ["test_perm1", "test_permABC"]

        fbad_oauth_url = fbad.get_oauth_url(**oauth_params)
        test_oauth_url = "%s?%s" % (OAUTH_URL, "&".join([
            "client_id=TEST_APP_ID-1",
            "redirect_uri=http://www.facebook.com/connect/login_success.html",
            "response_type=token",
            "display=popup",
            "scope=test_perm1,test_permABC"]))

        # test default oauth_params w/ state
        oauth_params = DEFAULT_OAUTH_PARAMS.copy()
        oauth_params['app_id'] = "TEST_APP_ID-2"
        oauth_params['state'] = "test_state"

        fbad_oauth_url = fbad.get_oauth_url(**oauth_params)
        test_oauth_url = "%s?%s" % (OAUTH_URL, "&".join([
            "client_id=TEST_APP_ID-2",
            "redirect_uri=http://www.facebook.com/connect/login_success.html",
            "response_type=token",
            "display=popup",
            "state=test_state"]))

        # test default oauth_params w/ scope and state
        oauth_params = DEFAULT_OAUTH_PARAMS.copy()
        oauth_params['app_id'] = "TEST_APP_ID-3"
        oauth_params['scope'] = ["test_perm1", "test_permABC"]
        oauth_params['state'] = "test_state"

        fbad_oauth_url = fbad.get_oauth_url(**oauth_params)
        test_oauth_url = "%s?%s" % (OAUTH_URL, "&".join([
            "client_id=TEST_APP_ID-3",
            "redirect_uri=http://www.facebook.com/connect/login_success.html",
            "response_type=token",
            "display=popup",
            "scope=test_perm1,test_permABC",
            "state=test_state"]))

        self.assertEqual(test_oauth_url, fbad_oauth_url)

    # -------------------------------------------------------------------------

    def test_startAuth(self):
        # setup temp variables for validating correct singals until I can find
        # a more generic and general method for confirming signal fires
        _errorOAuthException_code = None
        _errorOAuthException_message = None
        _urlChanged_url = None

        def slot_urlChanged(url):
            _urlChanged_url = url

        # create slot to confirm proper OAuthException error signal raised
        def slot_errorOAuthException(message, code):
            _errorOAuthException_message = message
            _errorOAuthException_code = code

        # setup widget to run tests with invalid app_id
        fbad = FBAuthDialog(FBAuthDialogTestCase.parentWidget,
                app_id="INVALID")

        # connect signals to slots
        fbad.urlChanged.connect(slot_urlChanged)
        fbad.signal_errorOAuthException.connect(slot_errorOAuthException)

        # ---------------------------------------------------------------------
        # TESTS
        # ---------------------------------------------------------------------

        fbad.start_auth()

        # wait for first urlChanged signal and then move onto tests
        sleep_time_cur = 0
        sleep_time_max = 10
        sleep_time_step = 1
        while _urlChanged_url is None:
            if sleep_time_cur > sleep_time_max:
                break

            time.sleep(sleep_time_step)

            sleep_time_cur += sleep_time_step

        self.assertEqual(FB_OAUTH_EXCEPTIONS["INVALID_APP_ID"]["code"],
                _errorOAuthException_code)
        self.assertEqual(FB_OAUTH_EXCEPTIONS["INVALID_APP_ID"]["message"],
                _errorOAuthException_message)


if __name__ == '__main__':
    unittest.main()
