#!/usr/bin/python

# (C) Copyright 2013 Graham Neubig
# 
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Lesser General Public License
# (LGPL) version 2.1 which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/lgpl-2.1.html
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.

import sys
import random
import argparse
from collections import defaultdict

# Main Method
def main():
    parser = argparse.ArgumentParser(description="Run mert on question answering systems")
    parser.add_argument('--init_weight_file', type=str)
    parser.add_argument('--random_restarts', default=20, type=int)
    parser.add_argument('--threshold_only', action="store_true")
    parser.add_argument('--threshold', default=1, type=float)
    args = parser.parse_args()

    # Data
    questions = defaultdict(lambda: [])
    feat_names = {}

    # load the file
    for line in sys.stdin:
        line = line.strip()
        (qid, correct, feat_str) = line.split(" ||| ")
        feats = {}
        for entry in feat_str.split(" "):
            (k, v) = entry.split("=")
            feats[k] = float(v)
            feat_names[k] = 1
        questions[qid].append( (int(correct), feats) )
    
    # Run mert with:
    # Initial weights if we have them
    init_weights = {}
    if args.init_weight_file:
        init_weight_file = open(args.init_weight_file, "r")
        for line in init_weight_file:
            k, v = line.split(" ")
            init_weights[k] = float(v)
        init_weight_file.close()

    best_weights = execute_mert(questions, feat_names, init_weights, args.threshold,args.random_restarts, args.threshold_only)

    for k, v in best_weights.items():
        print "%s %f" % (k, v)

# Public Method
# This is a public method which can be used from other python scripts.
# Param:
#   - questions
#        list of tuple which stores all candidate answers.
#        questions = [
#            choice(1,1) 
#            choice(1,2)
#            choice(1,3)
#            ....
#            choice(q,c)
#        ]
#        where q = number of question and c = number of choices and
#        choice(qj,cj) = ( 1 if is_correct(qj,cj) else 0 , feats_score )
#        feats_score = dictionary which map features score of each candidate to its score:
#        {
#            feat_1: score_feat_1 
#            ...
#            feat_n: score_feat_n
#        }
#   - feat_names
#        dictionary of all features_names which have values of 1s
#        {
#            feat_1: 1
#            feat_2: 1
#            ...
#            feat_n: 1
#        }
#   - threshold: value of threshold
#   - random_restart: number of restart (script will find the best value)
#
def execute_mert(questions, feat_names, init_weights={}, threshold=1.0, random_restarts=20,threshold_only=False):
    best_weights = {}
    if len(questions) > 0: # there is some work to do!
        (best_score, best_weights) = run_mert(questions, dict(init_weights), threshold, threshold_only,feat_names)
        if not len(init_weights):
            # one weight initialized
            for name in feat_names.keys():
                (next_score, next_weights) = run_mert(questions, {name: 1}, threshold, threshold_only,feat_names)
                if next_score > best_score: (best_score, best_weights) = (next_score, next_weights)
                (next_score, next_weights) = run_mert(questions, {name: -1}, threshold, threshold_only,feat_names)
                if next_score > best_score: (best_score, best_weights) = (next_score, next_weights)
            # random initalization
            for i in range(0, random_restarts):
                init_weights = dict()
                for name in feat_names.keys():
                    init_weights[name] = random.uniform(0, 100)
                (next_score, next_weights) = run_mert(questions, init_weights, threshold, threshold_only,feat_names)
                if next_score > best_score: (best_score, best_weights) = (next_score, next_weights)

        print >> sys.stderr, ""
        print >> sys.stderr, "BEST: C@1=%r, threshold=%r, weights=%r" % (best_score, threshold, best_weights)
    return {feat: (best_weights[feat] if feat in best_weights else 0) for feat in feat_names.keys()}

# Parameters
margin = 1
BIG_NUMBER = 1e10

def dot_product(feat1, feat2):
    ret = 0
    for k, v in feat1.items():
        if k in feat2:
            ret += v * feat2[k]
    return ret

def vec_scalar_product(feat1, scal2):
    if scal2 == 0:
        return {}
    for k, v in feat1.items():
        feat1[k] *= scal2
    return feat1

def vec_sum(feat1, feat2):
    ret = {k:v for (k,v) in feat1.items()}
    for k, v in feat2.items():
        if k not in ret:
            ret[k] = 0
        ret[k] += v
    return ret

def c_at_1(correct, unanswered, total):
    return (correct+float(unanswered)*correct/total)/total

############### Find the intersection between two lines ###############

def find_intersection(s1, v1, s2, v2):
    if s1 == s2:
        return None
    elif v1 == v2:
        return 0
    return (float(v1)-v2)/(s2-s1)

######### Find the second-best line at a particular position ##########

def find_second_best(lines, position):
    scored = []
    for i, line in enumerate(lines):
        scored.append( (-line[0]*position-line[1], line[0], i) )
    scored.sort()
    return lines[scored[1][2]]

########################### convex hull algorithm #####################

# Get the convex hull, which consists of:
#  (span_start, span_end, number_correct, number_unanswered)
#  in order of the span location
def calc_convex_hull(question, weights, gradient, threshold):
    lines = []
    # First, get all the lines. these are tuples of 
    #   value at zero
    #   slope of the line
    #   whether this is a correct answer
    #   whether this is a threshold value
    for correct, feat in question:
        val = dot_product(feat, weights)
        slope = dot_product(feat, gradient)
        lines.append( (slope, val+threshold, 0, 1) )
        lines.append( (slope, val, correct, 0) )
    # Find all the potential crossing points
    cross_map = defaultdict(lambda: set())
    # Get the borders
    cross_map[-BIG_NUMBER].add(-1)
    cross_map[BIG_NUMBER].add(-1)
    for j in range(1, len(lines)):
        for i in range(0, j):
            cross_loc = find_intersection(lines[i][0], lines[i][1], lines[j][0], lines[j][1])
            if cross_loc != None:
                cross_map[cross_loc].add(i)
                cross_map[cross_loc].add(j)
    crosses = sorted(cross_map.keys())
    # Go through all the crosses
    hull = []
    for i in range(1, len(crosses)):
        answer = find_second_best(lines, (crosses[i]+crosses[i-1])/2)
        if len(hull) != 0 and hull[-1][2] == answer[2] and hull[-1][3] == answer[3]:
            hull[-1][1] = crosses[i]
        else:
            hull.append( [crosses[i-1], crosses[i], answer[2], answer[3]] )
    return hull

# Unit tests for the convex hull algorithm to make sure that it is working
def test_calc_convex_hull1():
    weights = {"a": 1}
    gradient = {"b": 1}
    question = []
    question.append( (1, {"a": -2, "b": -1} ) )
    question.append( (0, {"a": 0, "b": 0} ) )
    question.append( (0, {"a": -2, "b": 1} ) )
    question.append( (0, {"a": -2.5, "b": 1} ) )
    question.append( (0, {"a": -8, "b": 2} ) )
    exp = [ [-BIG_NUMBER, -3.0, 1, 0], [-3.0, -1.0, 0, 1], [-1.0, 1.0, 0, 0], [1.0, 7.0, 0, 1], [7.0, BIG_NUMBER, 0, 0] ]
    act = calc_convex_hull(question, weights, gradient, 1)
    if exp != act:
        print "exp: %r\nact: %r" % (exp, act)
        sys.exit(1)


def test_calc_convex_hull2():
    weights = {"a": 1}
    gradient = {"b": 1}
    question = []
    question.append( (0, {"a": 0, "b": 2} ) )
    question.append( (0, {"a": 0, "b": 3} ) )
    question.append( (1, {"a": 0, "b": 3} ) )
    question.append( (0, {"a": 0, "b": 8} ) )
    question.append( (0, {"a": -1500, "b": 1000} ) )
    exp = [ [-BIG_NUMBER, -1.0, 0, 0], [-1.0, 0.2, 0, 1], [0.2, float(1500-1)/(1000-8), 0, 0], [float(1500-1)/(1000-8), float(1500+1)/(1000-8), 0, 1], [float(1500+1)/(1000-8), BIG_NUMBER, 0, 0] ]
    act = calc_convex_hull(question, weights, gradient, 1)
    if exp != act:
        print "exp: %r\nact: %r" % (exp, act)
        sys.exit(1)
    
def test_calc_convex_hull3():
    weights = {"a": 1}
    gradient = {"b": 1}
    question = []
    question.append( (0, {"a": 0, "b": 0} ) )
    question.append( (0, {"a": 0, "b": 2} ) )
    question.append( (1, {"a": 0, "b": 2} ) )
    question.append( (0, {"a": 0, "b": 3} ) )
    question.append( (0, {"a": 0, "b": 5} ) )
    exp = [ [-BIG_NUMBER, -0.5, 0, 0], [-0.5, 0.5, 0, 1], [0.5, BIG_NUMBER, 0, 0] ]
    act = calc_convex_hull(question, weights, gradient, 1)
    if exp != act:
        print "exp: %r\nact: %r" % (exp, act)
        sys.exit(1)

def test_calc_convex_hull4():
    weights = {"a": 1}
    gradient = {"b": 1}
    question = []
    question.append( (1, {"a": -2, "b": -1} ) )
    question.append( (0, {"a": 0, "b": 0} ) )
    question.append( (0, {"a": -2, "b": 1} ) )
    question.append( (0, {"a": -2.5, "b": 1} ) )
    question.append( (0, {"a": -8, "b": 2} ) )
    exp = [ [-BIG_NUMBER, -2.0, 1, 0], [-2.0, BIG_NUMBER, 0, 0] ]
    act = calc_convex_hull(question, weights, gradient, 0)
    if exp != act:
        print "exp: %r\nact: %r" % (exp, act)
        sys.exit(1)

# test_calc_convex_hull1()
# test_calc_convex_hull2()
# test_calc_convex_hull3()
# test_calc_convex_hull4()
# sys.exit(1)

############ calculate the number of correct answers #################

def calc_answers(questions, weights, threshold):
    correct_tot = 0
    unanswered_tot = 0
    for question in questions.values():
        answers = []
        for correct, feat in question:
            answers.append( (dot_product(weights, feat), correct) )
        answers.sort()
        answers.reverse()
        if answers[0][0] <= answers[1][0]+threshold:
            unanswered_tot += 1
        else:
            correct_tot += answers[0][1]
    return [correct_tot, unanswered_tot]

######################## line search algorithm #######################

def line_search(questions, weights, gradient, threshold):
    base_values = [0, 0]
    diff_values = defaultdict(lambda: (0,0))
    for question in questions.values():
        # Calculate the convex hull
        convex_hull = calc_convex_hull(question, weights, gradient, threshold)
        # Update the base values
        base_values[0] += convex_hull[0][2]
        base_values[1] += convex_hull[0][3]
        # For each pair in the hull
        for i in range(1, len(convex_hull)):
            prev_span = convex_hull[i-1]
            next_span = convex_hull[i]
            # find the difference, and ignore if its zero
            diffs = (next_span[2]-prev_span[2], next_span[3]-prev_span[3])
            if (diffs[0] != 0) or (diffs[1] != 0):
                prev_val = diff_values[next_span[0]]
                diff_values[next_span[0]] = (prev_val[0] + diffs[0], prev_val[1] + diffs[1])
    positions = sorted(diff_values.keys())
    if positions:
        # Given the different values, find the one with the lowest error
        positions.append(positions[-1]+2*margin) # to make the calculation loop easier
        best_score = c_at_1(base_values[0], base_values[1], len(questions))
        best_pos = min(positions[0] - margin, 0)
        best_values = list(base_values)
        for k in range(0, len(diff_values)):
            pos = positions[k]
            base_values[0] += diff_values[pos][0]
            base_values[1] += diff_values[pos][1]
            my_score = c_at_1(base_values[0], base_values[1], len(questions))
            if my_score > best_score:
                best_score = my_score
                if positions[k] < 0 and positions[k+1] > 0:
                    best_pos = 0
                else:
                    best_pos = (positions[k] + positions[k+1]) / 2.0
                best_values = list(base_values)
        weights = vec_sum(weights, vec_scalar_product(gradient, best_pos))
    act_values = calc_answers(questions, weights, threshold)
    act_score = c_at_1(act_values[0], act_values[1], len(questions))
    # if act_values != best_values:
    #     print "ERROR: act_values %r != best_values %r" % (act_values, best_values)
    #     sys.exit(1)
    return (weights, act_score)

def run_mert(questions, init_weights, threshold, threshold_only, feat_names):

    # Initialize
    weights = init_weights
    score_before = -1
    score_after = 0

    # Do the loop
    act_values = calc_answers(questions, weights, threshold)
    act_score = c_at_1(act_values[0], act_values[1], len(questions))
    # print >> sys.stderr, "BEFORE C@1=%r, threshold=%r, weights=%r" % (act_score, threshold, weights)
    while score_before < score_after:
        score_before = score_after
        if not threshold_only:
            for name in feat_names.keys():
                gradient = {name: 1}
                (weights, score_after) = line_search(questions, weights, gradient, threshold)
                # print >> sys.stderr, "C@1=%r, threshold=%r, weights=%r" % (score_after, threshold, weights)
        gradient = dict(weights)
        (weights, score_after) = line_search(questions, weights, gradient, threshold)
        # print >> sys.stderr, "C@1=%r, threshold=%r, weights=%r" % (score_after, threshold, weights)
    act_values = calc_answers(questions, weights, threshold)
    act_score = c_at_1(act_values[0], act_values[1], len(questions))

    print >> sys.stderr, "FINAL C@1=%r, threshold=%r, weights=%r" % (act_score, threshold, weights)
    return (score_after, weights)

############################ START #################################
if __name__ == '__main__':
    main()
