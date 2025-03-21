
import torch
import torch.nn as nn

import dmx.compressor as dmx

SZ = 128

class MyModule(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(128, 128)

    def forward(self, x):
        y = self.linear(x)
        return y

def test_exported():
    m = MyModule()
    x = torch.ones((SZ,))
    # ep = torch.export.export(m, (x,))
    additional_mappings = {"aten.linear", dmx.nn.Linear}
    # dmx_m = dmx.modeling.DmxModel.from_torch(ep.module(), additional_dmx_aware_mappings=additional_mappings)
    dmx_m = dmx.modeling.DmxModel.from_torch(m, additional_dmx_aware_mappings=additional_mappings)
    y = dmx_m(x)
    print(dmx_m._gm)
    dmx_m._gm.graph.print_tabular()
