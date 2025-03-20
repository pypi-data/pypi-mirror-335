#
# Copyright (c) 2019, 2023, ducesoft and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import asyncio
import os

import mesh


async def main():
    os.environ.setdefault("mesh.mode", str(1 << 6))
    os.environ.setdefault("mesh.proc", str(3))
    os.environ.setdefault("mesh.address", "10.99.193.33:7304")
    os.environ.setdefault("mesh.runtime", "192.168.31.11:9999")
    await mesh.start()
    await mesh.wait()


if __name__ == '__main__':

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
