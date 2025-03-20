import gzip
import pickle
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def reverse_complement(sequence):
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    reverse_seq = sequence[::-1]
    return ''.join(complement[base] for base in reverse_seq)


def open_file(filename):
    if filename.endswith('.gz'):
        return gzip.open(filename, 'rt')
    else:
        return open(filename, 'r')



def read_barcode(args):

    with open(os.path.join('./',args.run_name_step1+'_step1','barcode_to_seq_dict.pkl'), 'rb') as f:
        barcode_to_seq = pickle.load(f)

    new_dict = {key: 0 for key in barcode_to_seq.keys()}
    reads_count = 0

    read1_files = args.read_1
    for f1_name in read1_files:
        with open_file(f1_name) as f1:
            while True:
                lines1 = [f1.readline().strip() for _ in range(4)]
                if not any(lines1):
                    break
                qual1 = lines1[3]
                if len(qual1)==0:
                    continue
                avg_qual1 = sum(ord(c) - 33 for c in qual1) / len(qual1)
                if avg_qual1 < args.quality_threshold:
                    continue


                seq1 = lines1[1]
                index = seq1.find(args.barcode_after)
                if index>=args.barcode_length:
                    barcode_rev = seq1[index-args.barcode_length:index]
                    if 'N' in barcode_rev:
                        continue

                    barcode = reverse_complement(barcode_rev)
                    if barcode in new_dict:
                        new_dict[barcode]+=1
                        reads_count+=1

    with open(os.path.join('./',args.run_name+'_step2','log.txt'),'w') as f_out:
        f_out.write(f'total reads count: {reads_count}\n')

    np.savetxt(os.path.join('./',args.run_name+'_step2','plasmid_total_counts.txt'),np.array([reads_count]), fmt='%d')

    with open(os.path.join('./',args.run_name+'_step2','barcode_reads_counts.pkl'), 'wb') as f:
        pickle.dump(new_dict, f)

    return new_dict, barcode_to_seq


def read_barcode_position_mode(args):

    with open(os.path.join('./',args.run_name_step1+'_step1','barcode_to_seq_dict.pkl'), 'rb') as f:
        barcode_to_seq = pickle.load(f)

    new_dict = {key: 0 for key in barcode_to_seq.keys()}
    reads_count = 0

    read1_files = args.read_1
    for f1_name in read1_files:
        with open_file(f1_name) as f1:
            while True:
                lines1 = [f1.readline().strip() for _ in range(4)]
                if not any(lines1):
                    break
                qual1 = lines1[3]
                if len(qual1)==0:
                    continue
                avg_qual1 = sum(ord(c) - 33 for c in qual1) / len(qual1)
                if avg_qual1 < args.quality_threshold:
                    continue


                seq1 = lines1[1]
                barcode_rev = seq1[args.rela_position:args.rela_position+args.barcode_length]
                if 'N' in barcode_rev:
                    continue

                barcode = reverse_complement(barcode_rev)
                if barcode in new_dict:
                    new_dict[barcode]+=1
                    reads_count+=1

    with open(os.path.join('./',args.run_name+'_step2','log.txt'),'w') as f_out:
        f_out.write(f'total reads count: {reads_count}\n')

    np.savetxt(os.path.join('./',args.run_name+'_step2','plasmid_total_counts.txt'),np.array([reads_count]), fmt='%d')

    with open(os.path.join('./',args.run_name+'_step2','barcode_reads_counts.pkl'), 'wb') as f:
        pickle.dump(new_dict, f)

    return new_dict, barcode_to_seq



def barcode_qc1(args, barcode_count):

    empty_barcode_count_1 = 0
    empty_barcode_count_5 = 0
    empty_barcode_count_10 = 0
    barcode_count_1 = 0
    barcode_count_5 = 0
    barcode_count_10 = 0
    total_barcode_count = 0
    extreme_barcode = 0
    all_counts = []

    for key, value in barcode_count.items():
        if value>200:
            extreme_barcode += 1
            continue
        if value <1:
            empty_barcode_count_1+=1
        else:
            barcode_count_1 += 1
        if value <5:
            empty_barcode_count_5+=1
        else:
            barcode_count_5 +=1
        if value<10:
            empty_barcode_count_10+=1
        else:
            barcode_count_10 +=1
        total_barcode_count+=1
        all_counts.append(value)


    with open(os.path.join('./',args.run_name+'_step2','log.txt'),'a') as f_out:
        f_out.write(f"# of barcode not detected:{empty_barcode_count_1}\n")
        f_out.write(f"# of barcode with reads counts less than 5:{empty_barcode_count_5}\n")
        f_out.write(f"# of barcode with reads counts less than 10:{empty_barcode_count_10}\n")
        f_out.write(f"# of barcode with reads counts >= 1:{barcode_count_1}\n")
        f_out.write(f"# of barcode with reads counts >= 5:{barcode_count_5}\n")
        f_out.write(f"# of barcode with reads counts >= 10:{barcode_count_10}\n")
        f_out.write(f"# of barcode with reads counts larger than 200:{extreme_barcode}\n")
        f_out.write(f"total barocdes number:{total_barcode_count}\n")

        all_counts = np.array(all_counts)
        all_counts = all_counts[all_counts>0]
        f_out.write(f'mean barcode reads counts: {np.mean(all_counts)}\n')

    plt.hist(all_counts, bins=100)
    plt.title('Dist of barcodes reads count')
    plt.xlabel('value')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join('./',args.run_name+'_step2','dist_of_barcode_reads_counts.png'))
    plt.close()

    frequency = Counter(all_counts)
    frequency_list = [(item, count) for item, count in frequency.items()]
    np.savetxt(os.path.join('./',args.run_name+'_step2','dist_of_barcode_reads_counts.txt'), frequency_list, fmt='%d', delimiter='\t', header='barcode_counts\tfrequency')



def barcode_qc2(args, barcode_count, barcode_to_seq):

    with open(os.path.join('./',args.run_name_step1+'_step1','seq_to_barcode_dict.pkl'), 'rb') as f:
        seq_to_barcode = pickle.load(f)

    missed_barcode = []
    missed_barcode_3 = []
    missed_barcode_5 = []
    missed_barcode_10 = []

    for key, value in barcode_count.items():
        if value <1:
            missed_barcode.append(key)
        if value <3:
            missed_barcode_3.append(key)
        if value<5:
            missed_barcode_5.append(key)
        if value<10:
            missed_barcode_10.append(key)

    for barcode_temp in missed_barcode:
        seq_temp = barcode_to_seq[barcode_temp]
        list_orig = seq_to_barcode[seq_temp]
        new_list = [x for x in list_orig if x != barcode_temp]
        seq_to_barcode[seq_temp] = new_list[:]

    empty_list_count = 0
    total_list_length = 0
    valid_list_count = 0
    all_list_length = []
    all_reads_count = []


    for key, value in seq_to_barcode.items():
        if isinstance(value, list):
            unique_elements = set(value)
            if len(unique_elements)<args.min_barcode_per_oligo:
                empty_list_count+=1
            else:
                valid_list_count+=1
                total_list_length += len(unique_elements)
                all_list_length.append(len(unique_elements))
                all_reads_count.append(len(value))


    with open(os.path.join('./',args.run_name+'_step2','log.txt'),'a') as f_out:
        f_out.write(f"# of not qualified oligos after plasmid construct:{empty_list_count}\n")
        f_out.write(f"# of qualified oligos after plasmid construct:{valid_list_count}\n")
        f_out.write(f"# of total barcodes after plasmid construct:{total_list_length}\n")


    plt.hist(all_list_length, bins=100)
    plt.title('Dist of barcode counts for oligos after plasmid construct')
    plt.xlabel('value')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join('./',args.run_name+'_step2','dist_of_barcode_counts_for_oligos_after_plasmid_construct.png'))
    plt.close()

    frequency = Counter(all_list_length)
    frequency_list = [(item, count) for item, count in frequency.items()]
    np.savetxt(os.path.join('./',args.run_name+'_step2','dist_of_barcode_counts_for_oligos_after_plasmid_construct.txt'), frequency_list, fmt='%d', delimiter='\t', header='barcode_counts\tfrequency')



    for barcode_temp in missed_barcode_3:
        seq_temp = barcode_to_seq[barcode_temp]
        list_orig = seq_to_barcode[seq_temp]
        new_list = [x for x in list_orig if x != barcode_temp]
        seq_to_barcode[seq_temp] = new_list[:]

    empty_list_count = 0
    total_list_length = 0
    valid_list_count = 0
    all_list_length = []
    all_reads_count = []

    for key, value in seq_to_barcode.items():
        if isinstance(value, list):
            unique_elements = set(value)
            if len(unique_elements)<args.min_barcode_per_oligo:
                empty_list_count+=1
            else:
                valid_list_count+=1
                total_list_length += len(unique_elements)
                all_list_length.append(len(unique_elements))
                all_reads_count.append(len(value))


    with open(os.path.join('./',args.run_name+'_step2','log.txt'),'a') as f_out:
        f_out.write(f"# of not qualified oligos only barcode reads count >=3 are considered:{empty_list_count}\n")
        f_out.write(f"# of qualified oligos only barcode reads count >=3 are considered:{valid_list_count}\n")
        f_out.write(f"# of total barcodes only barcode reads count >=3 are considered:{total_list_length}\n")


    for barcode_temp in missed_barcode_5:
        seq_temp = barcode_to_seq[barcode_temp]
        list_orig = seq_to_barcode[seq_temp]
        new_list = [x for x in list_orig if x != barcode_temp]
        seq_to_barcode[seq_temp] = new_list[:]

    empty_list_count = 0
    total_list_length = 0
    valid_list_count = 0
    all_list_length = []
    all_reads_count = []

    for key, value in seq_to_barcode.items():
        if isinstance(value, list):
            unique_elements = set(value)
            if len(unique_elements)<args.min_barcode_per_oligo:
                empty_list_count+=1
            else:
                valid_list_count+=1
                total_list_length += len(unique_elements)
                all_list_length.append(len(unique_elements))
                all_reads_count.append(len(value))

    with open(os.path.join('./',args.run_name+'_step2','log.txt'),'a') as f_out:
        f_out.write(f"# of not qualified oligos only barcode reads count >=5 are considered:{empty_list_count}\n")
        f_out.write(f"# of qualified oligos only barcode reads count >=5 are considered:{valid_list_count}\n")
        f_out.write(f"# of total barcodes only barcode reads count >=5 are considered:{total_list_length}\n")


    for barcode_temp in missed_barcode_10:
        seq_temp = barcode_to_seq[barcode_temp]
        list_orig = seq_to_barcode[seq_temp]
        new_list = [x for x in list_orig if x != barcode_temp]
        seq_to_barcode[seq_temp] = new_list[:]

    empty_list_count = 0
    total_list_length = 0
    valid_list_count = 0
    all_list_length = []
    all_reads_count = []

    for key, value in seq_to_barcode.items():
        if isinstance(value, list):
            unique_elements = set(value)
            if len(unique_elements)<args.min_barcode_per_oligo:
                empty_list_count+=1
            else:
                valid_list_count+=1
                total_list_length += len(unique_elements)
                all_list_length.append(len(unique_elements))
                all_reads_count.append(len(value))

    with open(os.path.join('./',args.run_name+'_step2','log.txt'),'a') as f_out:
        f_out.write(f"# of not qualified oligos only barcode reads count >=10 are considered:{empty_list_count}\n")
        f_out.write(f"# of qualified oligos only barcode reads count >=10 are considered:{valid_list_count}\n")
        f_out.write(f"# of total barcodes only barcode reads count >=10 are considered:{total_list_length}\n")


def qc_plasmid(args, barcode_count, barcode_to_seq):

    down_ratio = [1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,0.3,1]
    coverage = []
    value_list = []

    for index, (key, values) in enumerate(barcode_count.items()):
        value_list.extend([index]*values)

    for ratio in down_ratio:
        selection_count = int(len(value_list) * ratio)
        selected_values = np.random.choice(value_list, selection_count, replace=False)
        unique_elements = len(set(selected_values))
        coverage.append(unique_elements)

    plt.plot(np.log10(down_ratio),coverage)
    plt.title('down sampling for plasmid')
    plt.xlabel('log10 ratio')
    plt.ylabel('coverage')
    plt.savefig(os.path.join('./',args.run_name+'_step2','down_sample_for_plasmid.png'))
    plt.close()

    combined_list = list(zip(np.log10(down_ratio), coverage))
    np.savetxt(os.path.join('./',args.run_name+'_step2','down_sample_for_plasmid.txt'), combined_list, fmt='%f %d', delimiter='\t', header='log10_ratio\tcoverage')


    coverage = []
    value_list = []
    seq_index_dic = {}

    for index, (key, values) in enumerate(barcode_count.items()):
        seq_temp = barcode_to_seq[key]
        if seq_temp in seq_index_dic:
            temp_value = seq_index_dic[seq_temp]
        else:
            seq_index_dic[seq_temp] = len(seq_index_dic)
            temp_value = seq_index_dic[seq_temp]
        value_list.extend([temp_value]*values)

    for ratio in down_ratio:
        selection_count = int(len(value_list) * ratio)
        selected_values = np.random.choice(value_list, selection_count, replace=False)
        unique_elements = len(set(selected_values))
        coverage.append(unique_elements)

    plt.plot(np.log10(down_ratio),coverage)
    plt.title('down sampling for plasmid mapped oligo')
    plt.xlabel('log10 ratio')
    plt.ylabel('coverage')
    plt.savefig(os.path.join('./',args.run_name+'_step2','down_sample_for_plasmid_oligo.png'))
    plt.close()

    combined_list = list(zip(np.log10(down_ratio), coverage))
    np.savetxt(os.path.join('./',args.run_name+'_step2','down_sample_for_plasmid_oligo.txt'), combined_list, fmt='%f %d', delimiter='\t', header='log10_ratio\tcoverage')





def main():    
    # Input arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--read_1', required=True, nargs='+', help='directory to R1 fastq file(s) (.fasta.gz format or .fasta format), sequences in this file are expected to contain the random barcode in reverse complement format; use space to separate multiple files; mitiple files will be processed as merged files')

    parser.add_argument('--run_name', required=True, help='the name of this run')
    parser.add_argument('--run_name_step1', help='the name of used run in step1, default is the same as the run name in this step')
    parser.add_argument('--barcode_after', default='TCTAGA', help='several base paires downstrame the random barcode, this is used to locate the random barcode')

    parser.add_argument('--min_barcode_per_oligo', default=3, type=int, help='an oligo was qualified only when it was assigned with more than this count of barcode')
    parser.add_argument('--quality_threshold', default=30, type=int, help='quality threshold for the sequencing reads')
    parser.add_argument('--barcode_length', default=20, type=int, help='the length of the random barcode in the experiment')
    parser.add_argument('--position_mode', action="store_true", help="use position mode, if use this mode, the barcode will be located according to the rela_position parameter")
    parser.add_argument('--rela_position', default=0, type=int, help='the start potision of the barcode in the read_1 file')

    args = parser.parse_args()

    if args.run_name_step1 is None:
        args.run_name_step1 = args.run_name

    # Main function
    os.makedirs(f'./{args.run_name}_step2')

    if args.position_mode:
        barcode_count, barcode_to_seq = read_barcode_position_mode(args)
    else:
        barcode_count, barcode_to_seq = read_barcode(args)

    barcode_qc1(args, barcode_count)
    barcode_qc2(args, barcode_count, barcode_to_seq)
    qc_plasmid(args, barcode_count, barcode_to_seq)

if __name__ == "__main__":
    main()
