import pandas as pd
import os
import logging
from Bio import SeqIO
from BCBio import GFF
from dbcan.parameter import GFFConfig
from dataclasses import fields

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GFFProcessor:
    """Base GFF processor class using template method pattern"""
    
    def __init__(self, config: GFFConfig):
        """Initialize processor with configuration"""
        self.config = config
        
        # Use template method pattern to set up all required attributes
        self._setup_processor()
    
    def _setup_processor(self):
        """Set up processor attributes using template method pattern"""
        #needed input parameters
        self.output_dir = self._derive_output_dir()
        self.input_gff = self._derive_input_gff()
        
        #get from output_dir
        self.input_total_faa = self._derive_input_total_faa()
        self.cazyme_overview = self._derive_cazyme_overview()
        self.cgc_sig_file = self._derive_cgc_sig_file()
        self.output_gff = self._derive_output_gff()
        
        # Validate required attributes
        self._validate_attributes()
    
    def _validate_attributes(self):
        """Validate that all required attributes are properly set"""
        required_attrs = ['output_dir', 'input_gff', 'output_gff', 'cazyme_overview', 'cgc_sig_file']
        
        for attr in required_attrs:
            if getattr(self, attr, None) is None:
                raise ValueError(f"Required attribute '{attr}' was not properly set")
        
        # Check if required files exist
        file_attrs = ['input_gff', 'cazyme_overview', 'cgc_sig_file']
        for attr in file_attrs:
            file_path = getattr(self, attr)
            if not os.path.exists(file_path):
                logging.warning(f"File not found: {file_path}")
                
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            
    def _derive_output_dir(self):
        """Derive output directory path"""
        return self.config.output_dir
    
    def _derive_input_total_faa(self):
        """Derive path to input protein sequences file"""
        return os.path.join(self.output_dir, 'uniInput.faa')
    
    def _derive_cazyme_overview(self):
        """Derive path to CAZyme overview file"""
        return os.path.join(self.output_dir, 'overview.tsv')
    
    def _derive_cgc_sig_file(self):
        """Derive path to CGC signature file"""
        return os.path.join(self.output_dir, 'total_cgc_info.tsv')
    
    def _derive_input_gff(self):
        """Derive path to input GFF file"""
        if not hasattr(self.config, 'input_gff') or not self.config.input_gff:
            raise ValueError("Input GFF file not specified in configuration")
        return self.config.input_gff
    
    def _derive_output_gff(self):
        """Derive path to output GFF file"""
        return os.path.join(self.output_dir, 'cgc.gff')

    def load_cgc_type(self):
        """Load and process CAZyme and CGC data to create annotation mapping dictionary"""
        try:
            # Verify files exist before attempting to read them
            if not os.path.exists(self.cazyme_overview):
                logging.error(f"CAZyme overview file not found: {self.cazyme_overview}")
                return {}
                
            if not os.path.exists(self.cgc_sig_file):
                logging.error(f"CGC signature file not found: {self.cgc_sig_file}")
                return {}
            
            # Process CAZyme overview data
            logging.info(f"Loading CAZyme data from {self.cazyme_overview}")
            df = pd.read_csv(self.cazyme_overview, sep='\t')
            
            # Ensure required columns exist
            required_cols = ['Gene ID', '#ofTools', 'Recommend Results']
            if not all(col in df.columns for col in required_cols):
                logging.error(f"Missing required columns in CAZyme overview. Found: {df.columns.tolist()}")
                return {}
            
            # Rename columns for consistency
            df = df.rename(columns={'Gene ID': 'protein_id', 'Recommend Results': 'CAZyme'})
            
            # Filter for CAZymes with sufficient tool support
            df['#ofTools'] = pd.to_numeric(df['#ofTools'], errors='coerce')
            overview_df = df[df['#ofTools'] >= 2].copy()
            overview_df['CGC_annotation'] = 'CAZyme' + '|' + overview_df['CAZyme'].astype(str)

            # Process CGC signature data
            logging.info(f"Loading CGC signature data from {self.cgc_sig_file}")
            try:
                cgc_sig_df = pd.read_csv(self.cgc_sig_file, sep='\t', usecols=[0, 2, 10], header=None, 
                                      names=['function_annotation', 'protein_id', 'type'])
                cgc_sig_df['CGC_annotation'] = cgc_sig_df['type'] + '|' + cgc_sig_df['function_annotation']
            except Exception as e:
                logging.error(f"Error reading CGC signature file: {str(e)}")
                # Try to continue with just the CAZyme data
                return overview_df.set_index('protein_id').to_dict('index')

            # Combine data from both sources
            logging.info("Combining CAZyme and CGC signature data")
            combined_df = pd.concat([overview_df[['protein_id', 'CGC_annotation']], 
                                    cgc_sig_df[['protein_id', 'CGC_annotation']]], ignore_index=True)
            combined_df = combined_df.groupby('protein_id')['CGC_annotation'].apply(lambda x: '+'.join(set(x))).reset_index()
            return combined_df.set_index('protein_id').to_dict('index')
        except Exception as e:
            logging.error(f"Error loading CGC data: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def process_gff(self):
        """Template method for processing GFF files"""
        # Create a temporary file to avoid read/write conflict
        temp_output_file = f"{self.output_gff}.temp"
        try:
            # Check if input GFF exists
            if not os.path.exists(self.input_gff):
                logging.error(f"Input GFF file not found: {self.input_gff}")
                return False
            
            # Sort GFF file
            logging.info(f"Sorting features in {self.input_gff}")
            self.sort_gff(self.input_gff, temp_output_file)
            
            # Load CGC annotation data
            logging.info("Loading CGC annotation data")
            cgc_data = self.load_cgc_type()
            
            # Process CGC data for specific formats if needed
            processed_cgc_data = self._preprocess_cgc_data(cgc_data)
            
            # Process the actual GFF file
            logging.info(f"Processing GFF file: {self.input_gff}")
            self._process_gff_format(temp_output_file, self.output_gff, processed_cgc_data)
            
            # Clean up temporary file
            if os.path.exists(temp_output_file):
                os.remove(temp_output_file)
                
            logging.info(f"Updated GFF file saved to {self.output_gff}.")
            return True
        except Exception as e:
            logging.error(f"Error processing GFF: {str(e)}")
            import traceback
            traceback.print_exc()
            if os.path.exists(temp_output_file):
                os.remove(temp_output_file)
            return False
    
    def _preprocess_cgc_data(self, cgc_data):
        """Preprocess CGC data - can be overridden by subclasses"""
        return cgc_data
    
    def _process_gff_format(self, input_file, output_file, cgc_data):
        """Process specific GFF format - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _process_gff_format method")

    def write_gff(self, record, feature, protein_id, cgc_annotation, output_file):
        """Write a feature to GFF format with protein ID and CGC annotation"""
        try:
            if not hasattr(feature, 'location') or feature.location is None:
                logging.warning(f"Feature {feature} has no location attribute")
                return

            start = feature.location.start + 1
            end = feature.location.end
            strand = '+' if feature.location.strand >= 0 else '-'
            line = f"{record.id}\t.\t{feature.type}\t{start}\t{end}\t.\t{strand}\t.\tprotein_id={protein_id};CGC_annotation={cgc_annotation}\n"
            output_file.write(line)
        except Exception as e:
            logging.error(f"Error writing GFF line: {str(e)}")
            # Continue processing other features

    def sort_gff(self, input_gff, output_gff):
        """Sort GFF features by start position"""
        try:
            if not os.path.exists(input_gff):
                raise FileNotFoundError(f"Input GFF file not found: {input_gff}")
                
            with open(input_gff) as input_file:
                records = list(GFF.parse(input_file))
            
            sorted_records = []
            for record in records:
                sorted_features = sorted(record.features, key=lambda f: (f.location.start, f.location.end))
                record.features = sorted_features
                sorted_records.append(record)
            
            with open(output_gff, 'w') as output_file:
                GFF.write(sorted_records, output_file)
        except Exception as e:
            logging.error(f"Error sorting GFF file: {str(e)}")
            raise


class NCBIEukProcessor(GFFProcessor):
    """Processor for NCBI Eukaryotic GFF format"""
    
    def _process_gff_format(self, input_file, output_file, cgc_data):
        """Process NCBI Eukaryotic GFF format"""
        try:
            with open(input_file) as in_file, open(output_file, 'w') as out_file:
                for record in GFF.parse(in_file):
                    for feature in record.features:
                        if feature.type == 'gene':
                            protein_id = 'unknown'
                            cgc_annotation = 'unknown'
                            non_mRNA_found = False
                            
                            for sub_feature in feature.sub_features:
                                if 'mRNA' not in sub_feature.type:
                                    protein_id = 'NA'
                                    Name = feature.qualifiers.get('Name', ['unknown'])[0]
                                    cgc_annotation = 'Other' + '|' + sub_feature.type
                                    non_mRNA_found = True
                                    break

                            if non_mRNA_found:
                                self.write_gff(record, feature, protein_id, cgc_annotation, out_file)
                                continue

                            for sub_feature in feature.sub_features:
                                if sub_feature.type == 'mRNA':
                                    for sub_sub_feature in sub_feature.sub_features:
                                        if sub_sub_feature.type == 'CDS':
                                            protein_id = sub_sub_feature.qualifiers.get('protein_id', ['unknown'])[0]
                                            break
                                    if protein_id != 'unknown':
                                        break

                            cgc_annotation = cgc_data.get(protein_id, {}).get('CGC_annotation', 'null')
                            self.write_gff(record, feature, protein_id, cgc_annotation, out_file)
        except Exception as e:
            logging.error(f"Error processing NCBI Eukaryotic GFF: {str(e)}")
            raise


class NCBIProkProcessor(GFFProcessor):
    """Processor for NCBI Prokaryotic GFF format"""
    
    def _process_gff_format(self, input_file, output_file, cgc_data):
        """Process NCBI Prokaryotic GFF format"""
        try:
            with open(input_file) as in_file, open(output_file, 'w') as out_file:
                for record in GFF.parse(in_file):
                    for feature in record.features:
                        if feature.type == 'gene':
                            protein_id = 'unknown'
                            cgc_annotation = 'unknown'
                            non_CDS_found = False
                            
                            for sub_feature in feature.sub_features:
                                if 'CDS' not in sub_feature.type:
                                    protein_id = 'NA'
                                    cgc_annotation = 'Other' + '|' + sub_feature.type
                                    non_CDS_found = True
                                    break

                            if non_CDS_found:
                                self.write_gff(record, feature, protein_id, cgc_annotation, out_file)
                                continue

                            for sub_feature in feature.sub_features:
                                if sub_feature.type == 'CDS':
                                    protein_id = sub_feature.qualifiers.get('protein_id', ['unknown'])[0]
                                if protein_id != 'unknown':
                                    break

                            cgc_annotation = cgc_data.get(protein_id, {}).get('CGC_annotation', 'null')
                            self.write_gff(record, feature, protein_id, cgc_annotation, out_file)
        except Exception as e:
            logging.error(f"Error processing NCBI Prokaryotic GFF: {str(e)}")
            raise


class JGIProcessor(GFFProcessor):
    """Processor for JGI GFF format"""
    
    def _preprocess_cgc_data(self, cgc_data):
        """Preprocess CGC data for JGI format"""
        # JGI uses a different protein ID format - need to extract the actual ID
        return {k.split('|')[2] if '|' in k else k: v for k, v in cgc_data.items()}
    
    def _process_gff_format(self, input_file, output_file, cgc_data):
        """Process JGI GFF format"""
        try:

            #use protein ID (the third column by "|") and original ID mapping
            original_id_mapping = {}
            if os.path.exists(self.input_total_faa):
                for record in SeqIO.parse(self.input_total_faa, 'fasta'):
                    original_id = record.id
                    simplified_id = original_id.split('|')[2] if '|' in original_id else original_id
                    original_id_mapping[simplified_id] = original_id
            else:
                logging.error(f"Input protein sequences file not found: {self.input_total_faa}")

            with open(input_file) as in_file, open(output_file, 'w') as out_file:
                for record in GFF.parse(in_file):
                    for feature in record.features:
                        if feature.type == 'gene':
                            protein_id = feature.qualifiers.get("proteinId", ["unknown"])[0]
                            simplified_id = protein_id.split('|')[2] if '|' in protein_id else protein_id
                            cgc_annotation = cgc_data.get(simplified_id, {}).get('CGC_annotation', 'null')
                            original_protein_id = original_id_mapping.get(simplified_id, protein_id)
                            self.write_gff(record, feature, original_protein_id, cgc_annotation, out_file)
        except Exception as e:
            logging.error(f"Error processing JGI GFF: {str(e)}")
            raise


class ProdigalProcessor(GFFProcessor):
    """Processor for Prodigal GFF format"""
    
    def _process_gff_format(self, input_file, output_file, cgc_data):
        """Process Prodigal GFF format"""
        try:
            with open(input_file) as in_file, open(output_file, 'w') as out_file:
                for record in GFF.parse(in_file):
                    for feature in record.features:
                        protein_id = feature.qualifiers.get("ID", ["unknown"])[0]
                        cgc_annotation = cgc_data.get(protein_id, {}).get('CGC_annotation', 'null')
                        self.write_gff(record, feature, protein_id, cgc_annotation, out_file)
        except Exception as e:
            logging.error(f"Error processing Prodigal GFF: {str(e)}")
            raise


def get_gff_processor(config: GFFConfig):
    """Factory function to get appropriate GFF processor based on GFF type"""
    gff_type = config.gff_type
    if gff_type == 'NCBI_euk':
        return NCBIEukProcessor(config)
    elif gff_type == 'NCBI_prok':
        return NCBIProkProcessor(config)
    elif gff_type == 'JGI':
        return JGIProcessor(config)
    elif gff_type == 'prodigal':
        return ProdigalProcessor(config)
    else:
        raise ValueError(f"Unsupported GFF type: {gff_type}")