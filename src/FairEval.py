# -*- coding: utf-8 -*-

'''
Created 09/2021

@author: Katrin Ortmann
'''

import argparse
import os, sys, re
from io import TextIOWrapper

#####################################

def precision(evaldict, version="traditional", weights={}):
    """
    Calculate traditional, fair or weighted precision value.
    
    Precision is calculated as the number of true positives
    divided by the number of true positives plus false positives
    plus (optionally) additional error types.

    Input:
    - A dictionary with error types as keys and counts as values, e.g.,
      {"TP" : 10, "FP" : 2, "LE" : 1, ...}

      For 'traditional' evaluation, true positives (key: TP) and 
      false positives (key: FP) are required.
      The 'fair' evaluation is based on true positives (TP),
      false positives (FP), labeling errors (LE), boundary errors (BE)
      and labeling-boundary errors (LBE).
      The 'weighted' evaluation can include any error type
      that is given as key in the weight dictionary.
      For missing keys, the count is set to 0.

    - The desired evaluation method. Options are 'traditional', 
      'fair', and 'weighted'. If no weight dictionary is specified,
      'weighted' is identical to 'fair'.

    - A weight dictionary to specify how much an error type should
      count as one of the traditional error types (or as true positive). 
      Per default, every traditional error is counted as one error (or true positive)
      and each error of the additional types is counted as half false positive and half false negative:

      {"TP" : {"TP" : 1},
       "FP" : {"FP" : 1},
       "FN" : {"FN" : 1},
       "LE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "BE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "LBE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5}}
    
      Other suggested weights to count boundary errors as half true positives:
      
      {"TP" : {"TP" : 1},
       "FP" : {"FP" : 1},
       "FN" : {"FN" : 1},
       "LE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "BE" : {"TP" : 0.5, "FP" : 0.25, "FN" : 0.25},
       "LBE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5}}
    
      Or to include different types of boundary errors:

      {"TP" : {"TP" : 1},
       "FP" : {"FP" : 1},
       "FN" : {"FN" : 1},
       "LE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "LBE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "BEO" : {"TP" : 0.5, "FP" : 0.25, "FN" : 0.25},
       "BES" : {"TP" : 0.5, "FP" : 0, "FN" : 0.5},
       "BEL" : {"TP" : 0.5, "FP" : 0.5, "FN" : 0}} 

    Output:
    The precision for the given input values. 
    In case of a ZeroDivisionError, the precision is set to 0.

    """
    traditional_weights = {
       "TP" : {"TP" : 1},
       "FP" : {"FP" : 1},
       "FN" : {"FN" : 1}
    }
    default_fair_weights = {
       "TP" : {"TP" : 1},
       "FP" : {"FP" : 1},
       "FN" : {"FN" : 1},
       "LE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "BE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "LBE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5}
       }
    try:
        tp = 0
        fp = 0

        #Set default weights for traditional evaluation
        if version == "traditional":
            weights = traditional_weights

        #Set weights to default 
        #for fair evaluation or if no weights are given      
        elif version == "fair" or not weights:
            weights = default_fair_weights

        #Add weighted errors to true positive count
        tp += sum(
            [w.get("TP", 0) * evaldict.get(error, 0) for error, w in weights.items()]
        )

        #Add weighted errors to false positive count
        fp += sum(
            [w.get("FP", 0) * evaldict.get(error, 0) for error, w in weights.items()]
        )
        
        #Calculate precision
        return tp / (tp + fp)

    #Output 0 if there is neither true nor false positives
    except ZeroDivisionError:
        return 0.0

######################

def recall(evaldict, version="traditional", weights={}):
    """
    Calculate traditional, fair or weighted recall value.
    
    Recall is calculated as the number of true positives
    divided by the number of true positives plus false negatives
    plus (optionally) additional error types.

    Input:
    - A dictionary with error types as keys and counts as values, e.g.,
      {"TP" : 10, "FN" : 2, "LE" : 1, ...}

      For 'traditional' evaluation, true positives (key: TP) and 
      false negatives (key: FN) are required.
      The 'fair' evaluation is based on true positives (TP),
      false negatives (FN), labeling errors (LE), boundary errors (BE)
      and labeling-boundary errors (LBE).
      The 'weighted' evaluation can include any error type
      that is given as key in the weight dictionary.
      For missing keys, the count is set to 0.

    - The desired evaluation method. Options are 'traditional', 
      'fair', and 'weighted'. If no weight dictionary is specified,
      'weighted' is identical to 'fair'.

    - A weight dictionary to specify how much an error type should
      count as one of the traditional error types (or as true positive). 
      Per default, every traditional error is counted as one error (or true positive)
      and each error of the additional types is counted as half false positive and half false negative:

      {"TP" : {"TP" : 1},
       "FP" : {"FP" : 1},
       "FN" : {"FN" : 1},
       "LE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "BE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "LBE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5}}
    
      Other suggested weights to count boundary errors as half true positives:
      
      {"TP" : {"TP" : 1},
       "FP" : {"FP" : 1},
       "FN" : {"FN" : 1},
       "LE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "BE" : {"TP" : 0.5, "FP" : 0.25, "FN" : 0.25},
       "LBE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5}}
    
      Or to include different types of boundary errors:

      {"TP" : {"TP" : 1},
       "FP" : {"FP" : 1},
       "FN" : {"FN" : 1},
       "LE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "LBE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "BEO" : {"TP" : 0.5, "FP" : 0.25, "FN" : 0.25},
       "BES" : {"TP" : 0.5, "FP" : 0, "FN" : 0.5},
       "BEL" : {"TP" : 0.5, "FP" : 0.5, "FN" : 0}} 

    Output:
    The recall for the given input values. 
    In case of a ZeroDivisionError, the recall is set to 0.

    """
    traditional_weights = {
       "TP" : {"TP" : 1},
       "FP" : {"FP" : 1},
       "FN" : {"FN" : 1}
    }
    default_fair_weights = {
       "TP" : {"TP" : 1},
       "FP" : {"FP" : 1},
       "FN" : {"FN" : 1},
       "LE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "BE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
       "LBE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5}
       }
    try:
        tp = 0
        fn = 0

        #Set default weights for traditional evaluation
        if version == "traditional":
            weights = traditional_weights

        #Set weights to default 
        #for fair evaluation or if no weights are given      
        elif version == "fair" or not weights:
            weights = default_fair_weights

        #Add weighted errors to true positive count
        tp += sum(
            [w.get("TP", 0) * evaldict.get(error, 0) for error, w in weights.items()]
        )

        #Add weighted errors to false negative count
        fn += sum(
            [w.get("FN", 0) * evaldict.get(error, 0) for error, w in weights.items()]
        )

        #Calculate recall
        return tp / (tp + fn)

    #Return zero if there are neither true positives nor false negatives
    except ZeroDivisionError:
        return 0.0

######################

def fscore(evaldict):
    """
    Calculates F1-Score from given precision and recall values.

    Input: A dictionary with a precision (key: Prec) and recall (key: Rec) value.
    Output: The F1-Score. In case of a ZeroDivisionError, the F1-Score is set to 0.
    """
    try:
        return 2 * (evaldict.get("Prec", 0) * evaldict.get("Rec", 0)) \
                 / (evaldict.get("Prec", 0) + evaldict.get("Rec", 0))
    except ZeroDivisionError:
        return 0.0

######################

def overlap_type(span1, span2):
    """
    Determine the error type of two (overlapping) spans.

    The function checks, if and how span1 and span2 overlap.
    The first span serves as the basis against which the second
    span is evaluated.

    span1 ---XXXX---
    span2 ---XXXX--- TP (identical)
    span2 ----XXXX-- BEO (overlap)
    span2 --XXXX---- BEO (overlap)
    span2 ----XX---- BES (smaller)
    span2 ---XX----- BES (smaller)
    span2 --XXXXXX-- BEL (larger)
    span2 --XXXXX--- BEL (larger)
    span2 -X-------- False (no overlap)

    Input:
    Tuples (beginSpan1, endSpan1) and (beginSpan2, endSpan2),
    where begin and end are the indices of the corresponding tokens.

    Output: 
    Either one of the following strings
    - "TP" = span1 and span2 are identical, i.e., actually no error here
    - "BES" = span2 is shorter and contained within span1 (with at most one identical boundary)
    - "BEL" = span2 is longer and contains span1 (with at most one identical boundary)
    - "BEO" = span1 and span2 overlap with no identical boundary
    or False if span1 and span2 do not overlap.   
    """
    #Identical spans
    if span1[0] == span2[0] and span1[1] == span2[1]:
        return "TP"

    #Start of spans is identical
    if span1[0] == span2[0]:
        #End of 2 is within span1
        if span2[1] >= span1[0] and span2[1] < span1[1]:
            return "BES"
        #End of 2 is behind span1
        else:
            return "BEL"
    #Start of 2 is before span1
    elif span2[0] < span1[0]:
        #End is before span 1
        if span2[1] < span1[0]:
            return False
        #End is within span1
        elif span2[1] < span1[1]:
            return "BEO"
        #End is identical or to the right
        else:
            return "BEL"
    #Start of 2 is within span1
    elif span2[0] >= span1[0] and span2[0] <= span1[1]:
        #End of 2 is wihtin span1
        if span2[1] <= span1[1]:
            return "BES"
        #End of 2 is to the right
        else:
            return "BEO"
    #Start of 2 is behind span1
    else:
        return False

#####################################

def compare_spans(target_spans, system_spans, focus="target"):
    """
    Compare system and target spans to identify correct/incorrect annotations.

    The function takes a list of target spans and system spans.
    Each span is a 4-tuple of 
    - label: the span type as string
    - begin: the index of first token; equals end for spans of length 1
    - end: the index of the last token; equals begin for spans of length 1
    - tokens: a set of token indices included in the span 
              (this allows the correct evaluation of 
               partially and multiply overlapping spans;
               to allow for changes of the token set, 
               the span tuple is actually implemented as a list.)

    The function first performs traditional evaluation on these spans
    to identify true positives, false positives, and false negatives.
    Then, the additional error types for fair evaluation are determined,
    following steps 1 to 4:
    1. Count 1:1 mappings (TP, LE)
    2. Count boundary errors (BE = BES + BEL + BEO)
    3. Count labeling-boundary errors (LBE)
    4. Count 1:0 and 0:1 mappings (FN, FP)    

    Input:
    - List of target spans
    - List of system spans
    - Wether to focus on the system or target annotation (default: target)

    Output: A dictionary containing
    - the counts of TP, FP, and FN according to traditional evaluation 
      (per label and overall)
    - the counts of TP, FP, LE, BE, BES, BEL, BEO, and FN 
      (per label and overall; BE = BES + BEL + BEO)
    - a confusion matrix {target_label1 : {system_label1 : count,
                                           system_label2 : count,
                                           ...},
                          target_label2 : ... 
                         }
      with an underscore '_' representing an empty label (FN/FP)
    """

    ##################################

    def _max_sim(t, S):
        """
        Determine the most similar span s from S for span t.

        Similarity is defined as 
        1. the maximum number of shared tokens between s and t and
        2. the minimum number of tokens only in t
        If multiple spans are equally similar, the shortest s is chosen.
        If still multiple spans are equally similar, the first one in the list is chosen,
        which corresponds to the left-most one if sentences are read from left to right.

        Input:
        - Span t as 4-tuple [label, begin, end, token_set]
        - List S containing > 1 spans

        Output: The most similar s for t.
        """
        S.sort(key=lambda s: (0-len(t[3].intersection(s[3])), 
                              len(t[3].difference(s[3])), 
                              len(s[3].difference(t[3])), 
                              s[2]-s[1]))
        return S[0]

    ##################################
        
    traditional_error_types = ["TP", "FP", "FN"]
    additional_error_types = ["LE", "BE", "BEO", "BES", "BEL", "LBE"]

    #Initialize empty eval dict
    eval_dict = {"overall" : {"traditional" : {err_type : 0 for err_type 
                                               in traditional_error_types},
                              "fair" : {err_type : 0 for err_type 
                                        in traditional_error_types + additional_error_types}},
                 "per_label" : {"traditional" : {},
                                "fair" : {}},
                 "conf" : {}}

    #Initialize per-label dict
    for s in target_spans + system_spans:
        if not s[0] in eval_dict["per_label"]["traditional"]:
            eval_dict["per_label"]["traditional"][s[0]] = {err_type : 0 for err_type 
                                                           in traditional_error_types}
            eval_dict["per_label"]["fair"][s[0]] = {err_type : 0 for err_type 
                                                    in traditional_error_types + additional_error_types}
        #Initialize confusion matrix
        if not s[0] in eval_dict["conf"]:
            eval_dict["conf"][s[0]] = {}
    eval_dict["conf"]["_"] = {}
    for lab in list(eval_dict["conf"])+["_"]:
        for lab2 in list(eval_dict["conf"])+["_"]:
            eval_dict["conf"][lab][lab2] = 0

    ################################################
    ### Traditional evaluation (overall + per label)
    
    for t in target_spans:
        #Spans in target and system annotation are true positives
        if t in system_spans:
            eval_dict["overall"]["traditional"]["TP"] += 1
            eval_dict["per_label"]["traditional"][t[0]]["TP"] += 1
        #Spans only in target annotation are false negatives
        else:
            eval_dict["overall"]["traditional"]["FN"] += 1
            eval_dict["per_label"]["traditional"][t[0]]["FN"] += 1
    for s in system_spans:
        #Spans only in system annotation are false positives
        if not s in target_spans:
            eval_dict["overall"]["traditional"]["FP"] += 1
            eval_dict["per_label"]["traditional"][s[0]]["FP"] += 1

    ###########################################################
    ### Fair evaluation (overall, per label + confusion matrix)

    ### Identical spans (TP and LE)
    
    ### TP
    #Identify true positives (identical spans between target and system)
    tps = [t for t in target_spans if t in system_spans]
    for t in tps:
        s = [s for s in system_spans if s == t]
        if s:
            s = s[0]
            eval_dict["overall"]["fair"]["TP"] += 1
            eval_dict["per_label"]["fair"][t[0]]["TP"] += 1
            #After counting, remove from input lists
            system_spans.remove(s)
            target_spans.remove(t)
    
    ### LE
    #Identify labeling error: identical span but different label
    les = [t for t in target_spans 
           if any(t[0] != s[0] and t[1:3] == s[1:3] for s in system_spans)]
    for t in les:
        s = [s for s in system_spans if t[0] != s[0] and t[1:3] == s[1:3]]
        if s:
            s = s[0]
            #Overall: count as one LE
            eval_dict["overall"]["fair"]["LE"] += 1
            #Per label: depending on focus count for target label or system label
            if focus == "target":
                eval_dict["per_label"]["fair"][t[0]]["LE"] += 1
            elif focus == "system":
                eval_dict["per_label"]["fair"][s[0]]["LE"] += 1
            #Add to confusion matrix
            eval_dict["conf"][t[0]][s[0]] += 1
            #After counting, remove from input lists
            system_spans.remove(s)
            target_spans.remove(t)
    
    ### Boundary errors

    #Create lists to collect matched spans
    counted_target = list()
    counted_system = list()

    #Sort lists by span length (shortest to longest)
    target_spans.sort(key=lambda t : t[2] - t[1])
    system_spans.sort(key=lambda s : s[2] - s[1])

    ### BE 

    ## 1. Compare input lists
    #Identify boundary errors: identical label but different, overlapping span
    for t in target_spans:

        #Find possible boundary errors
        be = [s for s in system_spans
              if t[0] == s[0] and t[1:3] != s[1:3] 
                 and overlap_type((t[1], t[2]), (s[1], s[2])) in ("BES", "BEL", "BEO")]
        if not be: continue

        #If there is more than one possible BE, take most similar one
        if len(be) > 1:
            s = _max_sim(t, be)
        else:        
            s = be[0]

        #Determine overlap type
        be_type = overlap_type((t[1], t[2]), (s[1], s[2]))

        #Overall: Count as BE and more fine-grained BE type
        eval_dict["overall"]["fair"]["BE"] += 1
        eval_dict["overall"]["fair"][be_type] += 1

        #Per-label: count as general BE and specific BE type
        eval_dict["per_label"]["fair"][t[0]]["BE"] += 1
        eval_dict["per_label"]["fair"][t[0]][be_type] += 1
        
        #Add to confusion matrix
        eval_dict["conf"][t[0]][s[0]] += 1

        #Remove matched spans from input list
        system_spans.remove(s)
        target_spans.remove(t)

        #Remove matched tokens from spans
        matching_tokens = t[3].intersection(s[3])
        s[3] = s[3].difference(matching_tokens)
        t[3] = t[3].difference(matching_tokens)

        #Move matched spans to counted list
        counted_system.append(s)
        counted_target.append(t)

    ## 2. Compare input target list with matched system list
    for t in target_spans:

        #Find possible boundary errors in already matched spans
        #that still share unmatched tokens
        be = [s for s in counted_system
              if t[0] == s[0] and t[1:3] != s[1:3] 
                and overlap_type((t[1], t[2]), (s[1], s[2])) in ("BES", "BEL", "BEO")
                and t[3].intersection(s[3])]
        if not be: continue

        #If there is more than one possible BE, take most similar one
        if len(be) > 1:
            s = _max_sim(t, be)
        else:        
            s = be[0]

        #Determine overlap type
        be_type = overlap_type((t[1], t[2]), (s[1], s[2]))

        #Overall: Count as BE and more fine-grained BE type
        eval_dict["overall"]["fair"]["BE"] += 1
        eval_dict["overall"]["fair"][be_type] += 1

        #Per-label: count as general BE and specific BE type
        eval_dict["per_label"]["fair"][t[0]]["BE"] += 1
        eval_dict["per_label"]["fair"][t[0]][be_type] += 1
        
        #Add to confusion matrix
        eval_dict["conf"][t[0]][s[0]] += 1

        #Remove matched span from input list
        target_spans.remove(t)

        #Remove matched tokens from spans
        matching_tokens = t[3].intersection(s[3])
        counted_system[counted_system.index(s)][3] = s[3].difference(matching_tokens)
        t[3] = t[3].difference(matching_tokens)

        #Move target span to counted list
        counted_target.append(t)
    
    ## 3. Compare input system list with matched target list
    for s in system_spans:

        #Find possible boundary errors in already matched target spans
        be = [t for t in counted_target
               if t[0] == s[0] and t[1:3] != s[1:3] 
                  and overlap_type((t[1], t[2]), (s[1], s[2])) in ("BES", "BEL", "BEO")
                  and t[3].intersection(s[3])]
        if not be: continue

        #If there is more than one possible BE, take most similar one
        if len(be) > 1:
            t = _max_sim(s, be)
        else:        
            t = be[0]

        #Determine overlap type
        be_type = overlap_type((t[1], t[2]), (s[1], s[2]))

        #Overall: Count as BE and more fine-grained BE type
        eval_dict["overall"]["fair"]["BE"] += 1
        eval_dict["overall"]["fair"][be_type] += 1

        #Per-label: count as general BE and specific BE type
        eval_dict["per_label"]["fair"][t[0]]["BE"] += 1
        eval_dict["per_label"]["fair"][t[0]][be_type] += 1
        
        #Add to confusion matrix
        eval_dict["conf"][t[0]][s[0]] += 1

        #Remove matched span from input list
        system_spans.remove(s)

        #Remove matched tokens from spans
        matching_tokens = t[3].intersection(s[3])
        counted_target[counted_target.index(t)][3] = t[3].difference(matching_tokens)
        s[3] = s[3].difference(matching_tokens)

        #Move system span to counted list
        counted_system.append(s)

    ### LBE 

    ## 1. Compare input lists
    #Identify labeling-boundary errors: different label but overlapping span
    for t in target_spans:

        #Find possible boundary errors
        lbe = [s for s in system_spans
               if t[0] != s[0] and t[1:3] != s[1:3] 
                  and overlap_type((t[1], t[2]), (s[1], s[2])) in ("BES", "BEL", "BEO")]
        if not lbe: continue

        #If there is more than one possible LBE, take most similar one
        if len(lbe) > 1:
            s = _max_sim(t, lbe)
        else:        
            s = lbe[0]

        #Overall: count as LBE
        eval_dict["overall"]["fair"]["LBE"] += 1

        #Per label: depending on focus count as LBE for target or system label
        if focus == "target":
            eval_dict["per_label"]["fair"][t[0]]["LBE"] += 1
        elif focus == "system":
            eval_dict["per_label"]["fair"][s[0]]["LBE"] += 1

        #Add to confusion matrix
        eval_dict["conf"][t[0]][s[0]] += 1

        #Remove matched spans from input list
        system_spans.remove(s)
        target_spans.remove(t)

        #Remove matched tokens from spans
        matching_tokens = t[3].intersection(s[3])
        s[3] = s[3].difference(matching_tokens)
        t[3] = t[3].difference(matching_tokens)

        #Move spans to counted lists
        counted_system.append(s)
        counted_target.append(t)

    ## 2. Compare input target list with matched system list
    for t in target_spans:

        #Find possible labeling-boundary errors in already matched system spans
        lbe = [s for s in counted_system
               if t[0] != s[0] and t[1:3] != s[1:3] 
                  and overlap_type((t[1], t[2]), (s[1], s[2])) in ("BES", "BEL", "BEO")
                  and t[3].intersection(s[3])]
        if not lbe: continue

        #If there is more than one possible LBE, take most similar one
        if len(lbe) > 1:
            s = _max_sim(t, lbe)
        else:        
            s = lbe[0]

        #Overall: count as LBE
        eval_dict["overall"]["fair"]["LBE"] += 1

        #Per label: depending on focus count as LBE for target or system label
        if focus == "target":
            eval_dict["per_label"]["fair"][t[0]]["LBE"] += 1
        elif focus == "system":
            eval_dict["per_label"]["fair"][s[0]]["LBE"] += 1

        #Add to confusion matrix
        eval_dict["conf"][t[0]][s[0]] += 1

        #Remove matched span from input list
        target_spans.remove(t)

        #Remove matched tokens from spans
        matching_tokens = t[3].intersection(s[3])
        counted_system[counted_system.index(s)][3] = s[3].difference(matching_tokens)
        t[3] = t[3].difference(matching_tokens)

        #Move target span to counted list
        counted_target.append(t)
    
    ## 3. Compare input system list with matched target list
    for s in system_spans:

        #Find possible labeling-boundary errors in already matched target spans
        lbe = [t for t in counted_target
               if t[0] != s[0] and t[1:3] != s[1:3] 
                  and overlap_type((t[1], t[2]), (s[1], s[2])) in ("BES", "BEL", "BEO")
                  and t[3].intersection(s[3])]
        if not lbe: continue

        #If there is more than one possible LBE, take most similar one
        if len(lbe) > 1:
            t = _max_sim(s, lbe)
        else:        
            t = lbe[0]

        #Overall: count as LBE
        eval_dict["overall"]["fair"]["LBE"] += 1

        #Per label: depending on focus count as LBE for target or system label
        if focus == "target":
            eval_dict["per_label"]["fair"][t[0]]["LBE"] += 1
        elif focus == "system":
            eval_dict["per_label"]["fair"][s[0]]["LBE"] += 1

        #Add to confusion matrix
        eval_dict["conf"][t[0]][s[0]] += 1

        #Remove matched span from input list
        system_spans.remove(s)

        #Remove matched tokens from spans
        matching_tokens = t[3].intersection(s[3])
        counted_target[counted_target.index(t)][3] = t[3].difference(matching_tokens)
        s[3] = s[3].difference(matching_tokens)

        #Move matched system span to counted list
        counted_system.append(s)

    ### 1:0 and 0:1 mappings

    #FN: identify false negatives
    for t in target_spans:
        eval_dict["overall"]["fair"]["FN"] += 1     
        eval_dict["per_label"]["fair"][t[0]]["FN"] += 1
        eval_dict["conf"][t[0]]["_"] += 1

    #FP: identify false positives
    for s in system_spans:
        eval_dict["overall"]["fair"]["FP"] += 1
        eval_dict["per_label"]["fair"][s[0]]["FP"] += 1
        eval_dict["conf"]["_"][s[0]] += 1

    return eval_dict

############################

def annotation_stats(target_spans, **config):
    """
    Count the target annotations to display simple statistics.

    The function takes a list of target spans
    with each span being a 4-tuple [label, begin, end, token_set]
    and adds the included labels to the general data stats dictionary.

    Input:
    - List of target spans
    - Config dictionary
    
    Output: The config dictionary is modified in-place.
    """
    stats_dict = config.get("data_stats", {})
    for span in target_spans:
        if span[0] in stats_dict:
            stats_dict[span[0]] += 1
        else:
            stats_dict[span[0]] = 1
    config["data_stats"] = stats_dict

############################

def get_spans(sentence, **config):
    """
    Return spans from CoNLL2000 or span files.

    The function determines the data format of the input sentence
    and extracts the spans from it accordingly.

    If desired, punctuation can be ignored (config['ignore_punct'] == True)
    for files in the CoNLL2000 format that include POS information.
    The following list of tags is considered as punctuation:
    ['$.', '$,', '$(', #STTS
     'PUNCT', #UPOS
     'PUNKT', 'KOMMA', 'COMMA', 'KLAMMER', #custom
     '.', ',', ':', '(', ')', '"', '‘', '“', '’', '”' #PTB
    ]

    Labels that should be ignored (included in config['exclude']
    or not included in config['labels'] if config['labels'] != 'all')
    are also removed from the resulting list.

    Input:
    - List of lines for a given sentence
    - Config dictionary

    Output: List of spans that are included in the sentence.
    """

    ################

    def spans_from_conll(sentence):
        """
        Read annotation spans from a CoNLL2000 file.

        The function takes a list of lines (belonging to one sentence)
        and extracts the annotated spans. The lines are expected to
        contain three space-separated columns:

        Form XPOS Annotation

        Form:       Word form
        XPOS:       POS tag of the word (ideally STTS, UPOS, or PTB)
        Annotation: Span annotation in BIO format (see below); 
                    multiple spans are separated with the pipe symbol '|'
        
        BIO tags consist of the token's position in the span 
        (begin 'B', inside 'I', outside 'O'), a dash '-' and the span label,
        e.g., B-NP, I-AC, or in the case of stacked annotations I-RELC|B-NP.

        The function accepts 'O', '_' and '' as annotations outside of spans.

        Input: List of lines belonging to one sentence.
        Output: List of spans as 4-tuples [label, begin, end, token_set]
        """
        spans = []
        span_stack = []

        #For each token
        for t, tok in enumerate(sentence):
            
            #Token is [Form, XPOS, Annotation]
            tok = tok.split()

            #Token is not annotated
            if tok[-1] in ["O", "_", ""]:
                #Add previous stack to span list
                #(sorted from left to right)
                while span_stack:
                    spans.append(span_stack.pop(0))
                span_stack = []
                continue
                                
            #Token is annotated
            #Split stacked annotations at pipe
            annotations = tok[-1].strip().split("|")

            #While there are more annotation levels on
            #the stack than at the current token,
            #close annotations on the stack (i.e., move
            #them to result list)
            while len(span_stack) > len(annotations):
                spans.append(span_stack.pop())

            #For each annotation of the current token
            for i, annotation in enumerate(annotations):
                
                #New span
                if annotation.startswith("B-"):
                    
                    #If it's the first annotation level and there is
                    #something on the stack, move it to result list
                    if i == 0 and span_stack:
                        while span_stack:
                            spans.append(span_stack.pop(0))
                    #Otherwise, end same-level annotation on the
                    #stack (because a new span begins here) and 
                    #move it to the result list
                    else:
                        while len(span_stack) > i:
                            spans.append(span_stack.pop())
                    
                    #Last part of BIO tag is the label
                    label = annotation.split("-")[1]

                    #Create a new span with this token's
                    #index as start and end (incremendet by one).
                    s = [label, t+1, t+1, {t+1}]
                    
                    #Add on top of stack
                    span_stack.append(s)

                #Span continues
                elif annotation.startswith("I-"):
                    #Increment the end index of the span
                    #at the level of this annotation on the stack
                    span_stack[i][2] = t+1
                    #Also, add the index to the token set
                    span_stack[i][-1].add(t+1)

        #Add sentence final span(s)
        while span_stack:
            spans.append(span_stack.pop(0))

        return spans

    ################

    def spans_from_lines(sentence):
        """
        Read annotation spans from a span file.

        The function takes a list of lines (belonging to one sentence)
        and extracts the annotated spans. The lines are expected to
        contain four tab-separated columns:

        Label    Begin    End    Tokens

        Label:  Span label
        Begin:  Index of the first included token (must be convertible to int)
        End:    Index of the last included token (must be convertible to int
                and equal or greater than begin)
        Tokens: Comma-separated list of indices of the tokens in the span
                (must be convertible to int with begin <= i <= end);
                if no (valid) indices are given, the range begin:end is used
        
        Input: List of lines belonging to one sentence.
        Output: List of spans as 4-tuples [label, begin, end, token_set]
        """
        spans = []
        for line in sentence:
            vals = line.split("\t")
            label = vals[0]
            if not label:
                print("ERROR: Missing label in input.")
                return []
            try:
                begin = int(vals[1])
                if begin < 1: raise ValueError
            except ValueError:
                print("ERROR: Begin {0} is not a legal index.".format(vals[1]))
                return []
            try:
                end = int(vals[2])
                if end < 1: raise ValueError
                if end < begin: begin, end = end, begin
            except ValueError:
                print("ERROR: End {0} is not a legal index.".format(vals[2]))
                return []
            try:
                toks = [int(v.strip()) for v in vals[-1].split(",") 
                        if int(v.strip()) >= begin and int(v.strip()) <= end]
                toks = set(toks)
            except ValueError:
                toks = []
            if not toks:
                toks = [i for i in range(begin, end+1)]
            spans.append([label, begin, end, toks])
        return spans

    ################

    #Determine data format

    #Span files contain 4 tab-separated columns
    if len(sentence[0].split("\t")) == 4:
        format = "spans"
        spans = spans_from_lines(sentence)

    #CoNLL2000 files contain 3 space-separated columns
    elif len(sentence[0].split(" ")) == 3:
        format = "conll2000"        
        spans = spans_from_conll(sentence)
    else:
        print("ERROR: Unknown input format")
        return []          
    
    #Exclude punctuation from CoNLL2000, if desired
    if format == "conll2000" \
        and config.get("ignore_punct") == True:

        #For each punctuation tok
        for i, line in enumerate(sentence):
            if line.split(" ")[1] in ["$.", "$,", "$(", #STTS
                                      "PUNCT", #UPOS
                                      "PUNKT", "KOMMA", "COMMA", "KLAMMER", #custom
                                      ".", ",", ":", "(", ")", "\"", "‘", "“", "’", "”" #PTB
                                     ]:

                for s in range(len(spans)):
                    #Remove punc tok from set
                    spans[s][-1].discard(i+1)

                    #If span begins with punc, move begin
                    if spans[s][1] == i+1:
                        if spans[s][2] != None and spans[s][2] > i+1:
                            spans[s][1] = i+2
                        else:
                            spans[s][1] = None
                        
                    #If span ends with punc, move end
                    if spans[s][2] == i+1:
                        if spans[s][1] != None and spans[s][1] <= i:
                            spans[s][2] = i
                        else:
                            spans[s][2] = None
                
                #Remove empty spans
                spans = [s for s in spans if s[1] != None and s[2] != None and len(s[3]) > 0]

    #Exclude unwanted labels
    spans = [s for s in spans 
             if not s[0] in config.get("exclude", []) 
                and ("all" in config.get("labels", [])
                     or s[0] in config.get("labels", []))]
    
    return spans

############################

def get_sentences(filename):
    """
    Reads sentences from input files.

    The function iterates through the input file and
    yields a list of lines that belong to one sentence.
    Sentences are expected to be separated by an empty line.

    Input: Filename of the input file.
    Output: Yields a list of lines for each sentence. 
    """
    file = open(filename, mode="r", encoding="utf-8")
    sent = []

    for line in file:
        #New line: yield collected lines
        if sent and not line.strip():
            yield sent
            sent = []
        #New line but nothing to yield
        elif not line.strip():
            continue
        #Collect line of current sentence
        else:
            sent.append(line.strip())

    #Last sentence if file doesn't end with empty line
    if sent:
        yield sent

    file.close()
        
#############################

def update_dict(eval_dict, sent_counts):
    """
    Add error counts of a given sentence to overall eval dict.

    The function takes the individual error counts of a sentence
    included in sent_counts dict and adds them the overall
    result dict eval_dict. Moreover, it updates the confusion matrix.

    Input: Overall eval dict and individual sentence dict
    Output: Modified eval dict
    """

    for version in ["traditional", "fair"]:
        #Add overall counts for traditional and fair evaluation
        for cat in sent_counts["overall"][version]:
            if not cat in eval_dict["overall"][version]:
                eval_dict["overall"][version][cat] = 0
            eval_dict["overall"][version][cat] += sent_counts["overall"][version][cat]

        #Add per-label counts for traditional and fair evaluation
        for label in sent_counts["per_label"][version]:
            if label in eval_dict["per_label"][version]:
                for cat in sent_counts["per_label"][version][label]:
                    if cat in eval_dict["per_label"][version][label]:
                        eval_dict["per_label"][version][label][cat] += sent_counts["per_label"][version][label][cat]
                    else:
                        eval_dict["per_label"][version][label][cat] = sent_counts["per_label"][version][label][cat]
            else:
                eval_dict["per_label"][version][label] = {}
                for cat in sent_counts["per_label"][version][label]:
                    eval_dict["per_label"][version][label][cat] = sent_counts["per_label"][version][label][cat]
    
    #Add counts to confusion matrix
    for lab in sent_counts["conf"]:
        if not lab in eval_dict["conf"]:
            eval_dict["conf"][lab] = {}
        for syslab in sent_counts["conf"][lab]:
            if not syslab in eval_dict["conf"][lab]:
                eval_dict["conf"][lab][syslab] = sent_counts["conf"][lab][syslab]
            else:
                eval_dict["conf"][lab][syslab] += sent_counts["conf"][lab][syslab]

    return eval_dict

#############################

def calculate_results(eval_dict, **config):
    """
    Calculate overall precision, recall, and F-scores.

    The function takes an evaluation dictionary with error counts
    and applies the precision, recall and fscore functions.

    It will calculate the traditional metrics 
    and fair and/or weighted metrics, depending on the 
    value of config['eval_method'].

    The results are stored in the eval dict as 'Prec', 'Rec' and 'F1'
    for overall and per-label counts.

    Input: Evaluation dict and config dict.
    Output: Evaluation dict with added precision, recall and F1 values.
    """

    #If weighted evaluation should be performed
    #copy error counts from fair evaluation
    if "weighted" in config.get("eval_method", []):
        eval_dict["overall"]["weighted"] = {}
        for err_type in eval_dict["overall"]["fair"]:
            eval_dict["overall"]["weighted"][err_type] = eval_dict["overall"]["fair"][err_type]
        for label in eval_dict["per_label"]["fair"]:
            eval_dict["per_label"]["weighted"][label] = {}
            for err_type in eval_dict["per_label"]["fair"][label]:
                eval_dict["per_label"]["weighted"][label][err_type] = eval_dict["per_label"]["fair"][label][err_type]

    #For each evaluation method
    for version in config.get("eval_method", ["traditional", "fair"]):
    
        #Overall results
        eval_dict["overall"][version]["Prec"] = precision(eval_dict["overall"][version], version, config.get("weights", {}))
        eval_dict["overall"][version]["Rec"] = recall(eval_dict["overall"][version], version, config.get("weights", {}))
        eval_dict["overall"][version]["F1"] = fscore(eval_dict["overall"][version])   

        #Per label results
        for label in eval_dict["per_label"][version]:
            eval_dict["per_label"][version][label]["Prec"] = precision(eval_dict["per_label"][version][label], version, config.get("weights", {}))
            eval_dict["per_label"][version][label]["Rec"] = recall(eval_dict["per_label"][version][label], version, config.get("weights", {}))
            eval_dict["per_label"][version][label]["F1"] = fscore(eval_dict["per_label"][version][label])

    return eval_dict

#############################

def output_results(eval_dict, **config):
    """
    Write evaluation results to the output (file).

    The function takes an evaluation dict and writes
    all results to the specified output (file):

    1. Traditional evaluation results
    2. Additional evaluation results (fair and/or weighted)
    3. Result comparison for different evaluation methods
    4. Confusion matrix
    5. Data statistics

    Input: Evaluation dict and config dict.
    """
    outfile = config.get("eval_out", sys.stdout)
    
    ### Output results for each evaluation method
    for version in config.get("eval_method", ["traditional", "fair"]):
        print(file=outfile)
        print("### {0} evaluation:".format(version.title()), file=outfile)

        #Determine error categories to output
        if version == "traditional":
            cats = ["TP", "FP", "FN"]
        elif version == "fair" or not config.get("weights", {}):
            cats = ["TP", "FP", "LE", "BE", "LBE", "FN"]
        else:
            cats = list(config.get("weights").keys())

        #Print header
        print("Label", "\t".join(cats), "Prec", "Rec", "F1", sep="\t", file=outfile)

        #Output results for each label
        for label,val in sorted(eval_dict["per_label"][version].items()):
            print(label, 
                  "\t".join([str(val.get(cat, eval_dict["per_label"]["fair"].get(cat, 0))) 
                             for cat in cats]),
                  "\t".join(["{:04.2f}".format(val.get(metric, 0)*100) 
                             for metric in ["Prec", "Rec", "F1"]]), 
                  sep="\t", file=outfile)

        #Output overall results
        print("overall", 
              "\t".join([str(eval_dict["overall"][version].get(cat, eval_dict["overall"]["fair"].get(cat, 0))) 
                         for cat in cats]),
              "\t".join(["{:04.2f}".format(eval_dict["overall"][version].get(metric, 0)*100) 
                         for metric in ["Prec", "Rec", "F1"]]), 
              sep="\t", file=outfile)

    ### Output result comparison
    print(file=outfile)
    print("### Comparison:", file=outfile)
    print("Version", "Prec", "Rec", "F1", sep="\t", file=outfile)
    for version in config.get("eval_method", ["traditional", "fair"]):
        print(version.title(), 
              "\t".join(["{:04.2f}".format(eval_dict["overall"][version].get(metric, 0)*100) 
                         for metric in ["Prec", "Rec", "F1"]]),
              sep="\t", file=outfile)
    
    ### Output confusion matrix
    print(file=outfile)
    print("### Confusion matrix:", file=outfile)

    #Get set of target labels
    labels = {lab for lab in eval_dict["conf"]}

    #Add system labels
    labels = list(labels.union({syslab 
                                for lab in eval_dict["conf"] 
                                for syslab in eval_dict["conf"][lab]}))

    #Sort alphabetically for output
    labels.sort()

    #Print top row with system labels
    print(r"Target\System", "\t".join(labels), sep="\t", file=outfile)

    #Print rows with target labels and counts
    for targetlab in labels:
        print(targetlab, 
              "\t".join([str(eval_dict["conf"][targetlab].get(syslab, 0)) 
                         for syslab in labels]), 
              sep="\t", file=outfile)

    #Output data statistic
    print(file=outfile)
    print("### Target data stats:", file=outfile)
    print("Label", "Freq", "%", sep="\t", file=outfile)
    total = sum(config.get("data_stats", {}).values())
    for lab, freq in config.get("data_stats", {}).items():
        print(lab, freq, "{:04.2f}".format(freq/total*100), sep="\t", file=outfile)

    #Close output if it is a file
    if isinstance(config.get("eval_out"), TextIOWrapper):
        outfile.close()
    
#############################

def read_config(config_file):
    """
    Function to set program parameters as specified in the config file.

    The following parameters are handled:

    - target_in: path to the target file(s) with gold standard annotation
                 -> output: 'target_files' : [list of target file paths]

    - system_in: path to the system's output file(s), which are evaluated
                 -> output: 'system_files' : [list of system file paths]

    - eval_out: path or filename, where evaluation results should be stored
                if value is a path, output file 'path/eval.csv' is created
                if value is 'cmd' or missing, output is set to sys.stdout
                -> output: 'eval_out' : output file or sys.stdout

    - labels: comma-separated list of labels to evaluate
              defaults to 'all'
              -> output: 'labels' : [list of labels as strings]

    - exclude: comma-separated list of labels to exclude from evaluation
               always contains 'NONE' and 'EMPTY'
               -> output: 'exclude' : [list of labels as strings]

    - ignore_punct: wether to ignore punctuation during evaluation (true/false)
                    -> output: 'ignore_punct' : True/False

    - focus: wether to focus the evaluation on 'target' or 'system' annotations
             defaults to 'target'
             -> output: 'focus' : 'target' or 'system'

    - weights: weights that should be applied during calculation of precision
               and recall; at the same time can serve as a list of additional
               error types to include in the evaluation
               the weights are parsed from comma-separated input formulas of the form
            
               error_type = weight * TP + weight2 * FP + weight3 * FN
            
               -> output: 'weights' : { 'error type' : { 
                                                        'TP' : weight, 
                                                        'FP' : weight, 
                                                        'FN' : weight
                                                        },
                                        'another error type' : {...}
                                      }

    - eval_method: defines which evaluation method(s) to use
                   one or more of: 'traditional', 'fair', 'weighted'
                   if value is 'all' or missing, all available methods are returned
                   -> output: 'eval_method' : [list of eval methods]

    Input: Filename of the config file.
    Output: Settings dictionary.
    """

    ############################

    def _parse_config(key, val):
        """
        Internal function to set specific values for the given keys.
        In case of illegal values, prints error message and sets key and/or value to None.
        Input: Key and value from config file
        Output: Modified key and value
        """
        if key in ["target_in", "system_in"]:
            if os.path.isdir(val): 
                val = os.path.normpath(val)
                files = [os.path.join(val, f) for f in os.listdir(val)]
            elif os.path.isfile(val):
                files = [os.path.normpath(val)]
            else:
                print("Error: '{0} = {1}' is not a file/directory.".format(key, val))
                return None, None
            if key == "target_in":
                return "target_files", files
            elif key == "system_in":
                return "system_files", files
        
        elif key == "eval_out":
            if os.path.isdir(val):
                val = os.path.normpath(val)
                outfile = os.path.join(val, "eval.csv")
            elif os.path.isfile(val):
                outfile = os.path.normpath(val)
            elif val == "cmd":
                outfile = sys.stdout
            else:
                try:
                    p, f = os.path.split(val)
                    if not os.path.isdir(p):
                        os.makedirs(p)
                    outfile = os.path.join(p, f)
                except:
                    print("Error: '{0} = {1}' is not a file/directory.".format(key, val))
                    return None, None
            return key, outfile

        elif key in ["labels", "exclude"]:
            labels = list(set([v.strip() for v in val.split(",") if v.strip()]))
            if key == "exclude":
                labels.append("NONE")
                labels.append("EMPTY")
            return key, labels
        
        elif key == "ignore_punct":
            if val.strip().lower() == "false":
                return key, False
            else:
                return key, True

        elif key == "focus":
            if val.strip().lower() == "system":
                return key, "system"
            else:
                return key, "target"

        elif key == "weights":
            if val == "default":
                return key, {"TP" :  {"TP" : 1},
                             "FP" :  {"FP" : 1},
                             "FN" :  {"FN" : 1},
                             "LE" :  {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
                             "BE" :  {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
                             "LBE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5}}
            else:
                formulas = val.split(",")
                weights = {}

                #For each given formula, i.e., for each error type
                for f in formulas:

                    #Match error type as string-initial letters before equal sign =
                    error_type = re.match(r"\s*(?P<Error>\w+)\s*=", f)
                    if error_type == None:
                        print("WARNING: No error type found in weight formula '{0}'.".format(f))
                        continue
                    else:
                        error_type = error_type.group("Error")

                    weights[error_type] = {}

                    #Match weight for TP
                    w_tp = re.search(r"(?P<TP>\d*\.?\d+)\s*\*?\s*TP", f)
                    if w_tp == None:
                        print("WARNING: Missing weight for TP for error type {0}. Set to 0.".format(error_type))
                        weights[error_type]["TP"] = 0
                    else:
                        try:
                            w_tp = w_tp.group("TP")
                            w_tp = float(w_tp)
                            weights[error_type]["TP"] = w_tp
                        except ValueError:
                            print("WARNING: Weight for TP for error type {0} is not a number. Set to 0.".format(error_type))
                            weights[error_type]["TP"] = 0

                    #Match weight for FP
                    w_fp = re.search(r"(?P<FP>\d*\.?\d+)\s*\*?\s*FP", f)
                    if w_fp == None:
                        print("WARNING: Missing weight for FP for error type {0}. Set to 0.".format(error_type))
                        weights[error_type]["FP"] = 0
                    else:
                        try:
                            w_fp = w_fp.group("FP")
                            w_fp = float(w_fp)
                            weights[error_type]["FP"] = w_fp
                        except ValueError:
                            print("WARNING: Weight for FP for error type {0} is not a number. Set to 0.".format(error_type))
                            weights[error_type]["FP"] = 0

                    #Match weight for FP
                    w_fn = re.search(r"(?P<FN>\d*\.?\d+)\s*\*?\s*FN", f)
                    if w_fn == None:
                        print("WARNING: Missing weight for FN for error type {0}. Set to 0.".format(error_type))
                        weights[error_type]["FN"] = 0
                    else:
                        try:
                            w_fn = w_fn.group("FN")
                            w_fn = float(w_fn)
                            weights[error_type]["FN"] = w_fn
                        except ValueError:
                            print("WARNING: Weight for FN for error type {0} is not a number. Set to 0.".format(error_type))
                            weights[error_type]["FN"] = 0
                if weights:
                    #Add default weights for traditional categories if needed
                    if not "TP" in weights:
                        weights["TP"] = {"TP" : 1}
                    if not "FP" in weights:
                        weights["FP"] = {"FP" : 1}
                    if not "FN" in weights:
                        weights["FN"] = {"FN" : 1}
                    return key, weights
                else:
                    print("WARNING: No valid weights found. Using default weights.")
                    return key, {"TP" :  {"TP" : 1},
                                 "FP" :  {"FP" : 1},
                                 "FN" :  {"FN" : 1},
                                 "LE" :  {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
                                 "BE" :  {"TP" : 0, "FP" : 0.5, "FN" : 0.5},
                                 "LBE" : {"TP" : 0, "FP" : 0.5, "FN" : 0.5}}

        elif key == "eval_method":
            available_methods = ["traditional", "fair", "weighted"]
            if val == "all":
                return key, available_methods
            else:
                methods = []
                for m in available_methods:
                    if m in [v.strip() for v in val.split(",") 
                             if v.strip() and v.strip().lower() in available_methods]:
                        methods.append(m)
                if methods:
                    return key, methods
                else:
                    print("WARNING: No evaluation method specified. Applying all methods.")
                    return key, available_methods

    #############################

    config = dict()
    
    f = open(config_file, mode="r", encoding="utf-8")
    
    for line in f:

        line = line.strip()

        #Skip empty lines and comments
        if not line or line.startswith("#"):
            continue
        
        line = line.split("=")
        key = line[0].strip()
        val = "=".join(line[1:]).strip()
        
        #Store original paths of input files
        if key in ["target_in", "system_in"]:
            print("{0}: {1}".format(key, val))
            config[key] = val

        #Parse config
        key, val = _parse_config(key, val)

        #Skip illegal configs
        if key is None or val is None:
            continue
        
        #Warn before overwriting duplicate config items.
        if key in config:
            print("WARNING: duplicate config item '{0}' found.".format(key))
    
        config[key] = val

    f.close()

    #Stop evaluation if either target or system files are missing
    if not "target_files" in config or not "system_files" in config:
        print("ERROR: Cannot evaluate without target AND system file(s). Quitting.")
        return None

    #Output to sys.stdout if no evaluation file is specified
    elif config.get("eval_out", None) == None:
        config["eval_out"] = sys.stdout  
    #Otherwise open eval file
    else:
        config["eval_out"] = open(config.get("eval_out"), mode="w", encoding="utf-8")
        
    #Set labels to 'all' if no specific labels are given
    if config.get("labels", None) == None:
        config["labels"] = ["all"]

    if config.get("eval_method", None) == None:
        config["eval_method"] = ["traditional", "fair", "weighted"]
    if not config.get("weights", {}) and "weighted" in config.get("eval_method"):
        if not "fair" in config["eval_method"]:
            config["eval_method"].append("fair")
        del config["eval_method"][config["eval_method"].index("weighted")]

    #Output settings at the top of evaluation file
    print("### Evaluation settings:", file=config.get("eval_out"))
    for key in sorted(config.keys()):
        if key in ["target_files", "system_files", "eval_out"]:
            continue
        print("{0}: {1}".format(key, config.get(key)), file=config.get("eval_out"))
    print(file=config.get("eval_out"))

    return config

###########################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',  help='Configuration File', required=True)

    args = parser.parse_args()

    #Read config file into dict
    config = read_config(args.config)

    #Create empty eval dict
    eval_dict = {"overall" : {"traditional" : {}, "fair" : {}}, 
                 "per_label" : {"traditional" : {}, "fair" : {}}, 
                 "conf" : {}}
    for method in config.get("eval_method", ["traditional", "fair"]):
        eval_dict["overall"][method] = {}
        eval_dict["per_label"][method] = {}

    #Create dict to count target annotations
    config["data_stats"] = {}

    #Get system and target files to compare
    #The files must have the same name to be compared
    file_pairs = []
    for t in config.get("target_files", []):
        s = [f for f in config.get("system_files", []) 
             if os.path.split(t)[-1] == os.path.split(f)[-1]]
        if s:
            file_pairs.append((t, s[0]))

    #Go through target and system files in parallel    
    for target_file, system_file in file_pairs:
        
        #For each sentence pair
        for target_sentence, system_sentence in zip(get_sentences(target_file), 
                                                    get_sentences(system_file)):
            
            #Get spans
            target_spans = get_spans(target_sentence, **config)
            system_spans = get_spans(system_sentence, **config)
            
            #Count target annotations for simple statistics.
            #Result is stored in data_stats key of config dict.
            annotation_stats(target_spans, **config)

            #Evaluate spans
            sent_counts = compare_spans(target_spans, system_spans, 
                                        config.get("focus", "target"))

            #Add results to eval dict
            eval_dict = update_dict(eval_dict, sent_counts)

    #Calculate overall results
    eval_dict = calculate_results(eval_dict, **config)

    #Output results
    output_results(eval_dict, **config)