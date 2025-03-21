Examples
########

Text without a condition
=========================

Text Styling
------------

Render my Text with **bold** and *italic* text.

code-block
----------

With an example for a code block:

.. code-block:: python

   print("Hello World")


Text with a condition
=====================

.. if:: html

   Text Styling
   ------------

   Render my Text with **bold** and *italic* text.

   code-block
   ----------

   With an example for a code block:

   .. code-block:: python

      print("Hello World")

Text with a negative condition
==============================

.. if:: pdf

   Text Styling
   ------------

   Render my Text with **bold** and *italic* text.

   code-block
   ----------

   With an example for a code block:

   .. code-block:: python

      print("Hello World")
