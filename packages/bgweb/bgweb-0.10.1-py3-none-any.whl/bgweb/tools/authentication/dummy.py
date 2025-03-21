"""
Dummy authentication
"""


import logging
import urllib

import cherrypy
from bgweb.profile import BGProfile
from .authentication import AuthenticationTool, AuthError, ITokenAuthentication, TokenNotFoundError, UserNotFoundError


logger = logging.getLogger(__name__)


class Profile(BGProfile):

    def _process_profile(self, profile):
        pass


class DummyAuthError(AuthError):

    def __init__(self, message, status=None, reason=None):
        self.message = message
        self.status = status
        self.reason = reason


# Store the profiles
PROFILES = {}


class DummyAuth(AuthenticationTool):

    def __init__(self, conf, app_url, login_path, logout_path, force_login_function, user_id_str='user_id',
                 add_profile=True, login_redirect=None, logout_redirect=None):
        """
        This tool is intended to intercept all requests to the server and check if the request
        is done to one of the login or logout paths or to a page/resource that is protected.

        It is pretty dummy, users are logged in using the configuration or a session key. See :param:`conf`.

        Args:
            conf (dict): dictionary with the configuration. The key "name" can be used as user name/email address.
               Otherwise, you can pass the user name/email using the "dummy_auth_user_name" session key.
            app_url (str): base URL for the application
            login_path (str): path to be intercepted for the log in
            logout_path (str): path to be intercepted for the log in
            force_login_function (func): function to be called if the login is required
            user_id_str (str): string that is used in the session as key of the value corresponding to the user ID
            login_redirect (str): URL to redirect after the user logs out via HTTPRedirect (default to None).
               The application should store in the session the redirect URL in "auth_redirect_url"
            logout_redirect (str): URL to redirect after the user logs out via HTTPRedirect (default to None).

        In order to emulate the reload of the page after log in done with Mozilla persona,
        the tool expects to receive the URL to redirect from the state parameter of the lock object.
        In this implementation it is done using the window.location.href

        Limitations are:
        - dummy_auth_user_name is used in the cherrypy session to
            store additional information from the user
        - If you want the page reload after log in feature to work, the force login
          function should retrieve the code for the page without changing the URL.
          E.g.: give a function that does something like:
          return self.env.get_template('login.html').render
        """

        self.__user_name = conf.get('name', 'random user') if conf is not None else 'random_user'

        self.__base_url = app_url

        mount_point = urllib.parse.urlparse(app_url).path
        mount_point = '' if mount_point in ['', '/'] else mount_point
        mount_point = mount_point[1:] if mount_point.startswith('/') else mount_point
        mount_point = mount_point[:-1] if mount_point.endswith('/') else mount_point

        self.__login_url = urllib.parse.urljoin(app_url, mount_point + login_path)
        self.__logout_url = urllib.parse.urljoin(app_url, mount_point + logout_path)

        self.__login_path = login_path
        self.__logout_path = logout_path
        super().__init__(self.authenticate, force_login_function, user_id_str)

        logger.debug('Using dummy authentication. Capturing %s for signin and %s for singout' % (login_path, logout_path))

        self.__login_redirect = login_redirect
        self.__logout_redirect = logout_redirect
        self.__use_profile = add_profile

    def authenticate(self, require=None):
        """
        Entry point for this tool.
        Intercepts the URL matching login_path or logout_path and changes the handlers.
        Additionally, checks if the request resource is under *authentication.require*

        Args:
            require (str): this parameter is given for the static content with the
               authentication.require

        """
        if cherrypy.request.path_info == self.__login_path:
            cherrypy.request.handler = self.login
            return
        elif cherrypy.request.path_info == self.__logout_path:
            cherrypy.request.handler = self.logout
            return

        if require is not None and self.get_user() is None:
            raise cherrypy.HTTPRedirect(require.format(cherrypy.request.path_info))

        conditions = cherrypy.request.config.get('authentication.require', None)

        if conditions is not None:

            if self.get_user() is None:
                # the user is not logged in, but the tool is enabled, so instead
                #  of allowing the default handler to run, respond instead with
                #  the authentication page.
                cherrypy.request.handler = self.force_login
            else:

                for condition in conditions:
                    # A condition is just a callable that returns true or false
                    if not condition(self.get_user()):
                        cherrypy.request.handler = self.force_login

    def login(self):
        """
        Handler for log-ins.

        Raises
            HTTPError if authentication fails

        The redirect URL is expected from the state parameter of the Auth0 Lock.

        """
        global PROFILES
        error = cherrypy.request.params.get('error', None)
        error_description = cherrypy.request.params.get('error_description', None)

        if error is not None:
            raise cherrypy.HTTPError(500, "Invalid. Error when connecting with Auth0. {} : {}".format(error, error_description))

        # We're saving all user information into the session
        name = cherrypy.session.get('dummy_auth_user_name', self.__user_name)
        self.login_user(name)

        logger.info('User %s has logged in' % name)

        user = self.get_user()
        # Always get the profile to be used for the Token if neeeded
        if user.id in PROFILES:
            profile = PROFILES[user.id]
        else:
            profile = Profile(user.id, None)  # Add profile to the user
            profile.email = user.id  # the email is used in many placed as user ID
            PROFILES[user.id] = profile

        if self.__use_profile:
            user.profile = profile

        if self.__login_redirect is not None:
            raise cherrypy.HTTPRedirect(self.__login_redirect)
        else:
            redirect_url = cherrypy.session.pop('auth_redirect_url', self.__base_url)
            raise cherrypy.HTTPRedirect(redirect_url)

    def logout(self):
        """
        Handler for log-outs.

        """
        cherrypy.response.headers['Cache-Control'] = 'no-cache'

        self.logout_user()

        if self.__logout_redirect is not None:
            raise cherrypy.HTTPRedirect(self.__logout_redirect)
        else:
            redirect_url = cherrypy.session.pop('auth_redirect_url', self.__base_url)
            raise cherrypy.HTTPRedirect(redirect_url)

    def get_login_url(self):
        """Trick to be compatible with Auth0 format. Just returns to the login URL"""
        return self.__login_url

    def get_logout_url(self):
        """Trick to be compatible with Auth0 format. Just returns to the logout URL"""
        return self.__logout_url


class DummyAuthToken(ITokenAuthentication):

    def check_token(self, user_id, token, application):
        profile = PROFILES.get(user_id, None)

        if profile is None:
            logger.warning('Cannot find user %s' % user_id)
            raise UserNotFoundError()

        if not profile.terms_accepted(application):
            logger.info('User %s has not accepted the terms' % user_id)
            raise AuthError(
                'Terms not accepted for this app. Please register and accept the terms in the application site')

        token_ = profile.rest_api_token

        if token_ is None:
            logger.warning('Cannot find token for %s' % user_id)
            raise TokenNotFoundError()
        else:
            return token == token_