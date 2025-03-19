```python
import asyncio
import dataclasses
import logging

from examples.books.messages import CreateBook, BookCreated, BookQuery
from examples.books.models import Book
from iambus import dispatcher as dp
from iambus.core import signals


# somewhere in your code
async def create_book_handler(command: CreateBook) -> BookCreated:
    """Create book"""

    # simplify for example
    print(f'got command {command}')
    book = Book(**dataclasses.asdict(command))

    # returning the event leads to emitting it by the dispatcher,
    # another way to do that will be described in classes example
    return BookCreated(book=book)


async def book_created_handler(event: BookCreated, storage: dict) -> None:
    """Handle book creation"""
    print(f'got event {event}')
    book = event.book
    storage[book.title] = book


async def book_query_handler(query: BookQuery, storage: dict) -> list[Book]:
    """Handle book query"""
    # find books in storage...
    books = [book for title, book in storage.items() if title == query.title]
    print(f"got query {query}, found {len(books)} books")
    return books


async def on_start() -> None:
    """Handlers without message argument also can be used"""
    # do something on startup
    print('application started')


async def main() -> None:
    """Application entrypoint"""
    logging.basicConfig(level=logging.DEBUG)

    # simple dictionary storage for example
    storage = {}

    dp.commands.bind(CreateBook, handler=create_book_handler, response_event=BookCreated)
    dp.events.bind(BookCreated, handler=book_created_handler, storage=storage)
    dp.queries.bind(BookQuery, handler=book_query_handler, storage=storage)

    # you can also use strings for message identifiers
    dp.events.bind('on startup', handler=on_start)

    dp.start()  # start router's engines

    await dp.events.handle('on startup')
    await dp.handle(
        CreateBook(title="Philosopher's Stone", author="J. K. Rowling", year=1997),
        key='createBook', wait_for_response=True,
    )
    await asyncio.sleep(0.2)  # ! CreateBook command will be executed without blocking
    books = await dp.handle(
        BookQuery(title="Philosopher's Stone"), wait_for_response=True,
        key='createBook',
    )
    print(f'found {books=}')

    await signals.wait_for_shutdown()


if __name__ == '__main__':
    asyncio.run(main())

```