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

    plt.figure(figsize=(8, 6))
    plt.plot(sub_ratio, value, label="tested results", color="blue", marker='o')
    plt.fill_between(sub_ratio, min_ratios, max_ratios, color="skyblue", alpha=0.4, label="ref range")
    plt.title("Sampling Depth vs Retention Ratio")
    plt.xlabel("Sampling Depth (log10)")
    plt.ylabel("Retention Ratio")
    plt.legend(loc="lower right")
    plot_filename = 'step1_sub_range.png'
    plt.savefig(plot_filename)
    plt.close()
    return plot_filename


def generate_plot_for_dist(value, ref_values):

    plt.figure(figsize=(7.5, 9))

    normality_results = []

    plt.subplot(2, 1, 1)
    for i, experiment in enumerate(ref_values):
        if i ==2:
            continue
        barcodes = experiment[:, 0]
        counts = experiment[:, 1]
        counts = counts.astype(int)
        full_barcodes = np.repeat(barcodes, counts)
        x_min = np.min(full_barcodes)
        x_max = np.max(full_barcodes)
        normalized = (full_barcodes - x_min) / (x_max - x_min)
        plt.hist(normalized, bins=100, alpha=0.3, density=True)
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
    plt.hist(full_barcodes, 100, alpha=0.6)

    plt.xlabel('Barcode Number')
    plt.ylabel('Frequency')
    plt.title('Test Barcode Distribution')
    plt.grid(True)
    plot_filename = 'step1_hist.png'
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
        table_data.append([metric_name, f"{value:.2f}", f"{reference_range[0]:.2f} - {reference_range[1]:.2f}", risk])
    
    table = Table(table_data, colWidths=[120, 100, 120, 100])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    
    table.wrapOn(c, 70, start_y)
    table.drawOn(c, 70, start_y)



def create_additional_metric_table(c, metrics_data, start_y=650):
    table_data = [["Metric Name", "Experimental Value", "Reference Range"]]
    for metric_name, (value, reference_range) in metrics_data.items():
        # risk = evaluate_metric(value, reference_range)

        if reference_range == '-':
            table_data.append([metric_name, f"{value:.2f}", f"-"])
        else:
            table_data.append([metric_name, f"{value:.2f}", f"{reference_range[0]:.2f} - {reference_range[1]:.2f}"])
    
    table = Table(table_data, colWidths=[160, 160, 160])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    
    table.wrapOn(c, 60, start_y)
    table.drawOn(c, 60, start_y)




def generate_qc_report(name_temp, metrics_data, plot_metric, other_metric, suggestions_data, target_metric):
    pdf_filename = f"qc_{name_temp}_step1.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Quality Control Report for Oligo-barcode Mapping Step")
    
    create_metric_evaluation_table(c, metrics_data, start_y=640)

    y_position = 620
    c.setFont("Helvetica", 12)
    
    c.drawString(50, y_position, "Reference Explanation for Quality Control Results:")

    y_position -= 25
    text = "qualified_oligo_ratio: A low ratio indicates an issue with the ligation efficiency during library construction. Check the plasmid construction and emulsion PCR steps if risk values occur."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "ambigous_barcode_ratio: The ratio of the same barcode being repeatedly linked to multiple oligos. A high ratio indicates insufficient barcode complexity or non-random ligation."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "mean_barcodes_counts: The average number of different barcode types linked to each oligo. A low count can cause inaccurate quantification, while a high count may reduce oligo coverage in later steps. Adjust library complexity if risk values occur."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "cv_barcodes_counts: CV(Coefficient of Variation) indicates the distribution of barcode counts. Risk values suggest issues with the efficiency or randomness of the ligation process. Check the barcode distribution plot for further analysis."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)


    plot_filename = generate_plot_for_subsample(plot_metric['oligo_coverage'][0], plot_metric['oligo_coverage'][1])
    c.drawImage(plot_filename, 90, 100, width=400, height=300)

    y_position = 85
    text = "Coverage of oligos at different downsampling ratios for sequencing results: The closer the curve is to the upper left, the more sufficient the sequencing depth. If the test result is in the lower right of the reference range, consider increasing the sequencing depth."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)


    c.showPage()


    c.setFont("Helvetica", 12)
    c.drawString(50, 700, "Distribution of barcodes number linked to oligos for reference:")

    plot_filename = generate_plot_for_dist(plot_metric['barcode_dist'][0], plot_metric['barcode_dist'][1])
    c.drawImage(plot_filename, 140, 230, width=300, height=450)

    y_position  = 200
    text = "The distribution of the tested barcodes should resemble one of the reference distributions. If the long-tail effect is too pronounced, it is likely that the linking process between barcodes and oligos is not random, or that the emulsion PCR step has not effectively controlled the amplification efficiency of different sequences. When there is a significant discrepancy between this distribution and the reference distribution, it is recommended to check whether the linking step and the emulsion PCR step have been carried out smoothly."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)


    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 740, "Additional Quality Control Metrics")

    create_additional_metric_table(c, other_metric, start_y=520)
    

    y_position = 500
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Reference for additional QC metrics:")


    y_position -= 30
    text = "all_seq_num: Total number of sequencing reads."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "mapped_seq_num: Number of reads that meet the sequencing quality requirements and exactly match with the oligo library sequences."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "mapped_seq_ratio: Ratio of reads that meet the sequencing quality requirements and exactly match with the oligo library sequences."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "ambiguous_barcode_num: Number of barcodes that are ambiguously linked to multiple oligos."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "unique_barcode_num: Number of barcode types that are uniquely linked to a single oligo."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "qualified_oligo_num: Number of oligos that are linked to a sufficient amount (default value is 3) of barcodes."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "not_qualified_oligo_num: Number of oligos that do not meet quality control requirements (due to insufficient types of linked barcodes)."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "not_qualified_oligo_ratio: Ratio of oligos that do not meet quality control requirements (due to insufficient types of linked barcodes)."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "unique_barcode_num_qualified: Number of available barcode types after removing not qualified oligos."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "mode_barcodes_counts: The mode of the number of different barcode types linked to each oligo."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    c.save()

    print(f"QC report generated and saved as {pdf_filename}")


def main():

    ref_file = pkg_resources.resource_filename("esMPRA", "data/step1_refdata.pkl")
    with open(ref_file, "rb") as f:
        loaded_workspace = pickle.load(f)

    globals().update(loaded_workspace)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run_name', required=True, help='the name of this run')
    args = parser.parse_args()

    rela_dir = args.run_name
    folder_path = rela_dir+'_step1'
    name_temp = rela_dir.split('/')[-1]

    file_path = os.path.join(folder_path, 'dist_of_barcode_counts_for_oligos.txt')
    if os.path.isfile(file_path):
        data = np.genfromtxt(file_path, skip_header=1)
        barcode_dist_temp = data
        barcodes = data[:, 0]
        counts = data[:, 1]
        counts = counts.astype(int)
        full_barcodes = np.repeat(barcodes, counts)
        mean_temp = np.mean(full_barcodes)
        std_dev_temp = np.std(full_barcodes)
        cv_temp = std_dev_temp/mean_temp
        mod_pos_temp = np.argmax(counts)
        mode_temp = barcodes[mod_pos_temp]     
    else:
        raise ValueError("run_name path doesn't exist or files are broken")

    file_path = os.path.join(folder_path, 'down_sample_for_mapping.txt')
    if os.path.isfile(file_path):
        data = np.genfromtxt(file_path, skip_header=1)
        sub_ratio = data[:, 0]
        counts = data[:, 1]
        ratio_temp = counts/counts[-1]
    else:
        raise ValueError("run_name path doesn't exist or files are broken")

    file_path = os.path.join(folder_path, 'log.txt')
    if os.path.isfile(file_path):
        with open(file_path) as f_in:
            temp = f_in.readline()
            seq_num = int(temp.strip())
            temp = f_in.readline()
            map_num = int(temp.strip())
            temp = f_in.readline()
            del_barcode = int(temp.strip())            
            temp = f_in.readline()
            usful_barcode = int(temp.strip())
            temp = f_in.readline()
            quali_oligo = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            unquali_oligo = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            quali_barcode = int(temp.strip().split(':')[1])
    else:
        raise ValueError("run_name path doesn't exist or files are broken")


    key_metric = {}
    min_value = np.min(qualified_oligo_ratio)
    max_value = np.max(qualified_oligo_ratio)
    key_metric['qualified_oligo_ratio'] = (quali_oligo/(quali_oligo+unquali_oligo),(0.95,1,0.9,1))
    min_value = np.min(ambigous_barcode_ratio)
    max_value = np.max(ambigous_barcode_ratio)
    key_metric['ambigous_barcode_ratio'] = (del_barcode/usful_barcode,(0,0.05,0,0.1))
    min_value = np.min(mean_barcodes_counts)
    max_value = np.max(mean_barcodes_counts)
    key_metric['mean_barcodes_counts'] = (mean_temp,(50,500,30,800))
    min_value = np.min(cv_barcodes_counts)
    max_value = np.max(cv_barcodes_counts)
    key_metric['cv_barcodes_counts'] = (cv_temp,(0.5,1.3,0.3,1.5))


    other_metric = {}
    min_value = np.min(all_seq_num)
    max_value = np.max(all_seq_num)
    other_metric['all_seq_num'] = (seq_num,('-'))
    min_value = np.min(mapped_seq_num)
    max_value = np.max(mapped_seq_num)
    other_metric['mapped_seq_num'] = (map_num,('-'))
    min_value = np.min(mapped_seq_ratio)
    max_value = np.max(mapped_seq_ratio)
    other_metric['mapped_seq_ratio'] = (map_num/seq_num,(0.3,0.8))
    min_value = np.min(ambigous_barcode_num)
    max_value = np.max(ambigous_barcode_num)
    other_metric['ambigous_barcode_num'] = (del_barcode,('-'))
    min_value = np.min(unique_barcode_num)
    max_value = np.max(unique_barcode_num)
    other_metric['unique_barcode_num'] = (usful_barcode,('-'))
    min_value = np.min(qualified_oligo_num)
    max_value = np.max(qualified_oligo_num)
    other_metric['qualified_oligo_num'] = (quali_oligo,('-'))
    min_value = np.min(not_qualified_oligo_num)
    max_value = np.max(not_qualified_oligo_num)
    other_metric['not_qualified_oligo_num'] = (unquali_oligo,('-'))
    min_value = np.min(not_qualified_oligo_ratio)
    max_value = np.max(not_qualified_oligo_ratio)
    other_metric['not_qualified_oligo_ratio'] = (unquali_oligo/(quali_oligo+unquali_oligo),(0,0.05))
    min_value = np.min(unique_barcode_num_qualified)
    max_value = np.max(unique_barcode_num_qualified)
    other_metric['unique_barcode_num_qualified'] = (quali_barcode,('-'))
    min_value = np.min(mode_barcodes_counts)
    max_value = np.max(mode_barcodes_counts)
    other_metric['mode_barcodes_counts'] = (mode_temp,(50,500))


    plot_metric = {}

    plot_metric['barcode_dist'] = [barcode_dist_temp, barcode_dist]
    plot_metric['oligo_coverage'] = [ratio_temp, oligo_coverage]


    suggestions_data = []
    for metric_name, (value, reference_range) in key_metric.items():
        risk = evaluate_metric(value, reference_range)
        if risk == 'High Risk' or risk == 'Medium Risk':
            suggestion = generate_qc_suggestion(risk, metric_name)
            suggestions_data.append(suggestion)


    generate_qc_report(name_temp, key_metric, plot_metric, other_metric, suggestions_data, target_metric="qualified_oligo_ratio")


if __name__ == "__main__":
    main()