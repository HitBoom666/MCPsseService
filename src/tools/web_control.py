import logging
import webbrowser

logger = logging.getLogger(__name__)

def open_website(url: str):
    try:
        logger.info(f"Open website, url: {url}")
        # make sure the url is correct
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # open the website
        webbrowser.open(url)
        return f"Open website: {url}"
    except Exception as e:
        return f"Open website failed: {str(e)}" 