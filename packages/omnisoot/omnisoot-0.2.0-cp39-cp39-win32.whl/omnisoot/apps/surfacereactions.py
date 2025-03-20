from ..lib._omnisoot import CFrenklachHACA
from .plugins import register

SURFACEREACTIONS_MODELS = [];

@register(SURFACEREACTIONS_MODELS)
class FrenklachHACA(CFrenklachHACA):
    serialized_name = "FrenklachHACA"
    def __init__(self, soot_gas):
        super().__init__(soot_gas);
