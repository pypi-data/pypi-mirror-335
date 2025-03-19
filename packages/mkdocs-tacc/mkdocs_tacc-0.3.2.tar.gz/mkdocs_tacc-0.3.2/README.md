# MkDocs TACC Theme

A [TACC](https://www.tacc.utexas.edu/)-styled [MkDocs](https://www.mkdocs.org/) theme based on MkDocs' own [ReadTheDocs theme](https://www.mkdocs.org/user-guide/choosing-your-theme/#readthedocs).

## Quick Start

<!-- Keep these steps synced with /docs/index.md -->

1. Install the theme e.g.

    ```shell
    pip install mkdocs-tacc
    ```

2. Use the theme in your MkDocs project; set —

    ```yaml
    theme:
        name: tacc_readthedocs
    ```

    — in your `mkdocs.yml`.

3. Include _at least_ the [minimum set of extensions][exts] —

    ```yaml
    markdown_extensions:
      - toc:
          permalink: "" # i.e. `true` but without "¶"
          permalink_class: headerlink fa fa-link
          permalink_title: Link to Heading
    ```

    — in your `mkdocs.yml`.

[exts]: https://tacc.github.io/Core-Docs/extensions/#core-extensions

Learn to [configure](https://tacc.github.io/Core-Docs/configure/), [customize](https://tacc.github.io/Core-Docs/customize/), and [extend](https://tacc.github.io/Core-Docs/extensions/) your MkDocs site.

## Known Clients

| Status | Repository |
| - | - |
| Active | None |
| Upcoming | [TACC-Docs](https://github.com/TACC/TACC-Docs)<br>[DesignSafe-CI/DS-User-Guide](https://github.com/DesignSafe-CI/DS-User-Guide) |
| Potential | [TACC/containers_at_tacc](https://github.com/TACC/containers_at_tacc)<br>[TACC/life_sciences_ml_at_tacc](https://github.com/TACC/life_sciences_ml_at_tacc) |

## For Developers

Learn [how to **develop**](./DEVELOP.md) and [how to **deploy**](./DEPLOY.md).
