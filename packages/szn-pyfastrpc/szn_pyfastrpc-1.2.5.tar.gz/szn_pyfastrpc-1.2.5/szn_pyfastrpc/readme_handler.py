# szn_pyfastrpc/readme_handler.py

from requests_html import HTMLSession

def fetch_and_print_readme() -> None:
    session = HTMLSession()
    r = session.get("https://opicevopice.github.io/")
    r.html.render(sleep=2)
    print(r.html.html)
