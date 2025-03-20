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


def process_with_flash(args):
    out_dir = os.path.join('./',args.run_name+'_step1','merged')

    read1_files = args.read_1
    read2_files = args.read_2

    for num, (f1_name, f2_name) in enumerate(zip(read1_files, read2_files)):
        os.system(f'flash2 -r {args.flash_read_len} -f {args.flash_frag_len} -o {out_dir}_{num} -t {args.flash_threads} {f2_name} {f1_name}')  

    with open_file(args.ref_fa) as f:
        fasta_lines = f.readlines()

    sequences_dict = {}
    current_sequence = ''
    for line in fasta_lines:
        line = line.strip()
        if line.startswith('>'):
            if current_sequence:
                key = current_sequence
                sequences_dict[key] = []
            current_sequence = ''
        else:
            current_sequence += line
    if current_sequence:
        key = current_sequence
        sequences_dict[key] = []


    reads_count = 0
    file_count = 0

    for num in range(len(read1_files)):
        with open(os.path.join('./',args.run_name+'_step1','merged_')+str(num)+'.extendedFrags.fastq', 'rt') as f1:
            while True:
                lines1 = [f1.readline().strip() for _ in range(4)]
                file_count+=1
                if not any(lines1):
                    break
                
                qual1 = lines1[3]
                if len(qual1)==0:
                    continue
                avg_qual1 = sum(ord(c) - 33 for c in qual1) / len(qual1)
                if avg_qual1 < args.quality_threshold:
                    continue

                seq = lines1[1]
                pre_index = seq.find(args.oligo_pre)
                end_index = seq.find(args.oligo_after)
                barcode_index = seq.find(args.barcode_pre)
                if (pre_index == -1) or (end_index == -1) or (barcode_index == -1):
                    continue

                aim_seq = seq[pre_index+len(args.oligo_pre):end_index]
                if aim_seq in sequences_dict:
                    extracted_sequence = seq[barcode_index+len(args.barcode_pre):]
                    if len(extracted_sequence) >= args.barcode_length:
                        barcode_seq = extracted_sequence[0:args.barcode_length]
                        if 'N' not in barcode_seq:
                            sequences_dict[aim_seq].append(barcode_seq)
                            reads_count+=1

    with open(os.path.join('./',args.run_name+'_step1','log.txt'),'w') as f_out:
        f_out.write(f'{file_count}\n')
        f_out.write(f'{reads_count}\n')

    with open(os.path.join('./',args.run_name+'_step1','seq_to_barcode_dict.pkl'), 'wb') as f:
        pickle.dump(sequences_dict, f)

    return sequences_dict


def process_without_flash(args):

    with open_file(args.ref_fa) as f:
        fasta_lines = f.readlines() 

    sequences_dict = {}
    current_sequence = ''
    for line in fasta_lines:
        line = line.strip()
        if line.startswith('>'):
            if current_sequence:
                key = current_sequence
                sequences_dict[key] = []
            current_sequence = ''
        else:
            current_sequence += line
    if current_sequence:
        key = current_sequence
        sequences_dict[key] = []

    reads_count = 0
    file_count = 0

    read1_files = args.read_1
    read2_files = args.read_2

    for f1_name, f2_name in zip(read1_files, read2_files):
        with open_file(f1_name) as f1, open_file(f2_name) as f2:
            while True:
                lines1 = [f1.readline().strip() for _ in range(4)]
                lines2 = [f2.readline().strip() for _ in range(4)]
                file_count+=1
                if not any(lines1) or not any(lines2):
                    break
                
                qual1, qual2 = lines1[3], lines2[3]
                if len(qual1)==0:
                    continue
                if len(qual2)==0:
                    continue
                avg_qual1 = sum(ord(c) - 33 for c in qual1) / len(qual1)
                avg_qual2 = sum(ord(c) - 33 for c in qual2) / len(qual2)
                if avg_qual1 < args.quality_threshold or avg_qual2 < args.quality_threshold:
                    continue

                seq1, seq2 = lines1[1], lines2[1]
                name1, name2 = lines1[0].split()[0], lines2[0].split()[0]
                if name1 != name2:
                    raise ValueError("Error: Sequence names do not match")
                
                seq_part1 = seq2
                seq_part2 = reverse_complement(seq1)
                pre_index = seq_part1.find(args.oligo_pre)
                pre_seq = seq_part1[pre_index+len(args.oligo_pre):]

                end_index = seq_part2.find(args.oligo_after)
                if end_index==-1:
                    continue
                after_seq = seq_part2[end_index-(args.oligo_length-len(pre_seq)):end_index]

                barcode_index = seq_part2.find(args.barcode_pre)
                if barcode_index==-1:
                    continue

                aim_seq = pre_seq+after_seq
                if aim_seq in sequences_dict:
                    remaining_sequence = seq_part2[barcode_index+len(args.barcode_pre):].strip()
                    if len(remaining_sequence) >= args.barcode_length:
                        extracted_sequence = remaining_sequence[:args.barcode_length]
                        if 'N' not in remaining_sequence:
                            sequences_dict[aim_seq].append(extracted_sequence)
                            reads_count+=1

    with open(os.path.join('./',args.run_name+'_step1','log.txt'),'w') as f_out:
        f_out.write(f'{file_count}\n')
        f_out.write(f'{reads_count}\n')


    return sequences_dict
    

def filt_dict(args, sequences_dict):
    dictionary = sequences_dict
    new_dict = {}
    deleted_keys = []
    ambigous_dic = {}

    for key, values in dictionary.items():
        unique_values = list(set(values))
        for value in unique_values:
            if value in new_dict:
                deleted_keys.append(value)
                if value not in ambigous_dic:
                    ambigous_dic[value]=[]
                ambigous_dic[value].append(key)
            else:
                new_dict[value] = key

    del_count = 0
    for del_key in list(set(deleted_keys)):
        ambigous_dic[del_key].append(new_dict[del_key])
        del_count+=1
        del new_dict[del_key]


    with open(os.path.join('./',args.run_name+'_step1','log.txt'),'a') as f_out:
        f_out.write(f'{del_count}\n')
        f_out.write(f'{len(new_dict)}\n')

    with open(os.path.join('./',args.run_name+'_step1','barcode_to_seq_dict.pkl'), 'wb') as f:
        pickle.dump(new_dict, f)


    return ambigous_dic


def to_oligo(args, sequences_dict, ambigous_dic):

    for key, value in ambigous_dic.items():
        for string in value:
            list_orig = sequences_dict[string]
            new_list = [x for x in list_orig if x != key]
            sequences_dict[string] = new_list[:]

    with open(os.path.join('./',args.run_name+'_step1','seq_to_barcode_dict.pkl'), 'wb') as f:
        pickle.dump(sequences_dict, f)


    empty_list_count = 0
    total_list_length = 0
    valid_list_count = 0
    all_list_length = []
    all_reads_count = []


    for key, value in sequences_dict.items():
        if isinstance(value, list):
            unique_elements = set(value)
            if len(unique_elements)<args.min_barcode_per_oligo:
                empty_list_count+=1
            else:
                valid_list_count+=1
                total_list_length += len(unique_elements)
                all_list_length.append(len(unique_elements))
                all_reads_count.append(len(value))

    with open(os.path.join('./',args.run_name+'_step1','log.txt'),'a') as f_out:
        f_out.write(f'number of qualified oligos: {valid_list_count}\n')
        f_out.write(f'number of not qualified oligos: {empty_list_count}\n')
        f_out.write(f'total count of barcodes: {total_list_length}\n')



    plt.hist(all_list_length, bins=100)
    plt.title('Dist of barcode counts for oligos')
    plt.xlabel('value')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join('./',args.run_name+'_step1','dist_of_barcode_counts_for_oligos.png'))
    plt.close()

    frequency = Counter(all_list_length)
    frequency_list = [(item, count) for item, count in frequency.items()]
    np.savetxt(os.path.join('./',args.run_name+'_step1','dist_of_barcode_counts_for_oligos.txt'), frequency_list, fmt='%d', delimiter='\t', header='barcode_counts\tfrequency')

    return sequences_dict



def qc_oligos(args, seq_to_barcode):

    down_ratio = [1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,0.3,1]
    coverage = []
    value_list = []

    for index, (key, values) in enumerate(seq_to_barcode.items()):
        value_list.extend([index]*len(values))

    for ratio in down_ratio:
        selection_count = int(len(value_list) * ratio)
        selected_values = np.random.choice(value_list, selection_count, replace=False)
        unique_elements = len(set(selected_values))
        coverage.append(unique_elements)

    plt.plot(np.log10(down_ratio),coverage)
    plt.title('down sampling for mapping')
    plt.xlabel('log10 ratio')
    plt.ylabel('coverage')
    plt.savefig(os.path.join('./',args.run_name+'_step1','down_sample_for_mapping.png'))
    plt.close()

    combined_list = list(zip(np.log10(down_ratio), coverage))
    np.savetxt(os.path.join('./',args.run_name+'_step1','down_sample_for_mapping.txt'), combined_list, fmt='%f %d', delimiter='\t', header='log10_ratio\tcoverage')

def main():
    
    # Input arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref_fa', required=True, help='the designed oligo library file in fasta format')
    # parser.add_argument('--read_1', required=True, help='R1 fastq file (.fasta.gz format or .fasta format), sequences in this file are expected to contain the end part of the deigned oligo and the random barcode in reverse complement format')
    # parser.add_argument('--read_2', required=True, help='R2 fastq file (.fasta.gz format or .fasta format), sequences in this file are expected contain the start part of the deigned oligo')
    parser.add_argument('--read_1', required=True, nargs='+', help='directory to R1 fastq file(s) (.fasta.gz format or .fasta format), sequences in this file are expected to contain the end part of the deigned oligo and the random barcode in reverse complement format; use space to separate multiple files; mitiple files will be processed as merged files')
    parser.add_argument('--read_2', required=True, nargs='+', help='directory to R2 fastq file(s) (.fasta.gz format or .fasta format), sequences in this file are expected contain the start part of the deigned oligo, the order should correspond to the order in read_1; use space to separate multiple files; mitiple files will be processed as merged files')

    parser.add_argument('--run_name', required=True, help='the name of this run')
    len_parser = parser.add_argument('--oligo_length', default=200, type=int, help='(required when not using FLASH mode) the length of the designed oligo, if use the FLASH mode, this parameter will be ignored')

    parser.add_argument('--use_flash', action="store_true", help="use FLASH mode, this requires flash2 software installed")
    parser.add_argument('--oligo_pre', default='GGCCGCTTGACG', help='several base paires upstrame the designed oligo, this is used to locate the oligo sequence')
    parser.add_argument('--oligo_after', default='CACTGCGGCTCC', help='several base paires downstrame the designed oligo, this is used to locate the oligo sequence')
    parser.add_argument('--barcode_pre', default='CGAACCTCTAGA', help='several base paires upstrame the random barcode, this is used to locate the random barcode')

    parser.add_argument('--quality_threshold', default=30, type=int, help='quality threshold for the sequencing reads')
    parser.add_argument('--barcode_length', default=20, type=int, help='the length of the random barcode in the experiment')
    parser.add_argument('--min_barcode_per_oligo', default=3, type=int, help='an oligo was qualified only when it was assigned with more than this count of barcode')

    parser.add_argument('--flash_read_len', default=250, type=int, help='average read length passed to flash2')
    parser.add_argument('--flash_frag_len', default=274, type=int, help='fragment length passed to flash2')
    parser.add_argument('--flash_threads', default=30, type=int, help='number of worker threads passed to flash2')

    namespace, remaining_args = parser.parse_known_args()

    if namespace.use_flash:
        len_parser.required = False
    else:
        len_parser.required = True

    args = parser.parse_args()

    # Main function
    os.makedirs(f'./{args.run_name}_step1')

    if args.use_flash:
        sequences_dict = process_with_flash(args)
    else:
        sequences_dict = process_without_flash(args)


    ambigous_dic = filt_dict(args, sequences_dict)

    seq_to_barcode = to_oligo(args, sequences_dict, ambigous_dic)

    qc_oligos(args, seq_to_barcode)


if __name__ == "__main__":
    main()