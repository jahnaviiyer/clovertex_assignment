nextflow.enable.dsl=2

// ======================
// PARAMETERS
// ======================
params.input = "${params.input ?: 'samples.csv'}"
params.outdir = "${params.outdir ?: 'results'}"

// ======================
// PROCESS: VEP ANNOTATE
// ======================
process VEP_ANNOTATE {
    tag "$sample_name"

    publishDir params.outdir, mode: 'copy'

    input:
    tuple val(sample_name), path(vcf), val(gender), val(case_control), val(assembly)

    output:
    path "${sample_name}_vep_output.vcf"

    script:
    """
    vep \
      -i ${vcf} \
      -o ${sample_name}_vep_output.vcf \
      --vcf \
      --everything \
      --database \
      --assembly ${assembly} \
      --no_stats \
      --force_overwrite
    """
}

// ======================
// WORKFLOW DEFINITION
// ======================
workflow {

    samples_ch = Channel
        .fromPath(params.input)
        .splitCsv(header:true)
        .map { row ->
            tuple(row.sample_name, file(row.vcf_path), row.gender, row.case_control, row.assembly)
        }

    VEP_ANNOTATE(samples_ch)
}

