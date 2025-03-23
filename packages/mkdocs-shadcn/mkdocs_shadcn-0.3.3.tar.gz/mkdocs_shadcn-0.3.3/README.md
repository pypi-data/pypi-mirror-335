<p align="center">
  <a href="https://asiffer.github.io/mkdocs-shadcn/">
    <img src="https://raw.githubusercontent.com/asiffer/mkdocs-shadcn/master/.github/assets/logo.svg" width="320" alt="mkdocs-shadcn">
  </a>
</p>

<p align="center">
    <b>The sleek <a href="https://ui.shadcn.com/">shadcn theme</a> on top of <a href="https://www.mkdocs.org/">MkDocs</a></b>
</p>

> [!IMPORTANT]  
> This is an unofficial port of shadcn/ui to MkDocs, and is not affiliated with [@shadcn](https://twitter.com/shadcn).

## Documentation

Yes, yes, the [documentation](https://asiffer.github.io/mkdocs-shadcn/) is built with this theme.

## Quick start

`mkdocs-shadcn` can be installed with `pip`

```shell
pip install mkdocs-shadcn
```

Add the following line to `mkdocs.yml`:

```yaml
theme:
  name: shadcn
```

## Extensions

The theme tries to support the built-in extensions along with some `pymdownx` ones. 

- [x] [`admonition`](https://python-markdown.github.io/extensions/admonition/)
- [x] [`codehilite`](https://python-markdown.github.io/extensions/code_hilite/)
- [x] [`fenced_code`](https://python-markdown.github.io/extensions/fenced_code_blocks/)
- [x] [`pymdownx.tabbed`](https://facelessuser.github.io/pymdown-extensions/extensions/tabbed/)
- [x] [`pymdownx.blocks.details`](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/details/) 
- [x] [`pymdownx.blocks.tab`](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/tab/) 
- [x] [`pymdownx.progressbar`](https://facelessuser.github.io/pymdown-extensions/extensions/progressbar/)
- [x] [`pymdownx.arithmatex`](https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/)
- [ ] custom [`shadcn.echarts`](https://echarts.apache.org)