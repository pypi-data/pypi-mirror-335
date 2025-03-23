import os

from pydantic import BaseModel

from qstd_config import ConfigManager, BaseConfig


CONFIG4_V1 = """
test:
  test_field4: 'test_field4'
"""


class Config(BaseConfig):
    class Test(BaseModel):
        test_field: str
        test_field2: str
        test_field3: str
        test_field4: str

    test: Test


manager = ConfigManager(
    Config,
    {
        'name': 'Test config',
        'version': '0.1.0'
    },
    root_config_dir=os.path.dirname(__file__),
    config_paths=[
        './config1.yaml',
        './config2.yaml',
        './config3.yaml',
        './config4.yaml'
    ]
)


with open(os.path.join(manager.root_config_dir, 'config4.yaml'), 'w') as file:
    file.write(CONFIG4_V1)

config = manager.load_config()


def reload_config():
    import importlib
    global config
    config = manager.load_config()
    importlib.reload(manager)
