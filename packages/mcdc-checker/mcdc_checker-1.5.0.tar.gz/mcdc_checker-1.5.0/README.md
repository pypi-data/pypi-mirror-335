# GTD MCDC Checker

This repository contains a tool to check all conditions in your C/C++ source code if they are in
the necessary form, so that Gcov can generate modified condition decision
coverage. This tool requires LLVM/Clang 19 or newer to be installed.

## Documentation

For instructions on how to setup and use this Tool, please refer to the
[Documentation](https://gtd-gmbh.gitlab.io/mcdc-checker/mcdc-checker).

## License

The MCDC Checker source code implemented by GTD GmbH is subject to the Mozilla Public License 2.0
as indicated by the headers of the corresponding source code files. Third party libraries used
herein are subject to their own licence terms, which is the BSD license for Clang itself and
patches to its source code as well as the PBL and PBDD libraries.
