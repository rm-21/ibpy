# IBPY
An unofficial wrapper for the [Interactive Brokers Client Portal API](https://interactivebrokers.github.io/cpwebapi/). It's asynchronous!

# Requirements
* Preferrably, a running [`ibeam`](https://github.com/Voyz/ibeam) instance, or the Java client as described by IB [here](https://interactivebrokers.github.io/cpwebapi/quickstart)

# Example Usage
## As a context manager
```python
import logging
from pprint import pprint

logging.basicConfig(level=logging.DEBUG)

async def main() -> None:
    async with IBRest() as api:
        res = await api.tickle()
        pprint(res.model_dump())

if __name__ == "__main__":
    import asyncio

    asyncio.run(main=main())

```
## With `try-except`
```python
import logging
from pprint import pprint

logging.basicConfig(level=logging.DEBUG)

async def main() -> None:
    api = IBRest()
    try:
        res = await api.tickle()
        pprint(res.model_dump())
    finally:
        await api.close_http_client()

if __name__ == "__main__":
    import asyncio

    asyncio.run(main=main())

```
