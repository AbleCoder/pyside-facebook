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

from PySide.QtCore    import QUrl
from PySide.QtCore    import Signal
from PySide.QtNetwork import QNetworkReply
from PySide.QtWebKit  import QWebView

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
    Emitted when a user authentication succesfully before authorizing
    permissions.

    @param state (str) The state value originally set in request.
    """

    signal_authSuccess = Signal(str)

    # -------------------------------------------------------------------------

    """
    Emitted when the auth form has loaded and is ready to be displayed.

    @param state (str) The state value originally set in request.
    """

    signal_authFormReady = Signal(str)

    # -------------------------------------------------------------------------

    """
    Emitted when an OAuthExeption is encountered.

    NOTE: This is can happen for a multitude of reasons. For example if your
          App ID is invalid you wil receive an OAuthEception code 101. You
          should read the message for details on the cause of the exception.

    @param message (str) A string explaining the exception.
    @param code    (int) OAuthException code
    """

    signal_errorOAuthException = Signal(str, int)

    # -------------------------------------------------------------------------

    """
    Emitted when a user authenticates, authorizes the requested permissions
    AND the `response_type` was set to: token

    @param access_token (str) Authenticated user's facebook access token.
    @param expires_in   (int) Number of seconds until token expires.
    @param state        (str) The state value originally set in request.
    """

    signal_permsAuthorizedAccessToken = Signal(str, int, str)

    # -------------------------------------------------------------------------

    """
    Emitted when a user authenticates, authorizes the requested permissions
    AND the `response_type` was set to: code

    @param oauth_code (str) OAuth code generated by facebook.
    @param state      (str) The state value originally set in request.
    """

    signal_permsAuthorizedOAuthCode = Signal(str, str)

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

        self._nam = self.page().networkAccessManager()

        # connect signals
        #self.urlChanged.connect(self._slot_urlChanged)
        self._nam.finished.connect(self._slot_httpResponseFinished)

    # -------------------------------------------------------------------------
    # INTERNAL METHODS
    # -------------------------------------------------------------------------

    def _slot_httpResponseFinished(self, reply):
        """
        Slot for QWebView's QNetworkAccessManager finished signal.

        @param reply (QNetworkReply)
        """

        #print "REPLY::ERROR>> ", reply.error()
        #print "REPLY::FINISHED>> ", self.url()

        url = self.url()

#    # -------------------------------------------------------------------------
#
#    def _slot_urlChanged(self, url):
#        """
#        Slot for QWebView urlChanged signal.
#
#        @param url (QUrl)
#        """

        # ---------------------------------------------------------------------
        # PARSE URL DATA
        # ---------------------------------------------------------------------

        fragment = url.fragment()
        path = url.path()
        query_items = dict(url.queryItems())

        fragment_items = []
        if fragment:
            qu = QUrl()
            qu.setEncodedQuery(str(fragment))

            fragment_items = qu.queryItems()

            # push fragment values into query items dict
            for i in fragment_items:
                query_items[i[0]] = i[1]

        state = ""
        if "state" in query_items:
            state = query_items["state"]

        # ---------------------------------------------------------------------
        # FIRE DESTINATION SIGNALS
        # ---------------------------------------------------------------------

        if "error" in query_items:
            error_reason = ""
            if "error_reason" in query_items:
                reason = query_items["error_reason"]

            error_description = ""
            if "error_description" in query_items:
                description = query_items["error_description"].replace("+"," ")

            # user canceled before granting permissions
            self.signal_permsNotAuthorized.emit(query_items["error"], reason,
                    description, state)

            return

        if path == "/login.php":
            if "skip_api_login" in query_items:
                # initial load of the login form
                self.signal_authFormReady.emit(state)

                return

            elif "login_attempt" in query_items:
                # user login credentials invalid
                self.signal_authFail.emit(state)

                return

        elif path == "/dialog/permissions.request":
            if "from_login" in query_items:
                # user authenticated successfully
                self.signal_authSuccess.emit(state)

                return

        elif path == "/connect/login_success.html":
            if "access_token" in query_items:
                access_token = query_items["access_token"]

                expires_in = 0
                if "expires_in" in query_items:
                    expires_in = int(query_items["expires_in"])

                # permissions authorized and access token received
                self.signal_permsAuthorizedAccessToken.emit(access_token,
                        expires_in, state)

                return

            elif "code" in query_items:
                oauth_code = query_items["code"]

                expires_in = 0
                if "expires_in" in query_items:
                    expires_in = int(query_items["expires_in"])

                # permissions authorized and OAuth code received
                self.signal_permsAuthorizedOAuthCode.emit(oauth_code, state)

                return

        # print url details if no destination matched
        print "URL Str: ", str(url)
        print "URL Path: ", path
        print "Query Items: ", query_items
        print "fragment: ", fragment
        print "fragment_items: ", fragment_items

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
        Set OAuth request params values.

        Facebook OAuth Dialog Param References:
         - https://developers.facebook.com/docs/reference/dialogs/oauth/

        Facebook Permissions Reference
         - https://developers.facebook.com/docs/authentication/permissions/

        NOTE: The default redirect_uri is the one provided by facebook
              specifically to allow desktop apps to login using OAuth 2.0
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

    def start_auth(self, state=None):
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
