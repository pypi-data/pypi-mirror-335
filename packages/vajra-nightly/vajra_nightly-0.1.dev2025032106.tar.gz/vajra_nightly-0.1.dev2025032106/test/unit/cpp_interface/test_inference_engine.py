import copy
import pickle

import pytest

from vajra.config import (
    BaseEndpointConfig,
    InferenceEngineConfig,
    LlmReplicasetControllerConfig,
)


@pytest.mark.parametrize(
    "controller_config, output_dir, replica_resource_mapping",
    [
        (LlmReplicasetControllerConfig(), ".", None),
        (LlmReplicasetControllerConfig(), "/tmp/test", {1: [("127.0.0.1", 0)]}),
        (
            LlmReplicasetControllerConfig(),
            "/var/log",
            {2: [("192.168.1.1", 0), ("192.168.1.2", 1)]},
        ),
    ],
)
@pytest.mark.unit
def test_valid_inference_engine_config_creation(
    controller_config, output_dir, replica_resource_mapping
):
    """Tests creating valid InferenceEngineConfig objects and accessing their properties."""
    config = InferenceEngineConfig(
        controller_config=controller_config,
        output_dir=output_dir,
        replica_resource_mapping=replica_resource_mapping,
    )
    config_c = config.native_handle
    assert config.output_dir == config_c.output_dir
    assert config.replica_resource_mapping == config_c.replica_resource_mapping
    # assert config.controller_config == config_c.controller_config


@pytest.mark.parametrize(
    "controller_config, output_dir, replica_resource_mapping",
    [
        (LlmReplicasetControllerConfig(), ".", None),
        (LlmReplicasetControllerConfig(), "/tmp/test", {1: [("127.0.0.1", 0)]}),
        (
            LlmReplicasetControllerConfig(),
            "/var/log",
            {2: [("192.168.1.1", 0), ("192.168.1.2", 1)]},
        ),
    ],
)
@pytest.mark.unit
def test_can_deep_copy_inference_engine_config(
    controller_config, output_dir, replica_resource_mapping
):
    """Tests deep copying valid InferenceEngineConfig objects and accessing their properties."""
    config = InferenceEngineConfig(
        controller_config=controller_config,
        output_dir=output_dir,
        replica_resource_mapping=replica_resource_mapping,
    )
    config_deep_copy = copy.deepcopy(config)
    assert config.output_dir == config_deep_copy.output_dir
    # assert config.controller_config == config_deep_copy.controller_config
    assert config.replica_resource_mapping == config_deep_copy.replica_resource_mapping


@pytest.mark.parametrize(
    "controller_config, output_dir, replica_resource_mapping",
    [
        (LlmReplicasetControllerConfig(), ".", None),
        (LlmReplicasetControllerConfig(), "/tmp/test", {1: [("127.0.0.1", 0)]}),
        (
            LlmReplicasetControllerConfig(),
            "/var/log",
            {2: [("192.168.1.1", 0), ("192.168.1.2", 1)]},
        ),
    ],
)
@pytest.mark.unit
def test_can_pickle_inference_engine_config(
    controller_config, output_dir, replica_resource_mapping
):
    """Tests pickling InferenceEngineConfig objects and accessing their properties."""
    config = InferenceEngineConfig(
        controller_config=controller_config,
        output_dir=output_dir,
        replica_resource_mapping=replica_resource_mapping,
    )
    pickled_config = pickle.dumps(config)

    config_from_pickle = pickle.loads(pickled_config)

    assert config.output_dir == config_from_pickle.output_dir
    # assert type(config.controller_config) == type(config_from_pickle.controller_config)
    assert (
        config.replica_resource_mapping == config_from_pickle.replica_resource_mapping
    )


@pytest.mark.parametrize(
    "log_level, output_dir",
    [("info", "output"), ("debug", "/tmp/test"), ("warning", "/var/log")],
)
@pytest.mark.unit
def test_valid_base_endpoint_config_creation(log_level, output_dir):
    """Tests creating valid BaseEndpointConfig objects and accessing their properties."""

    config = BaseEndpointConfig(
        inference_engine_config=InferenceEngineConfig(),
        log_level=log_level,
        output_dir=output_dir,
    )
    config_c = config.native_handle
    assert config.log_level == config_c.log_level
    assert config.output_dir == config_c.output_dir
    assert config.inference_engine_config.output_dir == config.output_dir


@pytest.mark.parametrize(
    "log_level, output_dir",
    [("info", "output"), ("debug", "/tmp/test"), ("warning", "/var/log")],
)
@pytest.mark.unit
def test_can_deep_copy_base_endpoint_config(log_level, output_dir):
    """Tests deep copying BaseEndpointConfig objects and accessing their properties."""

    config = BaseEndpointConfig(
        log_level=log_level,
        output_dir=output_dir,
        inference_engine_config=InferenceEngineConfig(),
    )
    config_deep_copy = copy.deepcopy(config)
    assert config.log_level == config_deep_copy.log_level
    assert config.output_dir == config_deep_copy.output_dir
    assert (
        config.inference_engine_config.output_dir
        == config_deep_copy.inference_engine_config.output_dir
    )


@pytest.mark.parametrize(
    "log_level, output_dir",
    [("info", "output"), ("debug", "/tmp/test"), ("warning", "/var/log")],
)
@pytest.mark.unit
def test_can_pickle_base_endpoint_config(log_level, output_dir):
    """Tests pickling BaseEndpointConfig objects and accessing their properties."""

    config = BaseEndpointConfig(
        log_level=log_level,
        output_dir=output_dir,
        inference_engine_config=InferenceEngineConfig(),
    )
    pickled_config = pickle.dumps(config)
    config_from_pickle = pickle.loads(pickled_config)
    assert config.log_level == config_from_pickle.log_level
    assert config.output_dir == config_from_pickle.output_dir
    assert (
        config.inference_engine_config.output_dir
        == config_from_pickle.inference_engine_config.output_dir
    )
