from __future__ import annotations


# start delvewheel patch
def _delvewheel_patch_1_10_0():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'flux_ws_module.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_0()
del _delvewheel_patch_1_10_0
# end delvewheel patch

from flux_ws_module._flux_ws_module import BaseExchangeConnector
from flux_ws_module._flux_ws_module import OkxConnector
from . import _flux_ws_module
__all__: list = ['OkxConnector', 'BaseExchangeConnector']
