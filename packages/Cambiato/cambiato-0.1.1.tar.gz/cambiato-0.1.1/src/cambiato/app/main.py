r"""The entry point of the Cambiato web app."""

# Standard library
from pathlib import Path

# Third party
import streamlit as st

# Local
from cambiato.app._pages import Pages

APP_PATH = Path(__file__)


def main() -> None:
    r"""The page router of the Cambiato web app."""

    pages = [st.Page(page=Pages.HOME, title='Home', default=True)]
    page = st.navigation(pages, position='sidebar')
    page.run()


if __name__ == '__main__':
    main()
