import logging
import os

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger()


def handler(request, context):
    print(f'Running tag_provider.handler with request: {request} and context: {context}')

    # Import here so the logging config is set
    import tag_provider
    provider = tag_provider.TagProvider()
    response = provider.handle(request, context)
    log.info(f'Response: {response}')
    return response
