# Select records by JSON via web2py's DAL.
# Common utility functions, methods and classes for web2py DAL statements.
# license: MIT
# author: lmk
# datetime: 2016-02-26 22:55:00

import json
import traceback

from collections import namedtuple


def generate_condition(table, field, value, operator="eq"):
    """
    Generate Web2py `WHERE` statement.

    table: <web2py TABLE object>
      e.g. "table1"

    field: <str>
      e.g. "field1"

    value: object
      e.g. 100

    operator: <str>
      default: "eq"
      e.g. "gte"
    """
    if operator == "eq":
        return (table[field] == value)
    elif operator == "ne":
        return (table[field] != value)
    elif operator == "gte":
        return (table[field] >= value)
    elif operator == "lte":
        return (table[field] <= value)
    elif operator == "gt":
        return (table[field] > value)
    elif operator == "lt":
        return (table[field] < value)
    elif operator == "start":
        return (table[field].startswith(value))
    elif operator == "end":
        return (table[field].endswith(value))
    elif operator == "contain":
        return (table[field].contains(value))


def generate_order_field(field, config):
    """
    Generate order field.

    Parameters:
        field: web2py FIELD object
        config: dict
            e.g. {"field": 'col1', "sort": "desc"}
    """
    if config.get("sort") == "desc":
        return ~field
    return field


def merge_tables(self, record, _extra=None):
    """
    Merge columns from joined tables into single table.

    Parameters:
        record: web2py table-joined record
        _extra: aliased field(s)
            format: [
                {"db.table.field AS alias1": "alias1"},
                {"db.table.field AS alias2": "alias2"}
            ]
    """
    merged = dict()
    for table_name in record.keys():
        if (table_name == "_extra") & (_extra is not None):
            for k, v in _extra.iteritems():
                value = record[table_name][k]
                if value:
                    merged[v] = value
        else:
            try:
                value = record[table_name]
                if (value is not None) & (isinstance(value, dict) is True):
                    merged.update(value)
            except:
                self.warn("merge_tables",
                          "%s\nAt: %s" % (traceback.format_exc(),
                                          table_name))
    return merged


class JsonQuery(object):

    def __init__(self, db, logger, verbose=False):
        self._db = db
        self._logger = logger
        self._verbose = verbose
        # _extra: pair w2p generated alias name with user-defined alias name
        # and store them in a list for later use.
        self._extra = []

    def load_json(self, jsonstr, funcname=None):
        parsed = None
        try:
            parsed = json.loads(jsonstr)
            self.log(funcname, "parsed", parsed)
        except:
            parsed = None
            self.warn(funcname,
                      traceback.format_exc())
        return parsed

    def log(self, funcname, varname, data):
        if self._verbose:
            self._logger.debug("[DD] %s :: %s" % (
                funcname,
                varname
            ))
            self._logger.debug(data)

    def warn(self, funcname, message):
        self._logger.warn("[WW] %s :: %s" % (
            funcname,
            message
        ))

    def construct_DISTINCT(self, distinct_field):
        """
        Construct DISTINCT field.

        Return: web2py DAL<field> object
        """
        parsed = self.load_json(distinct_field)
        if not parsed:
            return None

        parsed = json.loads(distinct_field)
        table = parsed.get('table')
        field = parsed.get('field')
        return self._db[table][field]

    def construct_FIELDS(self, fields):
        """
        Construct FIELDS to select from specific table.

        Return: list of web2py fields
        """
        _fields = []
        parsed = self.load_json(fields, "construct_FIELDS")
        if not parsed:
            return None

        for each in parsed:
            generated = None
            table = each["table"]
            fields = each.get("fields")
            if fields:
                for each_field in fields:
                    field = each_field["field"]
                    alias = each_field.get("alias")
                    # hasCount: true or false
                    # NOTE: that field is `count field` (used for `GROUP BY`)
                    hasCount = each_field.get("count") or False
                    generated = self._db[table][field]
                    if alias:
                        generated = generated.with_alias(alias)
                        tmp_dict = {str(generated): alias}
                        self._extra.append(tmp_dict)
                    if hasCount:
                        generated = generated.count()
                    _fields.append(generated)
            else:
                generated = self._db[table].ALL
                _fields.append(generated)

        self.log("construct_FIELDS", "_fields", _fields)

        return _fields

    def construct_GROUP(self, group_fields):
        """
        Construct GROUP statement.

        Return: web2py GROUP statement
        """
        _group = None
        parsed = self.load_json(group_fields, "construct_GROUP")
        if not parsed:
            return None

        for each in parsed:
            table = each["table"]
            fields = each.get("fields")
            if not fields:
                self.warn("construct_GROUP",
                          "There is no `groupby` field for `%s`. At least, "
                          "one field must be provided." % table)
                continue
            for each_field in fields:
                field = each_field["field"]
                if _group is None:
                    _group = self._db[table][field]
                else:
                    _group |= self._db[table][field]

        self.log("construct_GROUP", "_group", _group)

        return _group

    def construct_JOIN(self, join):
        """
        Construct JOIN statement.

        Return: web2py JOIN statement.
        """
        joined = []
        parsed = self.load_json(join, "construct_JOIN")
        if not parsed:
            return None

        for each in parsed:
            ON_table = each.get("on").get("table")
            ON_field = each.get("on").get("field")
            JOINER_table = each.get("joiner").get("table")
            JOINER_field = each.get("joiner").get("field")
            JOINER_value = self._db[JOINER_table][JOINER_field]
            where = generate_condition(
                self._db[ON_table],
                ON_field,
                JOINER_value
            )
            generated = self._db[ON_table].on(where)
            joined.append(generated)

        self.log("construct_JOIN", "joined", joined)

        return joined

    def construct_LIMIT(self, limit):
        """
        Construct LIMIT statement.

        Return: <int> tuple
            e.g. (start, end)
        """
        parsed = self.load_json(limit, "construct_LIMIT")
        if not parsed:
            return None
        return (parsed.get('start'), parsed.get('end'))

    def construct_ORDER(self, order_fields):
        """
        Construct ORDER statement.

        Return: web2py ORDER statement
        """
        _order = None
        parsed = self.load_json(order_fields, "construct_ORDER")
        if not parsed:
            return None

        for each in parsed:
            table = each["table"]
            fields = each.get("fields")
            if not fields:
                self.warn("construct_ORDER",
                          "There is no `orderby` field for `%s`. At least, "
                          "one field must be provided." % table)
                continue
            for each_field in fields:
                field = each_field["field"]
                generated = generate_order_field(
                    self._db[table][field],
                    each_field
                )
                if _order is None:
                    _order = generated
                else:
                    _order |= generated

        self.log("construct_ORDER", "_order", _order)

        return _order

    def construct_WHERE(self, where):
        """
        Construct WHERE statement.

        Return: web2py WHERE statement
        """
        _where = None
        parsed = self.load_json(where, "construct_WHERE")
        if not parsed:
            return None

        for each in parsed:
            table = each["table"]
            conditions = each["conditions"]
            for condition in conditions:
                field = condition["field"]
                value = condition["value"]
                operator = condition["operator"]
                generated = generate_condition(
                    self._db[table],
                    field,
                    value,
                    operator
                )
                if _where is None:
                    _where = generated
                else:
                    _where &= generated

        self.log("construct_WHERE", "_where", _where)

        return _where

    def run(self, stored):
        """
        Select record(s) according to given criteria written in JSON.

        stored: web2py REQUEST.vars object OR NamedTuple object

        Attributes of stored
        ==========================
        fields: JSON Object Array
          NOTE: FIELDS MUST BE PROVIDED.
          e.g-1. [{"table": "table1", "fields": [
                                        {"field": "f1", "alias": "field1"},
                                        {"field": "f2", "alias": "col2"},
                                        {"field": "col3"},
                                        {"field": "col4", "count": true}
                                    ]
                  }, ...]
          e.g-2. [{"table": "table1"}, {"table": "table2"}]

        order_fields: JSON Object Array
          default: None
          e.g. [{"table": "table1", "fields": [
                                        {"field": "f1", "sort": "desc"},
                                        {"field": "f2", "sort": "asc"},
                                        {"field": "col3"}] // default:"asc"
                }, ...]

        group_fields: JSON Object Array
          default: None
          e.g. Similar as `order_fields` value. But `sort` is not required.

        distinct_field: JSON Object
          default: None
          e.g. {"table": "table1", "field": "col1"}

        where: JSON Object Array
          default: None
          e.g. [{table: "table1",
                 conditions: [{"field": "field1",
                               "value": 1,
                               "operator": "eq"},
                               ...
                             ]}, ...]

        join: JSON Object Array
          default: None
          format:
              [{
                  "on":
                      {"table": "table1", "field": "col1"},
                  "joiner":
                      {"table": "table2", "field": "col1"}
              }, ...]

        limit: JSON Object
          default: None
          e.g. {"start": 1, "end": 10}

        merge: true or false
          default: false

        Return: web2py's DAL record(s)
        """
        fields = self.construct_FIELDS(stored.fields)
        order_fields = self.construct_ORDER(stored.order_fields)
        group_fields = self.construct_GROUP(stored.group_fields)
        distinct_field = self.construct_DISTINCT(
            stored.distinct_field)
        # NOTE: `where_additional` is DEPRECATED. Use `where` instead.
        # `where_additional` will be removed in FUTURE.
        where = self.construct_WHERE(
            stored.where or
            stored.where_additional)
        join = self.construct_JOIN(stored.join)
        limit = self.construct_LIMIT(stored.limit)
        merge = stored.merge or False

        records = self._db(where).select(
            *fields,
            left=join,
            distinct=distinct_field,
            orderby=order_fields,
            groupby=group_fields,
            limitby=limit)
        if merge:
            records = [merge_tables(record, self._extra) for record in records]
        return records

    def run_from_file(self, path, mode='rb'):
        try:
            json_file = open(path, mode)
            parsed = json.load(json_file)
            json_data = namedtuple('json_data', *parsed.keys)
            new_data = json_data(**parsed)
            return self.run(new_data)
        except:
            raise
