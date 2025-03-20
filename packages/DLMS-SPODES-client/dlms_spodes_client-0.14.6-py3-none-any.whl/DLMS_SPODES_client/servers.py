from dataclasses import dataclass, field
from typing import Optional
from threading import Thread, Event
from functools import cached_property
import asyncio
from DLMSCommunicationProfile.osi import OSI
from .client import Client, Errors, cdt
from . import task
from DLMS_SPODES import exceptions as exc
from .logger import LogLevel as logL


# todo: join with StructResult.Result
@dataclass(eq=False)
class Result:
    client: Client
    complete: bool = False
    """complete exchange"""
    errors: Errors = field(default_factory=Errors)
    value: Optional[cdt.CommonDataType] = None
    """response if available"""

    async def session(self,
                      t: task.ExTask):
        self.client.lock.acquire(timeout=10)  # 10 second, todo: keep parameter anywhere
        # try media open
        assert self.client.media is not None, F"media is absense"
        self.value = await t.run(self.client)
        self.client.lock.release()
        self.complete = True
        self.errors = self.client.errors
        # media close
        if not self.client.lock.locked():
            self.client.lock.acquire(timeout=1)
            if self.client.media.is_open():
                self.client.log(logL.DEB, F"close communication channel: {self.client.media}")
                await self.client.media.close()
            else:
                self.client.log(logL.WARN, F"communication channel: {self.client.media} already closed")
            self.client.lock.release()
            self.client.level = OSI.NONE
        else:
            """opened media use in other session"""

    def __hash__(self):
        return hash(self.client)


class Results:
    __values: tuple[Result, ...]
    name: str
    tsk: task.ExTask

    def __init__(self, clients: tuple[Client],
                 tsk: task.ExTask,
                 name: str = None):
        self.__values = tuple(Result(c) for c in clients)
        self.tsk = tsk
        self.name = name
        """common operation name"""

    def __getitem__(self, item) -> Result:
        return self.__values[item]

    @cached_property
    def clients(self) -> set[Client]:
        return {res.client for res in self.__values}

    @cached_property
    def ok_results(self) -> list[Result]:
        """without errors exchange clients"""
        res: Result
        ret = set()
        for res in self.__values:
            if all(map(lambda err_code: err_code.is_ok(), res.errors)):
                if res.value is None:
                    ...
                elif isinstance(res.value, exc.ResultError):
                    continue
                elif (
                    isinstance(res.value, list)
                    and any(map(lambda val: isinstance(val, exc.ResultError), res.value))
                ):
                    continue
                ret.add(res)
        return ret

    @cached_property
    def nok_results(self) -> set[Result]:
        """ With errors exchange clients """
        return set(self.__values).difference(self.ok_results)

    def is_complete(self) -> bool:
        return all((res.complete for res in self))


class TransactionServer:
    __t: Thread
    results: Results

    def __init__(self,
                 clients: list[Client] | tuple[Client],
                 tsk: task.ExTask,
                 name: str = None,
                 abort_timeout: int = 1):
        self.results = Results(clients, tsk, name)
        # self._tg = None
        self.__stop = Event()
        self.__t = Thread(
            target=self.__start_coro,
            args=(self.results, abort_timeout))

    def start(self):
        self.__t.start()

    def abort(self):
        self.__stop.set()

    def __start_coro(self, results, abort_timeout):
        asyncio.run(self.coro_loop(results, abort_timeout))

    async def coro_loop(self, results: Results, abort_timeout: int):
        async def check_stop(tg: asyncio.TaskGroup):
            while True:
                await asyncio.sleep(abort_timeout)
                if results.is_complete():
                    break
                elif self.__stop.is_set():
                    tg._abort()
                    break

        async with asyncio.TaskGroup() as tg:
            for res in results:
                # tg.create_task(
                    # coro=session(
                    #     c=res.client,
                    #     t=results.tsk,
                    #     result=res))
                tg.create_task(res.session(results.tsk))
            tg.create_task(
                coro=check_stop(tg),
                name="wait abort task")


async def session(c: Client,  # todo: move to Result as method
                  t: task.ExTask,
                  result: Result):
    if not result:  # if not use TransActionServer
        result = Result(c)
    c.lock.acquire(timeout=10)  # 10 second, todo: keep parameter anywhere
    # try media open
    assert c.media is not None, F"media is absense"
    result.value = await t.run(c)
    c.lock.release()
    result.complete = True
    result.errors = c.errors
    # media close
    if not c.lock.locked():
        c.lock.acquire(timeout=1)
        if c.media.is_open():
            await c.media.close()
            c.log(logL.DEB, F'Close communication channel: {c.media}')
        c.lock.release()
        c.level = OSI.NONE
    else:
        """opened media use in other session"""
    return result
