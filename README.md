# pyluno
Luno API for python

Master: [![Build Status Master](https://travis-ci.org/grantstephens/pyluno.svg?branch=master)](https://travis-ci.org/grantstephens/pyluno)

Develop: [![Build Status Develop](https://travis-ci.org/grantstephens/pyluno.svg?branch=develop)](https://travis-ci.org/grantstephens/pyluno)

# Installation

    pip install pyluno

# Usage

See the tests for detailed usage examples, but basically:

## API object creation

    from pyluno.api import Luno
    api = Luno(key, secret, options)

Where `options` is  dictions and can have any of the following keys and associated values:

| option key   | description      | default |
|--------------|------------------|---------|
| hostname | the API host | api.mybitx.com |
| port | the TCP port to attach to | 443 |
| pair | The currency pair to provide results for | XBTZAR |
| ca | The root certificate | None |
| timeout | The maximum time to wait for requests | 30 (s) |
| maxRate | The maximum number of calls per second. Set to None to deactivate |  1 |
| maxBurst | Number of call that can be made without being rate limited. After this number is exceeded the accumulated time is waited. Set to 1 to deactivate bursts. Irrelevant if maxRate is None | 5 |

## API calls

### Latest ticker

    api.get_ticker()

**Returns**: dictionary containing the latest ticker values

### All tickers

    api.get_all_tickers()

**Returns**: dictionary containing the latest ticker values for all currency pairs

# Known Issues

-   Rates published on the Luno website aren't accurate- your milliage may vary
-   Not all error handling has been handled

# Acknowledgements

This repo was called pybitc and made by @CjS77. It has since been updated
and adapted and gone though a name change

# To Do

-   Tests for some of the endpoints needing dynamic reponses
-   Tests for the rate limiter


# Contribute

-  Fork it
-  Contribute
-  Be Awesome
