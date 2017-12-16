"""
Insert boss header here
@RPSkillet
"""

import logging

import macleod.logical.Logical as Logical
import macleod.logical.Connective as Connective
import macleod.logical.Quantifier as Quantifier
import macleod.logical.Negation as Negation
import macleod.logical.Symbol as Symbol

import copy

LOGGER = logging.getLogger(__name__)

class Axiom(object):
    '''
    Our nice containing object that houses the cool stuff
    '''

    def __init__(self, sentence):

        if not isinstance(sentence, Logical.Logical):
            raise ValueError("Axiom's need Logicals")

        self.sentence = sentence

    def __repr__(self):

        return repr(self.sentence)

    def substitute_functions(self): 
        '''
        Step 1.

        Look through our axiom and replace any functions as necessary. Return
        any additional functional predicates that get created along the way.
        '''

        ret_object = copy.deepcopy(self.sentence)

        # Step 1. Substitute any nested functions!
        def dfs_functions(term, accumulator, parent):

            if isinstance(term, Symbol.Predicate):

                if term.has_functions():

                    clause, axiom = term.substitute_function()
                    accumulator.append(axiom)
                    return dfs_functions(clause, accumulator, term)


                else:

                    return term

            if isinstance(term, Quantifier.Quantifier):

                return type(term)(term.variables, [dfs_functions(x, accumulator, term) for x in term.get_term()])

            else:

                return type(term)([dfs_functions(x, accumulator, term) for x in term.get_term()])

        return Axiom(dfs_functions(ret_object, [], None))

    def standardize_variables(self):
        '''
        Step 2.

        Traverse through our sentence replacing quantifiers so everything is
        unique.
        '''

        ret_object = copy.deepcopy(self.sentence)

        def generator():
            '''
            Go through the alphabet backwards by using ASCII codes. If you run
            out... Complain.
            '''

            start = 122

            def next_term():

                nonlocal start

                character = chr(start)
                start -= 1

                if start == 96:

                    raise ValueError("Look man, 26 variables is just too many. I'm not going to even try")

                return character

            return next_term

        def dfs_standardize(term, gen, translations=[]):

            if isinstance(term, Symbol.Predicate):

                left = len(term.variables)

                for idx, var in enumerate(term.variables):

                    for trans in reversed(translations):

                        if var in trans:

                            term.variables[idx] = trans[var]
                            left -= 1
                            break

                if left != 0:
                    LOGGER.warning("Found a constant!")
                    #raise ValueError("Found a free variable!")

                return term

            elif isinstance(term, Quantifier.Quantifier):

                lookup_table = {}

                for idx, var in enumerate(term.variables):

                    lookup_table[var] = gen()
                    term.variables[idx] = lookup_table[var]

                translations.append(lookup_table)

                return type(term)(term.variables, [dfs_standardize(x, gen, translations) for x in term.get_term()])

            else:

                return type(term)([dfs_standardize(x, gen, translations) for x in term.get_term()])

        return Axiom(dfs_standardize(ret_object, generator(),))

    def push_negation(self):

        new = copy.deepcopy(self.sentence)

        def dfs_negate(term):

            if isinstance(term, Symbol.Predicate):

                return term

            elif isinstance(term, Quantifier.Quantifier):

                return type(term)(term.variables, [dfs_negate(x) for x in term.get_term()])

            elif isinstance(term, Negation.Negation):

                return term.push_complete()

            else:

                return type(term)([dfs_negate(x) for x in term.get_term()])

        return Axiom(dfs_negate(new))

    def to_pcnf(self):

        new = copy.deepcopy(self)
        LOGGER.debug("Initial Axiom: " + repr(new))
        ff = new.substitute_functions()
        LOGGER.debug("Substitute Functions: " + repr(ff))
        std_var = ff.standardize_variables()
        LOGGER.debug("Standardized Variables: " + repr(std_var))
        neg = std_var.push_negation()
        LOGGER.debug("Pushed negations: " + repr(neg))

        # Grab out starting logical
        obj = neg.sentence

        def reverse_bfs(root):
            '''
            Conduct a regular BFS over the tree packing each layer into a list
            of [[(term, parent), (term, parent)], ...]

            return that list
            '''

            accumulator = []

            #left = ([(x, root) for x in root.get_term()])
            left = [(root, None)]

            while left != []:

                current, parent = left.pop(0)
                accumulator.append((current, parent))

                if not isinstance(current, Symbol.Predicate):

                    # If care about L->R order do reversed(current.get_term())
                    left.extend([(x, current) for x in current.get_term()])

            return reversed(accumulator)

        queue = reverse_bfs(obj)

        LOGGER.debug("Beginning reversed BFS!")
        # Technically this is our reverse BFS
        for term, parent in queue:

            LOGGER.debug("Current term: " + repr(term))
            LOGGER.debug("Current parent: " + repr(parent))

            if isinstance(term, Quantifier.Quantifier):

                LOGGER.debug("Quantifier detected: " + repr(term))

                # Absorb like-quantifier children, may require multiple passes
                i = 1
                simplified = term.simplify()
                while True:
                    LOGGER.debug("Simplified pass #{}: {}".format(i, repr(simplified)))
                    temp = simplified.simplify()
                    if str(temp) == str(simplified):
                        break
                    else:
                        simplified = temp

                    i = i + 1


                if not parent is None:

                    parent.remove_term(term)
                    parent.set_term(simplified)

                else:

                    obj = simplified

            elif isinstance(term, Connective.Connective):

                # Quantifier coalescence
                p = 1
                coalesced_term = term.coalesce()
                # Keep rescoping till we push a quantifier outside
                #if isinstance(new_term, Connective.Connective):
                #    i = 1
                #    coalesced_term = new_term.coalesce()
                #    while True:
                #        LOGGER.debug("Coalesce pass #{}: {}".format(p, repr(coalesced_term)))

                #        if isinstance(coalesced_term, Connective.Connective):
                #            tmp = coalesced_term.coalesce()
                #            if (repr(tmp) == repr(coalesced_term)):
                #                break
                #            else:
                #                coalesced_term = tmp
                #            p = p + 1
                #        else:
                #            break

                #LOGGER.debug("Coalesced: " + repr(new_term))
                LOGGER.debug("Coalesced other: " + repr(coalesced_term))

                # Keep rescoping till we push a quantifier outside
                if isinstance(coalesced_term, Connective.Connective):
                    i = 1
                    LOGGER.debug("here")
                    scoped_term = coalesced_term.rescope(parent)
                    LOGGER.debug("here?")
                    #while True:
                    #    LOGGER.debug("Rescoped pass #{}: {}".format(i, repr(scoped_term)))

                    #    if isinstance(scoped_term, Connective.Connective):
                    #        tmp = scoped_term.rescope(parent)
                    #        if (repr(tmp) == repr(scoped_term)):
                    #            break
                    #        else:
                    #            scoped_term = tmp
                    #        i = i + 1
                    #    else:
                    #        break

                if not parent is None:

                    parent.remove_term(term)
                    parent.set_term(scoped_term)

                else:

                    obj = scoped_term

        LOGGER.debug("Created Prenex: " + repr(obj))
        onf_obj = obj.to_onf()

        return Axiom(onf_obj)
