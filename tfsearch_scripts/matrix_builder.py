'''
Takes both a query and control output file generated from running tfSearch
and molds such data into a count-matrix that can be used for machine-learning
and classification purposes.
'''

import argparse
import copy

ENTRY_QUALIFIER = '::' # valid tfSearch outputs contain the '::' string

class TFSearchOutputWrapper():
    def __init__(self, is_control):
        self._is_control = is_control
        self._pwms = {} # key => PWM, value => count
        self._accns = set()
        
    def get_pwms(self):
        return self._pwms
    
    def get_accessions(self):
        return self._accns
    
    def add_pwm(self, k, v):
        self._pwms[k] = v
        
    def add_accession(self, accn):
        self._accns.add(accn)
        
    def debug(self):
        print(len(self.get_accessions()), 'accessions;', len(self.get_pwms()), 'pwms')

def get_count(s):
    ''' 
    Extracts the numerical count of a PWM in any given tfSearch output string.
    @param s: tfSearch output string.
    @return: count representing PWM-count in a user-provided tfSearch string.
    '''
    str_found = s[s.rfind(ENTRY_QUALIFIER): ]
    str_found = str_found.replace(ENTRY_QUALIFIER, '').strip()
    num = str_found[0: str_found.find('(')] # right-brace ends the count
    return int(num)

def parse(f):
    ''' 
    Extract all PWMs shared across both query and control input files.
    @param files: List of both control and query input files.
    '''
    d = {} # key => accession, value => PWM and its respective count
    for i in open(f):
        i = i.strip()
        if ENTRY_QUALIFIER in i: # only print line if valid entry
            num = get_count(i)
            i = i.split(' ')
            # idx 2 => PWM ID, idx 3 => PWM name; remove trailing comma
            accn, pwm = i[0], i[2] + ' ' + i[3][:-1]
            if accn not in d:
                d[accn] = {pwm: 0}
            d[accn][pwm] = num
    return d

def unique_pwms(control, query):
    ''' 
    Extracts all PWMs which are shared across control and query parsed files.
    The end result is a collection representing all PWMs which serve as the
    columns of a count-matrix.
    @param control: Parsed control input file.
    @param query: Parsed query input file.
    @return: set of PWMs shared across both control and query input files.
    '''
    union = set()
    for d in [control, query]:
        for accn in d:
            pwms = set(list(d[accn].keys()))
            union.update(pwms)
    return union

def debug_matrix(m):
    for row in range(len(m)):
        for col in range(len(m[row])):
            print(m[row][col], ' ', end='')
        print()

def build_matrix(control, query, bool_array):
    ''' 
    The matrix is such that you have n rows. Each row is a sequence from both
    the control and query datasets. Each PWM column, j, references a list of 
    counts of length n. Thus, the index [ i , j ] can be used to retrieve the
    PWM-count in a given sequence.
    @param control: Parsed control input file.
    @param query: Parsed query input file.
    @param bool_array: Array referencing which dataset is control or not
    '''
    all_pwms = {pwm: 0 for pwm in unique_pwms(control, query)} # PWMs will serve as matrix columns
    #num_rows = len(control) + len(query) # references the total number of rows
    rownum = 0 # serves as the row-counter
    header = ['Sequence', '\t'.join(list(all_pwms.keys())), 'Target']
    print('\t'.join(header)) # display header; first line
    
    for i, dataset in enumerate([control, query]):        
        for accn in dataset: # for each accession in dataset...
            counts = copy.deepcopy(all_pwms) # create PWM copy; for saving counts to 
            pwms = dataset[accn] # ... get all accession-specific PWMs.
            print(accn, end='') ### references 'Sequence' column ###
            for pwm in pwms: # iterate over PWM collection, set PWM count
                num = pwms[pwm]
                counts[pwm] = num # set the PWM-specific count
            
            print('\t' + '\t'.join([str(i) for i in 
                             list(counts.values())]), end='') ### references PWM counts ###
            print('\t' + str(int(bool_array[i])))
            rownum += 1
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-control', metavar='FILE', required=True,
                        help='tfSearch output; control file [req]')
    parser.add_argument('-query', metavar='FILE', required=True,
                        help='tfSearch output; query file [req]')
    args = vars(parser.parse_args())
    try:
        control = parse(f = args['control'])
        query = parse(f = args['query'])
        build_matrix(control, query, [False, True])
        
    except KeyboardInterrupt:
        print()
    