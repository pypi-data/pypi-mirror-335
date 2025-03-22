import shutil
import subprocess
from pathlib import Path

from rich.console import Console

console = Console()


def shell(
    opts: str | list, popen: bool = False, path: str = None, error_msg: bool = True, raise_error: bool = False
) -> str | subprocess.CompletedProcess[bytes] | subprocess.Popen:
    try:
        if popen:
            retcode: subprocess.Popen = subprocess.Popen(
                opts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=path
            )
            # retcode = retcode.communicate()[0].decode("utf-8")
            return retcode
        else:
            retcode: subprocess.CompletedProcess[bytes] = subprocess.run(
                opts, stderr=subprocess.STDOUT, shell=True, cwd=path
            )
            if error_msg and retcode.returncode != 0:
                print(f"\n---- subprocess code:{retcode.returncode} ----\n{retcode.args}\n-----------------------------\n")
    except subprocess.CalledProcessError:
        print(opts)

    if raise_error and retcode.returncode != 0:
        raise ValueError("run subprocess error")

    return retcode


class CMake:
    """
    CMake class for managing build processes with CMake.

    Example:
        cmake = CMake(generator="Ninja Multi-Config")
        cmake.clean(deep=True)
        cmake.setup().build()
    """

    def __init__(
        self, build_dir: str = "build", generator: str = None, toolchain: str = None, excu: bool = True, quiet: bool = True
    ) -> None:
        """
        Initializes the CMake class instance with optional parameters for build configuration.

        Parameters:
            build_dir (str): Directory for build files. Defaults to "build".
            generator (str): CMake generator (e.g., "Ninja"). Defaults to None.
            toolchain (str): Path to toolchain file. Defaults to None.
            excu (bool): Whether to execute commands. Defaults to True.
            quiet (bool): Suppress command output if True. Defaults to True.
        """

        self.build_dir: str = build_dir
        self.generator: str = generator
        self.toolchain: str = toolchain
        self.excu: bool = excu
        self.quiet: bool = quiet
        self.cmd: str = ""

    def __excu(self, cmd: str = None, message: str = None) -> None:
        """
        Private method to execute a shell command.

        Parameters:
            cmd (str): Command to execute. Uses self.cmd if not provided.
            message (str): Status message to display during execution.
        """
        self.cmd = cmd or self.cmd

        if self.excu:
            rtn = shell(self.cmd, popen=self.quiet)
            if self.quiet:
                with console.status(f"{message} ..."):
                    self.shell_msg = rtn.communicate()
                    self.shell_msg = self.shell_msg[0].decode("utf-8")
                if rtn.returncode != 0:
                    console.print(self.shell_msg)
            self.is_ok = rtn.returncode == 0
        else:
            console.print(self.cmd)

    def clean(self, deep: bool = False) -> "CMake":
        """
        Clean the build directory. Optionally remove the entire directory if deep is True.

        Parameters:
            deep (bool): If True, delete the entire build directory. Default is False.

        Returns:
            self (CMake): Self instance for method chaining.
        """

        cmd = f"cmake --build {self.build_dir} -t clean"

        build_dir = Path(self.build_dir)
        if not build_dir.exists():
            return self

        self.__excu(cmd, "Clean")

        if deep:
            shutil.rmtree(build_dir)

        return self

    def setup(
        self, generator: str = None, toolchain: str = None, options: str | list[str] = None, defs: str | list[str] = None
    ) -> "CMake":
        """
        Configure the CMake project with the provided generator, toolchain, options, and definitions.

        Parameters:
            generator (str): CMake generator. Defaults to instance's generator.
            toolchain (str): Toolchain file path. Defaults to instance's toolchain.
            options (str | list[str]): Additional options.
            defs (str | list[str]): CMake definitions.

        Returns:
            self (CMake): Self instance for method chaining.
        """

        cmd = f"cmake . -B {self.build_dir} -UCMakeCache.txt"

        generator = generator or self.generator
        if generator is not None:
            cmd += f' -G "{self.generator}"'

        toolchain = toolchain or self.toolchain
        if toolchain is not None:
            cmd += f" -DCMAKE_TOOLCHAIN_FILE={toolchain}"

        if options:
            if isinstance(options, str):
                options = [options]
            cmd += f' {" ".join(options)}'

        if defs:
            if isinstance(defs, list):
                defs = " ".join([f"-D{d}" for d in defs])
            cmd += f' -D DEFS="{defs}"'

        self.__excu(cmd, "Setup")

        return self

    def build(self, config: str = None, parallel: int = 8) -> "CMake":
        """
        Build the CMake project with optional configuration and parallel execution.

        Parameters:
            config (str): Build configuration (e.g., "Debug", "Release").
            parallel (int): Number of parallel jobs. Default is 8.

        Returns:
            self (CMake): Self instance for method chaining.
        """

        cmd = f"cmake --build {self.build_dir}"

        if parallel is not None:
            cmd += f" -j{parallel}"

        if config is not None:
            cmd += f" --config {config.capitalize()}"

        self.__excu(cmd, "Build")

        return self
