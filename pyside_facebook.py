# This file is part of PySide-Facebook.
# Copyright (c) 2012 Brandon Orther. All rights reserved.
#
# The full license is available in the LICENSE file that was distributed with
# this source code.
#
# Author: Brandon Orther <an.able.coder@gmail.com>


"""
A general purpose PySide library to interact with facebook's API.
"""

from PySide.QtCore   import QUrl
from PySide.QtCore   import Signal
from PySide.QtWebKit import QWebView

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

REDIRECT_URI = "http://www.facebook.com/connect/login_success.html"
OAUTH_URL = "https://graph.facebook.com/oauth/authorize"


# -----------------------------------------------------------------------------
# EXCEPTIONS
# -----------------------------------------------------------------------------

class PySideFacebookException(Exception):

    pass


# -----------------------------------------------------------------------------

class FBAuthDialogException(PySideFacebookException):

    pass


# -----------------------------------------------------------------------------

class FBAuthDialogInvalidParamException(FBAuthDialogException):

    pass


# -----------------------------------------------------------------------------

class FBGraphAPIException(PySideFacebookException):

    pass


# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class FBAuthDialog(QWebView):

    """
    A QWebView extended to load Facebook's OAuth Dialog allowing a user to
    login and grant permissions to your facebook app and finally return the
    user's token or OAuth code.
    """

    # -------------------------------------------------------------------------
    # SIGNALS
    # -------------------------------------------------------------------------

    """
    Emitted when a user authentication fails. This is when a user submits the
    bad login details.

    @param state (str) The state value originally set in request.
    """

    signal_authFail = Signal(str)

    # -------------------------------------------------------------------------

    """
    Emitted when the auth form has loaded and is ready to be displayed.

    @param state (str) The state value originally set in request.
    """

    signal_authFormReady = Signal(str)

    # -------------------------------------------------------------------------

    """
    Emitted when a user authenticates, authorizes the requested permissions
    AND the `response_type` was set to: token

    @param access_token (str) Authenticated user's facebook access token.
    @param expires_in   (int) Number of seconds until token expires.
    @param state        (str) The state value originally set in request.
    """

    signal_authSuccessAccessToken = Signal(str, int, str)

    # -------------------------------------------------------------------------

    """
    Emitted when a user authenticates, authorizes the requested permissions
    AND the `response_type` was set to: code

    @param oauth_code (str) OAuth code generated by facebook.
    @param state      (str) The state value originally set in request.
    """

    signal_authSuccessQAuthCode = Signal(str, str)

    # -------------------------------------------------------------------------

    """
    Emitted when a the requested permissions are NOT authorized by the user.
    This happens when a user clicks "cancel" at any time before authorizing
    the permissions.

    @param error       (str) Error code (example: access_denied)
    @param reason      (str) Reason code (example: user_denied)
    @param description (str) A string explaining the error.
    @param state       (str) The state value originally set in request.
    """

    signal_permsNotAuthorized = Signal(str, str, str, str)

    # -------------------------------------------------------------------------

    """
    Emitted when a user doesn't authenticate within the amount of time
    specified in `user_auth_timeout`.

    @param time_elapsed (int) Number of seconds elapsed to cause the timeout.
    """

    signal_userAuthTimeout = Signal(int)

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def __init__(self, parent=None, app_id=None):
        """
        Instantiate FBAuthDialog object.

        @param [parent] (QWidget) Parent object that this widget belongs to.
        @param [app_id] (str)     Facebook App ID
        """

        super(FBAuthDialog, self).__init__(parent)

        # set default oauth params
        self.set_oauth_params(app_id=app_id)

        # calling the page() method makes DOM elements render correctly
        self.page()

        # connect signals
        self.urlChanged.connect(self._slot_urlChanged)

    # -------------------------------------------------------------------------
    # INTERNAL METHODS
    # -------------------------------------------------------------------------

    def _slot_urlChanged(self, url):
        """
        Slot for QWebView urlChanged signal.

        @param url (QUrl)
        """

        # ---------------------------------------------------------------------
        # PARSE URL DATA
        # ---------------------------------------------------------------------

        path = url.path()
        query_items = dict(url.queryItems())

        login_attempt = "login_attempt" in query_items
        skip_api_login = "skip_api_login" in query_items

        error_reason = ""
        if "error_reason" in query_items:
            error_reason = query_items["error_reason"]

        error_description = ""
        if "error_description" in query_items:
            error_description = query_items["error_description"]\
                    .replace("+"," ")

        state = ""
        if "state" in query_items:
            state = query_items["state"]

        # ---------------------------------------------------------------------
        # FIRE DESTINATION SIGNALS
        # ---------------------------------------------------------------------

        if path == "/login.php":
            if skip_api_login:
                # initial load of the login form
                self.signal_authFormReady.emit(state)

                return

            elif login_attempt:
                # user login credentials invalid
                self.signal_authFail.emit(state)

                return

        elif path == "/connect/login_success.html":
            if "error" in query_items:
                # user canceled before granting permissions
                self.signal_permsNotAuthorized.emit(query_items["error"],
                        error_reason, error_description, state)

                return


        # print url details if no destination matched
        print "URL Str: ", str(url)
        print "URL Path: ", url.path()
        print "Query Items: ", url.queryItems()

    # -------------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------------

    def get_oauth_url(self, app_id, redirect_uri, scope, state, response_type,
            display):
        """
        Return encoded OAuth URL with request params formated as GET params.

        @param app_id        (str/uni)
        @param redirect_uri  (str/uni)
        @param scope         (list)
        @param state         (str/uni)
        @param response_type (str/uni)
        @param display       (str/uni)

        @return (QUrl)
        """

        if type(app_id) not in (str, unicode):
            raise FBAuthDialogInvalidParamException(
                "app_id must be `str` or `unicode` but was: %s" % type(app_id))

        if type(redirect_uri) not in (type(None), str, unicode):
            raise FBAuthDialogInvalidParamException(
                "redirect_uri must be `None`, `str` or `unicode` but was: %s" %
                type(redirect_uri))

        if type(scope) not in (type(None), list):
            raise FBAuthDialogInvalidParamException(
                "scope must be `None` or `list` but was: %s" %
                type(scope))

        if type(state) not in (type(None), str, unicode):
            raise FBAuthDialogInvalidParamException(
                "state must be `None`, `str` or `unicode` but was: %s" %
                type(state))

        if type(response_type) not in (type(None), str, unicode):
            raise FBAuthDialogInvalidParamException(
                "response_type must be `None`, `str` or `unicode` but was: %s"
                % type(response_type))

        if type(display) not in (type(None), str, unicode):
            raise FBAuthDialogInvalidParamException(
                "display must be `None`, `str` or `unicode` but was: %s"
                % type(display))

        url = QUrl(OAUTH_URL)

        url.addQueryItem("client_id", app_id)
        url.addQueryItem("redirect_uri", redirect_uri)
        url.addQueryItem("response_type", response_type)
        url.addQueryItem("display", display)

        if scope:
            _scope = ",".join(map(unicode, scope))

            url.addQueryItem("scope", _scope)

        if state:
            url.addQueryItem("state", state)

        return url

    # -------------------------------------------------------------------------

    def set_oauth_params(self, app_id=None, redirect_uri=REDIRECT_URI,
            scope=[], state=None, response_type="token", display="popup"):
        """
        Set QAuth request params values.

        Facebook OAuth Dialog Param References:
         - https://developers.facebook.com/docs/reference/dialogs/oauth/

        Facebook Permissions Reference
         - https://developers.facebook.com/docs/authentication/permissions/

        NOTE: The default redirect_uri is the one provided by facebook
              specifically to allow desktop apps to login using QAuth 2.0
              implementation without having to have a webserver running to
              redirect users to after they have successfully authenticated.

        @param [app_id]        (str/uni)
        @param [redirect_uri]  (str/uni)
        @param [scope]         (list)
        @param [state]         (str/uni)
        @param [response_type] (str/uni)
        @param [display]       (str/uni)
        """

        self.oauth_params = {
            "app_id": app_id,
            "redirect_uri": REDIRECT_URI,
            "scope": scope,
            "state": state,
            "response_type": response_type,
            "display": display,
        }

    # -------------------------------------------------------------------------

    def startAuth(self, state=None):
        """
        Start authentication process by opening OAuth Dialog.

        @param [state] (str) If set, the value is passed in the OAuth request
                             instead the value set for state using the
                             `set_oauth_params` method.
        """

        oauth_params = self.oauth_params.copy()

        if state:
            oauth_params['state'] = state

        oauth_url = self.get_oauth_url(**oauth_params)

        self.load(oauth_url)
