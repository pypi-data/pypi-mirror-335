from setuptools import setup

name = "types-tensorflow"
description = "Typing stubs for tensorflow"
long_description = '''
## Typing stubs for tensorflow

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`tensorflow`](https://github.com/tensorflow/tensorflow) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `tensorflow`. This version of
`types-tensorflow` aims to provide accurate annotations for
`tensorflow~=2.18.0`.

Partially generated using [mypy-protobuf==3.6.0](https://github.com/nipunn1313/mypy-protobuf/tree/v3.6.0) and libprotoc 27.2 on `tensorflow==2.18.0`.

This stub package is marked as [partial](https://peps.python.org/pep-0561/#partial-stub-packages).
If you find that annotations are missing, feel free to contribute and help complete them.


This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/tensorflow`](https://github.com/python/typeshed/tree/main/stubs/tensorflow)
directory.

This package was tested with
mypy 1.15.0,
pyright 1.1.396,
and pytype 2024.10.11.
It was generated from typeshed commit
[`45e9a79e2644e5c561dc904f40f15c6659fe3234`](https://github.com/python/typeshed/commit/45e9a79e2644e5c561dc904f40f15c6659fe3234).
'''.lstrip()

setup(name=name,
      version="2.18.0.20250319",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/tensorflow.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-protobuf', 'types-requests', 'numpy>=1.20'],
      packages=['tensorflow-stubs'],
      package_data={'tensorflow-stubs': ['__init__.pyi', '_aliases.pyi', 'audio.pyi', 'autodiff.pyi', 'autograph/__init__.pyi', 'autograph/experimental.pyi', 'bitwise.pyi', 'compiler/xla/service/hlo_pb2.pyi', 'compiler/xla/service/hlo_profile_printer_data_pb2.pyi', 'compiler/xla/service/metrics_pb2.pyi', 'compiler/xla/service/test_compilation_environment_pb2.pyi', 'compiler/xla/service/xla_compile_result_pb2.pyi', 'compiler/xla/tsl/protobuf/bfc_memory_map_pb2.pyi', 'compiler/xla/tsl/protobuf/test_log_pb2.pyi', 'compiler/xla/xla_data_pb2.pyi', 'compiler/xla/xla_pb2.pyi', 'config/__init__.pyi', 'config/experimental.pyi', 'core/example/example_parser_configuration_pb2.pyi', 'core/example/example_pb2.pyi', 'core/example/feature_pb2.pyi', 'core/framework/allocation_description_pb2.pyi', 'core/framework/api_def_pb2.pyi', 'core/framework/attr_value_pb2.pyi', 'core/framework/cost_graph_pb2.pyi', 'core/framework/cpp_shape_inference_pb2.pyi', 'core/framework/dataset_metadata_pb2.pyi', 'core/framework/dataset_options_pb2.pyi', 'core/framework/dataset_pb2.pyi', 'core/framework/device_attributes_pb2.pyi', 'core/framework/full_type_pb2.pyi', 'core/framework/function_pb2.pyi', 'core/framework/graph_debug_info_pb2.pyi', 'core/framework/graph_pb2.pyi', 'core/framework/graph_transfer_info_pb2.pyi', 'core/framework/kernel_def_pb2.pyi', 'core/framework/log_memory_pb2.pyi', 'core/framework/model_pb2.pyi', 'core/framework/node_def_pb2.pyi', 'core/framework/op_def_pb2.pyi', 'core/framework/optimized_function_graph_pb2.pyi', 'core/framework/reader_base_pb2.pyi', 'core/framework/resource_handle_pb2.pyi', 'core/framework/step_stats_pb2.pyi', 'core/framework/summary_pb2.pyi', 'core/framework/tensor_description_pb2.pyi', 'core/framework/tensor_pb2.pyi', 'core/framework/tensor_shape_pb2.pyi', 'core/framework/tensor_slice_pb2.pyi', 'core/framework/types_pb2.pyi', 'core/framework/variable_pb2.pyi', 'core/framework/versions_pb2.pyi', 'core/protobuf/__init__.pyi', 'core/protobuf/bfc_memory_map_pb2.pyi', 'core/protobuf/cluster_pb2.pyi', 'core/protobuf/composite_tensor_variant_pb2.pyi', 'core/protobuf/config_pb2.pyi', 'core/protobuf/control_flow_pb2.pyi', 'core/protobuf/core_platform_payloads_pb2.pyi', 'core/protobuf/data_service_pb2.pyi', 'core/protobuf/debug_event_pb2.pyi', 'core/protobuf/debug_pb2.pyi', 'core/protobuf/device_filters_pb2.pyi', 'core/protobuf/device_properties_pb2.pyi', 'core/protobuf/error_codes_pb2.pyi', 'core/protobuf/fingerprint_pb2.pyi', 'core/protobuf/meta_graph_pb2.pyi', 'core/protobuf/named_tensor_pb2.pyi', 'core/protobuf/queue_runner_pb2.pyi', 'core/protobuf/remote_tensor_handle_pb2.pyi', 'core/protobuf/rewriter_config_pb2.pyi', 'core/protobuf/rpc_options_pb2.pyi', 'core/protobuf/saved_model_pb2.pyi', 'core/protobuf/saved_object_graph_pb2.pyi', 'core/protobuf/saver_pb2.pyi', 'core/protobuf/service_config_pb2.pyi', 'core/protobuf/snapshot_pb2.pyi', 'core/protobuf/status_pb2.pyi', 'core/protobuf/struct_pb2.pyi', 'core/protobuf/tensor_bundle_pb2.pyi', 'core/protobuf/tensorflow_server_pb2.pyi', 'core/protobuf/tpu/compilation_result_pb2.pyi', 'core/protobuf/tpu/dynamic_padding_pb2.pyi', 'core/protobuf/tpu/optimization_parameters_pb2.pyi', 'core/protobuf/tpu/topology_pb2.pyi', 'core/protobuf/tpu/tpu_embedding_configuration_pb2.pyi', 'core/protobuf/trackable_object_graph_pb2.pyi', 'core/protobuf/transport_options_pb2.pyi', 'core/protobuf/verifier_config_pb2.pyi', 'core/util/event_pb2.pyi', 'core/util/memmapped_file_system_pb2.pyi', 'core/util/saved_tensor_slice_pb2.pyi', 'core/util/test_log_pb2.pyi', 'data/__init__.pyi', 'data/experimental.pyi', 'distribute/__init__.pyi', 'distribute/coordinator.pyi', 'distribute/experimental/coordinator.pyi', 'dtypes.pyi', 'experimental/__init__.pyi', 'experimental/dtensor.pyi', 'feature_column/__init__.pyi', 'initializers.pyi', 'io/__init__.pyi', 'io/gfile.pyi', 'keras/__init__.pyi', 'keras/activations.pyi', 'keras/callbacks.pyi', 'keras/constraints.pyi', 'keras/initializers.pyi', 'keras/layers/__init__.pyi', 'keras/losses.pyi', 'keras/metrics.pyi', 'keras/models.pyi', 'keras/optimizers/__init__.pyi', 'keras/optimizers/legacy/__init__.pyi', 'keras/optimizers/schedules.pyi', 'keras/regularizers.pyi', 'linalg.pyi', 'math.pyi', 'nn.pyi', 'python/__init__.pyi', 'python/distribute/distribute_lib.pyi', 'python/feature_column/__init__.pyi', 'python/feature_column/feature_column_v2.pyi', 'python/feature_column/sequence_feature_column.pyi', 'python/framework/dtypes.pyi', 'python/keras/__init__.pyi', 'python/keras/protobuf/projector_config_pb2.pyi', 'python/keras/protobuf/saved_metadata_pb2.pyi', 'python/keras/protobuf/versions_pb2.pyi', 'python/trackable/__init__.pyi', 'python/trackable/autotrackable.pyi', 'python/trackable/base.pyi', 'python/trackable/resource.pyi', 'python/trackable/ressource.pyi', 'python/training/tracking/autotrackable.pyi', 'random.pyi', 'raw_ops.pyi', 'saved_model/__init__.pyi', 'saved_model/experimental.pyi', 'signal.pyi', 'sparse.pyi', 'strings.pyi', 'summary.pyi', 'train/__init__.pyi', 'train/experimental.pyi', 'tsl/protobuf/coordination_config_pb2.pyi', 'tsl/protobuf/coordination_service_pb2.pyi', 'tsl/protobuf/distributed_runtime_payloads_pb2.pyi', 'tsl/protobuf/dnn_pb2.pyi', 'tsl/protobuf/error_codes_pb2.pyi', 'tsl/protobuf/histogram_pb2.pyi', 'tsl/protobuf/rpc_options_pb2.pyi', 'tsl/protobuf/status_pb2.pyi', 'types/__init__.pyi', 'types/experimental.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0",
      python_requires=">=3.9",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
