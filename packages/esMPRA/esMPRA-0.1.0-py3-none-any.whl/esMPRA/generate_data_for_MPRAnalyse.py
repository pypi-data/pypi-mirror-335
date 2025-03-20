import pickle
import csv
import numpy as np
import pandas as pd
import argparse
import os


def main():

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--step1_dir', required=True, help='the step1 directory where data are used for MPRAnalyse')
    parser.add_argument('--step2_dir', required=True, help='the step2 directory where data are used for MPRAnalyse')
    parser.add_argument('--step3_dir', required=True, help='the step3 directory where data are used for MPRAnalyse')
    parser.add_argument('--run_tag', required=True, help='tag name used for this run')

    args = parser.parse_args()



    with open(os.path.join(args.step1_dir,'seq_to_barcode_dict.pkl'), 'rb') as f:
        seq_orig = pickle.load(f)

    seq_norm_count_rep1 = {key: [] for key in seq_orig.keys()}
    plm_norm_count_rep1 = {key: [] for key in seq_orig.keys()}

    with open(os.path.join(args.step1_dir,'barcode_to_seq_dict.pkl'), 'rb') as f:
        barcode_to_seq = pickle.load(f)


    with open(os.path.join(args.step2_dir,'barcode_reads_counts.pkl'), 'rb') as f:
        plasmid_barcode_count = pickle.load(f)

    with open(os.path.join(args.step3_dir,'RNA_reads_counts.pkl'), 'rb') as f:
        cdna_barcode_count = pickle.load(f)


    for barcode, prom_seq in barcode_to_seq.items():


        plm_count = plasmid_barcode_count[barcode]
        cdna_count = cdna_barcode_count[barcode]


        if (plm_count>0) or (cdna_count>0):
            seq_norm_count_rep1[prom_seq].append(cdna_count)
            plm_norm_count_rep1[prom_seq].append(plm_count)



    max_length = max(len(lst) for lst in seq_norm_count_rep1.values())
    col_names  = [f"MT.1.{i+1:04d}" for i in range(max_length)]

    row_names = []

    all_dna_data = []
    all_rna_data = []
    for key, values_rna in seq_norm_count_rep1.items():
        values_rna += [0] * (max_length - len(values_rna))
        values_dna = plm_norm_count_rep1[key]
        values_dna += [0] * (max_length - len(values_dna))
        all_rna_data.append(values_rna)
        all_dna_data.append(values_dna)
        row_names.append(key)
    all_dna_data = np.array(all_dna_data)
    all_rna_data = np.array(all_rna_data)

    df = pd.DataFrame(all_dna_data, index=row_names, columns=col_names)
    df.to_csv(f'{args.run_tag}_dna.csv', header=True, index=True)
    df = pd.DataFrame(all_rna_data, index=row_names, columns=col_names)
    df.to_csv(f'{args.run_tag}_rna.csv', header=True, index=True)

    matrix_data = {
        'batch': [1] * max_length,
        'condition': ['MT'] * max_length,
        'barcode': list(range(1, max_length + 1))
    }

    with open(f'{args.run_tag}_col_annot.csv', 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['batch', 'condition', 'barcode'])
        for i, item in enumerate(col_names):
            csv_writer.writerow([item, 1,'MT',i+1])


if __name__ == "__main__":
    main()
