"""
export PYTHONPATH=./
export TEST_CONFIG_CONFIG='config1.yaml;config2.yaml'
python3 ./test/single_process/__init__.py --config='config3.yaml;config4.yaml'
"""

import os

from tmp.single_process.test_config import config, manager, reload_config

CONFIG4_V1 = """
test:
  test_field4: 'test_field4'
"""

CONFIG4_V2 = """
test:
  test_field: 'test_field4'
  test_field2: 'test_field4'
  test_field3: 'test_field4'
  test_field4: 'test_field4'
"""


assert config.project.name == 'Test config'
assert config.project.version == '0.1.0'
assert config.is_production is True
assert config.mode == 'production'
assert config.test.test_field == 'test_field'
assert config.test.test_field2 == 'test_field2'
assert config.test.test_field3 == 'test_field3'
assert config.test.test_field4 == 'test_field4'


with open(os.path.join(manager.root_config_dir, 'config4.yaml'), 'w') as file:
    file.write(CONFIG4_V2)

reload_config()

assert config.test.test_field == 'test_field4'
assert config.test.test_field2 == 'test_field4'
assert config.test.test_field3 == 'test_field4'
assert config.test.test_field4 == 'test_field4'

with open(os.path.join(manager.root_config_dir, 'config4.yaml'), 'w') as file:
    file.write(CONFIG4_V1)
