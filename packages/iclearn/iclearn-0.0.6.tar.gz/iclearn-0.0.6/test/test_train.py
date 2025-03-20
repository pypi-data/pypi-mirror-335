import os
from pathlib import Path
import json

from iclearn.cli.train import Config, write_config

from iccore.test_utils import get_test_output_dir  

# Test write_config() function
def test_write_config():
    work_dir = get_test_output_dir()

    # Create a Config instance 
    config = Config(
        num_epochs=10,
        num_batches=2,
        batch_size=5,
        learning_rate=0.02,
        node_id=0,
        num_nodes=1,
        num_gpus=0,
        local_rank=0,
        with_profiling=False,
        dataset_dir=work_dir/"dataset",
        result_dir=work_dir/"results"
    )

    # Write config to the result_dir
    write_config(config, config.result_dir)

    # Check if the config file exists in the result_dir
    config_file = config.result_dir / "config.json"
    assert config_file.exists(), "Expected config.json in the result_dir"

    # Load the config json back
    with open(config_file, 'r') as f:
        json_data = json.load(f)

    # Make a new Config instance with the json
    c = Config(**json_data)

    # Compare new config with the original instance 
    assert config == c, f"Config json files don't match: {config} != {c}"
