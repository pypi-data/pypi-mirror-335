# szn_pyfastrpc/open_readme.py

from .readme_handler import fetch_and_print_readme

def open_readme() -> None:
    """
    Entry point function that opens the README page from the specified URL.
    This function delegates to fetch_and_print_readme() in the readme_handler module.
    """
    fetch_and_print_readme()
