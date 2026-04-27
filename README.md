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
docker compose run arango-bulk-test
```

I couldn't find the documentation for this version of the `python-arango` API, but you can explore with:

```commandline
docker compose run python-interpreter
```

You can use the `help()` command in the REPL and so forth.