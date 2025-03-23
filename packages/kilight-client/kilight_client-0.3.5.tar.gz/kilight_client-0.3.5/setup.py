import os
from importlib.resources.abc import Traversable
from pathlib import Path
from setuptools.command.build import build
from setuptools import setup, Command
from grpc_tools import protoc
from importlib import resources


class BuildProtocol(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.build_lib: str | None = None
        self.editable_mode: bool | None = False
        self.kilight_protocol_proto_files: list[Path] | None = None
        self.kilight_protocol_out_dir: Path | None = None
        self.kilight_protocol_dir: Path = Path("lib/kilight-protocol")
        self.kilight_protocol_src_dir: Path = self.kilight_protocol_dir.joinpath("src")
        self.embeddedproto_include_dir: Path = self.kilight_protocol_dir.joinpath("lib/EmbeddedProto/generator")
        self.protobuf_include_dir: Traversable = resources.files("grpc_tools").joinpath("_proto")

    def initialize_options(self):
        """Initialize command state to defaults"""
        self.kilight_protocol_dir = Path("lib/kilight-protocol")
        self.kilight_protocol_src_dir = self.kilight_protocol_dir.joinpath("src")

    def finalize_options(self):
        self.set_undefined_options("build_py", ("build_lib", "build_lib"))

        if self.editable_mode:
            self.kilight_protocol_out_dir = Path("src")
        else:
            self.kilight_protocol_out_dir = Path(self.build_lib)

        if self.kilight_protocol_proto_files is None:
            self.kilight_protocol_proto_files = list(self.kilight_protocol_src_dir.glob("**/*.proto"))

    def run(self):
        print("Building KiLight protocol from Protobuf files...")
        base_arguments = [
            'protoc',
            f"--proto_path={self.protobuf_include_dir}",
            f"--proto_path={self.embeddedproto_include_dir.absolute()}",
            f"--proto_path={self.kilight_protocol_src_dir.absolute()}",
            f"--python_out={self.kilight_protocol_out_dir.absolute()}",
            f"--pyi_out={self.kilight_protocol_out_dir.absolute()}"
        ]
        current_dir = os.getcwd()
        for proto_file in self.kilight_protocol_proto_files:
            print(f"\t * {proto_file} -> {self._output_path_for_file(proto_file)}")
            absolute_proto_file = str(proto_file.absolute())
            os.chdir(self.kilight_protocol_src_dir)
            current_arguments = base_arguments.copy()
            current_arguments.append(absolute_proto_file)
            protoc.main(current_arguments)
            os.chdir(current_dir)

        embeddedproto_options_file = self.embeddedproto_include_dir.joinpath("embedded_proto_options.proto")
        absolute_proto_file = str(embeddedproto_options_file.absolute())
        print(f"\t * {embeddedproto_options_file} -> embedded_proto_options_pb2.py")
        os.chdir(self.embeddedproto_include_dir)
        current_arguments = base_arguments.copy()
        current_arguments.append(absolute_proto_file)
        protoc.main(current_arguments)
        os.chdir(current_dir)

    def _output_path_for_file(self, input_file: Path) -> Path:
        relative_to_protocol_src_path = input_file.relative_to(self.kilight_protocol_src_dir)
        return relative_to_protocol_src_path.with_stem(relative_to_protocol_src_path.stem + "_pb2").with_suffix('.py')

    def _output_stub_for_file(self, input_file: Path) -> Path:
        relative_to_protocol_src_path = input_file.relative_to(self.kilight_protocol_src_dir)
        return relative_to_protocol_src_path.with_stem(relative_to_protocol_src_path.stem + "_pb2").with_suffix('.pyi')

    def get_output_mapping(self):
        output_mapping = dict()

        build_root_path = Path("{build_lib}")
        for proto_file in self.kilight_protocol_proto_files:
            output_file = str(build_root_path.joinpath(self._output_path_for_file(proto_file)))
            output_stub = str(build_root_path.joinpath(self._output_stub_for_file(proto_file)))
            output_mapping[output_file] = str(proto_file)
            output_mapping[output_stub] = str(proto_file)

        embeddedproto_options_file = self.embeddedproto_include_dir.joinpath("embedded_proto_options.proto")
        embeddedproto_output_options_file = str(build_root_path.joinpath("embedded_proto_options_pb2.py"))
        embeddedproto_output_options_stub = str(build_root_path.joinpath("embedded_proto_options_pb2.pyi"))
        output_mapping[embeddedproto_output_options_file] = str(embeddedproto_options_file)
        output_mapping[embeddedproto_output_options_stub] = str(embeddedproto_options_file)
        return output_mapping

    def get_outputs(self):
        return self.get_output_mapping().keys()

    def get_source_files(self):
        return self.get_output_mapping().values()


build.sub_commands.append(("build_protocol", None))

setup(
    cmdclass={
        "build_protocol": BuildProtocol
    }
)
