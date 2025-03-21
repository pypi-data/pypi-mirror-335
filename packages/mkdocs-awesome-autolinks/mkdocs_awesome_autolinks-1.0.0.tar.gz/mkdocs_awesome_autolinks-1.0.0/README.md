# mkdocs-awesome-autolinks

The MkDocs Awesome Autolinks plugin makes it possible to link to pages and images without specifying the full path. For example if there is a page `project/general/overview.md` this plugin allows you to
link to the page from any other page with just using a part of the path like `[overview](overview.md)`
or `[overview](general/overview.md)`. This not only works for links to other pages but also to any
other type of file.

In addition to automatically resolving links this plugin complements the 
[Awesome Nav][awesome-pages] plugin when [using a * glob pattern][glob-pattern] to automatically include pages in the menu.  
Of course the order of menu entries is important, when pages are automatically included the sort
order determines the order in the menu. This can easily be influenced by prefixing a page name or
directory with a number for sorting. Unfortunately this also means that links will more easily break
because of file renaming.

This plugin can automatically remove a prefix from all parts of a link. For example if there is a page `010-project/200-general/999-overview.md` this plugin allows you to
link to the page with `[overview](overview.md)`, `[overview](general/overview.md)` or 
`[overview](project/general/overview.md)`. Breaking links because of renaming a file to change the
sort order will no longer be an issue.

The functionality to remove a part of file and directory names can be disabled in `mkdocs.yml` and
the autolink functionality will continue to work.

[awesome-pages]: https://github.com/lukasgeiter/mkdocs-awesome-nav
[glob-pattern]: https://lukasgeiter.github.io/mkdocs-awesome-nav/features/nav/#glob-patterns

## Installation

> **Note:** This package requires Python >=3.7 and MkDocs version 1.4 or higher.  

Install the package with pip:

```bash
pip install mkdocs-awesome-autolinks
```

Enable the plugin in your `mkdocs.yml`:

```yaml
plugins:
    - awesome-autolinks
```

Configuration of the plugin is possible but not necessary if the default behavior suits your need.

## Usage
More information will be provided in the future. Here is a short summary of how the
automatic linking can be used.

* The default prefix that is automatically removed from all parts of a link has the following pattern:
One or more numbers followed by a `-`. For example `010-about.md` or
in case of a file in a directory `100-examples/010-about.md` will be replaced with `about.md`
and `examples/about.md`.<br>
You can define your own pattern in the config. Removal of a prefix can be disabled by setting
`remove_re` to an empty string.

* Instead of specifying the entire relative path in a link, include only the part of the destination that you are certain will remain unique. From here on
it will be called a *short link*.<br>
This plugin will replace a short link with the relative path to the page file it points to.
Normal MkDocs processing will transform the Markdown link with relative path to HTML.

* In case there is a short link on a page but there are multiple files in the whole docs directory
that match the path of that short link a warning will be logged. If configuration setting `warn_less`
is true, a warning is not logged if there is a single destination in the same directory branch of the page that contains the short link.

  So it is ok to have a link `[About](about.md)` on a page if file `about.md` is located somewhere in
a subdirectory of the directory where the page with the short link is located. Even if there are
other `about.md` files in other directory branches, as long as they can only be reached by going
higher up in the directory tree (do a ../ first).


## Configuration

The following configuration options can be set in `mkdocs.yml`. Values shown here are the default.

``` yaml
plugins:
  - awesome-autolinks:
      remove_re: '^[0-9]+-'
      warn_less: false
      warn_on_no_use: true
      ignore_dirs:
        - css
        - fonts
        - img
        - js
        - search
        - javascripts
        - assets/javascripts
      debug: false
```
