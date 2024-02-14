import logging
import os

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def handler(request, context):
    # Import here so the logging config is set
    import tag_provider

    return tag_provider.handler(request, context)
