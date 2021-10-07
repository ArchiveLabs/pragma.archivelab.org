# pragma.archivelab.org
An API for citing Wayback snapshots using OpenAnnotations

## Performing a Capture

For those who want to make a capture without saving a record or an annotation to the database:

    curl -X POST -H "Content-Type: application/json" -d '{"url": "https://google.com"}}' https://pragma.archivelab.org/capture

## Creating an Annotation

Submitting a POST request to the root path (`https://pragma.archivelab.org`) with JSON data containing `url` (String) and `annotation` (Object) fields will save a snapshot of `url` using the Wayback Machine and store the `annotation` object, making a bidirectional link between the stored snapshot and annotation entries. Here's an example of such a request:

    curl -X POST -H "Content-Type: application/json" -d '{"url": "google.com", "annotation": {"id": "lst-ib", "message": "Theres a microphone button in the searchbox"}}' https://pragma.archivelab.org

## Querying Annotations

Making a GET request The root path (`https://pragma.archivelab.org`) will return a list of wayback snapshots created through the system, while the path `https://pragma.archivelab.org/annotations` will return a list of annotations. In both cases, individual items can be requested by suffixing the id of the item desired, e.g. `https://pragma.archivelab.org/5` for snapshot 5, or `https://pragma.archivelab.org/annotations/13` for annotation 13.

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
