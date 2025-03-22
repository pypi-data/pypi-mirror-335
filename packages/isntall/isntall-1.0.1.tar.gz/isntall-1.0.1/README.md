# Testing reserved names for PyPI packages

PyPI prevents you from uploading a package with the same name as an existing package,
as well as reserved names. The package name `install` is reserved.
However, the name `isntall` - a common misspelling of `install` - is not.

This is a test project to see how often people misspell `install`.

After sufficient time, I will contact PyPI to see if they are willing to expand the list of reserved names to include common misspellings.

## Download stats

You can see the download stats yourself: https://pypistats.org/packages/isntall

The library indeed gets downloaded a few times every day.
