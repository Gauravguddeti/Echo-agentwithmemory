import webbrowser
from urllib.parse import quote_plus

class WebManager:
    def search(self, query: str, engine="google"):
        if engine == "google":
            url = f"https://www.google.com/search?q={quote_plus(query)}"
        elif engine == "youtube":
            url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        else:
            url = f"https://www.google.com/search?q={quote_plus(query)}"
        
        webbrowser.open(url)
        return f"Searching {engine} for '{query}'"

    def open_url(self, url: str):
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opening {url}"

web_manager = WebManager()

def get_web_manager():
    return web_manager
