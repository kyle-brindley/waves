pip check
set working_directory=%CD%
cd %SP_DIR%\%PKG_NAME%
pytest -vvv -n 4 -m "not require_third_party" --system-test-dir=%working_directory%
pytest -v -n 4 -m "systemtest and require_third_party" --tb=short --system-test-dir=%working_directory%
