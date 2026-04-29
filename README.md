# Investigate ArangoDB bulk loading issues

We're covering this issue here: https://github.com/suttacentral/suttacentral/issues/3618

And old commit explained:

```python
# python-arango import_bulk function is pretty dangerous to use
# in current version unless you set "halt_on_error=True" it silently
# ignores errors. But if you set "halt_on_error=True" you get an
# exception but lose the response body containing the error details
# so you have no idea what went wrong!
# It's pretty much a no-win.
# I expect this will be improved in the library in time but for now
# I'm patching in a more sensible version which always logs errors
# and can be told to raise an exception.
```

So there are two issues here:

- `import_bulk` silently ignores errors unless `halt_on_error=True`
- If you set `halt_on_error=True` you get an exception without the error details.

We have three versions of the `python-arango` package to test:

- `3.12.1`: Used when the comment was written.
- `7.5.3`: Currently used in SuttaCentral.
- `8.3.2`: The latest.

So... let's write some tests!

## Testing ArangoDB `3.12.1`

I needed to create a docker container given the age of the dependencies I wanted to replicate. 

I've used:

- Docker image `python:3.6.2`
- ArangoDB docker image `arangodb/arangodb:3.3.1`. We used `arangodb/arangodb` at the time but this would be the latest version available.
- A `requirements.txt` file with `python-arango==3.12.1` and the required dependencies to make it work.

To run the tests:

```commandline
docker compose up old-arango-db
docker compose run --build arango-bulk-test
```

You can explore the API in the Python REPL with this command:

```commandline
docker compose run python-interpreter
```

You can use the `help()` command in the REPL and so forth.

## Testing ArangoDB `7.5.3`

The setup here is much simpler. 

- Use the current SuttaCentral ArangoDB container.
- Set python version to `==3.11.3` 
- Add `python-arango` version `7.5.3` with `uv`. An older `setuptools` package was required.

In the suttacentral project:

```commandline
make run-dev-arango-only
```

Then to run the tests:

```commandline
uv run pytest
```

## Testing ArangoDB `8.3.2`

The setup is very similar to `7.5.3`. Just update the `python-arango` package and remove the old `setuptools` which is not required. Run the tests as above.

## What have we learned?

In `3.12.1` the documentation for `arango.collections.standard.Collection.import_bulk()` says

> `halt_on_error` – halt the entire import on an error (default: `True`)

When in fact the type signature is

```python
@api_method
def import_bulk(self,
                documents: list,
                halt_on_error: bool = None,
                details: bool = True,
                from_prefix: str = None,
                to_prefix: str = None,
                overwrite: bool = None,
                on_duplicate: str = None,
                sync: bool = None) -> dict:
                ...
```

So in fact it defaults to `None`. I can see why Blake had an issue with this.

However, by `7.5.3` the method has moved to `arango.collection.Collection` and the type signature has changed

```python
def import_bulk(self,
                documents: Sequence[dict[str, Any]],
                halt_on_error: bool = True,
                details: bool = True,
                from_prefix: str | None = None,
                to_prefix: str | None = None,
                overwrite: bool | None = None,
                on_duplicate: str | None = None,
                sync: bool | None = None,
                batch_size: int | None = None) -> dict[str, Any] | AsyncJob[dict[str, Any]] | BatchJob[dict[str, Any]] | None | list[dict[str, Any] | AsyncJob[dict[str, Any]] | BatchJob[dict[str, Any]] | None]:
                ...
```

Our tests confirm that if we use the default `halt_on_error` we get a `DocumentInsertError` in `python-arango` `7.5.3` and `8.3.2` but it does fail silently with `3.12.1`. However, `import_bulk` does not give any error context apart from the type of error. e.g. `[HTTP 409][ERR 1210] unique constraint violated` which makes it hard to debug the problem when it occurs.

However, from a review of the API, there are alternatives:

- Collections have a `import_many()` method which returns a list that includes the exception objects rather than raising the exception and halting.
- Use [batch API execution](https://aioarango.readthedocs.io/en/stable/batch.html)