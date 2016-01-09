# pragma.archivelab.org
An API for citing Wayback snapshots using OpenAnnotations

## Creating an Annotation

Submitting a POST to `https://pragma.archivelab.org` will a field `url` (String) and `annotation` (Object) will save a snapshot of `url` using the Wayback Machine and store the `annotation` object for this `url`. Here's an example:

    curl -X POST -H "Content-Type: application/json" -d '{"url": "google.com", "annotation": {"id": "lst-ib", "message": "Theres a microphone button in the searchbox"}}' https://pragma.archivelab.org
