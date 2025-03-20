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
    plot_filename = 'step4_sub_range.png'
    plt.savefig(plot_filename)
    plt.close()
    return plot_filename


def generate_plot_for_dist(value, ref_values):

    plt.figure(figsize=(10, 12))

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

    # 设置图表
    plt.xlabel('Barcode Number')
    plt.ylabel('Frequency')
    plt.title('Test Barcode Distribution')
    plt.legend()
    plt.grid(True)
    plot_filename = 'step4_hist.png'
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
        if reference_range == (0,0,0,0):
            table_data.append([metric_name, f"{value:.2f}", f"-",f"-"])
        elif reference_range[0] == -np.inf:
            table_data.append([metric_name, f"{value:.2f}", f"<={reference_range[1]:.2f}", risk])
        else:
            table_data.append([metric_name, f"{value:.2f}", f"{reference_range[0]:.2f} - {reference_range[1]:.2f}", risk])
    
    table = Table(table_data, colWidths=[150, 100, 120, 100])
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
    
    table.wrapOn(c, 50, start_y)
    table.drawOn(c, 50, start_y)



def generate_qc_report(name_temp, metrics_data, plot_filename, suggestions_data, target_metric):
    pdf_filename = f"qc_{name_temp}_step4.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Quality Control Report for Activity Calculation Step")

    create_metric_evaluation_table(c, metrics_data, start_y=655)

    y_position = 635
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Reference Explanation for Quality Control Results:")
    
    
    y_position -= 25
    text = "qualified_oligo_num: The number of oligos linked with a sufficient number (default value: 3) of barcodes that appear at least the specified number of times (default value: 1) in both plasmid and cDNA sequencing."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    y_position -= 5
    text = "qualified_oligo_ratio: The ratio of oligos linked with a sufficient number (default value: 3) of barcodes that appear at least the specified number of times (default value: 1) in both plasmid and cDNA sequencing."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)



    c.drawImage(plot_filename, 100,110, width=400, height=300)

    y_position -= 5
    text = "PCC_between_plasmid_cDNA: The correlation between the counts of the same barcode detected in plasmid and cDNA sequencing. A high correlation value may indicate that the original plasmid DNA was not effectively removed during cDNA sequencing after reverse transcription. It is recommended to check whether the steps for removing plasmid DNA were effectively performed."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)



    y_position = 100
    text = "Distribution of barcode counts in plasmid and cDNA sequencing: The x-axis and y-axis show the counts of the same barcode in plasmid and cDNA sequencing. A significant correlation suggests that plasmid DNA was not effectively removed during cDNA sequencing. Check the plasmid DNA removal steps if this happens."
    y_position = draw_multiline_string(c, 50, y_position, text, max_width=500)

    c.save()

    print(f"QC report generated and saved as {pdf_filename}")


def main():
    ref_file = pkg_resources.resource_filename("esMPRA", "data/step4_refdata.pkl")
    with open(ref_file, "rb") as f:
        loaded_workspace = pickle.load(f)

    globals().update(loaded_workspace)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run_name', required=True, help='the name of this run')
    args = parser.parse_args()
    rela_dir = args.run_name
    folder_path = rela_dir+'_step4'
    name_temp = rela_dir.split('/')[-1]

    plot_filename = os.path.join(folder_path, 'plm_exp_PCC.png')
    file_path = os.path.join(folder_path, 'log.txt')
    if os.path.isfile(file_path):
        with open(file_path) as f_in:
            temp = f_in.readline()
            qualified_oligo_num_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            total_oligo_num_temp = int(temp.strip().split(':')[1])
            temp = f_in.readline()
            PCC_between_plasmid_cDNA_temp = float(temp.strip().split(':')[1])
    else:
        raise ValueError("run_name path doesn't exist or files are broken")


    key_metric = {}
    min_value = np.min(qualified_oligo_num)
    max_value = np.max(qualified_oligo_num)
    key_metric['qualified_oligo_num'] = (qualified_oligo_num_temp,(0,0,0,0))
    min_value = np.min(qualified_oligo_ratio)
    max_value = np.max(qualified_oligo_ratio)
    key_metric['qualified_oligo_ratio'] = (qualified_oligo_num_temp/total_oligo_num_temp,(0,0,0,0))
    min_value = np.min(PCC_between_plasmid_cDNA)
    max_value = np.max(PCC_between_plasmid_cDNA)
    key_metric['PCC_between_plasmid_cDNA'] = (PCC_between_plasmid_cDNA_temp,(-np.inf,0.35,-np.inf,0.6))


    suggestions_data = []
    for metric_name, (value, reference_range) in key_metric.items():
        risk = evaluate_metric(value, reference_range)
        if risk == 'High Risk' or risk == 'Medium Risk':
            suggestion = generate_qc_suggestion(risk, metric_name)
            suggestions_data.append(suggestion)


    generate_qc_report(name_temp, key_metric,plot_filename, suggestions_data, target_metric="qualified_oligo_ratio")


if __name__ == "__main__":
    main()