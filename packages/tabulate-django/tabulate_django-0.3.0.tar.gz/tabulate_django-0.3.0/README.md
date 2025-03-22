# Tabulate-Django

Tabulate-Django is a small collection of functions to make working with Django Querysets
and Objects in the shell easier.

Tabulate-Django uses the [tabulate](https://pypi.org/project/tabulate/) library for
formatting.

## Motivation

When using Django, I often need to drop to the shell to retrieve information. In such
cases I will usually look at the result of a QuerySet, the default output of which is
not particularly useful. I tended to use `.values()` to extract the fields that I
wanted and then pass them into the excellent tabulate library. I would often make the
same calls over an over and ended up creating functions to avoid repetition. Over time 
these functions grew in size and capabilities.

In order to make it easy to put into any codebase I am working on, I decided to publish
it on PyPI, with the added bonus of making it available for other users.

My motivation is primarily my own needs, so I won't commit to adding any features that
would not be of use to me, however PRs are welcome.

## Licence

This software is licensed under the MIT licence

## Installation

The package is available on PyPI so installation is as simple as

```shell
pip install tabulate-django
```

or use the package manager of your choice

This version supports Python 2.7, however compatibility may be removed in a future
release as I no longer code for Python 2.7

## Usage

For examples, I am using a simple e-commerce style app called test_app that contains
three models, Country, Account and Order.

Account has a foreign key to Country and Order has a
foreign key to Account.

Commands are assumed to be running in the Django shell started with
`python manage.py shell`

First, let's get a queryset with all Accounts

```python
from test_app.models import Account
all_accounts = Account.objects.order_by("name")
print(all_accounts)
```

response:

```
<QuerySet [<Account: Alice Smith>, <Account: Bob Jones>, <Account: Charlotte Muller>, <Account: Dietrich Schmidt>, <Account: Eva Dupont>, <Account: Francois Michel>]>
```

more information could be provided by running `print(account.values("name", "email")`

```
<QuerySet [{'name': 'Alice Smith', 'email': 'alice@smith.example'}, {'name': 'Bob Jones', 'email': 'bob.jones@example.com'}, {'name': 'Charlotte Muller', 'email': 'charlie@example.com'}, {'name': 'Dietrich Schmidt', 'email': 'dschmidt@example.de'}, {'name': 'Eva Dupont', 'email': 'eva@dupont.example'}, {'name': 'Francois Michel', 'email': 'francois.michel@example.fr'}]>
```

As the number of records and the number of fields gets bigger this becomes hard to read
and will eventually be truncated

### queryset_table

let's see what Tabulate Django can do. Pass the queryset and an iterable of fields that
you wish to extract to the queryset_table

```python
from tabulate_django import queryset_table
queryset_table(all_accounts, ["name", "email"])
```

```
╒══════════════════╤════════════════════════════╕
│ Name             │ Email                      │
╞══════════════════╪════════════════════════════╡
│ Alice Smith      │ alice@smith.example        │
├──────────────────┼────────────────────────────┤
│ Bob Jones        │ bob.jones@example.com      │
├──────────────────┼────────────────────────────┤
│ Charlotte Muller │ charlie@example.com        │
├──────────────────┼────────────────────────────┤
│ Dietrich Schmidt │ dschmidt@example.de        │
├──────────────────┼────────────────────────────┤
│ Eva Dupont       │ eva@dupont.example         │
├──────────────────┼────────────────────────────┤
│ Francois Michel  │ francois.michel@example.fr │
╘══════════════════╧════════════════════════════╛

```

As you can see, it puts the output in a pretty printed table with automatically named
headers

### Table Format

You can change the format by setting table_format to any of [the formats supported by
tabulate](https://github.com/astanin/python-tabulate/blob/master/README.md#table-format)

So to user presto format

```python
queryset_table(all_accounts, ["name", "email"], table_format="presto")
```

```
 Name             | Email
------------------+----------------------------
 Alice Smith      | alice@smith.example
 Bob Jones        | bob.jones@example.com
...
```

The default is fancy_grid

### TSVs

In addition to the output formats provided by tabulate, there is an additional format
"tsv" which outputs in a simple tsv format. This is useful for exporting the results for
importing into a spreadsheet or other tool. No escaping is performed so if the data has
linebreaks or tabs then it will not be correctly imported

### Output to variable

The default behaviour of the function is to print the output to the console. If instead
you wish for the output to be placed inside a variable, add the parameter print_result=False
e.g.

```python
users=queryset_table(all_accounts, ["name", "email"], print_result=False)
```

### Foreign Keys

You can traverse model relationships using `__` notation, so to retrieve the country
name of each Account you can do

```python
queryset_table(all_accounts, ["name", "email", "country__name"])
```

would output

```
╒══════════════════╤════════════════════════════╤════════════════╕
│ Name             │ Email                      │ Country Name   │
╞══════════════════╪════════════════════════════╪════════════════╡
│ Alice Smith      │ alice@smith.example        │ United Kingdom │
├──────────────────┼────────────────────────────┼────────────────┤
│ Bob Jones        │ bob.jones@example.com      │ United Kingdom │
├──────────────────┼────────────────────────────┼────────────────┤
│ Charlotte Muller │ charlie@example.com        │ Germany        │
├──────────────────┼────────────────────────────┼────────────────┤
│ Dietrich Schmidt │ dschmidt@example.de        │ Germany        │
├──────────────────┼────────────────────────────┼────────────────┤
│ Eva Dupont       │ eva@dupont.example         │ France         │
├──────────────────┼────────────────────────────┼────────────────┤
│ Francois Michel  │ francois.michel@example.fr │ France         │
╘══════════════════╧════════════════════════════╧════════════════╛
...
```

### Changing Table Headings

If you were unhappy with the generated headers (more likely when using foreign keys and
more advanced operations) then you can replace a field with a tuple, the first entry
containing the field specification and the second the heading that you wish the column
to have

e.g.

```python
queryset_table(all_accounts, ["name", "email", ("country__name", "Residence")])
```

would output

```
╒══════════════════╤════════════════════════════╤════════════════╕
│ Name             │ Email                      │ Residence      │
╞══════════════════╪════════════════════════════╪════════════════╡
│ Alice Smith      │ alice@smith.example        │ United Kingdom │
├──────────────────┼────────────────────────────┼────────────────┤
│ Bob Jones        │ bob.jones@example.com      │ United Kingdom │
├──────────────────┼────────────────────────────┼────────────────┤
...
```

### Aggregation

As well as getting simple fields from tables, it is also possible to use certain
aggregation functions to retrieve more information, by using specially formatted field
specifications

These are accessed by preceding the field (or table) name with a symbol

| Function  | Symbol | Notes                                |
| --------- |--------|--------------------------------------|
| Count     | `#`    |                                      |
| Count     | `1#`   | with distinct=True                   |
| Min       | `_`    |                                      |
| Max       | `^`    |                                      |
| Sum       | `+`    |                                      |
| Average   | `~`    |                                      |
| StringAgg | `*`    | Postgres only - used for strings     |
| StringAgg | `1*`   | as above, with distinct=True         |
| ArrayAgg  | `[]`   | Postgres only - used for non-strings |
| ArrayAgg  | `1[]`  | as above, with distinct=True         |

e.g

```python
queryset_table(all_accounts, ["name", "email", "#order", "+order__order_total"])
```

```
╒══════════════════╤════════════════════════════╤══════════╤══════════════════════╕
│ Name             │ Email                      │   #Order │   +Order Order Total │
╞══════════════════╪════════════════════════════╪══════════╪══════════════════════╡
│ Alice Smith      │ alice@smith.example        │        3 │                   45 │
├──────────────────┼────────────────────────────┼──────────┼──────────────────────┤
│ Bob Jones        │ bob.jones@example.com      │        1 │                  250 │
├──────────────────┼────────────────────────────┼──────────┼──────────────────────┤
│ Charlotte Muller │ charlie@example.com        │        1 │                   10 │
├──────────────────┼────────────────────────────┼──────────┼──────────────────────┤
│ Dietrich Schmidt │ dschmidt@example.de        │        2 │                  300 │
├──────────────────┼────────────────────────────┼──────────┼──────────────────────┤
│ Eva Dupont       │ eva@dupont.example         │        1 │                  220 │
├──────────────────┼────────────────────────────┼──────────┼──────────────────────┤
│ Francois Michel  │ francois.michel@example.fr │        1 │                  220 │
╘══════════════════╧════════════════════════════╧══════════╧══════════════════════╛
```

Alternatively you can use custom aggregate expressions, e.g.

```python
from django.db.models import Count, Sum
queryset_table(
            all_accounts,
            [
                "name",
                "email",
                (Count("order"), "Orders"),
                (Sum("order__order_total"), "Order Value"),
            ]
)
```

would output

```
╒══════════════════╤════════════════════════════╤══════════╤═══════════════╕
│ Name             │ Email                      │   Orders │   Order Value │
╞══════════════════╪════════════════════════════╪══════════╪═══════════════╡
│ Alice Smith      │ alice@smith.example        │        3 │            45 │
├──────────────────┼────────────────────────────┼──────────┼───────────────┤
│ Bob Jones        │ bob.jones@example.com      │        1 │           250 │
├──────────────────┼────────────────────────────┼──────────┼───────────────┤
...
```

Header aliases are used here as the default representation of the expression is not
particularly friendly

### Filtering

The queryset can of course be filtered before being passed into the function, however
you might wish to only show accounts that have made more than one order. Rather than
requiring you to generate the expression yourself you can pass a filter option to the
function which is a dictionary which will be passed as kwargs to `.filter()`

```python
queryset_table(
    all_accounts,
    [
        "name",
        "email",
        ("#order", "Orders"),
        ("+order__order_total", "Order Value"),
    ],
    filter={"_count_order__gt": 1},
)
```

which would output:

```
╒══════════════════╤═════════════════════╤══════════╤═══════════════╕
│ Name             │ Email               │   Orders │   Order Value │
╞══════════════════╪═════════════════════╪══════════╪═══════════════╡
│ Alice Smith      │ alice@smith.example │        3 │            45 │
├──────────────────┼─────────────────────┼──────────┼───────────────┤
│ Dietrich Schmidt │ dschmidt@example.de │        2 │           300 │
╘══════════════════╧═════════════════════╧══════════╧═══════════════╛
```

to get the keys to use for generated fields you can pass `show_keys=True` to the function

```python
queryset_table(
    all_accounts,
    [
        "name",
        "email",
        ("#order", "Orders"),
        ("+order__order_total", "Order Value"),
    ],
    show_keys=True,
)
```

outputting

```
╒══════════════════╤════════════════════════════╤═════════════════════════╤═════════════════════════════════════════╕
│ Name (name)      │ Email (email)              │   Orders (_count_order) │   Order Value (_sum_order__order_total) │
╞══════════════════╪════════════════════════════╪═════════════════════════╪═════════════════════════════════════════╡
│ Alice Smith      │ alice@smith.example        │                       3 │                                      45 │
├──────────────────┼────────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
...
```

### Formatted Strings

Sometimes you may want to transform one or more fields into a string, this can be
accomplished by using a field specification starting with `f|` followed by a format
string containing the name of one or more fields e.g.

```python
queryset_table(
    all_accounts,
    [
        "name",
        ("f|https://example.com/admin/test_app/account/{id}/change", "Django Admin URL"),
    ],
)

```

```
╒══════════════════╤═════════════════════════════════════════════════════╕
│ Name             │ Django Admin URL                                    │
╞══════════════════╪═════════════════════════════════════════════════════╡
│ Alice Smith      │ https://example.com/admin/test_app/account/1/change │
├──────────────────┼─────────────────────────────────────────────────────┤
│ Bob Jones        │ https://example.com/admin/test_app/account/2/change │
├──────────────────┼─────────────────────────────────────────────────────┤
...
```

### Slicing

To slice the resulting queryset (to paginate results for example) you can pass a slice
parameter which is a 2-tuple containg start and end values

```python
queryset_table(all_accounts, ["name", "email"], print_result=False, slice=(2, 4))
```

which would output:

```
╒══════════════════╤═════════════════════╕
│ Name             │ Email               │
╞══════════════════╪═════════════════════╡
│ Charlotte Muller │ charlie@example.com │
├──────────────────┼─────────────────────┤
│ Dietrich Schmidt │ dschmidt@example.de │
╘══════════════════╧═════════════════════╛
```

## Printing Instance

You can also print a single instance of a model by passing the instance to the
instance_table function

```python
from ptk_tabulate import instance_table
instance_table(all_accounts[0])
```

This uses the dictionary representation of the instance, and sorts by key

```
╒════════════╤═════════════════════╕
│ country_id │ 1                   │
├────────────┼─────────────────────┤
│ email      │ alice@smith.example │
├────────────┼─────────────────────┤
│ id         │ 1                   │
├────────────┼─────────────────────┤
│ name       │ Alice Smith         │
╘════════════╧═════════════════════╛
```

This will automatically hide members that begin with an underscore, to show these
members, pass `private=True` to the function.

`print_result` and `table_format` parameters have the same meaning as in queryset_table
however the special tsv value for table_format is not available

# Contributing

Contributions are welcome, please open an issue or PR on the 
[GitHub repository](https://github.com/MrWeeble/tabulate-django)

Local installation should be as simple as checking out the code nad running 
`poetry install`

Tests can be run in all combinations of supported environments with the command 
`poetry run tox`

Code formatting and standards are enforced use [pre-commit](https://pre-commit.com/). 
Please ensure PRs pass all checks.