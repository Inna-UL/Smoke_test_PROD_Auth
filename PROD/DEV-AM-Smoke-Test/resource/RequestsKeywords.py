import httplib
import json
import sys
from urllib import urlencode

import requests
import robot
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn


try:
    from requests_ntlm import HttpNtlmAuth
except ImportError:
    pass


class WritableObject:
    ''' HTTP stream handler '''

    def __init__(self):
        self.content = []

    def write(self, string):
        self.content.append(string)


class RequestsKeywords(object):
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self._cache = robot.utils.ConnectionCache('No sessions created')
        self.builtin = BuiltIn()
        self.debug = 0

    def _create_session(
            self,
            alias,
            url,
            headers,
            cookies,
            auth,
            timeout,
            max_retries,
            proxies,
            verify,
            debug):
        """ Create Session: create a HTTP session to a server

        `url` Base url of the server

        `alias` Robot Framework alias to identify the session

        `headers` Dictionary of default headers

        `auth` List of username & password for HTTP Basic Auth

        `timeout` Connection timeout

        `proxies` Dictionary that contains proxy urls for HTTP and HTTPS communication

        `verify` Whether the SSL cert will be verified. A CA_BUNDLE path can also be provided.

        `debug` Enable http verbosity option more information
                https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel
        """

        self.builtin.log('Creating session: %s' % alias, 'DEBUG')
        s = session = requests.Session()
        s.headers.update(headers)
        s.auth = auth if auth else s.auth
        s.proxies = proxies if proxies else s.proxies

        max_retries = self.builtin.convert_to_integer(max_retries)

        if max_retries > 0:
            http = requests.adapters.HTTPAdapter(max_retries=max_retries)
            https = requests.adapters.HTTPAdapter(max_retries=max_retries)

            # Replace the session's original adapters
            s.mount('http://', http)
            s.mount('https://', https)

        # verify can be a Boolean or a String
        if isinstance(verify, bool):
            s.verify = verify
        elif isinstance(verify, unicode) or isinstance(verify, str):
            if verify.lower() == 'true' or verify.lower() == 'false':
                verify = self.builtin.convert_to_boolean(verify)
        else:
            # not a Boolean nor a String
            s.verify = verify

        # cant pass these into the Session anymore
        self.timeout = float(timeout) if timeout is not None else None
        self.cookies = cookies
        self.verify = verify

        s.url = url

        # Enable http verbosity
        if debug >= 1:
            self.debug = int(debug)
            httplib.HTTPConnection.debuglevel = self.debug

        self._cache.register(session, alias=alias)
        return session

    def create_session(self, alias, url, headers={}, cookies=None,
                       auth=None, timeout=None, proxies=None,
                       verify=False, debug=0, max_retries=3):
        """ Create Session: create a HTTP session to a server

        `url` Base url of the server

        `alias` Robot Framework alias to identify the session

        `headers` Dictionary of default headers

        `auth` List of username & password for HTTP Basic Auth

        `timeout` Connection timeout

        `proxies` Dictionary that contains proxy urls for HTTP and HTTPS communication

        `verify` Whether the SSL cert will be verified. A CA_BUNDLE path can also be provided.
                 Defaults to False.

        `debug` Enable http verbosity option more information
                https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        `max_retries` The maximum number of retries each connection should attempt.
        """
        auth = requests.auth.HTTPBasicAuth(*auth) if auth else None

        logger.info('Creating Session using : alias=%s, url=%s, headers=%s, \
                    cookies=%s, auth=%s, timeout=%s, proxies=%s, verify=%s, \
                    debug=%s ' % (alias, url, headers, cookies, auth, timeout,
                                  proxies, verify, debug))
        return self._create_session(
            alias,
            url,
            headers,
            cookies,
            auth,
            timeout,
            max_retries,
            proxies,
            verify,
            debug)

    def create_ntlm_session(
            self,
            alias,
            url,
            auth,
            headers={},
            cookies=None,
            timeout=None,
            proxies=None,
            verify=False,
            debug=0,
            max_retries=3):
        """ Create Session: create a HTTP session to a server

        `url` Base url of the server

        `alias` Robot Framework alias to identify the session

        `headers` Dictionary of default headers

        `auth` ['DOMAIN', 'username', 'password'] for NTLM Authentication

        `timeout` Connection timeout

        `proxies` Dictionary that contains proxy urls for HTTP and HTTPS communication

        `verify` Whether the SSL cert will be verified. A CA_BUNDLE path can also be provided.
                 Defaults to False.

        `debug` Enable http verbosity option more information
                https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        `max_retries` The maximum number of retries each connection should attempt.
        """
        if not HttpNtlmAuth:
            raise AssertionError('Requests NTLM module not loaded')
        elif len(auth) != 3:
            raise AssertionError('Incorrect number of authentication arguments'
                                 ' - expected 3, got {}'.format(len(auth)))
        else:
            ntlm_auth = HttpNtlmAuth('{}\\{}'.format(auth[0], auth[1]),
                                     auth[2])
            logger.info('Creating NTLM Session using : alias=%s, url=%s, \
                        headers=%s, cookies=%s, ntlm_auth=%s, timeout=%s, \
                        proxies=%s, verify=%s, debug=%s '
                        % (alias, url, headers, cookies, ntlm_auth,
                           timeout, proxies, verify, debug))

            return self._create_session(
                alias,
                url,
                headers,
                cookies,
                ntlm_auth,
                timeout,
                max_retries,
                proxies,
                verify,
                debug)

    def create_digest_session(self, alias, url, auth, headers={}, cookies=None,
                              timeout=None, proxies=None, verify=False,
                              debug=0, max_retries=3):
        """ Create Session: create a HTTP session to a server

        `url` Base url of the server

        `alias` Robot Framework alias to identify the session

        `headers` Dictionary of default headers

        `auth` ['DOMAIN', 'username', 'password'] for NTLM Authentication

        `timeout` Connection timeout

        `proxies` Dictionary that contains proxy urls for HTTP and HTTPS communication

        `verify` Whether the SSL cert will be verified. A CA_BUNDLE path can also be provided.
                 Defaults to False.

        `debug` Enable http verbosity option more information
                https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        `max_retries` The maximum number of retries each connection should attempt.
        """
        digest_auth = requests.auth.HTTPDigestAuth(*auth) if auth else None

        return self._create_session(
            alias,
            url,
            headers,
            cookies,
            digest_auth,
            timeout,
            max_retries,
            proxies,
            verify,
            debug)

    def delete_all_sessions(self):
        """ Removes all the session objects """
        logger.info('Delete All Sessions')

        self._cache.empty_cache()

    def to_json(self, content, pretty_print=False):
        """ Convert a string to a JSON object

        `content` String content to convert into JSON

        'pretty_print' If defined, will output JSON is pretty print format
        """
        if pretty_print:
            json_ = self._json_pretty_print(content)
        else:
            json_ = json.loads(content)
        logger.info('To JSON using : content=%s ' % (content))
        logger.info('To JSON using : pretty_print=%s ' % (pretty_print))

        return json_

    def get_request(
            self,
            alias,
            uri,
            headers=None,
            params=None,
            allow_redirects=None,
            timeout=None):
        """ Send a GET request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the GET request to

        `params` url parameters to append to the uri

        `headers` a dictionary of headers to use with the request

        `timeout` connection timeout
        """
        session = self._cache.switch(alias)
        redir = True if allow_redirects is None else allow_redirects

        response = self._get_request(
            session, uri, params, headers, redir, timeout)

        logger.info(
            'Get Request using : alias=%s, uri=%s, headers=%s ' %
            (alias, uri, headers))

        return response

    def get(
            self,
            alias,
            uri,
            params=None,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ **Deprecated- See Get Request now**

        Send a GET request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the GET request to

        `headers` a dictionary of headers to use with the request

        `timeout` connection timeout
        """
        logger.warn("Deprecation Warning: Use Get Request in the future")
        session = self._cache.switch(alias)

        redir = True if allow_redirects is None else allow_redirects

        response = self._get_request(
            session, uri, params, headers, redir, timeout)

        return response

    def post_request(
            self,
            alias,
            uri,
            data=None,
            params=None,
            headers=None,
            files=None,
            allow_redirects=None,
            timeout=None):
        """ Send a POST request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the POST request to

        `data` a dictionary of key-value pairs that will be urlencoded
               and sent as POST data
               or binary data that is sent as the raw body content

        `params` url parameters to append to the uri

        `headers` a dictionary of headers to use with the request

        `files` a dictionary of file names containing file data to POST to the server

        `allow_redirects` requests redirection

        `timeout` connection timeout
        """
        session = self._cache.switch(alias)
        data = self._format_data_according_to_header(data, headers)
        redir = True if allow_redirects is None else allow_redirects

        response = self._body_request(
            "post",
            session,
            uri,
            data,
            params,
            files,
            headers,
            redir,
            timeout)

        if isinstance(data, str):
            data = data.decode('utf-8')
        logger.info('Post Request using : alias=%s, uri=%s, data=%s, \
                    headers=%s, files=%s, allow_redirects=%s '
                    % (alias, uri, data, headers, files, redir))

        return response

    def post(
            self,
            alias,
            uri,
            data={},
            headers=None,
            files=None,
            allow_redirects=None,
            timeout=None):
        """ **Deprecated- See Post Request now**

        Send a POST request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the GET request to

        `data` a dictionary of key-value pairs that will be urlencoded
               and sent as POST data
               or binary data that is sent as the raw body content

        `headers` a dictionary of headers to use with the request

        `files` a dictionary of file names containing file data to POST to the server

        `timeout` connection timeout
        """
        logger.warn("Deprecation Warning: Use Post Request in the future")
        session = self._cache.switch(alias)
        data = self._utf8_urlencode(data)
        redir = True if allow_redirects is None else allow_redirects

        response = self._body_request(
            "post",
            session,
            uri,
            data,
            None,
            files,
            headers,
            redir,
            timeout)

        return response

    def patch_request(
            self,
            alias,
            uri,
            data=None,
            params=None,
            headers=None,
            files=None,
            allow_redirects=None,
            timeout=None):
        """ Send a PATCH request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the PATCH request to

        `data` a dictionary of key-value pairs that will be urlencoded
               and sent as PATCH data
               or binary data that is sent as the raw body content

        `headers` a dictionary of headers to use with the request

        `files` a dictionary of file names containing file data to PATCH to the server

        `allow_redirects` requests redirection

        `params` url parameters to append to the uri

        `timeout` connection timeout
        """
        session = self._cache.switch(alias)
        data = self._format_data_according_to_header(data, headers)
        redir = True if allow_redirects is None else allow_redirects

        response = self._body_request(
            "patch",
            session,
            uri,
            data,
            params,
            files,
            headers,
            redir,
            timeout)

        if isinstance(data, str):
            data = data.decode('utf-8')
        logger.info('Patch Request using : alias=%s, uri=%s, data=%s, \
                    headers=%s, files=%s, allow_redirects=%s '
                    % (alias, uri, data, headers, files, redir))

        return response

    def patch(
            self,
            alias,
            uri,
            data={},
            headers=None,
            files={},
            allow_redirects=None,
            timeout=None):
        """ **Deprecated- See Patch Request now**

        Send a PATCH request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the PATCH request to

        `data` a dictionary of key-value pairs that will be urlencoded
               and sent as PATCH data
               or binary data that is sent as the raw body content

        `headers` a dictionary of headers to use with the request

        `files` a dictionary of file names containing file data to PATCH to the server

        `timeout` connection timeout
        """
        logger.warn("Deprecation Warning: Use Patch Request in the future")
        session = self._cache.switch(alias)
        data = self._utf8_urlencode(data)
        redir = True if allow_redirects is None else allow_redirects

        response = self._body_request(
            "patch",
            session,
            uri,
            data,
            None,
            files,
            headers,
            redir,
            timeout)

        return response

    def put_request(
            self,
            alias,
            uri,
            data=None,
            params=None,
            files=None,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ Send a PUT request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the PUT request to

        `headers` a dictionary of headers to use with the request

        `allow_redirects` requests redirection

        `params` url parameters to append to the uri

        `timeout` connection timeout
        """
        session = self._cache.switch(alias)
        data = self._format_data_according_to_header(data, headers)
        redir = True if allow_redirects is None else allow_redirects

        response = self._body_request(
            "put",
            session,
            uri,
            data,
            params,
            files,
            headers,
            redir,
            timeout)

        if isinstance(data, str):
            data = data.decode('utf-8')
        logger.info('Put Request using : alias=%s, uri=%s, data=%s, \
                    headers=%s, allow_redirects=%s ' % (alias, uri, data, headers, redir))

        return response

    def put(
            self,
            alias,
            uri,
            data=None,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ **Deprecated- See Put Request now**

        Send a PUT request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the PUT request to

        `headers` a dictionary of headers to use with the request

        `timeout` connection timeout
        """
        logger.warn("Deprecation Warning: Use Put Request in the future")
        session = self._cache.switch(alias)
        data = self._utf8_urlencode(data)
        redir = True if allow_redirects is None else allow_redirects

        response = self._body_request(
            "put",
            session,
            uri,
            data,
            None,
            None,
            headers,
            redir,
            timeout)

        return response

    def delete_request(
            self,
            alias,
            uri,
            data=(),
            params=None,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ Send a DELETE request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the DELETE request to

        `headers` a dictionary of headers to use with the request

        `timeout` connection timeout
        """
        session = self._cache.switch(alias)
        data = self._utf8_urlencode(data)
        redir = True if allow_redirects is None else allow_redirects

        response = self._delete_request(
            session, uri, data, params, headers, redir, timeout)

        if isinstance(data, str):
            data = data.decode('utf-8')
        logger.info('Delete Request using : alias=%s, uri=%s, data=%s, \
                    headers=%s, allow_redirects=%s ' % (alias, uri, data, headers, redir))

        return response

    def delete(
            self,
            alias,
            uri,
            data=(),
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ * * *   Deprecated- See Delete Request now   * * *

        Send a DELETE request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the DELETE request to

        `headers` a dictionary of headers to use with the request

        `timeout` connection timeout
        """
        logger.warn("Deprecation Warning: Use Delete Request in the future")
        session = self._cache.switch(alias)
        data = self._utf8_urlencode(data)
        redir = True if allow_redirects is None else allow_redirects

        response = self._delete_request(
            session, uri, data, None, headers, redir, timeout)

        return response

    def head_request(
            self,
            alias,
            uri,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ Send a HEAD request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the HEAD request to

        `headers` a dictionary of headers to use with the request
        """
        session = self._cache.switch(alias)
        redir = False if allow_redirects is None else allow_redirects
        response = self._head_request(session, uri, headers, redir, timeout)
        logger.info('Head Request using : alias=%s, uri=%s, headers=%s, \
        allow_redirects=%s ' % (alias, uri, headers, redir))

        return response

    def head(
            self,
            alias,
            uri,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ **Deprecated- See Head Request now**

        Send a HEAD request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the HEAD request to

        `headers` a dictionary of headers to use with the request
        """
        logger.warn("Deprecation Warning: Use Head Request in the future")
        session = self._cache.switch(alias)
        redir = False if allow_redirects is None else allow_redirects
        response = self._head_request(session, uri, headers, redir, timeout)

        return response

    def options_request(
            self,
            alias,
            uri,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ Send an OPTIONS request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the OPTIONS request to

        `headers` a dictionary of headers to use with the request
        """
        session = self._cache.switch(alias)
        redir = True if allow_redirects is None else allow_redirects
        response = self._options_request(session, uri, headers, redir, timeout)
        logger.info(
            'Options Request using : alias=%s, uri=%s, headers=%s, allow_redirects=%s ' %
            (alias, uri, headers, redir))

        return response

    def options(
            self,
            alias,
            uri,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ **Deprecated- See Options Request now**
        Send an OPTIONS request on the session object found using the
        given `alias`

        `alias` that will be used to identify the Session object in the cache

        `uri` to send the OPTIONS request to

        `headers` a dictionary of headers to use with the request
        """
        logger.warn("Deprecation Warning: Use Options Request in the future")
        session = self._cache.switch(alias)
        redir = True if allow_redirects is None else allow_redirects
        response = self._options_request(session, uri, headers, redir, timeout)

        return response

    def _get_request(
            self,
            session,
            uri,
            params,
            headers,
            allow_redirects,
            timeout):
        self._capture_output()

        resp = session.get(self._get_url(session, uri),
                           headers=headers,
                           params=self._utf8_urlencode(params),
                           allow_redirects=allow_redirects,
                           timeout=self._get_timeout(timeout),
                           cookies=self.cookies)

        self._print_debug()
        # Store the last session object (@Kosuri Why?)
        session.last_resp = resp

        return resp

    def _body_request(
            self,
            method_name,
            session,
            uri,
            data,
            params,
            files,
            headers,
            allow_redirects,
            timeout):
        self._capture_output()

        method = getattr(session, method_name)
        resp = method(self._get_url(session, uri),
                      data=data,
                      params=self._utf8_urlencode(params),
                      files=files,
                      headers=headers,
                      allow_redirects=allow_redirects,
                      timeout=self._get_timeout(timeout),
                      cookies=self.cookies)

        self._print_debug()

        # Store the last session object (@Kosuri Why?)
        session.last_resp = resp
        self.builtin.log(method_name + " response: " + resp.content, 'DEBUG')

        return resp

    def _delete_request(
            self,
            session,
            uri,
            data,
            params,
            headers,
            allow_redirects,
            timeout):
        self._capture_output()

        resp = session.delete(self._get_url(session, uri),
                              data=data,
                              params=self._utf8_urlencode(params),
                              headers=headers,
                              allow_redirects=allow_redirects,
                              timeout=self._get_timeout(timeout),
                              cookies=self.cookies)

        self._print_debug()

        # Store the last session object (@Kosuri Why?)
        session.last_resp = resp

        return resp

    def _head_request(self, session, uri, headers, allow_redirects, timeout):
        self._capture_output()

        resp = session.head(self._get_url(session, uri),
                            headers=headers,
                            allow_redirects=allow_redirects,
                            timeout=self._get_timeout(timeout),
                            cookies=self.cookies)

        self._print_debug()

        # Store the last session object (@Kosuri Why?)
        session.last_resp = resp

        return resp

    def _options_request(
            self,
            session,
            uri,
            headers,
            allow_redirects,
            timeout):
        self._capture_output()

        resp = session.options(self._get_url(session, uri),
                               headers=headers,
                               cookies=self.cookies,
                               allow_redirects=allow_redirects,
                               timeout=self._get_timeout(timeout))

        self._print_debug()

        # Store the last session object (@Kosuri Why?)
        session.last_resp = resp

        return resp

    def _get_url(self, session, uri):
        ''' Helper method to get the full url
        '''
        url = session.url
        if uri:
            slash = '' if uri.startswith('/') else '/'
            url = "%s%s%s" % (session.url, slash, uri)
        return url

    def _get_timeout(self, timeout):
        return float(timeout) if timeout is not None else self.timeout

    def _capture_output(self):
        if self.debug >= 1:
            self.http_log = WritableObject()
            sys.stdout = self.http_log

    def _print_debug(self):
        if self.debug >= 1:
            sys.stdout = sys.__stdout__  # Restore stdout
            debug_info = ''.join(
                self.http_log.content).replace(
                '\\r',
                '').decode('string_escape').replace(
                '\'',
                '')

            # Remove empty lines
            debug_info = "\n".join(
                [ll.rstrip() for ll in debug_info.splitlines() if ll.strip()])
            self.builtin.log(debug_info, 'DEBUG')

    def _json_pretty_print(self, content):
        """ Pretty print a JSON object

        'content'  JSON object to pretty print
        """
        temp = json.loads(content)
        return json.dumps(
            temp,
            sort_keys=True,
            indent=4,
            separators=(
                ',',
                ': '))

    def _utf8_urlencode(self, data):
        if isinstance(data, unicode):
            return data.encode('utf-8')

        if not isinstance(data, dict):
            return data

        utf8_data = {}
        for k, v in data.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            utf8_data[k] = v
        return urlencode(utf8_data)

    def _format_data_according_to_header(self, data, headers):
        if data is not None and headers is not None and 'Content-Type' in headers and not self._is_json(data):
            if headers['Content-Type'].find("application/json") != -1:
                data = json.dumps(data)
            elif headers['Content-Type'].find("application/x-www-form-urlencoded") != -1:
                data = self._utf8_urlencode(data)
        else:
            data = self._utf8_urlencode(data)

        return data

    @staticmethod
    def _is_json(data):
        try:
            json.loads(data)
        except (TypeError, ValueError):
            return False
        return True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Error')