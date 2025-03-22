from django.urls import get_resolver


def get_all_urls():
    resolver = get_resolver()
    all_urls = []

    def extract_urls(patterns, namespace=""):
        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                new_namespace = (
                    namespace + pattern.namespace + ":"
                    if pattern.namespace
                    else namespace
                )
                extract_urls(pattern.url_patterns, new_namespace)
            if hasattr(pattern, "pattern"):
                url = namespace + pattern.pattern.regex.pattern
                callback = pattern.callback
                if callback:
                    callback_info = f"{callback.__module__}.{callback.__name__}"
                else:
                    callback_info = "No callback"
                all_urls.append((url, callback_info))

    extract_urls(resolver.url_patterns)
    return all_urls
