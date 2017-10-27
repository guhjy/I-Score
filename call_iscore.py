import iscore as isc
import pandas
import math
import itertools
import numpy
import string
import equal_bin_discretization as discrete

#The values of each column should be between 0 and 1
#def scale_up(in_list, up_value):
    


def read_file(f_addr):
    df = pandas.read_excel(f_addr)
#    columns = df.columns
    return df


##########################Test if df has changed at the end (i.e., columns is not a view only)
def convert_nominal_to_int(df):
    columns = df.columns
    for c in columns:
        temp_list = []
        temp_dict = {}
        count = 1
        if type(df[c].values[0]) == type(u''):
            for val in df[c].values:
                if val not in temp_dict:
                    temp_dict[val] = count
                    count += 1
                temp_list.append(temp_dict[val])
            df[c] = pandas.DataFrame({c: temp_list})
    return df


##########################Test if df has changed at the end (i.e., columns is not a view only)
#Gives us the ganularity of 11
def convert_normalized_to_discrete_equal_section(df):
    columns = df.columns
    for c in columns:
        temp_list = []
        temp_dict = {}
        if type(df[c].values[0]) == type(numpy.float64(1.4)):#1.4 is just a random number
            for val in df[c].values:
                if val not in temp_dict:
                    temp_dict[val] = int(round(val * 10))
                temp_list.append(temp_dict[val])
            df[c] = pandas.DataFrame({c:temp_list})
    return df


def convert_normalized_to_discrete_equal_bin(df, bins_num):
    columns = df.columns
    for c in columns:
        temp_columns = []
        #temp_dict = {}
        if type(df[c].values[0]) == type(numpy.float64(1.4)):#1.4 is just a random number
            for val in df[c].values:
                temp_columns.append(int(round(val * 10)))
                #if val not in temp_dict:
                    #temp_dict[val] = int(round(val * 10))
                #temp_list.append(temp_dict[val])
            discrete_col, cutoff = discrete.discretize(temp_columns, bins_num) 
            df[c] = pandas.DataFrame({c:discrete_col})
    return df


def get_all_initial_subsets(columns_label_list, subset_len):
    return set(itertools.combinations(columns_label_list, subset_len))    



#Not very efficient in terms of space
def initialize_cells(subset_len, granularity_num):
    #cells = [[] for i in xrange(pow(granularity_num, subset_len))]
    cells = []
    count = pow(granularity_num, subset_len)
    while count > 0:
        cells.append([])
        count -= 1
    return cells



def correct_name(name):
    #No name starts with number or special character, or has : in the name
    invalidChars = set(string.punctuation)
#    invalidChars = set(string.punctuation.replace("_", ""))
#    if any(char in invalidChars for char in word):
    for char in name:
        if char in invalidChars:
            name = name.replace(char, "_")
    if (name[0] in invalidChars) or name[0].isdigit():
        name = 'dummy' + name
    return name



def partition(df, features_subset, granularity_num):
    #cells = initialize_cells(len(features_subset), granularity_num)
    cells = {}
    cell_inx = 0
    for row_num, row in enumerate(df.itertuples(), 1):
        height = len(features_subset) - 1
        cell_inx = 0
        for f in features_subset:
            cell_inx += getattr(row, f) * pow(granularity_num, height)
            height -= 1
        #cells[cell_inx].append(row)
        if cell_inx not in cells:
            cells[cell_inx] = [row]
        else:
            cells[cell_inx].append
    return cells



def get_iscore(df, feature_sample, granularity_num, target_feature_name):
    cells = partition(df, feature_sample, granularity_num)
    target_values = df[target_feature_name].values
    cells_avg = []    

    for key in cells:
        cl = cells[key]
        temp = 0
        temp_counter = 0
        avg = 0
        for elem in cl:
            temp += getattr(elem, target_feature_name)
            temp_counter += 1
        if temp_counter != 0:
            avg = float(temp)/temp_counter
        cells_avg.append(avg)
    
    return isc.compute_iscore(target_values, cells_avg)


#Backward Dropping Algorithm
def BDA(df, initial_features_sample, granularity_num, target_feature_name):
    #global_max_iscore = -float('Inf')
    #global_max_subset = []
    global_max_iscore = get_iscore(df, initial_features_sample, granularity_num, target_feature_name)
    global_max_subset = initial_features_sample
    sample_star = initial_features_sample


    while len(sample_star) > 1: 
        local_max_iscore = -float('Inf')
        local_max_subset = []
        for i in range(len(sample_star)):
            feature_sample = sample_star[:i] + sample_star[i+1:] 
            #Compute I-Score
            iscore = get_iscore(df, feature_sample, granularity_num, target_feature_name)
             
            if iscore > local_max_iscore:
                local_max_iscore = iscore
                local_max_subset = feature_sample

        #Drop a variable
        sample_star = local_max_subset
       
        #Keep the best I-Score
        if local_max_iscore > global_max_iscore:
            global_max_iscore = local_max_iscore
            global_max_subset = local_max_subset
#        print 'global_max_subset', global_max_subset
    return global_max_iscore, global_max_subset


#Backward Dropping Algorithm
#def BDA(df, initial_features_sample, granularity_num, target_feature_name):
#    #global_max_iscore = -float('Inf')
#    #global_max_subset = []
#    global_max_iscore = get_iscore(df, initial_features_sample, granularity_num, target_feature_name)
#    global_max_subset = [initial_features_sample]
#    sample_star = initial_features_sample
#    
#    print 'before: ', initial_features_sample
#
#    while len(sample_star) > 1: 
#        local_max_iscore = -float('Inf')
#        local_max_subset = []
#        print 'local_max_subset1: ', local_max_subset
#        for i in range(len(sample_star)):
#            feature_sample = sample_star[:i] + sample_star[i+1:] 
#            #Compute I-Score
#            iscore = get_iscore(df, feature_sample, granularity_num, target_feature_name)
#             
#            if iscore > local_max_iscore:
#                local_max_iscore = iscore
#                local_max_subset = [feature_sample]
#                print 'local_max_subset4: ', local_max_subset, '[feature_sample]: ', [feature_sample]
#            if iscore == local_max_iscore:
#                local_max_subset = local_max_subset.append(feature_sample)
#                print 'local_max_subset5: ', local_max_subset
#            print 'local_max_subset2: ', local_max_subset
#
#        print 'local_max_subset3: ', local_max_subset
#        #Drop a variable
#        sample_star = local_max_subset
#       
#        #Keep the best I-Score
#        if local_max_iscore > global_max_iscore:
#            global_max_iscore = local_max_iscore
#            global_max_subset = local_max_subset
#        if local_max_iscore == global_max_iscore:
#            global_max_subset.append(local_max_subset)
##        print 'global_max_subset', global_max_subset
#    return global_max_iscore, global_max_subset

#def add_max(max_list, vector):
#    if len(max_list) > 0:
#        if max_list[0] < value:
#            max_list = [value]
#        if max_list[0] == value:
#           max_list.append(value)
#    return max_list
     

if __name__ == '__main__':
    f_addr = '/home/seyedmah/Desktop/normalized_data_Oct25.xlsx'
    target_feature_name = 'skip_percentage'
    initial_subset_len = 45
    bins_num = 11#It is fixed according to convert_normalized_to_discrete function
    max_iscore = -float('Inf')
    max_subset = []

    df = read_file(f_addr)   
    df = convert_nominal_to_int(df)
    df = convert_normalized_to_discrete_equal_bin(df, bins_num)

    #Standard columns' name: starts with no number of special characters
    temp = {}
    for name in df.columns:
        temp[name] = correct_name(name) 
    df = df.rename(columns = temp)
 
    #Remove target column for creating the feature sets
    df2 = df.copy(deep=True)
######Check is the drop function creats a copy of df2 or use aliasing???
    df2 = df2.drop(target_feature_name, 1)#where 1 is the axis number (0 for rows and 1 for columns)
#    all_subsets = get_all_initial_subsets(df2.columns, initial_subset_len)
    all_subsets = [df2.columns]
   
    #print all_subsets
     
    count = 0
    total_num = len(all_subsets)
    while len(all_subsets) > 0:
        s = all_subsets.pop()
    #for s in all_subsets:
        
        #Get the feature set with the highest I-Score according to the initial set 
        iscore, selected_set = BDA(df, s, bins_num, target_feature_name)
        count += 1
        print  '(', str(count), ' out of ', total_num, ') I-Score: ', iscore
        print 'Selected Subset: ', selected_set, '\n'
        
        if iscore > max_iscore:
            max_iscore = iscore
            max_subset = [selected_set] 
        if iscore == max_iscore:
           max_subset.append(selected_set)
    print 'Initial subset length: ', initial_subset_len
    print 'Best I-Score: ', max_iscore
    print 'Best feature set: ', max_subset










