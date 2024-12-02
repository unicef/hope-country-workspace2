from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_response_headers
from django.utils.deprecation import MiddlewareMixin

from country_workspace.cache.manager import cache_manager


class UpdateCacheMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.page_timeout = 10
        self.manager = cache_manager

    def _should_update_cache(self, request, response):
        return hasattr(request, "_cache_update_cache") and request._cache_update_cache

    def process_response(self, request, response):
        """Set the cache, if needed."""
        if not self._should_update_cache(request, response):
            # We don't need to update the cache, just return.
            return response

        if response.streaming or response.status_code not in (200, 304):
            return response

        # Don't cache responses that set a user-specific (and maybe security
        # sensitive) cookie in response to a cookie-less request.
        # if not request.COOKIES and response.cookies and has_vary_header(response, "Cookie"):
        #     return response

        # Don't cache a response with 'Cache-Control: private'
        if "private" in response.get("Cache-Control", ()):
            return response

        # Page timeout takes precedence over the "max-age" and the default
        # cache timeout.
        timeout = self.page_timeout
        # if timeout is None:
        #     # The timeout from the "max-age" section of the "Cache-Control"
        #     # header takes precedence over the default cache timeout.
        #     timeout = get_max_age(response)
        #     if timeout is None:
        #         timeout = self.cache_timeout
        #     elif timeout == 0:
        #         # max-age was set to 0, don't cache.
        #         return response
        patch_response_headers(response, timeout)
        if response.status_code == 200:
            cache_key = self.manager.build_key_from_request(request)
            response.headers["Etag"] = cache_key
            if hasattr(response, "render") and callable(response.render):
                response.add_post_render_callback(lambda r: self.manager.store(cache_key, r))
            else:
                self.manager.store(cache_key, response)
        return response


class FetchFromCacheMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.manager = cache_manager

    def process_request(self, request):
        if request.method not in ("GET", "HEAD"):
            request._cache_update_cache = False
            return None  # Don't bother checking the cache.

        # try and get the cached GET response
        # cache_key = get_cache_key(request, self.key_prefix, "GET", cache=self.cache)
        cache_key = self.manager.build_key_from_request(request)
        if cache_key is None:
            request._cache_update_cache = True
            return None  # No cache information available, need to rebuild.
        if request.headers.get("etag") == cache_key:
            return HttpResponse(status=304, headers={"Etag": cache_key})
        response = self.manager.retrieve(cache_key)
        # if it wasn't found and we are looking for a HEAD, try looking just for that
        # if response is None and request.method == "HEAD":
        #     cache_key = get_cache_key(request, self.key_prefix, "HEAD", cache=self.cache)
        #     response = self.manager.get(cache_key)

        if response is None:
            request._cache_update_cache = True
            return None  # No cache information available, need to rebuild.

        # hit, return cached response
        request._cache_update_cache = False

        return response
