Getting Started with SpotterBase
================================

Installation
------------

You can install SpotterBase from source:

.. code-block:: console

   git clone https://github.com/jfschaefer/spotterbase
   cd spotterbase
   python3 -m pip install -r requirements.txt
   python3 -m pip install -e .


If you want, you can test the installation by running the tests:

.. code-block:: console

   python3 -m spotterbase.test


Ways to use SpotterBase
-----------------------

SpotterBase can be used in different ways:

1. As a **command line tool**. There are various commands for pre-processing documents and
   converting annotations in different formats.
2. As a **library**. It has a lot of functionality for working with annotations and documents.
3. As a **framework**. It can act as a framework for building and running your own spotters.


How can I develop a spotter?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are two different approaches you can take:

1. Use the SpotterBase command line tools and develop your own spotter as a separate program.

   - **Steps:**

      1. Use the SpotterBase command line tools to pre-process the documents or download
         an existing pre-processed corpus.
         Depending your needs, you may need a custom pre-processing pipeline.
      2. Run your custom spotter over the pre-processed documents and create annotations.
      3. Use the SpotterBase command line tools to convert the annotations to the desired format.

   - **Advantages:** You don't have to get to know the SpotterBase code base and you don't have to
     worry about adding SpotterBase as a dependency.
     Furthermore, you are free to choose any programming language you want.
   - **Disadvantages:** The pre-processed documents may not contain all the information you need.
     Furthermore, you miss out on the existing SpotterBase code for running spotters
     and aggregating results.

2. Develop a spotter using SpotterBase as a library.

   - **Approach:** Iterate over the documents and create the annotations for them.
     How much of the SpotterBase library you use is up to you.
   - **Advantages:** You get all the functionality of SpotterBase and you can use it in your
     own code.
   - **Disadvantages:** You have to get to know the SpotterBase code base and have SpotterBase
     as a dependency.

3. Develop a spotter using SpotterBase as a framework.

   - **Approach:** Implement your spotter as a subclass of :class:`spotterbase.spotters.spotter.Spotter` class.
     In particular, you will have to implement a method that takes a document and returns annotations
     as an interator over RDF triples.
   - **Advantages:** You can use SpotterBase functionality for running your spotter over a corpus
     and aggregating the results.
   - **Disadvantages:** You have to get to know the SpotterBase code base and have SpotterBase
     as a dependency.

