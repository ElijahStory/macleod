Macleod
======================================================

Start here:
----------

If you're on Mac or Linux, you are going to have a good time. If you are on Windows, come back tomorrow.

* Navigate to the gui subfolder
* Execute the gui_alpha.py file with python

To check the consistency of modules you will need to place the prover executables into the provers/ sub-directory. Once you have the provers in the correct directory edit the configuration file for your platform within the conf/ sub-directory. 

About the project:
------------------

This program consists of a set of scripts designed for key reasoning tasks frequently encountered in ontology design and verification. At the moment it focuses on automating tasks that can be accomplished independent of the semantic of concepts and relations. These tasks are consistency checking of ontologies and their modules as well as checking whether competency questions, providing as ''lemmas'', are entailed.

While the program primarily targets first-order ontologies specified in the Common Logic (CL) syntax, some parts of it can also be used for reasoning about ontologies in LADR (Prover9/Mace4) or TPTP syntax (accepted by many first-order theorem provers and model finders). The tasks are accomplished by running existing automated theorem provers and model finders in parallel to establish consistency or inconsistency of an ontology or a module thereof, or to prove a sentence from an ontology (or module) or to find a counterexample of the sentence.
Moreover, the tool exploits the modularity of ontologies, which manifests itself in its file CL imports structure. 

In the near future it will be integrated with COLORE to provide design, verification, and other reasoning support for all ontologies in the repository.

