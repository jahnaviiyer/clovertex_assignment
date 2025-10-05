nextflow.enable.dsl=2
params.input = "samples.csv"

workflow {
    Channel
        .fromPath(params.input)
        .splitCsv(header: true)
        .map { row -> row }
        .view()
}
