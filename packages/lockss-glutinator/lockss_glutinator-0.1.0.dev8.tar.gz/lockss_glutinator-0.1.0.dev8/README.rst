==========
Glutinator
==========

Glutinator is a modest static Web site generator specializing in scholarly journal articles.

Glutinator was developed by the `LOCKSS Program <https://www.lockss.org/>`_ and is available under a 3-Clause BSD License.

*Glutinator* is the Latin word for "bookbinder". Although it can be made to rhyme with "Terminator", it actually sounds like "glue" + "Tina" + "tore".

--------
Overview
--------

Glutinator's main command, ``generate-static-site`` (or ``gss``), takes an inventory file as input and produces a static site as output.

*  The ``--inventory`` option is mandatory. The value is the inventory file.

*  The ``--base-url`` option is mandatory. The value is the base URL of the live static website, for ``<meta>`` tags that require an absolute URL value.

*  By default, the Glutinator configuration file is ``glutinator.yaml`` (in the current directory), but this can be overridden with the ``--configuration`` option.

*  By default, the output directory is ``static-site`` (in the current directory), but this can be overridden with the ``--output-directory`` option.

--------------
Inventory File
--------------

The inventory file is JSON data that conforms to the JSON Schema file ``src/lockss/glutinator/resources/jsonschema/root.json``. Hierarchically:

*  The root object consists of ``metadata`` which is always ``null`` and ``publishers`` which is a list of ``Publisher`` objects.

*  A ``Publisher`` object consists of ``metadata`` which is a ``PublisherMetadata`` object and ``journals`` which is a list of ``Journal`` objects.

*  A ``Journal`` object consists of ``metadata`` which is a ``JournalMetadata`` object and ``journal_volumes`` which is a list of ``JournalVolume`` objects.

*  A ``JournalVolume`` object consists of ``metadata`` which is a ``JournalVolumeMetadata`` object and ``journal_issues`` which is a list of ``JournalIssue`` objects.

*  A ``JournalIssue`` object consists of ``metadata`` which is a ``JournalIssueMetadata`` object and ``journal_articles`` which is a list of ``JournalArticle`` objects.

*  A ``JournalArticle`` object consists of ``metadata`` which is a ``ModelItem`` object, and an optional ``license_type`` from the enum ``LicenseType``.

*  ``Publisher`` and ``Journal`` further have an optional ``logo`` field which can be a ``file::`` reference to an image.

All the above objects are in the ``lockss.glutinator.item`` module and their definitions are easier to read in code than in JSON Schema. The JSON Schema is generated from Pydantic by the ``dev/generate_jsonschema_item.py`` script. The exception is the ``ModelItem`` class which is in ``lockss.glutinator.csl_data``, generated from the CSL-JSON standard by the ``dev/generate-python-csl-json`` script, which requires installing the ``dev`` dependency group of Glutinator. In the future, there will likely be a similar object native to Glutinator, not derived from CSL-JSON.

-----------
Static Site
-----------

Structure
=========

The static site mirrors the hierarchical structure of the inventory file:

*  ``index.html`` is a gallery of publishers.

*  ``<p.metadata.id>/index.html`` is a gallery of journals from publisher ``p``. The menu and breadcrumbs use the label ``p.metadata.name``. For each journal ``j``, the gallery uses the label ``j.metadata.name``.

*  ``<p.metadata.id>/<j.metadata.id>/index.html`` is a gallery of journal volumes in the journal ``j`` from publisher ``p``. The menu and breadcrumbs use the label ``j.metadata.name``. For each journal volume ``v``, the gallery uses the label ``v.metadata.name``.

*  ``<p.metadata.id>/<j.metadata.id>/<v.metadata.id>/index.html`` is a gallery of journal issues in journal volume ``v`` from journal ``j`` from publisher ``p``. The menu and breadcrumbs use the label ``v.metadata.short_name``. For each journal issue ``i``, the gallery uses the label ``i.metadata.name``.

*  ``<p.metadata.id>/<j.metadata.id>/<v.metadata.id>/<i.metadata.id>/index.html`` is a table of contents of journal articles in journal issue ``i`` from journal volume ``v`` from journal ``j`` from publisher ``p``. The menu and breadcrumbs use the label ``i.metadata.short_name``. For each journal article ``a``, the gallery uses the label ``a.metadata.title``.

*  ``<p.metadata.id>/<j.metadata.id>/<v.metadata.id>/<i.metadata.id>/<a.metadata.id>/index.html`` is a landing page for journal article ``a`` in journal issue ``i`` from journal volume ``v`` from journal ``j`` from publisher ``p``. The menu and breadcrumbs use the label ``a.metadata.title_short``.

   *  The main body displays the article title (``a.metadata.title``), list of authors (``a.metadata.author``), and DOI (``a.metadata.DOI``). For each author at index ``i``, if ``a.metadata.custom.author_email[i]`` is defined, a ``mailto:`` link is generated, and if ``a.metadata.custom.author_affiliation[i]`` is defined, the corresponding author affiliation is appended. Finally, the body ends with a ``CC BY 4.0`` or ``CC BY-NC-ND 4.0`` license blurb if applicable from ``a.license_type``.

   *  The menu sidebar displays the article title, compact list of author names, DOI, and published online date.

   *  If ``a.metadata.custom.article_pdf`` is a ``file::`` reference, the corresponding file is linked to as ``<p.metadata.id>/<j.metadata.id>/<v.metadata.id>/<i.metadata.id>/<a.metadata.id>/article_pdf/<a.metadata.id>.pdf``.

   *  Likewise, if ``a.metadata.custom.metadata_jats`` is a ``file::`` reference, the corresponding file is linked to as ``<p.metadata.id>/<j.metadata.id>/<v.metadata.id>/<i.metadata.id>/<a.metadata.id>/metadata_jats/<a.metadata.id>.xml``.

Skin
====

Glutinator currently comes with a single skin called `Editorial <https://html5up.net/editorial>`_ by `HTML5 UP <https://html5up.net/>`_, used under a Creative Commons license. The Jinja template files are in ``src/lockss/glutinator/resources/editorial``. In the future there may be more than one skin, and skins may be grouped into a common subdirectory of ``src/lockss/glutinator/resources``.

--------------
Other Commands
--------------

Glutinator also has an ``unpack-sources`` (or ``us``) command, which unpacks LOCKSS v1 AU gzipped tarballs from ``--input-directory`` (by default ``sources``) to ``--output-directory`` (by default ``sources-unpacked``). Given an AU nickname ``n``, the tarballs are either plain (``<n>.tgz``), or split and sequentially numbered (``<n>.tgz.0``, ``<n>.tgz.1``, etc. or ``<n>.tgz.00``, ``<n>.tgz.01``, etc. or ``<n>.tgz.000``, ``<n>.tgz.001``, etc.). The nicknames are found in the Glutinator configuration file as a list under the ``source-aus`` key.

Glutinator also has boilerplate commands: ``copyright``, ``license``, ``usage`` and ``version``.

Each Glutinator command (and ``glutinator`` itself) comes with a ``--help`` option that displays a help message focusing on the corresponding command.
