# JSON Query for Web2py

A [web2py](http://www.web2py.com) module to retrieve data using JSON.

## Features

* [Field selection](#field-selection)
  * [Alias](#alias)
* [Total rows](#total-rows)
* [ORDER BY](#order-by)
* [GROUP By](#group-by)
  * [COUNT]
* [DISTINCT](#distinct)
* [WHERE](#where)
* [JOIN](#join)
* [LIMIT](#limit)

## Examples

To use, put `jsonquery.py` under project's module folder. Then, import in
controller.

e.g.

``` python
from jsonquery import JsonQuery

def testpage():
  jsq = JsonQuery(db, logger)
  query = dict(fields=[dict(table="students")])
  rows = jsq.run(query)
  return rows
```

### Field Selection

Query with specific fields.

Selecting All fields. The following is quivalent to `db(db.students).select()`

```python
query = {
  "fields": [{
    "table": "students"
  }]
}

OR

query = dict(fields=[dict(table="students")])
```

Selecting with specific fields. The following is equivalent to `db(db.students).select(db.students.id, db.students.name)`

```python
query = {
  "fields": [{
    "table": "students",
    "fields": [
      {"field": "id"},
      {"field": "name"}
    ]
  }]
}
```

#### Alias

Aliasing fields. In web2py: `db(db.students).select(db.students.name.with_alias("student_name"))`

```python
query = {
  "fields": [
  "table": "students",
  "fields": [
      {"field": "name", "alias": "student_name"}
    ]
  ]
}
```

### Total rows

### ORDER By

### GROUP BY

#### COUNT

### DISTINCT

### WHERE

### JOIN

### LIMIT
