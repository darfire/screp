==================================
screp, easy command-line scrapping
==================================


What is screp?
==============

**screp** is a command line utility that provides easy and flexible scrapping of HTML documents.


Invoking screp
==============

**screp** is invoked using the following syntax:

$ screp [OPTION] FORMAT_SPEC PRIMARY_SELECTOR [FILE]

where:
* FORMAT_SPEC is a format specification, one of:
  - *-c CSV_FORMAT_SPEC*, as detailed below
* PRIMARY_SELECTOR is a CSS selector that specifies the *primary anchor*, as detailed below
* FILE can be either a local file or an absolute URL; if not FILEs are specified the standard input
  is read


How does screp work?
====================

screp tries to automate many of the steps taken when writing your own scrapper, steps like:

* fetching the HTML documents, if necessary
* parsing HTML
* locating areas of interest in the DOM of the document
* locating interesting information around those areas
* simple processing of these pieces of information
* formatting of the information
* outputting the information

To use screp, you need to take a series of steps:
* tell screp where to take the HTML documents; it works with multiple documents, from sources such
  as the web, the local file-system or STDIN
* define the *primary anchor* using a CSS selector: these are elements through which you access
  records of interest in the HTML documents
* specify the output format; this implies specifying:
  - *terms*, which are string computed relative to the anchors
  - how these terms are combined to produce a record; currently screp only supports CSV formatting
* optionally, you can also define *secondary anchors*, which are elements computed relative to the
  *primary anchor* that can be used to define *terms* in a more succinct way

Defining terms
==============

A *term* has the following format::
    anchor.accessor.accessor.accessor|filter|filter|filter

In other words, a term is an anchor(primary or secondary) followed by zero or more accessors
followed by zero or more filters.

*Accessors* and *filters* (also collectively called *actions*) are functions that take the output
value of the last function (or the anchor, if this is the first action) and output another value. In
other words, they form a pipeline.  Accessors act on DOM elements and sets (actually ordered lists)
of elements, whereas filters act on strings. Each action has an in_type and an out_type. For a term
to be correctly defined the out_type of an action needs to be equal to the in_type of the following
action.

The supported types are: 'string', 'element', 'element_set'.

Actions can have zero or more parameters. When the action takes parameters it is specified as a
function::
    action(parameter1, parameter2, parameter3)

When not, only the action name is specified (no parentheses).

Finally, terms have restrictions of the out_type of their last action (also called the out_type of
the term):
* if a term is used inside a format specification, its out_type must be 'string'
* if a term is used to define a secondary anchor, its out_type must be 'element'

Examples of terms
-----------------

These are correct term definitions::
    '$.parent.parent.attr(title)|upper' outputs 'string'
    '@.desc(".record").first' outputs 'element    
    'anchor.ancestors(".box").children(".price")' outputs 'element_set'

Predefined anchors and actions
==============================

The following anchors are predefined:
* **$** is the primary anchor defined by the primary anchor selector
* **@** is the primary anchor representing the root of the current document

The following accessors are predefined:
* **first** [in_type='element_set', out_type='element']: returns the first element in an element_set
* **last** [in_type='element_set', out_type='element']: returns the last element in an element_set
* **nth(n)** [in_type='element_set', out_type='element']: returns the n-th element in an
  element_set; it also supports negative indexes, where -1 represents the last element, -2 the
  second-to-last element, and so on
* **class** [in_type='element', out_type='string']: returns the value of the 'class' attribute 
* **id** [in_type='element', out_type='string']: returns the value of the 'id' attribute 
* **parent** [in_type='element', out_type='element']: returns the parent of the current element
* **text** [in_type='element', out_type='string']: returns the text enclosed by the current element
* **tag** [in_type='element', out_type='string']: returns the tag of the current element
* **attr(attr_name)** [in_type='element', out_type='string']: returns the value of the current element's
  attribute with name 'attr_name'
* **desc(css_sel)** [in_type='element', out_type='element_set']: returns the ordered list of
  descendants of the current element selected by the CSS selector specified by 'css_sel'
* **fdesc(css_sel)** [in_type='element', out_type='element']: equivalent to
  .desc(css_sel).first
* **ancestors(css_sel)** [in_type='element', out_type='element_set']: returns the list of ancestors
  of the current element that satisfy the CSS selector specified by 'css_sel'
* **children(css_sel)** [in_type='element', out_type='element_set']: returns the list of children
  of the current element that satisfy the CSS selector specified by 'css_sel'
* **psiblings(css_sel)** [in_type='element', out_type='element_set']: returns the list of preceding
  siblings of the current element that satisfy the CSS selector specified by 'css_sel'
* **fsiblings(css_sel)** [in_type='element', out_type='element_set']: returns the list of following
  siblings of the current element that satisfy the CSS selector specified by 'css_sel'
* **siblings(css_sel)** [in_type='element', out_type='element_set']: returns the list of siblings of
  the current element that satisfy the CSS selector specified by 'css_sel'
* **matching(css_sel)** [in_type='element_set', out_type='element_set']: filters an element_set and
  returns all elements that match the CSS selector specified by 'css_sel'

The following filters are predefined:
* **upper** [in_type='string', out_type='string']: converts string to uppercase
* **lower** [in_type='string', out_type='string']: converts string to lowercase
* **trim** [in_type='string', out_type='string']: removes spaces at the beginning and end of the
  string
* **strip(chars)** [in_type='string', out_type='string']: removes characters specified by 'chars'
  at the beginning and end of the string
* **replace(old, new)** [in_type='string', out_type='string']: replaces all occurrences of 'old' with
  'new'

Specifying output formats
=========================

Currently the only output format defined is comma-separated-value

Specifying CSV format
---------------------

The CSV output format is specified using the -c option. Optionally, using the -H option you can
specify a CSV header to output before outputting records.

Example::
    -c '$.attr(title), $.parent.desc(".price").text | trim' -H 'name, price'


Specifying secondary anchors
============================

Secondary anchors are specified using the -a option. There can be any number of secondary anchors
definitions. The definitions have the format **<name>=<term>** where <name> is an identifier and
<term> is a term definition relative to any of the previously defined anchors (primary or
secondary) that has outputs an element. Secondary anchors can be redefined in later -a options but
only the last definition is retained.

Secondary anchors examples
--------------------------

These are examples of secondary anchors definitions::
    -a 'p=$.parent' -a 'gp=p.parent' 

    -a 'interesting=$.fdesc(".interesting-class")' -a 'interesting=interesting.parent'
