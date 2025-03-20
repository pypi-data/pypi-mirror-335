.. include:: /includes/_links.rst

How to pass MIB to the Manager
------------------------------

Q. How to make use of random MIBs at my Manager application?

A. Starting from PySNMP 4.3.x, plain-text (ASN.1) MIBs can be
   automatically parsed into PySNMP form by the
   `PySMI`_ tool.  PySNMP will call PySMI
   automatically, parsed PySNMP MIB will be cached in
   $HOME/.pysnmp/mibs/ (default location).

   MIB compiler could be configured to search for plain-text
   MIBs at multiple local and remote locations. As for remote
   MIB repos, you are welcome to use our collection of ASN.1
   MIB files at `mibs.pysnmp.com`_ as shown below.

.. literalinclude:: /../../examples/hlapi/v3arch/asyncio/manager/cmdgen/custom-asn1-mib-search-path.py
   :start-after: """  #
   :language: python

.. code:
    :language: python

    # Configure the SNMP engine with access to the
    # common Linux ASN.1 (Textual) MIB directories...
    from pysnmp import hlapi
    from pysnmp.smi import compiler
    engine = hlapi.Engine()
    builder = engine.get_mib_builder()
    compiler.add_mib_compiler(builder, sources=[
        '/usr/share/snmp/mibs',
        os.path.expanduser('~/.snmp/mibs'),
        'https://mibs.pysnmp.com/asn1/@mib@',
    ])

:download:`Download</../../examples/hlapi/v3arch/asyncio/manager/cmdgen/custom-asn1-mib-search-path.py>` script.

Alternatively, you can invoke the `mibdump`_ command
(shipped with PySMI) by hand and this way compile plain-text MIB
into PySNMP format. Once the compiled MIBs are stored in a directory,
add the directory to your MibBuilder's MibSources.

.. code::

    builder = engine.get_mib_builder()
    # Make ./mibs available to all OIDs that are created
    # e.g. with "MIB-NAME-MIB::identifier"
    builder.add_mib_sources(builder_module.DirMibSource(
        os.path.join( HERE, 'mibs')
    ))
