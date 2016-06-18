# JSON Query for Web2py

A [web2py](http://www.web2py.com) module to retrieve data using JSON.

## Possible Query attributes

* `fields`: Projection.
* `order_fields`: Ordering records.
* `group_fields`: Grouping records.
* `distinct_field`: Distinct record. (support only single field)
* `where`: Selection.
* `join`: Join tables.
* `limit`: Limit records.
* `merge`: Flatten record. Use for e.g. `join`.

## Features

* [Field selection](#field-selection)
  * [Alias](#alias)
* [Total rows](#total-rows)
* [ORDER BY](#order-by)
* [GROUP BY](#group-by)
  * [COUNT](#count)
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

### Field Selection (mandatory)

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

Getting total number of rows in a table. In web2py, this can be done simply `db(db.students).count()`.
But, in jsonquery's way:

```python
query = {"fields": [
  {
    "table": "students",
    "fields": [
      {"field": "id", "count": True}
    ]
  }
]}
```

### ORDER BY

#### Ascending

Web2py Query: `db(db.students).select(orderby=db.students.name)`

```python
query = {
  "fields": [{"table": "students"}],
  "order_fields": [
    "table": "students",
    "fields": [
      {"field": "name"}
    ]
  ]
}
```

#### Descending

Web2py Query: `db(db.students).select(orderby=~db.student.name)`

```python
query = {
  "fields": [{"table": "students"}],
  "order_fields": [
    "table": "students",
    "fields": [
      {"field": "name", "sort": "desc"}
    ]
  ]
}
```

### GROUP BY

#### COUNT

Web2py Query: `db(db.students).select(db.students.class_id, db.students.id.count(), groupby=db.students.class_id)`

```python
query = {"fields": [
  {
    "table": "students",
    "fields": [
      {"field": "class_id"},
      {"field": "id", "count": True}
    ]
  }],
  "group_fields": [
    {
      "table": "students",
      "fields": [
        {"field": "class_id"}
      ]
    }
  ]}
```

Count field can be aliased, too.

```python
query = {"fields": [
  {
    "table": "students",
    "fields": [
      {"field": "class_id"},
      {"field": "id", "count": True, "alias": "student_count"}
    ]
  }],
  "group_fields": [
    {
      "table": "students",
      "fields": [
        {"field": "class_id"}
      ]
    }
  ]}
```

### DISTINCT

Web2py query: `db(db.students).select(db.students.class_id, distinct=db.students.class_id)`

```python
query = {
  "fields": [
    {
      "table": "students",
      "fields": [
        {"field": "class_id"}
      ]
    }
  ],
  "distinct_field": {
    "table": "students",
    "field": "class_id"
  }
}
```

**NOTE:** Reference for current approach - [#316](https://github.com/web2py/pydal/issues/316) and [#1129](https://github.com/web2py/web2py/issues/1129)

WORKAROUND for DISTINCT

```python
query = {
  "fields": [
    {
      "table": "students",
      "fields": [
        {"field": "class_id"}
      ]}
  ],
  "group_fields": [
    {
      "table": "students",
      "fields": [
        {"field": "class_id"}
      ]
    }
  ]
}
```

### WHERE

#### Conditional operators

1. `eq` is similar to `==`
2. `ne` is similar to `!=`
3. `gte` is similar to `>=`
4. `lte` is similar to `<=`
5. `gt` is similar to `>`
6. `lt` is similar to `<`
7. `start` is similar to `db.students.name.startswith('Aung')`
8. `end` is similar to `db.students.name.endswith('Naing')`
9. `contain` is similar to `db.students.name.contains('Myint')`

For example in jsonquery's way:
```python
query = {"where": [
  {
    "table": "students",
    "conditions": [
      {
        "field": "name",
        "value": "Aung",
        "operator": "start"
      }
    ]
  }
]}
```

### JOIN

#### INNER JOIN

Joining two tables in web2py: `db(db.students).select(db.students.ALL,
db.borrow.ALL, join=db.borrow.on(db.students.id == db.borrow.borrower_id))`.

In jsonquery:
```python
query = {
  "fields": [{
    "table": "students"
  }, {
    "table": "borrow"
  }],
  "join": [{
    "on": {"table": "students", "field": "id"},
    "joiner": {"table": "borrow", "field": "borrower_id"}
  }]
}
```

### LIMIT

In web2py:`db(db.students).select(limitby=(0, 10))`.

In jsonquery:
```python
query = {
  "limit": {
    "start": 0,
    "end": 10
  }
}
```
