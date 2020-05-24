#!/usr/bin/env python3

# first import the Model class from docplex.mp
from docplex.mp.model import Model
from cplex import Cplex

# https://ibmdecisionoptimization.github.io/tutorials/html/Linear_Programming.html#Algorithms-for-solving-LPs
class ILPSummarizer:

    def __init__(self, sentence_importance, sentence_lengths, maxlen = 50):
        # create one model instance, with a name
        model = Model(name='ILPSummarizerModel')

        self.nr_s = len(sentence_lengths)
        # params
        w = sentence_importance                              # sentence importance 
        l = sentence_lengths                                 # lenth of each sentence -> nr of words
        xkeys = range(0, len(sentence_importance))
        x = model.binary_var_list(keys=len(sentence_importance), name="", key_format="%s")  # weather sentence_i should be included in the variables

        expr = model.sum(l[i] * w[i] * x[i]  for i in range(0, self.nr_s)) 
        model.set_objective(sense="max", expr=expr)              # Max sum(l_i * w_i * x_i)
        model.add_constraint(sum(l[i] * x[i] for i in range(0, self.nr_s)) <= maxlen) # where we have a constraint on the max pres length                  

        self.model = model

    def solve_summ(self):
        print("Solving the model\n")
        sol = self.model.solve(log_output=True)
        vars = [int(x.name) for x in sol.iter_variables()]

        return vars
        



# ilp_sum = ILPSummarizer(sentence_importance=[0.3, 0.5, 0.7], sentence_lengths=[4, 5, 10])
# ilp_sum.solve_summ()