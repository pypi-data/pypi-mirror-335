from openmodule.database.migration import run_env_py
from tests.test_utils_access_service import Base

run_env_py([Base])
