Products.PrintingMailHost
=========================

This is a hack. :)

This product, when installed, will check if Zope is running in debug mode,
and if so, monkey patch (that is, grab the internals of, squeeze tight, then
rip hard, just like monkeys do) Zope's MailHost class, meaning that *any and
all* uses of a MailHost will be "fixed" so that instead of sending mail, it
prints messages to the zope event log. Optionally the individual emails can
be saved to a location on the filesystem.

This is useful if you don't have a local mailhost for testing, or if you
prefer not to spam the crap out of yourself whilst finding out if your bulk
mail script is working.

If Zope is not running in debug mode, it will not install itself. However,
I wouldn't recommend putting it on a production site. You never know what
those monkeys may get up to...

You can optionally enable the PrintingMailHost with an environment variable
as of version 0.3.  See the installation instructions for more information
about how to use it.


Author
------

Martin Aspeli <optilude (AT) gmx (DOT) net>
    Initial idea, release management


Contributors
------------

Dorneles Tremea <deo (AT) plonesolutions (DOT) com>
    Fixed to work both with old-style and new-style classes. Extended
    to also patch SecureMailBase from SecureMailHost, if available.

Clayton Parker <clayton (AT) sixfeetup (DOT) com>

Maurits van Rees <maurits (AT) vanrees (DOT) org>


Products.PrintingMailHost Installation
======================================

To install Products.PrintingMailHost into your Plone instance in
buildout, you can do this:

- Add ``Products.PrintingMailHost`` to the list of eggs to install, e.g.::

    [instance]
    ...
    eggs =
        ...
        Products.PrintingMailHost

- If you want to enable PrintingMailHost when debug-mode is off::

    [instance]
    ...
    environment-vars =
        ...
        ENABLE_PRINTING_MAILHOST True

- If you want to disable PrintingMailHost when debug-mode is on::

    [instance]
    ...
    environment-vars =
        ...
        ENABLE_PRINTING_MAILHOST False

- If you want to save emails to a filesystem location, specify
the additional environment variable. Don't forget to enable the printing
mailhost as well::

    [instance]
    ...
    environment-vars =
        ...
        ENABLE_PRINTING_MAILHOST True
        PRINTING_MAILHOST_SAVETO /var/www/debug-emails

- Re-run buildout in order to make any of the above changes active::

    $ ./bin/buildout
