# Truth Systems SDK

This is the Python SDK for the Truth Systems API. It allows you to easily interact with the API to judge the veracity of claims based on provided sources.

To use it, you must first have access to the Truth Systems API. See [our website](https://www.truthsystems.ai/) for more information.

## Quickstart

```python
from truthsys import (
    Client,  # or AsyncClient if you like
    TextInfluence,
    TextSource,
    Verdict,
)


client = Client.from_url("YOUR_BASE_URL")  # or Client.from_httpx

ruling = client.judge(
    claim="Sally is a pretty cat",
    sources=[
        TextSource.from_text("I have a cat"),
        TextSource.from_text("I only have one pet"),
        TextSource.from_text("My pet is called Sally"),
    ],
)

# ruling.verdict is an overall judgement of the claim's truthfulness
if ruling.verdict is Verdict.SUPPORTS:
    print("Sally really is a pretty cat!")

for statement in ruling.statements:
    # in this case, there are two statements: "Sally is a cat" and "Sally is pretty"
    print(f'The statement "{statement.text}" has been judged as {statement.verdict}')

    for influence in statement.influences:
        print(f"This is because {influence.source} says: {influence.text}")

        if isinstance(influence, TextInfluence):  # currently always true
            print(f"The character IDs are {influence.span[0]} to {influence.span[1]}")
```

## Types

All types are available to import from `truthsys`. These are:

- `Client` and `AsyncClient` for interacting with the API
- `Influence` and `TextInfluence` - a statement made in a source
- `Ruling` - the top-level object returned by the SDK
- `Source` and `TextSource` - a source that could support or refute a claim, e.g. a document
- `Statement` - a single statement in a claim
- `Verdict` - an enum representing the possible assessments of a claim

## Errors

All error types raised by the SDK are available to import from `truthsys.errors`. Please report unexpected errors.
