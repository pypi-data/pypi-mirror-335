import asyncio
from typing import AsyncGenerator, Awaitable, Callable, List, Tuple, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def get_all_items(queue: asyncio.Queue):
    """Get all items from the queue without waiting."""
    items = []
    try:
        while True:
            item = queue.get_nowait()
            items.append(item)
    except asyncio.QueueEmpty:
        # Once the queue is empty, get_nowait raises QueueEmpty, and we stop
        pass
    return items


def set_event_loop_if_not_exist():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError' will be raised if there is no running loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def retry_predicate(
    pred: Callable[[], Awaitable[bool]], max_retries: int, delay_secs: float
) -> Callable[[], Awaitable[bool]]:
    async def wrapper():
        for attempt in range(max_retries):
            try:
                if await pred():
                    return True
            except Exception:
                pass
            if attempt < max_retries - 1:
                await asyncio.sleep(delay_secs)
        return False

    return wrapper


def predicate_with_timeout(
    pred: Callable[[], Awaitable[bool]], timeout_secs: float
) -> Callable[[], Awaitable[bool]]:
    async def wrapper():
        try:
            return await asyncio.wait_for(pred(), timeout=timeout_secs)
        except Exception:
            return False

    return wrapper


async def interleave_generators(*generators: AsyncGenerator[T, None]) -> AsyncGenerator[T, None]:
    """Interleaves multiple generators."""
    queue = asyncio.Queue()
    active = len(generators)

    async def feed_queue(generator: AsyncGenerator[T, None]):
        nonlocal active
        try:
            async for item in generator:
                await queue.put(item)
        except Exception as e:
            await queue.put(e)
        finally:
            active -= 1

    try:
        tasks = [asyncio.create_task(feed_queue(generator)) for generator in generators]

        while active > 0 or not queue.empty():
            item_or_exception = await queue.get()
            if isinstance(item_or_exception, Exception):
                raise item_or_exception
            yield item_or_exception
    finally:
        pending_tasks = [t for t in tasks if not t.done()]
        for task in pending_tasks:
            task.cancel()
        if pending_tasks:
            await asyncio.gather(*pending_tasks, return_exceptions=True)


async def try_advance_generator(generator: AsyncGenerator[T, None]) -> AsyncGenerator[T, None]:
    """Advances a generator once and returns the original generator with all items.

    Useful if an error might be thrown on the first iteration that needs to be caught.
    """
    it = aiter(generator)
    try:
        first = await anext(it)

        async def gen():
            yield first
            async for x in it:
                yield x

        return gen()
    except StopAsyncIteration:
        empty_list: List[T] = []

        async def gen():
            for x in empty_list:
                yield x

        return gen()


async def tap_generator(
    generator: AsyncGenerator[T, None], fn: Callable[[T], None]
) -> AsyncGenerator[T, None]:
    """Applies a function to each element of a generator without modifying the sequence."""
    async for item in generator:
        fn(item)
        yield item


async def map_generator(
    generator: AsyncGenerator[T, None], fn: Callable[[T], U]
) -> AsyncGenerator[U, None]:
    """Transforms each element of a generator."""
    async for item in generator:
        yield fn(item)


async def aenumerate(
    generator: AsyncGenerator[T, None], start: int = 0
) -> AsyncGenerator[Tuple[int, T], None]:
    i = start
    async for item in generator:
        yield i, item
        i += 1


async def ajoin(generator: AsyncGenerator[str, None], separator: str = "") -> str:
    result = ""
    first = True
    async for item in generator:
        if first:
            result = item
            first = False
        else:
            result += separator + item
    return result
