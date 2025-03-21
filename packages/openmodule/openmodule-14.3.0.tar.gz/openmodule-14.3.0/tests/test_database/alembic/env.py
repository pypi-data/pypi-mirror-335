from openmodule.database.migration import run_env_py
from tests.database_models_test import Base

run_env_py([Base])
