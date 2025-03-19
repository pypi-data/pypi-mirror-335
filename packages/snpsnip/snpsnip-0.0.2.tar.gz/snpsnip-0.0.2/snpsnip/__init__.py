#!/usr/bin/env python3
"""
SNPSnip - Interactive VCF filtering tool

This tool provides an interactive web interface for filtering VCF files
in multiple stages, with checkpointing to allow resuming sessions.
"""

import argparse
import json
import logging
import os
import random
import subprocess
import sys
import tempfile
import threading
import shlex
import time
import csv
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory
from sklearn.decomposition import PCA
from waitress import serve


from ._version import __version__, __version_tuple__
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("snpsnip")

# Constants
DEFAULT_PORT = 2790
DEFAULT_HOST = "localhost"
STATE_FILE = "snpsnip_state.json"
TEMP_DIR = "snpsnip_temp"
SUBSET_FREQ = 0.01

class SNPSnip:
    """Main class for SNP filtering application."""
    
    def __init__(self, args):
        """Initialize with command line arguments."""
        self.args = args
        self.vcf_file = args.vcf
        self.output_dir = Path(args.output_dir)


        if args.state_file:
            self.state_file = Path(args.state_file)
        else:
            self.state_file = self.output_dir / "state.json"
        if args.temp_dir:
            self.temp_dir = Path(args.temp_dir)
        else:
            self.temp_dir = self.output_dir / "tmp"

        self.host = args.host
        self.port = args.port
        self.subset_freq = args.subset_freq
        
        # Initial filters
        self.maf = args.maf
        self.max_missing = args.max_missing
        self.min_qual = args.min_qual
        
        # State variables
        self.state = self._load_state() or {
            "stage": "init",
            "subset_vcf": None,
            "sample_stats": None,
            "variant_stats": None,
            "sample_groups": {},
            "filter_thresholds": {},
            "completed": False,
            "predefined_groups": {}
        }
        
        # Load predefined groups if provided
        if args.groups_file:
            self._load_groups_from_file(args.groups_file)
        
        # Create directories if they don't exist
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Web app
        self.app = self._create_app()
        self.server_thread = None
    
    def _load_state(self) -> Optional[Dict]:
        """Load state from state file if it exists."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse state file {self.state_file}")
                return None
        return None
    
    def _save_state(self):
        """Save current state to state file."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _load_groups_from_file(self, groups_file: str):
        """Load sample groups from a CSV or TSV file."""
        logger.info(f"Loading sample groups from {groups_file}")
        
        # Determine delimiter based on file extension
        delimiter = ',' if groups_file.lower().endswith('.csv') else '\t'
        
        groups = {}
        try:
            with open(groups_file, 'r') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                if 'sample' not in reader.fieldnames and 'group' not in reader.fieldnames:
                    logger.error(f"Groups file must contain 'sample' and 'group' columns. Found: {reader.fieldnames}")
                    return
                
                for row in reader:
                    sample = row['sample']
                    group = row['group']
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(sample)
            
            self.state["predefined_groups"] = groups
            self.state["sample_groups"] = groups.copy()
            logger.info(f"Loaded {len(groups)} groups with {sum(len(samples) for samples in groups.values())} samples")
        except Exception as e:
            logger.error(f"Error loading groups file: {e}")
    
    def _create_app(self) -> Flask:
        """Create Flask app for the web interface."""
        app = Flask(__name__, 
                   static_folder=str(Path(__file__).parent / "static"),
                   template_folder=str(Path(__file__).parent / "templates"))
        
        @app.route('/')
        def index():
            return render_template('index.html', state=self.state)
        
        @app.route('/api/state')
        def get_state():
            return jsonify(self.state)
        
        @app.route('/api/sample_stats')
        def get_sample_stats():
            if self.state["sample_stats"]:
                return jsonify(self.state["sample_stats"])
            return jsonify({"error": "Sample stats not available"}), 404
        
        @app.route('/api/variant_stats/<group>')
        def get_variant_stats(group):
            if group in self.state.get("variant_stats", {}):
                return jsonify(self.state["variant_stats"][group])
            return jsonify({"error": f"Variant stats for group {group} not available"}), 404
        
        @app.route('/api/pca')
        def get_pca():
            if "pca" in self.state:
                # Add group information if available
                if self.state.get("predefined_groups") and self.state["pca"]:
                    # Create a mapping from sample to group
                    sample_to_group = {}
                    for group, samples in self.state["predefined_groups"].items():
                        for sample in samples:
                            sample_to_group[sample] = group
                    
                    # Add group information to PCA data
                    for point in self.state["pca"]:
                        point["group"] = sample_to_group.get(point["sample"], "unassigned")
                
                return jsonify(self.state["pca"])
            return jsonify({"error": "PCA not available"}), 404
        
        @app.route('/api/submit_sample_filters', methods=['POST'])
        def submit_sample_filters():
            data = request.json
            self.state["sample_groups"] = data["groups"]
            self.state["stage"] = "sample_filtered"
            self._save_state()
            
            # Process variant stats for each group
            self._process_variant_stats()
            
            return jsonify({"success": True})
        
        @app.route('/api/submit_variant_filters', methods=['POST'])
        def submit_variant_filters():
            data = request.json
            self.state["filter_thresholds"] = data["thresholds"]
            self.state["stage"] = "ready_for_final"
            self._save_state()
            
            # Apply final filters
            self._apply_final_filters()
            
            return jsonify({"success": True, "output_files": self.state.get("output_files", [])})
        
        return app
    
    def run(self):
        """Main execution flow."""
        if self.state["stage"] == "init":
            logger.info("Starting initial processing...")
            self._create_snp_subset()
            self._compute_sample_stats()
            self._compute_pca()
            self.state["stage"] = "ready_for_sample_filtering"
            self._save_state()
        
        if self.state["stage"] == "sample_filtered":
            logger.info("Processing variant statistics...")
            self._process_variant_stats()
            self._save_state()
        
        if self.state["stage"] == "ready_for_final" and not self.state.get("completed", False):
            logger.info("Applying final filters...")
            self._apply_final_filters()
            self.state["completed"] = True
            self._save_state()
        
        # Start web server if not completed
        if not self.state.get("completed", False):
            self._start_web_server()
        else:
            logger.info("Processing completed. Output files:")
            for file in self.state.get("output_files", []):
                logger.info(f"  - {file}")
    
    def _start_web_server(self):
        """Start the web server in a separate thread."""
        def run_server():
            logger.info(f"Starting web server at http://{self.host}:{self.port}")
            serve(self.app, host=self.host, port=self.port)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        try:
            # Keep running until processing is completed
            while self.server_thread.is_alive() and not self.state.get("completed", False):
                time.sleep(1)
            
            if self.state.get("completed", False):
                logger.info("Processing completed. Shutting down server...")
                # Give a moment for any final requests to complete
                time.sleep(2)
                sys.exit(0)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            sys.exit(0)
    
    def _run_pipeline(self, cmds: List[List[str]], check: bool = True, stdout=subprocess.PIPE) -> subprocess.CompletedProcess:
        cmds = [shlex.join(c) for c in cmds]
        shellcmd = " | ".join(cmds)
        logger.info(f"Running: {shellcmd}")
        proc =  subprocess.run(shellcmd, shell=True, text=True, stdout=stdout, stderr=subprocess.PIPE)
        try:
            if check:
                proc.check_returncode()
            return proc
        except subprocess.CalledProcessError as exc:
            logger.error(proc.stderr)
            raise exc

    def _run_bcftools(self, cmd: List[str], check: bool = True, stdout=subprocess.PIPE) -> subprocess.CompletedProcess:
        """Run a bcftools command."""
        full_cmd = ["bcftools"] + cmd
        return self._run_pipeline([full_cmd,], check=check, stdout=stdout)
    
    def _create_snp_subset(self):
        """Create a random subset of SNPs passing basic filters."""
        logger.info("Creating SNP subset...")
        
        # Create initial filter string
        filters = []
        if self.maf:
            filters.append(f"MAF>{self.maf}")
        if self.max_missing:
            filters.append(f"F_MISSING<{self.max_missing}")
        if self.min_qual:
            filters.append(f"QUAL>{self.min_qual}")
        filter_str = " && ".join(filters) if filters else None
        filters = ["-i", filter_str] if filter_str else []

        filled_vcf = str(self.temp_dir / "subset_filled.vcf.gz")
        commands = [
           ["bcftools", "view", "-Ov", *filters, self.vcf_file], 
           ["awk", f'/^#/ {{print; next}} {{if (rand() < {self.subset_freq}) print}}'], 
           ["bcftools", "+fill-tags", "-o", filled_vcf, '-Oz', "--write-index", "--", "-t", "all,F_MISSING"]
        ]

        self._run_pipeline(commands)
        
        self.state["subset_vcf"] = filled_vcf
    
    def _compute_sample_stats(self):
        """Compute per-sample statistics."""
        logger.info("Computing sample statistics...")
        
        subset_vcf = self.state["subset_vcf"]
        
        # Get sample names
        samples_result = self._run_bcftools(["query", "-l", subset_vcf])
        samples = samples_result.stdout.strip().split('\n')
        
        # Compute per-sample missingness
        missing_file = self.temp_dir / "vcf_stats.txt"
        with open(missing_file, "w") as ofh:
            self._run_bcftools(["stats", "-s", "-", subset_vcf], stdout=ofh)
        
        
        # Parse stats files
        sample_stats = {sample: {"id": sample} for sample in samples}
        
        # Process missing data
        try:
            with open(missing_file, 'r') as f:
                for line in f:
                    if line.startswith("PSC"):
                        parts = line.strip().split('\t')
                        sample = parts[2]
                        nrefhom, nalthom, nhet, nts, ntv, nindel, mean_depth, nsingle, nhapref, nhapalt, nmissing = map(float, parts[3:14])
                        ncall = nrefhom + nalthom + nhet + nindel + nsingle + nhapref + nhapalt
                        missing_rate = nmissing / ncall
                        if sample in sample_stats:
                            sample_stats[sample]["missing_rate"] = missing_rate
                            sample_stats[sample]["mean_depth"] = mean_depth
        except Exception as e:
            logger.error(f"Error processing missing data: {e}")
        
        self.state["sample_stats"] = list(sample_stats.values())
    
    def _compute_pca(self):
        """Compute PCA for samples."""
        logger.info("Computing PCA...")
        
        subset_vcf = self.state["subset_vcf"]
        
        # Extract genotypes as a matrix
        geno_file = str(self.temp_dir / "genotypes.txt")
        with open(geno_file, 'w') as ofh:
            self._run_bcftools(
                ["query", "-f", "[%GT\t]\n", subset_vcf],
                check=False,
                stdout=ofh
            )
        
        # Get sample names
        samples_result = self._run_bcftools(["query", "-l", subset_vcf])
        samples = samples_result.stdout.strip().split('\n')
        
        # Parse genotype matrix
        try:
            # Read genotype data
            geno_matrix = []
            with open(geno_file, 'r') as f:
                for line in f:
                    row = []
                    for gt in line.strip().split('\t'):
                        # Convert genotype to numeric value (0, 1, 2)
                        if gt in ("0/0", "0|0"):
                            row.append(0)
                        elif gt in ("0/1", "0|1", "1|0", "1/0"):
                            row.append(1)
                        elif gt in ("1/1", "1|1"):
                            row.append(2)
                        else:
                            row.append(np.nan)  # Missing or other genotypes
                    geno_matrix.append(row)
            
            # Convert to numpy array
            geno_array = np.array(geno_matrix, dtype=float).T  # Transpose to have samples as rows
            
            # Impute missing values with mean
            for i in range(geno_array.shape[0]):
                mask = np.isnan(geno_array[i])
                if mask.any():
                    valid = ~mask
                    if valid.any():
                        geno_array[i, mask] = np.mean(geno_array[i, valid])
                    else:
                        geno_array[i, mask] = 0
            
            # Run PCA
            pca = PCA(n_components=2)
            pca_result = pca.fit_transform(geno_array)
            
            # Format PCA results
            pca_data = []
            for i, sample in enumerate(samples):
                pca_data.append({
                    "sample": sample,
                    "pc1": float(pca_result[i, 0]),
                    "pc2": float(pca_result[i, 1])
                })
            
            self.state["pca"] = pca_data
            
        except Exception as e:
            logger.error(f"Error computing PCA: {e}")
            self.state["pca"] = []
    
    def _process_variant_stats(self):
        """Process variant statistics for each sample group."""
        logger.info("Processing variant statistics for each sample group...")
        
        subset_vcf = self.state["subset_vcf"]
        sample_groups = self.state["sample_groups"]
        
        if not sample_groups:
            logger.warning("No sample groups defined")
            return
        
        self.state["variant_stats"] = {}
        
        for group_name, samples in sample_groups.items():
            logger.info(f"Processing group: {group_name} with {len(samples)} samples")
            
            # Create a temporary file with sample names
            sample_file = str(self.temp_dir / f"{group_name}_samples.txt")
            with open(sample_file, 'w') as f:
                for sample in samples:
                    f.write(f"{sample}\n")
            
            # Create a subset VCF with only these samples
            group_vcf = str(self.temp_dir / f"{group_name}_subset.vcf.gz")
            self._run_bcftools(["view", subset_vcf, "-S", sample_file, "-Oz", "--write-index", "-o", group_vcf])
            
            # Compute variant statistics
            stats = {}
            
            # Quality
            qual_file = str(self.temp_dir / f"{group_name}_qual.txt")
            with open(qual_file, 'w') as ofh:
                self._run_bcftools(["query", "-f", "%QUAL\n", group_vcf], check=False, stdout=ofh)
            
            # Depth
            depth_file = str(self.temp_dir / f"{group_name}_depth.txt")
            with open(depth_file, 'w') as ofh:
                self._run_bcftools(["query", "-f", "%INFO/DP\n", group_vcf], check=False, stdout=ofh)
            
            # Allele frequency
            af_file = str(self.temp_dir / f"{group_name}_af.txt")
            with open(af_file, 'w') as ofh:
                self._run_bcftools(["query", "-f", "%INFO/AF\n", group_vcf], check=False, stdout=ofh)
            
            # Missing rate
            missing_file = str(self.temp_dir / f"{group_name}_missing.txt")
            with open(missing_file, 'w') as ofh:
                self._run_bcftools(["query", "-f", "%F_MISSING\n", group_vcf], check=False, stdout=ofh)
            
            # Parse statistics files
            try:
                # Quality
                quals = []
                with open(qual_file, 'r') as f:
                    for line in f:
                        try:
                            quals.append(float(line.strip()))
                        except ValueError:
                            pass
                stats["qual"] = self._compute_histogram(quals)
                
                # Depth
                depths = []
                with open(depth_file, 'r') as f:
                    for line in f:
                        try:
                            depths.append(float(line.strip()))
                        except ValueError:
                            pass
                stats["depth"] = self._compute_histogram(depths)
                
                # Allele frequency
                afs = []
                with open(af_file, 'r') as f:
                    for line in f:
                        try:
                            afs.append(float(line.strip()))
                        except ValueError:
                            pass
                stats["af"] = self._compute_histogram(afs)
                
                # Missing rate
                missing_rates = []
                with open(missing_file, 'r') as f:
                    for line in f:
                        try:
                            missing_rates.append(float(line.strip()))
                        except ValueError:
                            pass
                stats["missing"] = self._compute_histogram(missing_rates)
                
                self.state["variant_stats"][group_name] = stats
                
            except Exception as e:
                logger.error(f"Error processing variant stats for group {group_name}: {e}")
        
        self.state["stage"] = "ready_for_variant_filtering"
        self._save_state()
    
    def _compute_histogram(self, values, bins=50):
        """Compute histogram for a list of values."""
        if not values:
            return {"bins": [], "counts": []}
        
        hist, bin_edges = np.histogram(values, bins=bins)
        return {
            "bins": bin_edges[:-1].tolist(),
            "counts": hist.tolist()
        }
    
    def _apply_final_filters(self):
        """Apply final filters to the full VCF file."""
        logger.info("Applying final filters to the full VCF file...")
        
        sample_groups = self.state["sample_groups"]
        filter_thresholds = self.state["filter_thresholds"]
        
        output_files = []
        
        for group_name, samples in sample_groups.items():
            logger.info(f"Processing group: {group_name}")
            
            # Create a temporary file with sample names
            sample_file = str(self.temp_dir / f"{group_name}_samples.txt")
            with open(sample_file, 'w') as f:
                for sample in samples:
                    f.write(f"{sample}\n")
            
            # Get filter thresholds for this group
            group_filters = filter_thresholds.get(group_name, {})
            filter_expressions = []
            
            if "qual" in group_filters:
                min_qual = group_filters["qual"].get("min")
                max_qual = group_filters["qual"].get("max")
                if min_qual is not None:
                    filter_expressions.append(f"QUAL>={min_qual}")
                if max_qual is not None:
                    filter_expressions.append(f"QUAL<={max_qual}")
            
            if "depth" in group_filters:
                min_depth = group_filters["depth"].get("min")
                max_depth = group_filters["depth"].get("max")
                if min_depth is not None:
                    filter_expressions.append(f"INFO/DP>={min_depth}")
                if max_depth is not None:
                    filter_expressions.append(f"INFO/DP<={max_depth}")
            
            if "af" in group_filters:
                min_af = group_filters["af"].get("min")
                max_af = group_filters["af"].get("max")
                if min_af is not None:
                    filter_expressions.append(f"INFO/AF>={min_af}")
                if max_af is not None:
                    filter_expressions.append(f"INFO/AF<={max_af}")
            
            if "missing" in group_filters:
                min_missing = group_filters["missing"].get("min")
                max_missing = group_filters["missing"].get("max")
                if min_missing is not None:
                    filter_expressions.append(f"F_MISSING>={min_missing}")
                if max_missing is not None:
                    filter_expressions.append(f"F_MISSING<={max_missing}")
            
            # Add initial filters
            if self.maf:
                filter_expressions.append(f"MAF>{self.maf}")
            if self.max_missing:
                filter_expressions.append(f"F_MISSING<{self.max_missing}")
            if self.min_qual:
                filter_expressions.append(f"QUAL>{self.min_qual}")
            
            # Combine filter expressions
            filter_str = " && ".join(filter_expressions) if filter_expressions else None
            
            # Output file path
            output_file = os.path.join(self.output_dir, f"{group_name}_filtered.vcf.gz")
            
            # Apply filters and extract samples
            filter_cmd = ["view", self.vcf_file, "-S", sample_file, "-Oz", "-o", output_file]
            if filter_str:
                filter_cmd.extend(["-i", filter_str])
            
            logger.info(f"Running filter command: {' '.join(filter_cmd)}")
            self._run_bcftools(filter_cmd)
            
            # Index the output file
            self._run_bcftools(["index", output_file])
            
            output_files.append(output_file)
        
        self.state["output_files"] = output_files
        self.state["completed"] = True
        self._save_state()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SNPSnip - Interactive VCF filtering tool", prog="snpsnip")
    
    # Input/output options
    parser.add_argument("--vcf", required=True, help="Input VCF/BCF file (must be indexed)")
    parser.add_argument("--output-dir", default=".", help="Output directory for filtered VCFs")
    parser.add_argument("--state-file", help="State file for checkpointing")
    parser.add_argument("--temp-dir", help="Directory for temporary files")
    
    # Web server options
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind the web server to")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port for the web server")
    
    # Initial filtering options
    parser.add_argument("--maf", type=float, help="Minimum minor allele frequency")
    parser.add_argument("--max-missing", type=float, help="Maximum missingness rate")
    parser.add_argument("--min-qual", type=float, help="Minimum variant quality")
    parser.add_argument("--subset-freq", type=float, default=SUBSET_FREQ, 
                       help="Fraction of SNPs to sample for interactive analysis")
    parser.add_argument("--groups-file", help="CSV or TSV file with sample and group columns for predefined groups")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.vcf):
        logger.error(f"Input VCF file not found: {args.vcf}")
        sys.exit(1)
    
    # Check if bcftools is available
    try:
        subprocess.run(["bcftools", "--version"], check=True, 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("bcftools not found. Please install bcftools and make sure it's in your PATH.")
        sys.exit(1)
    
    # Run the application
    app = SNPSnip(args)
    app.run()

if __name__ == "__main__":
    main()
