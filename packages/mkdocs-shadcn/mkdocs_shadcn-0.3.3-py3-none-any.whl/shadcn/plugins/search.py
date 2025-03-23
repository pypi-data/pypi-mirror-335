from typing import Set

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.contrib.search import SearchPlugin as BaseSearchPlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from shadcn.filters import setattribute


class SearchPlugin(BaseSearchPlugin):
    """⚠️ HACK ⚠️
    Custom plugin. As search is load by default, we subclass it so as
    to inject what we want (and without adding a list of additional plugins)
    """

    page_index = 0
    page_indices: Set[int] = set()

    def on_env(self, env, /, *, config: MkDocsConfig, files: Files):
        # custom jinja2 filter
        env.filters["setattribute"] = setattribute
        return env

    def on_page_markdown(
        self,
        markdown: str,
        /,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ):
        # add order to page if not defined
        page.meta["order"] = page.meta.get("order", self.page_index)
        self.page_indices.add(self.page_index)
        # increment page index
        while self.page_index in self.page_indices:
            self.page_index += 1
        return markdown
