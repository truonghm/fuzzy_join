import pandas as pd
import jellyfish as jf
import numpy as np
import re

def iter_levenshtein_distance(df:pd.DataFrame, first_column:str, second_column:str, remove_special_char:bool=True):
    distances = []
    
    for left_str, right_str in df[[first_column, second_column]].itertuples(index=False):
        if remove_special_char:
            left_str_strip = re.sub(r'[^\w\s]|_', '', left_str.strip().lower())
            right_str_strip = re.sub(r'[^\w\s]|_', '', right_str.strip().lower())
        else:
            left_str_strip = left_str.strip().lower().replace(' ','')
            right_str_strip = right_str.strip().lower().replace(' ','')
        d = jf.levenshtein_distance(left_str_strip, right_str_strip)
        distances.append(d)
    
    return pd.Series(distances)

def vectorized_levenshtein_distance(df:pd.DataFrame, first_column:str, second_column:str, remove_special_char:bool=True):
    if remove_special_char:
        a = df[first_column].str.strip().str.lower().str.replace(' ','').str.replace(r'[^\w\s]|_', '', regex=True)
        b = df[second_column].str.strip().str.lower().str.replace(' ','').str.replace(r'[^\w\s]|_', '', regex=True)
    else:
        a = df[first_column].str.strip().str.lower().str.replace(' ','')
        b = df[second_column].str.strip().str.lower().str.replace(' ','')        
    return np.vectorize(jf.levenshtein_distance)(a, b)
    

def fuzzy_join(left_df, right_df, left_on:list, right_on:list, method:str='best', threshold = 3, apply:str='iteration', remove_special_char:bool=True):

    if method not in ['best', 'full'] or type(left_on) != list or type(right_on) != list:
        raise Exception("Invalid input")

    if len(left_on) != len(right_on):
        raise Exception("Number of key columns for left and right dataframes must be the same")

    if type(threshold) == int:
        threshold = [threshold for x in left_on]
    elif type(threshold) != int:
        if type(threshold) == list and len(threshold) != len(left_on):
            raise Exception("Number of threshold input must be the same with number of key columns")
        elif type(threshold) == list and any([type(t) != int for t in threshold]):
            raise Exception("Invalid input")
        elif type(threshold) != list:
            raise Exception("Invalid input")

    if left_on == right_on:
        left_on = left_on + '_x'
        right_on = right_on + '_y'

    try:
        cross_df = pd.merge(
            pd.concat([left_df, pd.DataFrame({'LEFT_INDEX':range(len(left_df))})], axis=1), 
            right_df, 
            how='cross')
    except pd.errors.MergeError as e:
        cross_df = pd.merge(
            pd.concat([left_df, pd.DataFrame({'LEFT_INDEX':range(len(left_df)), 'tmp_col':1})], axis=1), 
            pd.concat([right_df, pd.DataFrame({'tmp_col':[1]*len(right_df)})], axis=1), 
            on='tmp_col'
        )
        cross_df.drop(columns=['tmp_col'], inplace=True)

    # print(cross_df.columns)
    for i, (m, n) in enumerate(zip(left_on, right_on)):
        if len(left_on) == 1:
            col = 'DISTANCE'
        else:
            col = f'DISTANCE_{i}'
        
        if apply == 'iteration':
            cross_df[col] = iter_levenshtein_distance(
                df=cross_df, 
                first_column=m, 
                second_column=n,
                remove_special_char=remove_special_char
                )
        elif apply == 'vectorized':
            cross_df[col] = vectorized_levenshtein_distance(
                df=cross_df, 
                first_column=m, 
                second_column=n,
                remove_special_char=remove_special_char
                )   
        else:
            raise Exception("Invalid input for apply method")

    if len(left_on) == 1:
        conditions = f'DISTANCE<={threshold[0]}'
    else:
        conditions = " & ".join([f'DISTANCE_{n}<={t}' for n, t in enumerate(threshold)])

    if method == 'full':
        cross_df.drop(columns=['LEFT_INDEX'], inplace=True)
        return cross_df.query(conditions).reset_index(drop=True)

    if method == 'best':
        return cross_df.query(conditions).sort_values('DISTANCE',ascending = True).groupby('LEFT_INDEX').head(1).reset_index(drop=True)[[col for col in cross_df if col != 'LEFT_INDEX']]