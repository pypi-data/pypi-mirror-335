import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
import itertools
import pandas as pd


def process(args):

    combinations = list(itertools.combinations(args.run_name_step4, 2))

    for comb in combinations:

        file1 = f'./{comb[0]}_step4/exp_values.tsv'
        file2 = f'./{comb[1]}_step4/exp_values.tsv'
        df1 = pd.read_csv(file1, sep="\t", header=None, names=["col1", "col2", "col3"])
        df2 = pd.read_csv(file2, sep="\t", header=None, names=["col1", "col2", "col3"])
        common_rows = pd.merge(df1, df2, on="col1", suffixes=("_file1", "_file2"))

        x = common_rows["col2_file1"]
        y = common_rows["col2_file2"]

        correlation_coefficient = np.corrcoef(np.array(x), np.array(y))[0, 1]
        with open(os.path.join('./',args.run_name+'_step5','log.txt'),'a') as f_out:
            f_out.write(f'PCC between {comb[0]} and {comb[1]}: {correlation_coefficient}\n')

        plt.scatter(x, y, alpha=0.7)
        plt.xlabel(f'exp in {comb[0]}')
        plt.ylabel(f'exp in {comb[1]}')
        plt.title(f"PCC: {correlation_coefficient}")
        plt.grid(True)
        plt.savefig(os.path.join('./',args.run_name+'_step5',comb[0]+'_vs_'+comb[1]+'.png'))
        plt.close()


def main():    
    # Input arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run_name', required=True, help='the name of this run')
    parser.add_argument('--run_name_step4', required=True, nargs='+', help='all names of runs in step4 to be compared')

    args = parser.parse_args()

    if len(args.run_name_step4) < 2:
        parser.error('--run_name_step4 expects at least two values')

    # Main function

    os.makedirs(f'./{args.run_name}_step5')

    process(args)


if __name__ == "__main__":
    main()


