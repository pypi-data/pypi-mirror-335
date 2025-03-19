from pycirclize import Circos, config as circos_config  # Rename to avoid confusion
from pycirclize.parser import Gff
import pandas as pd
import os
from matplotlib.patches import Patch
import matplotlib.pyplot as plt

from dbcan.parameter import CGCPlotConfig
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CGCCircosPlot:
    def __init__(self, config: CGCPlotConfig):
        self.config = config
        self.input_dir = config.output_dir.strip() if hasattr(config, 'output_dir') else ""
        self.gff_file = os.path.join(self.input_dir, "cgc.gff")
        self.tsv_file = os.path.join(self.input_dir, "cgc_standard_out.tsv")
        self.output_dir = os.path.join(self.input_dir, "cgc_circos")
        # Validate file existence
        if not os.path.exists(self.gff_file):
            raise FileNotFoundError(f"GFF file not found: {self.gff_file}")
        if not os.path.exists(self.tsv_file):
            raise FileNotFoundError(f"TSV file not found: {self.tsv_file}")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            
        # Load GFF data
        self.gff = Gff(self.gff_file)
        self.seqid2size = self.gff.get_seqid2size()
        self.space = 0 if len(self.seqid2size) == 1 else 2
        self.circos = Circos(sectors=self.seqid2size, space=self.space)
        self.feature_type = "gene"
        self.seqid2features = self.gff.get_seqid2features(feature_type=self.feature_type)
        self.circos.text("CGC Annotation Circos Plot", size=40)
        
        # Load TSV data with enhanced error handling
        try:
            self.tsv_data = pd.read_csv(self.tsv_file, sep='\t')
            # Validate required columns
            required_columns = ['CGC#', 'Contig ID', 'Protein ID', 'Gene Start', 'Gene Stop']
            missing_cols = [col for col in required_columns if col not in self.tsv_data.columns]
            if missing_cols:
                logging.warning(f"Missing required columns in TSV file: {missing_cols}")
        except Exception as e:
            logging.error(f"Error reading TSV file: {str(e)}")
            self.tsv_data = pd.DataFrame()  # Create empty DataFrame

    def plot_feature_outer(self, circos=None):
        """Plot outer track with position markers"""
        if circos is None:
            circos = self.circos
            
        for sector in circos.sectors:
            outer_track = sector.add_track((99.7, 100))
            outer_track.axis(fc="black")
            major_interval = 100000
            minor_interval = int(major_interval / 10)
            if sector.size > minor_interval:
                outer_track.xticks_by_interval(major_interval, label_formatter=lambda v: f"{v / 1000:.0f} Kb")
                outer_track.xticks_by_interval(minor_interval, tick_length=1, show_label=False)

    def plot_features_cazyme(self, circos=None, sector_name=None):
        """Plot CAZyme features"""
        if circos is None:
            circos = self.circos
            
        for sector in circos.sectors:
            if sector_name and sector.name != sector_name:
                continue
                
            cds_track = sector.add_track((45, 60), r_pad_ratio=0.1)
            cds_track.axis(fc="#EEEEEE", ec="none")
            cds_track.grid(2, color="black")
            features = self.seqid2features[sector.name]
            for feature in features:
                if feature.type == self.feature_type:
                    cgc_type = feature.qualifiers.get("CGC_annotation", ["unknown"])[0].split("|")[0]
                    if cgc_type == "CAZyme":  # only plot CAZyme features
                        color = self.get_feature_color(cgc_type)
                        cds_track.genomic_features(feature, fc=color)

    def plot_features_cgc(self, circos=None, sector_name=None):
        """Plot CGC features"""
        if circos is None:
            circos = self.circos
            
        for sector in circos.sectors:
            if sector_name and sector.name != sector_name:
                continue
                
            cds_track = sector.add_track((65,80), r_pad_ratio=0.1)
            cds_track.axis(fc="#EEEEEE", ec="none")
            cds_track.grid(2, color="black")
            features = self.seqid2features[sector.name]
            
            # Protect against empty DataFrame
            if not self.tsv_data.empty and 'Protein ID' in self.tsv_data.columns:
                cgc_ids_list = self.tsv_data['Protein ID'].unique().astype(str)
                for feature in features:
                    if feature.type == self.feature_type:
                        cgc_type = feature.qualifiers.get("CGC_annotation", ["unknown"])[0].split("|")[0]
                        cgc_id  = str(feature.qualifiers.get("protein_id", ["unknown"])[0])
                        if cgc_id in cgc_ids_list:
                            color = self.get_feature_color(cgc_type)
                            cds_track.genomic_features(feature, fc=color)

    def plot_cgc_range(self, circos=None, sector_name=None):
        """Plot CGC range as rectangles"""
        if circos is None:
            circos = self.circos
            
        for sector in circos.sectors:
            if sector_name and sector.name != sector_name:
                continue
                
            cgc_track = sector.add_track((83, 88), r_pad_ratio=0.1)
            cgc_track.axis(fc="#EEEEEE", ec="none")
            cgc_track.grid(2, color="black")
            
            # Get sector size for validation
            sector_size = self.seqid2size[sector.name]
            
            # Filter data for current sector
            if self.tsv_data.empty or 'Contig ID' not in self.tsv_data.columns:
                continue
                
            # use sector name as string for comparison
            sector_data = self.tsv_data[self.tsv_data['Contig ID'].astype(str) == sector.name]
            
            # Process CGC ranges
            if 'CGC#' in sector_data.columns:
                for cgc_id in sector_data['CGC#'].unique():
                    cgc_rows = sector_data[sector_data['CGC#'] == cgc_id]
                    if 'Gene Start' in cgc_rows.columns and 'Gene Stop' in cgc_rows.columns:
                        try:
                            start = cgc_rows['Gene Start'].min()
                            end = cgc_rows['Gene Stop'].max()
                            
                            # verify coordinates are within sector size
                            if start >= sector_size or end > sector_size:
                                logging.warning(
                                    f"Skipping CGC {cgc_id} with coordinates ({start}-{end}) "
                                    f"that exceed sector '{sector.name}' size ({sector_size})"
                                )
                                continue
                            
                            # make sure start < end
                            start = max(0, min(start, sector_size-1))
                            end = max(1, min(end, sector_size))
                            
                            cgc_track.rect(start, end, fc="lightblue", ec="black")
                            
                            # if end - start > sector_size * 0.01:
                            cgc_track.annotate((start + end) / 2, cgc_id, label_size=10)
                        
                        except Exception as e:
                            logging.warning(f"Error plotting CGC {cgc_id} on {sector.name}: {str(e)}")

    def get_feature_color(self, cgc_type):
        """Get color for different feature types"""
        color_map = {
            "CAZyme": "red",
            "TC": "green",
            "TF": "blue",
            "STP": "yellow"
        }
        return color_map.get(cgc_type, "gray")

    def add_legend(self, circos=None):
        """Add legend to the plot"""
        if circos is None:
            circos = self.circos
            
        legend_labels = ["CAZyme", "TC", "TF", "STP"]
        legend_colors = [self.get_feature_color(label) for label in legend_labels]
        rect_handles = []
        for idx, color in enumerate(legend_colors):
            rect_handles.append(Patch(color=color, label=legend_labels[idx]))
        _ = circos.ax.legend(
            handles=rect_handles,
            bbox_to_anchor=(0.5, 0.4),
            loc="center",
            fontsize=20,
            title="Types",
            title_fontsize=20,
            ncol=2,
        )

    def plot_single_contig(self, contig_name):
        """Plot a single contig and save to individual file"""
        try:
            # Create independent Circos object for this contig
            contig_size = {contig_name: self.seqid2size[contig_name]}
            contig_circos = Circos(sectors=contig_size, space=0)
            contig_circos.text(f"CGC Annotation - {contig_name}", size=40)
            
            # Add various features
            self.plot_feature_outer(contig_circos)
            self.plot_features_cazyme(contig_circos, contig_name)
            self.plot_features_cgc(contig_circos, contig_name)
            self.plot_cgc_range(contig_circos, contig_name)
            
            # Enable annotation adjustment to avoid overlap
            circos_config.ann_adjust.enable = True
            
            # Dynamically adjust figure size based on contig size
            size = min(30, max(15, 15 + len(self.seqid2size) / 2)) # Scale based on contig length
            fig = contig_circos.plotfig(figsize=(size, size))
            self.add_legend(contig_circos)
            
            # Save to file
            output_path = os.path.join(self.output_dir, f"cgc_circos_{contig_name}.svg")
            fig.savefig(output_path, format='svg', dpi=300)
            plt.close(fig) 
            logging.info(f"Individual contig plot saved to: {output_path}")
            
        except Exception as e:
            logging.error(f"Error plotting contig {contig_name}: {str(e)}")

    def plot(self):
        """Plot everything - combined and individual contigs"""
        try:
            # 1. First plot containing all contigs
            self.plot_feature_outer()
            self.plot_features_cazyme()
            self.plot_features_cgc()
            self.plot_cgc_range()
            circos_config.ann_adjust.enable = True  # Avoid annotation overlap
            
            # Adjust figure size based on number of contigs
            size = min(30, max(15, 15 + len(self.seqid2size) / 2))
            fig = self.circos.plotfig(figsize=(size, size))
            self.add_legend()

            output_path = os.path.join(self.output_dir, "cgc_circos_plot.svg")
            fig.savefig(output_path, format='svg', dpi=300)
            plt.close(fig)  # Close the figure to free memory
            logging.info(f"Combined circos plot saved to: {output_path}")
            
            # 2. Then plot each contig individually
            total_contigs = len(self.seqid2size)
            logging.info(f"Creating individual plots for {total_contigs} contigs...")
            
            for idx, contig_name in enumerate(sorted(self.seqid2size.keys()), 1):
                logging.info(f"Processing contig {idx}/{total_contigs}: {contig_name}")
                self.plot_single_contig(contig_name)
                if idx % 10 == 0:
                    plt.close('all')  # Close all figures to free memory every 10 plots

                plt.close('all')  # Close all figures to free memory after each plot
                
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())  # Print full traceback for debugging

# if __name__ == "__main__":
#     config_dict = {
#         "gff_file": "/mnt/array2/xinpeng/dbcan_nf/dbCAN-xinpeng/bcb-unl-github/run_dbcan_new/dbcan_test/test_data/old_output/cgc.gff",
#         "tsv_file": "/mnt/array2/xinpeng/dbcan_nf/dbCAN-xinpeng/bcb-unl-github/run_dbcan_new/dbcan_test/test_data/old_output/cgc_standard_out.tsv",
#         "output_dir": "/mnt/array2/xinpeng/dbcan_nf/dbCAN-xinpeng/bcb-unl-github/run_dbcan_new/dbcan_test/test_data/old_output",
#     }
#     config = CGCPlotConfig.from_dict(CGCPlotConfig, config_dict)
#     plotter = CGCCircosPlot(config)
#     plotter.plot()


# if __name__ == "__main__":
#     config_dict = {
#         "gff_file": "/mnt/array2/xinpeng/dbcan_nf/dbCAN-xinpeng/bcb-unl-github/run_dbcan_new/dbcan_test/test_data/cgc.gff",
#         "tsv_file": "/mnt/array2/xinpeng/dbcan_nf/dbCAN-xinpeng/bcb-unl-github/run_dbcan_new/dbcan_test/test_data/cgc_standard_out.tsv",
#         "output_dir": "/mnt/array2/xinpeng/dbcan_nf/dbCAN-xinpeng/bcb-unl-github/run_dbcan_new/dbcan_test/test_data/",
#     }
#     config = CGCPlotConfig.from_dict(CGCPlotConfig, config_dict)
#     plotter = CGCCircosPlot(config)
#     plotter.plot()
