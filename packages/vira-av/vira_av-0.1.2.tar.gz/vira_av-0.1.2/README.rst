VIRA: By-Reference Exon and CDS Viral Genome Annotation.
=======================================================================================================================================================================

.. image:: https://badge.fury.io/py/vira-av.svg
    :target: https://pypi.org/project/vira-av/
    :alt: VIRA Install
.. image:: https://img.shields.io/github/downloads/alevar/vira/total.svg
    :target: https://github.com/alevar/VIRA/releases/latest
    :alt: Github All Releases
.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg
    :target: https://opensource.org/licenses/GPL-3.0
    :alt: GPLv3 License

.. contents::
    :local:
    :depth: 2

Introduction
^^^^^^^^^^^^

VIRA is a fully-automated protocol for lifting annotations over from reference to target genomes 
optimized for viral genomes and primarily developed and tested on HIV and SIV genomes.
The method uses a both the nucleotide and protein sequence information to search for correct alignments between genomes with high degree of sequence divergence. 
The method is also tailored to take advantage of guide protein annotations to further improve the accuracy of alignments and final annotations.


Publications
^^^^^^^^^^^^
Coming...

Documentation
^^^^^^^^^^^^

Installation
^^^^^^^^^^^^

PyPi
""""""""""""

By far the easiest way to install VIRA is by using PyPi.

::

        $ pip install vira-av
        $ vira --help

To uninstall VIRA, simply run:

::

        $ pip uninstall vira-av

Building from source
""""""""""""""""""""

If you want to build it from source, we recommend cloning the git repository as shown below.

::

    $ git clone https://github.com/alevar/snapper.git --recursive
    $ cd snapper
    $ pip install -r requirements.txt
    $ pip install .

.. list-table:: **Requirements**
   :widths: 15 35

   * - Language support
     - Python ≥ 3.6
   * - Dependencies
     - gffread: Install via https://github.com/gpertea/gffread
     - minimap2: Install via https://github.com/lh3/minimap2
     - miniprot: Install via https://github.com/lh3/miniprot
     - snapper: Install via https://github.com/alevar/snapper

Getting started
^^^^^^^^^^^^^^^

Usage: vira [-h] -a ANNOTATION -g GENOME -t TARGET [-q GUIDE] [-o OUTPUT] [--force-cds] [--gffread GFFREAD] [--minimap2 MINIMAP2] [--miniprot MINIPROT]
                   [--snapper SNAPPER] [--keep-tmp] [--tmp-dir TMP_DIR]

Options:

  -a ANNOTATION, --annotation ANNOTATION
                        Path to the query GTF/GFF annotation file
  -g GENOME, --genome GENOME
                        Path to the query genome FASTA file
  -t TARGET, --target TARGET
                        Path to the target genome FASTA file
  -q GUIDE, --guide GUIDE
                        Optional path to the guide annotation file for the target genome. Transcripts and CDS from the guide will be used to validate the annotation
  -o OUTPUT, --output OUTPUT
                        Path to the output GTF file
  --force-cds           Force the CDS from the guide onto the transcript chain, even if that means merging adjacent exons together (can fix alignment artifacts such as
                        spurious introns). If the CDS does not fit the transcript chain, the transcript will be skipped
  --gffread GFFREAD     Path to the gffread executable
  --minimap2 MINIMAP2   Path to the minimap2 executable
  --miniprot MINIPROT   Path to the miniprot executable. If not set - minimap2 will be used to align nucleotide sequence of the CDS instead
  --snapper SNAPPER     Path to the snapper executable
  --keep-tmp            Keep temporary files
  --tmp-dir TMP_DIR     Directory to store temporary files

Help options:

  -h, --help            Prints help message.

Data
^^^^

Sample datasets are provided in the "example" directory to test and get familiar with VIRA.
The included examples can be run with the following base commands from the root directory of the repository:

1. vira --annotation example/query.gtf --output example/output.gtf --genome example/query.fasta --target example/target.fasta --guide example/guide.gtf
