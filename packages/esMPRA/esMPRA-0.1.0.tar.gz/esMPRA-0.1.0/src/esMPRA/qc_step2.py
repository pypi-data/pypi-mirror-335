import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import pickle
import os
import argparse
import pkg_resources

def draw_multiline_string(c, x, y, text, font_name="Helvetica", font_size=12, max_width=400):

    c.setFont(font_name, font_size)
    words = text.split(' ')
    lines = []
    current_line = words[0]
    
    for word in words[1:]:
        if c.stringWidth(current_line + ' ' + word, font_name, font_size) < max_width:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    
    for line in lines:
        c.drawString(x, y, line)
        y -= 20
    return y


def generate_plot_for_subsample(value, ref_values):

    sub_ratio = [1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,0.3,1]
    sub_ratio = np.log10(sub_ratio)

    all_ratios = []
    for i, experiment in enumerate(ref_values):
        all_ratios.append(experiment)

    max_ratios = np.max(all_ratios, axis=0)
    min_ratios = np.min(all_ratios, axis=0)

    plt.figure(figsize=(7.5, 5))
    plt.plot(sub_ratio, value, label="tested results", color="blue", marker='o')
    plt.fill_between(sub_ratio, min_ratios, max_ratios, color="skyblue", alpha=0.4, label="ref range")
    plt.title("Sampling Depth vs Retention Ratio")
    plt.xlabel("Sampling Depth (log10)")
    plt.ylabel("Retention Ratio")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plot_filename = 'step2_sub_range.png'
    plt.savefig(plot_filename)
    plt.close()
    return plot_filename

def generate_plot_for_subsample_barcode(value, ref_values):

    sub_ratio = [1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,0.3,1]
    sub_ratio = np.log10(sub_ratio)

    all_ratios = []
    for i, experiment in enumerate(ref_values):
        all_ratios.append(experiment)

    max_ratios = np.max(all_ratios, axis=0)
    min_ratios = np.min(all_ratios, axis=0)

    plt.figure(figsize=(8, 6))
    plt.plot(sub_ratio, value, label="tested results", color="blue", marker='o')
    plt.fill_between(sub_ratio, min_ratios, max_ratios, color="skyblue", alpha=0.4, label="ref range")
    plt.title("Sampling Depth vs Retention Ratio")
    plt.xlabel("Sampling Depth (log10)")
    plt.ylabel("Retention Ratio")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plot_filename = 'step2_sub_barcode.png'
    plt.savefig(plot_filename)
    plt.close()
    return plot_filename


def generate_plot_for_dist(value, ref_values):

    plt.figure(figsize=(7, 9))

    normality_results = []

    plt.subplot(2, 1, 1)
    for i, experiment in enumerate(ref_values):
        barcodes = experiment[:, 0]
        counts = experiment[:, 1]
        counts = counts.astype(int)
        full_barcodes = np.repeat(barcodes, counts)
        x_min = np.min(full_barcodes)
        x_max = np.max(full_barcodes)
        normalized = (full_barcodes - x_min) / (x_max - x_min)
        plt.hist(normalized, bins=50, alpha=0.1, density=True)
        # stat, p_value = shapiro(full_barcodes)
        # normality_results.append((stat, p_value))
        plt.xlabel('Normalized Barcode Number')
        plt.ylabel('Normalized Density')
        plt.title('Reference Barcode Distribution')

    plt.subplot(2, 1, 2)
    barcodes = value[:, 0]
    counts = value[:, 1]
    counts = counts.astype(int)
    full_barcodes = np.repeat(barcodes, counts)
    plt.hist(full_barcodes, 50, alpha=0.6)

    plt.xlabel('Barcode Number')
    plt.ylabel('Frequency')
    plt.title('Test Barcode Distribution')
    plt.grid(True)
    plot_filename = 'step2_hist.png'
    plt.tight_layout()
    plt.savefig(plot_filename)
    plt.close()
    return plot_filename


def generate_plot_for_dist_barcode(value, ref_values):

    plt.figure(figsize=(7.5, 9))

    normality_results = []

    plt.subplot(2, 1, 1)
    for i, experiment in enumerate(ref_values):
        barcodes = experiment[:, 0]
        counts = experiment[:, 1]
        counts = counts.astype(int)
        full_barcodes = np.repeat(barcodes, counts)
        x_min = np.min(full_barcodes)
        x_max = np.max(full_barcodes)
        normalized = (full_barcodes - x_min) / (x_max - x_min)
        plt.hist(normalized, bins=50, alpha=0.1, density=True)
        # stat, p_value = shapiro(full_barcodes)
        # normality_results.append((stat, p_value))
        plt.xlabel('Normalized Barcode Number')
        plt.ylabel('Normalized Density')
        plt.title('Reference Barcode Distribution')

    plt.subplot(2, 1, 2)
    barcodes = value[:, 0]
    counts = value[:, 1]
    counts = counts.astype(int)
    full_barcodes = np.repeat(barcodes, counts)
    plt.hist(full_barcodes, 50, alpha=0.6)

    plt.xlabel('Barcode Number')
    plt.ylabel('Frequency')
    plt.title('Test Barcode Distribution')
    plt.grid(True)
    plot_filename = 'step2_hist_barcode.png'
    plt.tight_layout()
    plt.savefig(plot_filename)
    plt.close()
    return plot_filename


def evaluate_metric(value, reference_range):
    min_value, max_value, min_high, max_high = reference_range
    if value < min_high:
        risk = 'High Risk'
    elif value > max_high:
        risk = 'High Risk'
    elif value < min_value:
        risk = 'Medium Risk'
    elif value > max_value:
        risk = 'Medium Risk'
    else:
        risk = 'checked OK'
    return risk


def generate_qc_suggestion(risk, metric_name):
    if risk == 'High Risk':
        return f"{metric_name}: Action required! Check the experimental setup or data collection."
    elif risk == 'Medium Risk':
        return f"{metric_name}: Review the process and consider minor adjustments."
    else:
        return f"{metric_name}: The metric is within acceptable limits."


def create_metric_evaluation_table(c, metrics_data, start_y=650):
    table_data = [["Metric Name", "Experimental Value", "Reference Range", "Risk Level"]]
    for metric_name, (value, reference_range) in metrics_data.items():
        risk = evaluate_metric(value, reference_range)
        if reference_range[1] == np.inf:
            table_data.append([metric_name, f"{value:.2f}", f">={reference_range[0]:.2f}", risk])
        else:
            table_data.append([metric_name, f"{value:.2f}", f"{reference_range[0]:.2f} - {reference_range[1]:.2f}", risk])
    
    table = Table(table_data, colWidths=[180, 100, 100, 100])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    
    table.wrapOn(c, 65, start_y)
    table.drawOn(c, 65, start_y)



def create_additional_metric_table(c, metrics_data, start_y=650):
    table_data = [["Metric Name", "Experimental Value", "Reference Range"]]
    for metric_name, (value, reference_range) in metrics_data.items():
        # risk = evaluate_metric(value, reference_range)

        if reference_range == '-':
            table_data.append([metric_name, f"{value:.2f}", f"-"])
        elif reference_range[0] == -np.inf:
            table_data.append([metric_name, f"{value:.2f}", f"<={reference_range[1]:.2f}"])
        elif reference_range[1] == np.inf:
            table_data.append([metric_name, f"{value:.2f}", f">={reference_range[0]:.2f}"])
        else:
            table_data.append([metric_name, f"{value:.2f}", f"{reference_range[0]:.2f} - {reference_range[1]:.2f}"])
    
    table = Table(table_data, colWidths=[200, 150, 150])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))

    table.wrapOn(c, 50, start_y)
    table.drawOn(c, 50, start_y)



def generate_qc_report(name_temp, metrics_data, plot_metric, other_metric, suggestions_data, target_metric):
    pdf_filename = f"qc_{name_temp}_step2.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Quality Control Report for Plasmid Counting Step")

    create_metric_evaluation_table(c, metrics_data, start_y=550)

    y_position = 530
    c.setFont("Helvetica", 12)
    
    c.drawString(50, y_position, "Reference Explanation for Quality Control Results:")

    y_position -= 25
    text = "barcode_detected_1/5/10_ratio: The proportion of barcodes detected at least 1/5/10 times."
    c.drawString(50, y_position, text)
    y_position -= 20
    text = "mean_barcodes_detected_counts: The average number of times barcodes are detected."
    c.drawString(50, y_position, text)
    y_position -= 20
    text = "qualified_oligo_ratio/_with_bc_count3/5/10: The proportion of oligos linked with sufficient barcodes (default value is 3), using barcodes detected at least 1/3/5/10 times."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)


    
    text = "mean_barcodes_count_for_oligo: The average number of barcode types linked to each oligo. Abnormal values here are usually lower than expected, causing inaccurate quantification"
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "Low values in above metrics may indicate insufficient sequencing depth or low plasmid construction efficiency. If so, check the plasmid construction experiment firstly."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    plot_filename = generate_plot_for_subsample(plot_metric['oligo_coverage'][0], plot_metric['oligo_coverage'][1])
    c.drawImage(plot_filename, 120, 100, width=340, height=250)

    y_position = 85
    text = "Coverage of oligos at different downsampling ratios for sequencing results: The closer the curve is to the upper left, the more sufficient the sequencing depth. If the test result is in the lower right of the reference range, consider increasing the sequencing depth."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)


    c.showPage()


    c.setFont("Helvetica", 12)
    c.drawString(50, 700, "Distribution of barcodes number linked to oligos for reference:")

    plot_filename = generate_plot_for_dist(plot_metric['barcode_dist_for_oligo'][0], plot_metric['barcode_dist_for_oligo'][1])
    c.drawImage(plot_filename, 140, 230, width=300, height=450)

    y_position  = 200
    text = "The distribution of the tested barcodes should resemble one of the reference distributions. If a long-tail effect is significant here despite qualified QC in the previous step, it likely indicates uneven plasmid distribution due to issues in the target gene insertion process. If so, it is recommended to check the plasmid construction process and refer to the previous page of report to make sure the sequencing depth is enough."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)


    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 740, "Additional Quality Control Metrics")

    create_additional_metric_table(c, other_metric, start_y=90)
    
    y_position = 70
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Reference for additional QC metrics:(see next page)")


    c.showPage()

    y_position = 700
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Reference for additional QC metrics:")

    y_position -= 30
    text = "all_seq_num: Total number of sequencing reads."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "mapped_seq_num: Number of reads that meet the sequencing quality requirements and exactly match with the oligo library sequences."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "barcode_less_1/5/10: The number of barcodes detected fewer than 1/5/10 times."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "barcode_less_1/5/10_ratio: The proportion of barcodes detected fewer than 1/5/10 times. A high value may indicate insufficient sequencing depth or low plasmid construction efficiency."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "barcode_detected_1/5/10: The number of barcodes detected at least 1/5/10 times"
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "barcode_detected_200: The number of barcodes detected more than 200 times. This value usually represents outliers and may be associated with highly uneven plasmid distribution."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "total_barcodes_type: The total number of barcode types."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "not_qualified_oligo_num/_with_bc_count3/5/10: The number of oligos that do not link to a sufficient amount (default is 3) of barcodes when using barcodes detected at least 1/3/5/10 times."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "not_qualified_oligo_ratio/_with_bc_count3/5/10: The ratio of oligos that do not link to a sufficient amount (default is 3) of barcodes when using barcodes detected at least 1/3/5/10 times. A high value may indicate insufficient sequencing depth or low plasmid construction efficiency."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "qualified_oligo_num/_with_bc_count3/5/10: The number of oligos that link to a sufficient amount (default is 3) of barcodes when using barcodes detected at least 1/3/5/10 times."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "qualified_barcodes_num/_with_bc_count3/5/10: The number of barcodes linked to oligos that meet the required number of barcodes (default is 3) when using barcodes detected at least 1/3/5/10 times."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "cv_barcodes_count_for_oligo: The coefficient of variation for the number of barcode types linked to each oligo."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "mode_barcodes_count_for_oligo: The mode for the number of barcode types linked to each oligo."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "mean_barcodes_counts: The mean number of times each barcode is detected."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "cv_barcodes_for_counts: The coefficient of variation for the number of times each barcode is detected."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    
    text = "mode_barcodes_for_counts: The mode for the number of times each barcode is detected."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)



    c.showPage()

    y_position = 720
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Coverage of barcodes at different downsampling ratios for sequencing results (for reference): ")


    plot_filename = generate_plot_for_subsample_barcode(plot_metric['barcode_coverage'][0], plot_metric['barcode_coverage'][1])
    c.drawImage(plot_filename, 120, 460, width=340, height=250)

    y_position = 440
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Distribution for the number of times each barcode is detected (for reference): ")


    plot_filename = generate_plot_for_dist_barcode(plot_metric['barcode_counts_dist'][0], plot_metric['barcode_counts_dist'][1])
    c.drawImage(plot_filename, 150, 30, width=300, height=400)


    c.save()


    print(f"QC report generated and saved as {pdf_filename}")


def main():
    ref_file = pkg_resources.resource_filename("esMPRA", "data/step2_refdata.pkl")
    with open(ref_file, "rb") as f:
        loaded_workspace = pickle.load(f)

    globals().update(loaded_workspace)


    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run_name', required=True, help='the name of this run')
    args = parser.parse_args()
    rela_dir = args.run_name
    folder_path = rela_dir+'_step2'
    name_temp = rela_dir.split('/')[-1]

    file_path = os.path.join(folder_path, 'dist_of_barcode_counts_for_oligos_after_plasmid_construct.txt')
    if os.path.isfile(file_path):
        data = np.genfromtxt(file_path, skip_header=1)
        barcode_dist_for_oligo_temp = data
        barcodes = data[:, 0]
        counts = data[:, 1]
        counts = counts.astype(int)
        full_barcodes = np.repeat(barcodes, counts)
        mean = np.mean(full_barcodes)
        std_dev = np.std(full_barcodes)
        mod_pos = np.argmax(counts)
        mode = barcodes[mod_pos]        
        mean_barcodes_count_for_oligo_temp = (mean)
        cv_barcodes_count_for_oligo_temp = (std_dev/mean)
        mode_barcodes_count_for_oligo_temp = (mode)
    else:
        raise ValueError("run_name path doesn't exist or files are broken")


    file_path = os.path.join(folder_path, 'dist_of_barcode_reads_counts.txt')
    if os.path.isfile(file_path):
        data = np.genfromtxt(file_path, skip_header=1)
        barcode_counts_dist_temp = data
        barcodes = data[:, 0]
        counts = data[:, 1]
        counts = counts.astype(int)
        full_barcodes = np.repeat(barcodes, counts)
        mean = np.mean(full_barcodes)
        std_dev = np.std(full_barcodes)
        mod_pos = np.argmax(counts)
        mode = barcodes[mod_pos]        
        mean_barcodes_counts_temp = (mean)
        cv_barcodes_for_counts_temp = (std_dev/mean)
        mode_barcodes_for_counts_temp = (mode)
    else:
        raise ValueError("run_name path doesn't exist or files are broken")

    file_path = os.path.join(folder_path, 'down_sample_for_plasmid_oligo.txt')
    if os.path.isfile(file_path):
        data = np.genfromtxt(file_path, skip_header=1)
        sub_ratio = data[:, 0]
        counts = data[:, 1]
        ratio = counts/counts[-1]
        oligo_coverage_temp = (ratio)
    else:
        raise ValueError("run_name path doesn't exist or files are broken")

    file_path = os.path.join(folder_path, 'down_sample_for_plasmid.txt')
    if os.path.isfile(file_path):
        data = np.genfromtxt(file_path, skip_header=1)
        sub_ratio = data[:, 0]
        counts = data[:, 1]
        ratio = counts/counts[-1]
        barcode_coverage_temp = (ratio)
    else:
        raise ValueError("run_name path doesn't exist or files are broken")

    file_path = os.path.join(folder_path, 'log.txt')
    if os.path.isfile(file_path):
        with open(file_path) as f_in:
            temp = f_in.readline()
            mapped_seq_num_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            barcode_less_1_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            barcode_less_5_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            barcode_less_10_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            barcode_detected_1_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            barcode_detected_5_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            barcode_detected_10_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            barcode_detected_200_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            total_barcodes_type_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            mean_barcodes_detected_counts_temp = float(temp.strip().split(':')[1])

            temp = f_in.readline()
            not_qualified_oligo_num_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            qualified_oligo_num_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            qualified_barcodes_num_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            not_qalified_oligo_num_with_bc_count3_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            qalified_oligo_num_with_bc_count3_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            qualified_barcodes_num_with_bc_count3_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            not_qalified_oligo_num_with_bc_count5_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            qalified_oligo_num_with_bc_count5_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            qualified_barcodes_num_with_bc_count5_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            not_qalified_oligo_num_with_bc_count10_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            qalified_oligo_num_with_bc_count10_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            qualified_barcodes_num_with_bc_count10_temp = int(temp.strip().split(':')[1])
    else:
        raise ValueError("run_name path doesn't exist or files are broken")

    total_oligo = not_qualified_oligo_num_temp+qualified_oligo_num_temp


    key_metric = {}
    min_value = np.min(barcode_detected_1_ratio)
    max_value = np.max(barcode_detected_1_ratio)
    key_metric['barcode_detected_1_ratio'] = (barcode_detected_1_temp/(total_barcodes_type_temp),(0.28,np.inf,0.2,np.inf))
    min_value = np.min(barcode_detected_5_ratio)
    max_value = np.max(barcode_detected_5_ratio)
    key_metric['barcode_detected_5_ratio'] = (barcode_detected_5_temp/(total_barcodes_type_temp),(0.1,np.inf,0.05,np.inf))
    min_value = np.min(barcode_detected_10_ratio)
    max_value = np.max(barcode_detected_10_ratio)
    key_metric['barcode_detected_10_ratio'] = (barcode_detected_10_temp/(total_barcodes_type_temp),(0.02,np.inf,0.005,np.inf))

    min_value = np.min(mean_barcodes_detected_counts)
    max_value = np.max(mean_barcodes_detected_counts)
    key_metric['mean_barcodes_detected_counts'] = (mean_barcodes_detected_counts_temp,(3,np.inf,2,np.inf))

    min_value = np.min(qualified_oligo_ratio)
    max_value = np.max(qualified_oligo_ratio)
    key_metric['qualified_oligo_ratio'] = (qualified_oligo_num_temp/total_oligo,(0.92,np.inf,0.8,np.inf))

    min_value = np.min(qalified_oligo_ratio_with_bc_count3)
    max_value = np.max(qalified_oligo_ratio_with_bc_count3)
    key_metric['qualified_oligo_ratio_with_bc_count3'] = (qalified_oligo_num_with_bc_count3_temp/total_oligo,(0.9,np.inf,0.85,np.inf))
    min_value = np.min(qalified_oligo_ratio_with_bc_count5)
    max_value = np.max(qalified_oligo_ratio_with_bc_count5)
    key_metric['qualified_oligo_ratio_with_bc_count5'] = (qalified_oligo_num_with_bc_count5_temp/total_oligo,(0.85,np.inf,0.7,np.inf))
    min_value = np.min(qalified_oligo_ratio_with_bc_count10)
    max_value = np.max(qalified_oligo_ratio_with_bc_count10)
    key_metric['qualified_oligo_ratio_with_bc_count10'] = (qalified_oligo_num_with_bc_count10_temp/total_oligo,(0.6,np.inf,0.1,np.inf))

    min_value = np.min(mean_barcodes_count_for_oligo)
    max_value = np.max(mean_barcodes_count_for_oligo)
    key_metric['mean_barcodes_count_for_oligo'] = (mean_barcodes_count_for_oligo_temp,(40,300,20,600))


    other_metric = {}
    min_value = np.min(mapped_seq_num)
    max_value = np.max(mapped_seq_num)
    other_metric['mapped_seq_num'] = (mapped_seq_num_temp,('-'))
    min_value = np.min(barcode_less_1)
    max_value = np.max(barcode_less_1)
    other_metric['barcode_less_1'] = (barcode_less_1_temp,('-'))
    min_value = np.min(barcode_less_1_ratio)
    max_value = np.max(barcode_less_1_ratio)
    other_metric['barcode_less_1_ratio'] = (barcode_less_1_temp/total_barcodes_type_temp,(-np.inf,0.72))
    min_value = np.min(barcode_less_5)
    max_value = np.max(barcode_less_5)
    other_metric['barcode_less_5'] = (barcode_less_5_temp,('-'))
    min_value = np.min(barcode_less_5_ratio)
    max_value = np.max(barcode_less_5_ratio)
    other_metric['barcode_less_5_ratio'] = (barcode_less_5_temp/total_barcodes_type_temp,(-np.inf,0.9))
    min_value = np.min(barcode_less_10)
    max_value = np.max(barcode_less_10)
    other_metric['barcode_less_10'] = (barcode_less_10_temp,('-'))
    min_value = np.min(barcode_less_10_ratio)
    max_value = np.max(barcode_less_10_ratio)
    other_metric['barcode_less_10_ratio'] = (barcode_less_10_temp/total_barcodes_type_temp,(-np.inf,0.98))
    min_value = np.min(barcode_detected_1)
    max_value = np.max(barcode_detected_1)
    other_metric['barcode_detected_1'] = (barcode_detected_1_temp,('-'))
    min_value = np.min(barcode_detected_5)
    max_value = np.max(barcode_detected_5)
    other_metric['barcode_detected_5'] = (barcode_detected_5_temp,('-'))
    min_value = np.min(barcode_detected_10)
    max_value = np.max(barcode_detected_10)
    other_metric['barcode_detected_10'] = (barcode_detected_10_temp,('-'))
    min_value = np.min(barcode_detected_200)
    max_value = np.max(barcode_detected_200)
    other_metric['barcode_detected_200'] = (barcode_detected_200_temp,('-'))
    min_value = np.min(total_barcodes_type)
    max_value = np.max(total_barcodes_type)
    other_metric['total_barcodes_type'] = (total_barcodes_type_temp,('-'))

    min_value = np.min(not_qualified_oligo_num)
    max_value = np.max(not_qualified_oligo_num)
    other_metric['not_qualified_oligo_num'] = (not_qualified_oligo_num_temp,('-'))
    min_value = np.min(not_qualified_oligo_ratio)
    max_value = np.max(not_qualified_oligo_ratio)
    other_metric['not_qualified_oligo_ratio'] = (not_qualified_oligo_num_temp/total_oligo,(-np.inf,0.08))
    min_value = np.min(qualified_oligo_num)
    max_value = np.max(qualified_oligo_num)
    other_metric['qualified_oligo_num'] = (qualified_oligo_num_temp,('-'))
    min_value = np.min(qualified_barcodes_num)
    max_value = np.max(qualified_barcodes_num)
    other_metric['qualified_barcodes_num'] = (qualified_barcodes_num_temp,('-'))
    min_value = np.min(qualified_barcodes_ratio)
    max_value = np.max(qualified_barcodes_ratio)
    other_metric['qualified_barcodes_ratio'] = (qualified_barcodes_num_temp/total_barcodes_type_temp,(0.25,np.inf))

    min_value = np.min(not_qalified_oligo_num_with_bc_count3)
    max_value = np.max(not_qalified_oligo_num_with_bc_count3)
    other_metric['not_qalified_oligo_num_with_bc_count3'] = (not_qalified_oligo_num_with_bc_count3_temp,('-'))
    min_value = np.min(not_qalified_oligo_ratio_with_bc_count3)
    max_value = np.max(not_qalified_oligo_ratio_with_bc_count3)
    other_metric['not_qalified_oligo_ratio_with_bc_count3'] = (not_qalified_oligo_num_with_bc_count3_temp/total_oligo,(-np.inf,0.1))
    min_value = np.min(qalified_oligo_num_with_bc_count3)
    max_value = np.max(qalified_oligo_num_with_bc_count3)
    other_metric['qalified_oligo_num_with_bc_count3'] = (qalified_oligo_num_with_bc_count3_temp,('-'))
    min_value = np.min(qualified_barcodes_num_with_bc_count3)
    max_value = np.max(qualified_barcodes_num_with_bc_count3)
    other_metric['qualified_barcodes_num_with_bc_count3'] = (qualified_barcodes_num_with_bc_count3_temp,('-'))


    min_value = np.min(not_qalified_oligo_num_with_bc_count5)
    max_value = np.max(not_qalified_oligo_num_with_bc_count5)
    other_metric['not_qalified_oligo_num_with_bc_count5'] = (not_qalified_oligo_num_with_bc_count5_temp,('-'))
    min_value = np.min(not_qalified_oligo_ratio_with_bc_count5)
    max_value = np.max(not_qalified_oligo_ratio_with_bc_count5)
    other_metric['not_qalified_oligo_ratio_with_bc_count5'] = (not_qalified_oligo_num_with_bc_count5_temp/total_oligo,(-np.inf,0.15))
    min_value = np.min(qalified_oligo_num_with_bc_count5)
    max_value = np.max(qalified_oligo_num_with_bc_count5)
    other_metric['qalified_oligo_num_with_bc_count5'] = (qalified_oligo_num_with_bc_count5_temp,('-'))
    min_value = np.min(qualified_barcodes_num_with_bc_count5)
    max_value = np.max(qualified_barcodes_num_with_bc_count5)
    other_metric['qualified_barcodes_num_with_bc_count5'] = (qualified_barcodes_num_with_bc_count5_temp,('-'))


    min_value = np.min(not_qalified_oligo_num_with_bc_count10)
    max_value = np.max(not_qalified_oligo_num_with_bc_count10)
    other_metric['not_qalified_oligo_num_with_bc_count10'] = (not_qalified_oligo_num_with_bc_count10_temp,('-'))
    min_value = np.min(not_qalified_oligo_ratio_with_bc_count10)
    max_value = np.max(not_qalified_oligo_ratio_with_bc_count10)
    other_metric['not_qalified_oligo_ratio_with_bc_count10'] = (not_qalified_oligo_num_with_bc_count10_temp/total_oligo,(-np.inf,0.5))
    min_value = np.min(qalified_oligo_num_with_bc_count10)
    max_value = np.max(qalified_oligo_num_with_bc_count10)
    other_metric['qalified_oligo_num_with_bc_count10'] = (qalified_oligo_num_with_bc_count10_temp,('-'))
    min_value = np.min(qualified_barcodes_num_with_bc_count10)
    max_value = np.max(qualified_barcodes_num_with_bc_count10)
    other_metric['qualified_barcodes_num_with_bc_count10'] = (qualified_barcodes_num_with_bc_count10_temp,('-'))

    min_value = np.min(cv_barcodes_count_for_oligo)
    max_value = np.max(cv_barcodes_count_for_oligo)
    other_metric['cv_barcodes_count_for_oligo'] = (cv_barcodes_count_for_oligo_temp,(0.6,0.8))
    min_value = np.min(mode_barcodes_count_for_oligo)
    max_value = np.max(mode_barcodes_count_for_oligo)
    other_metric['mode_barcodes_count_for_oligo'] = (mode_barcodes_count_for_oligo_temp,(40,300))
    min_value = np.min(mean_barcodes_counts)
    max_value = np.max(mean_barcodes_counts)
    other_metric['mean_barcodes_counts'] = (mean_barcodes_counts_temp,(2,10))
    min_value = np.min(cv_barcodes_for_counts)
    max_value = np.max(cv_barcodes_for_counts)
    other_metric['cv_barcodes_for_counts'] = (cv_barcodes_for_counts_temp,(0.8,1))
    min_value = np.min(mode_barcodes_for_counts)
    max_value = np.max(mode_barcodes_for_counts)
    other_metric['mode_barcodes_for_counts'] = (mode_barcodes_for_counts_temp,(1,5))



    plot_metric = {}

    plot_metric['oligo_coverage'] = [oligo_coverage_temp, oligo_coverage]
    plot_metric['barcode_coverage'] = [barcode_coverage_temp, barcode_coverage]
    plot_metric['barcode_dist_for_oligo'] = [barcode_dist_for_oligo_temp, barcode_dist_for_oligo]
    plot_metric['barcode_counts_dist'] = [barcode_counts_dist_temp, barcode_counts_dist]


    suggestions_data = []
    for metric_name, (value, reference_range) in key_metric.items():
        risk = evaluate_metric(value, reference_range)
        if risk == 'High Risk' or risk == 'Medium Risk':
            suggestion = generate_qc_suggestion(risk, metric_name)
            suggestions_data.append(suggestion)


    generate_qc_report(name_temp, key_metric, plot_metric, other_metric, suggestions_data, target_metric="qualified_oligo_ratio")


if __name__ == "__main__":
    main()