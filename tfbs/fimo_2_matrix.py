'''
Creates a count-matrix given FIMO output using its --text format.
'''

import argparse
import pandas
import sys
from collections import OrderedDict

COLNAME_SEQ = 'Sequence'
COLNAME_TARGET = 'Target'
PROG_CHAR ='*'
PROG_TRIGGER = 5e4

def build_skeleton(cont, query):
    sys.stdout.write('Building skeleton matrix')
    sys.stdout.flush()
    pwms = set() # ordering is not important
    all_seqs = []
    
    # loop through both files to derive row-count
    for dataset in [cont, query]:
        seqs = set()
        for linenum, line in enumerate(open(dataset)):
            if linenum != 0:
                line = line.strip().split('\t')
                pwm, seq = line[0: 2]
                pwms.add(pwm)
                seqs.add(seq)
            if linenum % PROG_TRIGGER == 0:
                sys.stdout.write(PROG_CHAR)
                sys.stdout.flush()
        all_seqs.extend(seqs)
    
    # wrap counts in a DataFrame
    m = OrderedDict({COLNAME_SEQ: all_seqs})
    m.update({pwm: [0] * len(all_seqs) for pwm in pwms})
    m.update({COLNAME_TARGET: ['None'] * len(all_seqs)})
    df = pandas.DataFrame(m, index=all_seqs)
    sys.stdout.write('\n')
    sys.stdout.flush()
    return df # return dataframe capturing the matrix

def write(df, csv):
    sys.stdout.write('Saving file\n')
    sys.stdout.flush()
    for i, seq in enumerate(df[COLNAME_SEQ]):
        seq = df[COLNAME_SEQ][i] 
        # replace unique delimiters so both control and query sequences
        # share possible sub-sequences., i.e. match.chr1.111.553
        # is related to chr1.111.553, and so on.
        df[COLNAME_SEQ][i] = seq.replace(':', '.').replace('-', '.')
    df.to_csv(csv)


def populate(df, cont, query):
    sys.stdout.write('Populating count-matrix')
    for i, dataset in enumerate([cont, query]):
        for linenum, line in enumerate(open(dataset)):
            if linenum != 0:
                line = line.strip().split('\t')
                pwm, seq = line[0: 2]
                df[pwm][seq] += 1 # increment sequence-PWM count
                df[COLNAME_TARGET][seq] = i
            if linenum % PROG_TRIGGER == 0:
                sys.stdout.write(PROG_CHAR)
                sys.stdout.flush()
    sys.stdout.write('\n')
    sys.stdout.flush()
    return df # contains actual counts

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-control', required=True, metavar='FILE',
                        help='FIMO --text mode output; control [req]')
    parser.add_argument('-query', required=True, metavar='FILE',
                        help='FIMO --text mode output; query [req]')
    parser.add_argument('-csv', metavar='FILE', default='./out.csv',
                        help='Output file [./out.csv]')
    args = vars(parser.parse_args())
    cont_fname, query_fname = args['control'], args['query']
    df = build_skeleton(cont_fname, query_fname)
    df = populate(df, cont_fname, query_fname)
    write(df, args['csv'])