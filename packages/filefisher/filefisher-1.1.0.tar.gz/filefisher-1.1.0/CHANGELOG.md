# Changelog

## v1.1.0 - 19.03.2025

Version v1.1.0 fixes a regression from v1.0.0 and adds `FileContainer.search_single`.

- Restore behavior of `FileContainer.search(key=None)` - passing `None` to `search` is ignored again ([#143](https://github.com/mpytools/filefisher/issues/143)).
- Added `FileContainer.search_single` to search for _exactly_ one path in a `FileContainer` ([#158](https://github.com/mpytools/filefisher/pull/158)).
- Fixed issues of non-unique `test_path` ([#139](https://github.com/mpytools/filefisher/issues/139)).

## v1.0.1 - 16.01.205
This version patches a bug from v1.0.0. that broke `FileContainer.concat()`.

- compare keys of two `FileContainer`s with `pandas.Index.equals()` instead of `is` in `FileContainer.concat()` ([#145](https://github.com/mpytools/filefisher/pull/145)) - this fixes a bug where no two FileContainers that are not the same object could be concatenated together, see [#143](https://github.com/mpytools/filefisher/issues/143).

## v1.0.0 - 07.01.2025

Version 1.0.0 renames the package to filefisher (from filefinder) and makes the first release to pypi. It includes some modifications of the `FileContainer` class to be more user friendly, allows concatenating two `FileContainers` and adds methods to find exactly one path or file. Defines and tests minimum supported versions of the dependencies and adds documentation on readthedocs.

- Renamed from filefinder to filefisher ([#131](https://github.com/mpytools/filefisher/pull/131)) and deprecated
  filefinder ([#132](https://github.com/mpytools/filefisher/pull/132))
- Added documentation for readthedocs ([#134](https://github.com/mpytools/filefisher/pull/134))
  and extended the documentation with usage ([#135](https://github.com/mpytools/filefisher/pull/135)) and
  installation instructions ([#136](https://github.com/mpytools/filefisher/pull/136)), as well as extension of the api documentation ([#141](https://github.com/mpytools/filefisher/pull/141))
- Added method to concatenate two FileContainers ([#126](https://github.com/mpytools/filefisher/pull/126))
- Added two methods to find _exactly_ one file or path (and raise an error otherwise):
  `FileFinder.find_single_file` and `FileFinder.find_single_path`
  ([#101](https://github.com/mpytools/filefisher/pull/101)).
- Raise an error if an unnamed placeholder (e.g., `"{}"`) is passed
  ([#110](https://github.com/mpytools/filefisher/pull/110))
- The `FileFinder.find_files` arguments `on_parse_error` and `_allow_empty` can no
  longer be passed by position ([#99](https://github.com/mpytools/filefisher/pull/99)).
- `FileFinder` now raises an error if an invalid `"{placeholder}"` is used
   ([#99](https://github.com/mpytools/filefisher/pull/99)).
- Define and test the minimum supported versions of the dependencies ([#125](https://github.com/mpytools/filefisher/pull/125)).

  | Package    | Old     | New    |
  | ---------- | ------- | ------ |
  | numpy      | undefined | 1.24 |
  | pandas     | undefined |  2.0 |
  | parse      | undefined | 1.19 |

- Changes to `FileContainer`:
  - An empty `FileContainer` is returned instead of an empty list when no files/ paths are
    found ([#114](https://github.com/mpytools/filefisher/pull/114))
  - Renamed the `"filename"` column to `"path"` and made it a `pd.Index`, thus removing
    this column from the underlying `DataFrame` ([#113](https://github.com/mpytools/filefisher/pull/113)).
  - Added `meta` and `paths` properties to `FileContainer` which allow to iterate over them
    ([#121](https://github.com/mpytools/filefisher/pull/121)).
  - Added `items()` method to `FileContainer`, which iterates over `path, meta`
    ([#128](https://github.com/mpytools/filefisher/pull/128)).
  - Deprecated iterating over `FileContainer`, use `.paths`, `.meta` or `items()` instead
    ([#128](https://github.com/mpytools/filefisher/pull/128)).
  - Deprecated `combine_by_key`, create a `pd.MultiIndex` instead
    ([#115](https://github.com/mpytools/filefisher/pull/115)).
  - Added the number of paths to the repr ([#116](https://github.com/mpytools/filefisher/pull/116)).
  - Added capability to concat two `FileContainer`s ([#126](https://github.com/mpytools/filefisher/pull/126)).
  - Refactor `FileContainer.search` using `isin` ([#117](https://github.com/mpytools/filefisher/pull/117)).

- Explicitly test on python 3.13 ([#103](https://github.com/mpytools/filefisher/pull/103)).
- Drop support for python 3.9 ([#102](https://github.com/mpytools/filefisher/pull/102)).

## v0.3.0 - 27.03.2024

New release that adds handling for parsing errors. It also drops python 3.7 and 3.8 support.

- Change `on_missing` option in the `priority_filter` from "error" to "raise".
  ([#79](https://github.com/mpytools/filefisher/pull/79))
- Drop support for python 3.7 and 3.8 ([#80](https://github.com/mpytools/filefisher/pull/80))
- Allow passing scalar numbers to `find_paths` and `find_files` ([#58](https://github.com/mpytools/filefisher/issues/58)).
- Show duplicates for non-unique queries
    ([#73](https://github.com/mpytools/filefisher/pull/73))
- Add options on how to handle parsing errors
    ([#75](https://github.com/mpytools/filefisher/pull/75))

## v0.2.0 - 23.05.2023

New release that allows to specify a format spec which allows parsing more complex file name structures. It also drops python 3.6 support and modernizes the build system.

- Allow passing format spec to the captured names to allow more precise name matching
  ([#57](https://github.com/mpytools/filefisher/pull/57)).
- Add tests for the cmip functionality and fix issue with `filefinder.cmip.ensure_unique_grid`
  ([#35](https://github.com/mpytools/filefisher/pull/35)).
- Removed support for python 3.6.
- Explicitly test python 3.11.

## v0.1.0 - 05.08.2022

- First version released based on the code developed for my IPCC AR6 analyses and including some additions (e.g. `priority_filter`, preferring `kwargs` over keys passed via a dictionary, more complete tests).
