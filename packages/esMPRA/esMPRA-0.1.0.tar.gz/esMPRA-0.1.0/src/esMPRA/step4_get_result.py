import gzip
import pickle
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np


def open_file(filename):
    if filename.endswith('.gz'):
        return gzip.open(filename, 'rt')
    else:
        return open(filename, 'r')


def process(args):

    with open(os.path.join('./',args.run_name_step1+'_step1','seq_to_barcode_dict.pkl'), 'rb') as f:
        seq_to_barcode = pickle.load(f)

    with open(os.path.join('./',args.run_name_step1+'_step1','barcode_to_seq_dict.pkl'), 'rb') as f:
        barcode_to_seq = pickle.load(f)

    plm_counts = np.loadtxt(os.path.join('./',args.run_name_step2+'_step2','plasmid_total_counts.txt'))
    cDNA_counts = np.loadtxt(os.path.join('./',args.run_name_step3+'_step3','RNA_total_counts.txt'))

    plm_counts = int(plm_counts)
    cDNA_counts = int(cDNA_counts)


    with open(os.path.join('./',args.run_name_step2+'_step2','barcode_reads_counts.pkl'), 'rb') as f:
        plasmid_barcode = pickle.load(f)
    plm_norm_count = {key: [] for key in seq_to_barcode.keys()}


    with open(os.path.join('./',args.run_name_step3+'_step3','RNA_reads_counts.pkl'), 'rb') as f:
        cdna_barcode = pickle.load(f)
    seq_norm_count = {key: [] for key in seq_to_barcode.keys()}



    for barcode, prom_seq in barcode_to_seq.items():
        plm_count = plasmid_barcode[barcode]
        cdna_counts = cdna_barcode[barcode]
        if (plm_count>=args.thresh_for_plm) and (cdna_counts>=args.thresh_for_rna):
            normdna1 = cdna_counts*args.norm_counts/cDNA_counts
            normplm = plm_count*args.norm_counts/plm_counts
            seq_norm_count[prom_seq].append(normdna1)
            plm_norm_count[prom_seq].append(normplm)


    with open_file(args.ref_fa) as f:
        fasta_lines = f.readlines() 

    exp_all = []

    with open(f'./{args.run_name}_step4/exp_values.tsv','w') as out:
        for line in fasta_lines:
            line = line.strip()
            if line.startswith('>'):
                name = line[1:]
            else:
                prom_seq = line[:]

                if len(seq_norm_count[prom_seq])<args.min_barcode_per_oligo:
                    continue
                if (np.sum(seq_norm_count[prom_seq])<=args.thresh_for_norm) or (np.sum(plm_norm_count[prom_seq])<=args.thresh_for_norm):
                    continue
                out.write(prom_seq + '\t')
                exp = np.sum(seq_norm_count[prom_seq])/np.sum(plm_norm_count[prom_seq])
                out.write(str(exp) + '\t')
                exp_all.append(exp)
                out.write(name + '\n')

    with open(os.path.join('./',args.run_name+'_step4','log.txt'),'w') as f_out:
        f_out.write(f'final qualified oligo count: {len(exp_all)}\n')
        f_out.write(f'designed total oligo count: {len(fasta_lines)}\n')

    return plasmid_barcode, cdna_barcode


def exp_qc1(args, cdna_barcode, plasmid_barcode):


    plasmid_value = []
    cDNA_value = []
    for barcode in plasmid_barcode:
        if barcode in cdna_barcode:
            plasmid_value.append(plasmid_barcode[barcode])
            cDNA_value.append(cdna_barcode[barcode])


    pearson_corr = np.corrcoef(np.array(plasmid_value), np.array(cDNA_value))[0, 1]
    with open(os.path.join('./',args.run_name+'_step4','log.txt'),'a') as f_out:
        f_out.write(f'PCC between plasmid counts and cDNA counts: {pearson_corr}\n')

    plt.scatter(plasmid_value, cDNA_value,s=1,alpha=0.5)
    plt.xlabel('plasmid counts')
    plt.ylabel('cDNA counts')
    plt.title('PCC: ' + str(pearson_corr))
    plt.grid(True)
    plt.savefig(os.path.join('./',args.run_name+'_step4','plm_exp_PCC.png'))
    plt.close()


def main():    
    # Input arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref_fa', required=True, help='the designed oligo library file in fasta format')
    parser.add_argument('--run_name', required=True, help='the name of this run')
    parser.add_argument('--run_name_step1', help='the name of used run in step1, default is the same as the run name in this step')
    parser.add_argument('--run_name_step2', help='the name of used run in step2, default is the same as the run name in this step')
    parser.add_argument('--run_name_step3', help='the name of used run in step3, default is the same as the run name in this step')

    parser.add_argument('--norm_counts', default=1000000, type=int, help='estimated counts for normalization')
    parser.add_argument('--thresh_for_plm', default=1, type=int, help='threshold for min plasmid counts, only barcodes with read counts more than (or equal to) this value will be reserved')
    parser.add_argument('--thresh_for_rna', default=1, type=int, help='threshold for min rna counts, only barcodes with read counts more than (or equal to) this value will be reserved')
    parser.add_argument('--thresh_for_norm', default=0, type=int, help='threshold for min normalized counts, only oligos with total normalized counts more than this value will be reserved')
    parser.add_argument('--min_barcode_per_oligo', default=3, type=int, help='an oligo was qualified only when it was assigned with more than (or equal to) this count of valid barcode')

    args = parser.parse_args()

    if args.run_name_step1 is None:
        args.run_name_step1 = args.run_name

    if args.run_name_step2 is None:
        args.run_name_step2 = args.run_name

    if args.run_name_step3 is None:
        args.run_name_step3 = args.run_name

    # Main function

    os.makedirs(f'./{args.run_name}_step4')

    plasmid_barcode, cdna_barcode = process(args)
    exp_qc1(args, cdna_barcode, plasmid_barcode)


if __name__ == "__main__":
    main()
