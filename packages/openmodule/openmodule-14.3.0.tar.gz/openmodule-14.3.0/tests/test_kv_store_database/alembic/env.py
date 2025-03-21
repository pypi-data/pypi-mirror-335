from openmodule.database.migration import run_env_py
from tests.test_utils_kv_store import Base

run_env_py([Base])
