# pragma.archivelab.org
An API for citing Wayback snapshots using OpenAnnotations

## Creating an Annotation

Submitting a POST to `https://pragma.archivelab.org` will a field `url` (String) and `annotation` (Object) will save a snapshot of `url` using the Wayback Machine and store the `annotation` object for this `url`. Here's an example:

    curl -X POST -H "Content-Type: application/json" -d '{"url": "google.com", "annotation": {"id": "lst-ib", "message": "Theres a microphone button in the searchbox"}}' https://pragma.archivelab.org

## Installation

Clone the pragma repository

    $ git clone https://github.com/ArchiveLabs/pragma.archivelab.org.git

Install postgres & system dependencies

    $ sudo apt-get install postgresql-9.4 postgresql-server-dev-9.4

Install python libraries

    $ cd pragma
    $ sudo pip install .

Connect to postgres and create database:

    $ sudo -upostgres psql # connect to postgres

Change user and password below as desired:

    CREATE USER annotator WITH PASSWORD 'myPassword';
    CREATE DATABASE pragma OWNER annotator;
    GRANT ALL PRIVILEGES ON DATABASE pragma to annotator;

Create the following config file in pragma: `configs/settings.cfg`

    [server]
    host = 0.0.0.0
    port = 8080
    debug = 0
    
    [ssl]
    crt =
    key =
    
    [db]
    host = localhost
    user = annotator
    pw = myPassword
    dbn = postgres
    db = pragma
    port = 5432

Generate sqlalchemy models:

    $ python
    >>> from pragma.api import engine
    >>> from pragma.api import Pragma
    >>> Pragma.metadata.create_all(engine)

Start the server:

    $ python app.py
