# CHANGELOG

Included is a summary of changes to the project, by version. Details can be found in the commit history.

## v2.0.2

### Bugfixes

* Paths for files in the `pages/` root no longer have an extra `./` in them, which made URLs look ugly and also added an
  extra blank breadcrumb in the breadcrumbs.

### Improvements

* `custom-static` in the instance dir is now ignored and has no special handling --- put static files in `pages/static/`
  like all the other files that get copied. This also fixes a bug where the build errored if the directory didn't exist.
* Some README typos fixed.

## v2.0.1

### Improvements

* The `Image` tag in Markdown files no longer requires the full URL to be specified. Now `Config.BASE_HOST` is
  prepended to the tag value, which should be the full path to the image.
* `.files` are skipped when copying files to the SSG output directory.

## v2.0.0

### Features

* The project has been rewritten as a static site generator. This is of course a larger change than one line, so see the
  commit involved for the nitty gritty.
* Notably, this means I am now --- yes :( --- shipping some JavaScript, to handle the style switching, which is all
  client-side now.
* CHANGELOG.md added.
