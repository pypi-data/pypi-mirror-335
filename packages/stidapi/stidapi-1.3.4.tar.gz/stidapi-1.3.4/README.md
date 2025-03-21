# STIDapi-python [![SNYK dependency check](https://github.com/equinor/STIDapi-python/actions/workflows/snyk.yml/badge.svg)](https://github.com/equinor/STIDapi-python/actions/workflows/snyk.yml)

A simple wrapper package to interface Equinor [STIDapi](https://stidapi.equinor.com/) using python and get plant, system, tag and doc data.


## Use

Try it out by running the [demo](examples/demo.py) or the sample code below.

```
from stidapi import Plant, Tag, Doc


p = Plant("JSV")
t = p.search_tag("*20LIC*")
t2 = Tag("JSV",t[0].no)


d = t2.get_doc()
d2 = p.get_doc(d[0].no)
d3 = Doc(p.inst_code, d[0].no)
```

## Installing

Install package from pypi using `pip install stidapi`

## Developing / testing

Poetry is preferred for developers. Install with required packages for testing and coverage:  
`poetry install`

Call `poetry run pytest` to run tests.

To generate coverage report in html run `poetry run pytest --cov=stidapi tests/ --cov-report html`

