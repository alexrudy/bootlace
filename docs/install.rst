Getting Started
===============

Installing :mod:`bootlace`
--------------------------

Install :mod:`bootlace` with ``pip``::

    pip install bootlace

Using Bootlace
--------------

Bootlace depends on `bootstrap`_, which must currently be installed separately.

Individual :mod:`bootlace` components generally don't require any additional installation.

Using bootlace will require that your website loads the bootstrap CSS and javascript assets. Bootlace relies on
`dominate`_ to render HTML tags, and provides two primary utility functions, :func:`~bootlace.util.as_tag` and
:func:`~bootlace.util.render` to help you do this::

    from bootlace import as_tag, render
    from bootlace.icon import Icon

    # Create a bootstrap icon
    icon = Icon('home')

    # Convert the icon to a dominate tag
    icon_tag = as_tag(icon)

    # Render the icon tag to a string
    icon_html = render(icon_tag)

    print(icon_html)






.. _bootstrap: https://getbootstrap.com
.. _dominate: https://pypi.org/project/dominate/
