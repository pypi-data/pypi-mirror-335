#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from mesh.kinds.principal import Principal
from mesh.macro import index, serializable


@serializable
class Location(Principal):

    @staticmethod
    async def localize(self: "Location"):
        from mesh.prsim import Network
        from mesh.macro import ServiceLoader
        import mesh.tool as tool
        network = ServiceLoader.load(Network).get_default()
        environ = await network.get_environ()
        self.inst_id = environ.inst_id
        self.node_id = environ.node_id
        self.ip = tool.get_mesh_direct()
        self.host = tool.get_hostname()
        self.port = f"{tool.get_mesh_runtime().port}"
        self.name = tool.get_mesh_name()

    @index(10)
    def ip(self) -> str:
        return ""

    @index(15)
    def port(self) -> str:
        return ""

    @index(20)
    def host(self) -> str:
        return ""

    @index(25)
    def name(self) -> str:
        return ""
