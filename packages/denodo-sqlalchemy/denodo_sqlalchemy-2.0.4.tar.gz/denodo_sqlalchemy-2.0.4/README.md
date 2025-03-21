This package includes the Denodo Dialect for SQLAlchemy, which offers an easy way to connect to Denodo databases from SQLAlchemy https://www.sqlalchemy.org/

Denodo documentation and software resources are available at https://community.denodo.com

This dialect supports Denodo 8.0 and higher.


## Pre-requisites

Python 3.9 or newer is needed.

This dialect requires the following Python modules:
   * SQLAlchemy 1.4.36 or higher. SQLAlchemy 2.0.x is recommended.
   * psycopg2 version 2.9.6 or higher.

These Python modules are also required dependencies in order to use Denodo Virtual DataPort's Flight SQL interface
(available since Denodo 9.1):
   * SQLAlchemy 2.0.0 or higher.
   * adbc-driver-flightsql version 1.3.0.
   * pyarrow version 19.0.0.
 
Required dependencies will be installed automatically, in order to install dependencies for Flight SQL 
the `flightsql` extras package needs to be installed:

```shell        
pip install denodo-sqlalchemy[flightsql]
```

Alternatively, dependency packages can be installed manually:

```shell        
pip install sqlalchemy~=2.0.0
pip install psycopg2-binary>=2.9.6
pip install adbc-driver-flightsql~=1.3.0
pip install pyarrow~=19.0.0
```

Important: note also that psycopg2 has its own requirements for installation which need to be satisfied: https://www.psycopg.org/docs/install.html#prerequisites


## Installation

The Denodo Dialect for SQLAlchemy can be installed from the public PyPI repository using `pip`:

```shell        
pip install --upgrade denodo-sqlalchemy
```
Or (only for Denodo 9.1+):
```shell        
pip install --upgrade denodo-sqlalchemy[flightsql]
```

`pip` automatically installs all required dependencies.


## Usage

To connect to Denodo VDP Server with SQLAlchemy, the following URL pattern can be used:

```
denodo://<username>:<password>@<host>:<port[9996]>/<database>
```

This will create a connection using the default driver `psycopg2`, so it is equivalent to:

```
denodo+psycopg2://<username>:<password>@<host>:<port[9996]>/<database>
```

In order to create a connection using Flight SQL, you would need: 

```
denodo+flightsql://<username>:<password>@<host>:<port[9994]>/<database>
```

Please note that Flight SQL connections assume SSL is enabled at the server. If not, you would need to add the `use_encryption` parameter set to `False`, like:

```
engine = sqlalchemy.create_engine("denodo+flightsql://<username>:<password>@<host>:<port[9994]>/<database>", connect_args={"use_encryption":"false"})
```
