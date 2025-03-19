```python
import asyncio
import dataclasses
import logging

from examples.books.messages import CreateBook, BookCreated, BookQuery
from examples.books.models import Book
from iambus import dispatcher as dp
from iambus.core import signals
from iambus.core.dependency.providers import Singleton


async def get_storage():
    """Dependency injection of storage."""
    return {}


# somewhere in your code
@dp.commands.register(CreateBook, response_event=BookCreated)
# ensure Singleton dependency name is the same that in handler's args
async def create_book_handler(command: CreateBook) -> BookCreated:
    """Create book"""

    # simplify for example
    print(f'got command {command}')
    book = Book(**dataclasses.asdict(command))

    # returning the event leads to emitting it by the dispatcher,
    # another way to do that will be described in classes example
    return BookCreated(book=book)


@dp.events.register(BookCreated, storage=Singleton["storage": get_storage])
async def book_created_handler(event: BookCreated, storage: dict) -> None:
    """Handle book creation"""
    print(f'got event {event}')
    book = event.book
    storage[book.title] = book


@dp.queries.register(BookQuery, storage=Singleton["storage": get_storage])
# ensure you did not reassign the type of provider (f.e. from Singleton to Factory)
async def book_query_handler(query: BookQuery, storage: dict) -> list[Book]:
    """Handle book query"""
    # find books in storage...
    books = [book for title, book in storage.items() if title == query.title]
    print(f"got query {query}, found {len(books)} books")
    return books


@dp.events.register('on startup')
# # you can also use strings for message identifiers
async def on_start() -> None:
    """Handlers without message argument also can be used"""
    # do something on startup
    print('application started')


async def main() -> None:
    """Application entrypoint"""
    logging.basicConfig(level=logging.DEBUG)

    dp.start()  # start router's engines

    await dp.handle('on startup')
    await dp.handle(
        CreateBook(title="Philosopher's Stone", author="J. K. Rowling", year=1997),
        key='createBook',
    )
    books = await dp.handle(
        BookQuery(title="Philosopher's Stone"), wait_for_response=True,
    )
    print(f"found {books=}")

    await signals.wait_for_shutdown()


if __name__ == '__main__':
    asyncio.run(main())

```