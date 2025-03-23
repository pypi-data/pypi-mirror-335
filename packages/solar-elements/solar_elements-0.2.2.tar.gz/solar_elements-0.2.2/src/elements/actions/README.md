# Actions

Actions are functions which can be applied from any standard SOLAR path.

Actions use HTTP Request Methods to indicate generally what is being done:

## GET

A "GET" request of an action will return the data corresponding to that
endpoint. GET /comments, for example, will return a rendered view of all
the comments at that endpoint.

## POST

A "POST" request to an action will add a new entry to the corresponding
data set. (i.e. a new comment)

## PATCH

A "PATCH" request will update information on an existing entry with data
passed in the request body (only available with addressable events)

## PUT

**Unlike standard HTTP methodology**, a "PUT" request will return a form
which can be used to make the appropriate POST or PATCH request at the
given endpoint.

## DELETE

A "DELETE" request will unsave corresponding data based on the values
of the query string and/or request body 
