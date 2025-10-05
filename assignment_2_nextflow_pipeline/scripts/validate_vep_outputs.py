#!/usr/bin/env python3
"""
validate_vep_outputs.py
Run quick post-run validation for Nextflow VEP annotated VCFs.

Outputs a CSV report to:
  ~/clovertex_assignment/assignment_2_nextflow_pipeline/results/validation_report_nextflow.csv
"""

import os
import csv
import gzip
import argparse
from pathlib import Path

# --- helpers ---
def open_text(path):
    if str(path).endswith('.gz'):
        return gzip.open(path, 'rt')
    return open(path, 'r')

def count_non_header(path):
    cnt = 0
    with open_text(path) as fh:
        for line in fh:
            if not line.startswith('#'):
                cnt += 1
    return cnt

def find_annotated_path(project_dir, sample_name):
    # try likely places for annotated vcf
    candidates = [
        project_dir / 'results' / f"{sample_name}_vep_output.vcf",
        project_dir / 'results' / f"{sample_name}_vep_output.vcf.gz",
        project_dir / f"{sample_name}_vep_output.vcf",
        project_dir / f"{sample_name}_vep_output.vcf.gz",
    ]
    for p in candidates:
        if p.exists():
            return p
    # fallback: search results folder for file that contains sample_name and 'vep_output'
    results_dir = project_dir / 'results'
    if results_dir.exists():
        for p in results_dir.iterdir():
            if sample_name in p.name and 'vep_output' in p.name and p.suffix in ('.vcf', '.gz', '.vcf.gz'):
                return p
    return None

def analyze_annotated_vcf(path):
    stats = {
        'annotated_total_records': 0,
        'vcf_records_with_CSQ': 0,
        'csq_header_present': False,
        'annotated_unique_variants_count': 0,
        'csq_entries_total': 0,
        'variants_with_multiple_csq_entries': 0
    }
    per_variant_csq = {}
    unique_variants = set()

    with open_text(path) as fh:
        for line in fh:
            if line.startswith('##INFO=<ID=CSQ'):
                stats['csq_header_present'] = True
            if not line.startswith('#'):
                cols = line.rstrip('\n').split('\t')
                if len(cols) < 8:
                    continue
                chrom, pos, vid, ref, alt, qual, flt, info = cols[:8]
                stats['annotated_total_records'] += 1
                if 'CSQ=' in info:
                    stats['vcf_records_with_CSQ'] += 1
                    key = (chrom, pos, ref, alt)
                    unique_variants.add(key)
                    csq_data = info.split('CSQ=')[1].split(';')[0]
                    entries = csq_data.split(',')
                    n = len(entries)
                    stats['csq_entries_total'] += n
                    per_variant_csq[key] = per_variant_csq.get(key, 0) + n

    stats['annotated_unique_variants_count'] = len(unique_variants)
    stats['variants_with_multiple_csq_entries'] = sum(1 for v,n in per_variant_csq.items() if n > 1)
    return stats

# --- main ---
def main():
    p = argparse.ArgumentParser(description="Validate VEP annotated VCFs from Nextflow run")
    p.add_argument('--project', default=os.path.expanduser('~/clovertex_assignment/assignment_2_nextflow_pipeline'),
                   help='Path to assignment_2_nextflow_pipeline folder')
    p.add_argument('--manifest', default='samples.csv', help='Manifest CSV relative to project folder')
    args = p.parse_args()

    project_dir = Path(os.path.expanduser(args.project)).resolve()
    manifest_path = project_dir / args.manifest
    results_dir = project_dir / 'results'
    results_dir.mkdir(parents=True, exist_ok=True)

    if not manifest_path.exists():
        print("ERROR: manifest not found:", manifest_path)
        return

    report_rows = []
    with open(manifest_path) as mh:
        header = mh.readline().strip().split(',')
        # simple CSV reading assuming header as: sample_name,vcf_path,...
        mh.seek(0)  # rewind
        import csv
        reader = csv.DictReader(open(manifest_path))
        for row in reader:
            sample = row.get('sample_name') or row.get('sample') or row.get('name')
            raw_vcf = row.get('vcf_path') or row.get('vcf') or ''
            raw_vcf = os.path.expanduser(raw_vcf)
            raw_vcf = Path(raw_vcf) if raw_vcf else None

            annotated = find_annotated_path(project_dir, sample)
            rec = {
                'sample': sample,
                'raw_vcf_path': str(raw_vcf) if raw_vcf else '',
                'annotated_vcf_path': str(annotated) if annotated else ''
            }

            # raw counts
            if raw_vcf and raw_vcf.exists():
                rec['vcf_total_records_raw'] = count_non_header(raw_vcf)
            else:
                rec['vcf_total_records_raw'] = None

            if annotated and annotated.exists():
                ann_stats = analyze_annotated_vcf(annotated)
                rec.update(ann_stats)
            else:
                rec.update({
                    'annotated_total_records': None,
                    'vcf_records_with_CSQ': None,
                    'csq_header_present': False,
                    'annotated_unique_variants_count': None,
                    'csq_entries_total': None,
                    'variants_with_multiple_csq_entries': None
                })

            # quick checks / notes
            notes = []
            if rec['vcf_total_records_raw'] is not None and rec['annotated_total_records'] is not None:
                if rec['vcf_total_records_raw'] != rec['annotated_total_records']:
                    notes.append('raw_vs_annotated_count_mismatch')
            if annotated is None:
                notes.append('annotated_not_found')
            if rec['csq_header_present'] is False:
                notes.append('CSQ_header_missing')

            rec['note'] = ';'.join(notes) if notes else ''
            report_rows.append(rec)

    # write CSV
    out_csv = results_dir / 'validation_report_nextflow.csv'
    keys = ['sample','raw_vcf_path','annotated_vcf_path',
            'vcf_total_records_raw','annotated_total_records','vcf_records_with_CSQ',
            'csq_header_present','annotated_unique_variants_count','csq_entries_total',
            'variants_with_multiple_csq_entries','note']
    with open(out_csv, 'w', newline='') as outfh:
        writer = csv.DictWriter(outfh, fieldnames=keys)
        writer.writeheader()
        for r in report_rows:
            writer.writerow({k: r.get(k, '') for k in keys})

    print("Validation report written to:", out_csv)
    # print summary
    for r in report_rows:
        print(f"{r['sample']}: raw={r['vcf_total_records_raw']} ann={r['annotated_total_records']} CSQ_lines={r['vcf_records_with_CSQ']} notes={r['note']}")

if __name__ == '__main__':
    main()
