## 0.0.1 (2018-08-29): First release

* Initial commit

## 0.10.0 (2023-04-15)

* Migrated to poetry
* Enabled CI

## 0.10.1 (2025-03-10)

* Documentation:
  * Migrated to `pydata` theme.
  * Updated installation steps.
* Package:
  * Exposed `DEFAULT_CACHE_STORAGE_BASE_DIR`, `make_cache_dir`.
  * Updated `AUTHORS.md` and `HISTORY.md`.
* `DblpConnector`:
  * Improved `DocType` handling.
  * Implemented timer to mitigate rate limitation queries.
  * Fixed URL when data is fetched through the XML API.
* Bug fix:
  * Fixed `DocType.__str__`.
  * Fixed `Query.__str__`.
* Improved tests to be more robust to network failures:
  * `GoogleScholarConnector`.
  * `HalConnector`.
