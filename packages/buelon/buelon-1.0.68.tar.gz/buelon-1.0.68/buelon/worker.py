import asyncio
from buelon.hub import run_worker, work as _work


def run():
    run_worker()


def work():
    asyncio.run(_work())


if __name__ == '__main__':
    run()
