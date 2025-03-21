#!/user/bin/Rscript
options(repos=structure(c(CRAN="https://mirrors.tuna.tsinghua.edu.cn/CRAN/")))  
if (!requireNamespace("optparse", quietly = TRUE))
  # install.packages("optparse",repos="https://mirrors.tuna.tsinghua.edu.cn/CRAN/")
  install.packages("optparse")
library(optparse)
option_list <- list(
  make_option(c("-i", "--input"), type = "character", default = FALSE,
              help = "You input file "),
  make_option(c("-s", "--species"), type = "character", default = FALSE,
              help = "You species in [human,mouse] "), 
  make_option(c("-o", "--outputDir"), type = "character", default = FALSE,
              help = "Your outputDir "),
  make_option(c("-p", "--path"), type = "character", default = FALSE,
              help = "You script path ")
)
opt_parser = OptionParser(option_list = option_list);
opt = parse_args(opt_parser);

# 1.library package
library(modelr)
library(magrittr)
library(tidyverse)
library(legendBaseModel)
options(na.action = na.warn)
# vignette("dplyr" ,package = "dplyr")
# 2.global variables

# input_  <- clean_path(opt$input)
# species_ <- opt$species
# output_ <-clean_path(opt$outputDir)
# fun_path_ <-clean_path(opt$path)

# run xucaixia's DEA
input_  <- clean_path("./1-output/2022/07_xucaixia/xucaixia/input/")
species_ <- "human"
output_ <-clean_path("./1-output/2022/07_xucaixia/xucaixia/DEanalysis_0705/")
fun_path_ <- clean_path("./0-pipeline/legend_ONT-ISO_V1/")

## run liuqiang's DEA
input_  <- clean_path("./1-output/2022/06_liuqiang/liuqiang/input/")
species_ <- "mouse"
output_ <-clean_path("./1-output/2022/06_liuqiang/liuqiang/liuqiang_ONT-ISO_result/")
fun_path_ <- clean_path("./0-pipeline/legend_ONT-ISO_V1/")

## run zhangzhouyi's DEA
input_  <-  clean_path("./1-output/20231030_zhangzhouyi/00_inputs/")
species <- choose_species("human")
output_ <- clean_path("./1-output/20231030_zhangzhouyi/01_output")
fun_path_ <-  clean_path("./0-pipeline/legend_ONT-ISO_V1/")

## run zhangxuedi's DEA
input_  <-  clean_path("./1-output/20241014_zhangxuedi/00_inputs/")
species <- choose_species("mouse")
output_ <- clean_path("./1-output/20241014_zhangxuedi/01_output")
fun_path_ <-  clean_path("./0-pipeline/legend_ONT-ISO_V1/")

## run zhanghongyang's DEA
input_  <-  clean_path("./1-output/20250107_mm_2sample/00_inputs/")
species <- choose_species("mouse")
output_ <- clean_path("./1-output/20250107_mm_2sample/01_output")
fun_path_ <-  clean_path("./0-pipeline/legend_ONT-ISO_V1/")

## run zhanghongyang's DEA
input_  <-  clean_path("./1-output/20250107_mm_2sample/00_inputs/")
species <- choose_species("mouse")
output_ <- clean_path("./1-output/20250107_mm_2sample/01_output")
fun_path_ <-  clean_path("./0-pipeline/legend_ONT-ISO_V1/")

## run leiyumei's DEA
input_  <-  clean_path("./1-output/20250310_mm_4sample/00_inputs/")
species <- choose_species("mouse")
output_ <- clean_path("./1-output/20250310_mm_4sample/01_output")
fun_path_ <-  clean_path("./0-pipeline/legend_ONT-ISO_V1/")

# 1.add analysis function
# BiocManager::install("ggtree", force = TRUE)
source(paste0(fun_path_, "/fun/basis_fun.R"), encoding = "UTF-8")

one_step_load_data_fun <- function() {

    if (dir.exists(output_) == FALSE) {dir.create(output_)}
    if (dir.exists(paste0(output_, "/1.gene&isoform_expression")) == FALSE) {dir.create(paste0(output_, "/1.gene&isoform_expression"))}

    sampleDesign <- list.files(input_, pattern = "sampleSheet.csv$", full.names = TRUE) %>%
        read.table(., header=TRUE, sep=",", fill = NA)

    tpm <- list.files(input_, pattern = "counts_matrix.tsv.tpm.tsv$", full.names = TRUE) %>%
        read.table(., header=TRUE, row.names = 1, sep="\t", fill = NA) %>%
        dplyr::select(sampleDesign$raw_name) %>%
        dplyr::rename(setNames(sampleDesign$raw_name, paste0(sampleDesign$rename_name, "_tpm"))) %>% 
        rownames_to_column()

    all_data <- list.files(input_, pattern = "counts_matrix.tsv$", full.names = TRUE) %>%
        read.table(., header=TRUE, row.names = 1, sep="\t", fill = NA) %>% 
        dplyr::select(sampleDesign$raw_name) %>%
        dplyr::rename(setNames(sampleDesign$raw_name, sampleDesign$rename_name)) %>% 
        rownames_to_column() %>% 
        left_join(., tpm, by=c("rowname"="rowname")) %>%
        tidyr::separate(rowname, c("iso", "gene_id"), sep = "[_]") %>%
        dplyr::filter(str_detect(.$gene_id, "^ENS"))

    gene_allRNA <- all_data %>% 
        dplyr::select(-iso) %>% 
        dplyr::group_by(gene_id) %>%
        dplyr::summarise(across(where(is.numeric), ~sum(.x, na.rm = TRUE))) %>%
        gene_id_trans(organism = species) %T>% 
        write.table(., paste0(output_, "/1.gene&isoform_expression/ONT-ISO_filtered_gene.tsv"), 
            sep="\t", row.names = T, quote = FALSE) %>% 
        dplyr::select(sampleDesign$rename_name)

    isoform_allRNA <- all_data %>%
        dplyr::filter(str_detect(.$iso, "^ENS")) %>% 
        tidyr::separate(iso, c("iso", "name"), sep = "[-]") %>% 
        dplyr::select(-name) %>% 
        distinct(iso, .keep_all = T) %>%
        gene_id_trans(organism = species, dup = F)  %T>% 
        write.table(.,  paste0(output_, "/1.gene&isoform_expression/ONT-ISO_filtered_isoform.tsv"),
            sep="\t", row.names = T, quote = FALSE) %>% 
        dplyr::select(sampleDesign$rename_name)
    
    allRNA_tappas <- all_data %>%
        dplyr::filter(str_detect(.$iso, "^ENS")) %>% 
        tidyr::separate(iso, c("iso", "name"), sep = "[-]") %>% 
        dplyr::select(-c("name","gene_id")) %>% 
        distinct(iso, .keep_all = T)  %>% 
        column_to_rownames(., var = "iso") %>% 
        dplyr::select(!ends_with("tpm")) %T>% 
        write.table(.,  paste0(output_, "/1.gene&isoform_expression/ONT-ISO_filtered_tappas.tsv"),
            sep="\t", row.names = T, quote = FALSE) 
    
    sample_tappas <- sampleDesign %>% 
        mutate(group = case_when(
            str_detect(rename_name, "^control") ~ "CONTROL",
            TRUE ~ "CASE")) %>%
        dplyr::rename(., sample = rename_name) %>%
        dplyr::select(sample, group) %T>% 
        write.table(.,  paste0(output_, "/1.gene&isoform_expression/tappas_sample.tsv"),
            sep="\t", row.names = F, quote = FALSE)


    data_list <- list(gene_matrix=gene_allRNA, isoform_matrix=isoform_allRNA)

    return(data_list)
}

one_step_de_fun <- function(gene_matrix, isoform_matrix = NA, species = "hsa", prefix) { 
    # parameter
    # prefix <- output_
    # gene_matrix <- load_data$gene_matrix
    library(ComplexHeatmap)
    if (dir.exists(paste0(prefix, "/2.gene&isoform_DE")) == FALSE) {
        dir.create(paste0(prefix, "/2.gene&isoform_DE"))
        prefix_gene <- paste0(prefix, "/2.gene&isoform_DE/gene")
        dds_gene <- gene_matrix %>% 
            build_S4_1() %>% 
            data_filter_2() %>% 
            DEA_deseq2_4()
        res_gene <- dds_gene %>%
            DEA_result_5(prefix = prefix_gene)
        # polt vocano and heatmap
        res_gene %>% build_senior_volcano_list_1.0() %>% 
            plot_senior_vocano_1.1(prefix = prefix_gene)
        vsd_gene <- gene_matrix %>% 
            build_S4_1() %>%
            data_filter_2() %>%
            data_normalized_3()
        gene_pathway <- as.data.frame(res_gene) %>% 
            filter(pvalue <=0.05) %>% 
            rownames()
        heatmap_gene <- vsd_gene %>% 
            built_senior_matrix_1.0(gene_list = gene_pathway) %>% 
            Heatmap(., name = "mat",
                show_column_names = T,
                show_row_names = F,
                row_split = 2,
                row_title = NULL,
                cluster_column_slices = T
            )
        pdf(paste0(prefix_gene, "_heatmap.pdf"), width = 8, height = 8)
        ComplexHeatmap::draw(heatmap_gene)
        dev.off()
        png(paste0(prefix_gene, "_heatmap.png"), width = 480, height = 480)
        ComplexHeatmap::draw(heatmap_gene)
        dev.off()
        # polt isoform volcano and heatmap
        # if (is.na(isoform_matrix) == FALSE) {
            prefix_isoform <- paste0(prefix, "/2.gene&isoform_DE/isoform")
            # isoform_matrix <- load_data$isoform_matrix
            # isoform_matrix <- read.table(paste0(output_, "/1.gene&isoform_expression/ONT-ISO_filtered_isoform.tsv"), header = T) %>% 
            #     dplyr::select(!ends_with("tpm"))
            dds_isoform <- isoform_matrix %>% 
                build_S4_1() %>% 
                data_filter_2() %>% 
                DEA_deseq2_4()
            
            res_isoform <- dds_isoform %>%
                DEA_result_5(prefix = prefix_isoform)
            # polt vocano
            res_isoform %>% build_senior_volcano_list_1.0(isoform = T) %>% 
                plot_senior_vocano_1.1(prefix = prefix_isoform)

            vsd_isoform <- isoform_matrix %>% 
                build_S4_1() %>%
                data_filter_2() %>%
                data_normalized_3()
            
            pathway_isoform <- as.data.frame(res_isoform) %>% 
                filter(pvalue <=0.05) %>% 
                rownames_to_column() %>%
                tidyr::separate(., rowname, into=c("gene", "iso_id"), sep="_", remove = F) %>%
                .$gene
            # pathway_isoform <- read.csv(paste0(output_, "/2.gene&isoform_DE/isoform_desq2_p0.05.csv"), header = T, row.names = 1) %>% 
            #     rownames_to_column() %>%
            #     tidyr::separate(., rowname, into=c("gene", "iso_id"), sep="_", remove = F) %>%
            #     .$gene
            heatmap_isoform <- vsd_isoform %>% 
                built_senior_matrix_1.0(gene_list = pathway_isoform, isoform = T) %>% 
                Heatmap(., name = "mat",
                        show_column_names = T,
                        show_row_names = F,
                        row_title = NULL,
                        cluster_column_slices = T
                    ) 
            # prefix_isoform <- paste0(output_, "/2.gene&isoform_DE/isoform")

            pdf(paste0(prefix_isoform, "_heatmap.pdf"), width = 10, height = 12)
            ComplexHeatmap::draw(heatmap_isoform)
            dev.off()
            png(paste0(prefix_isoform, "_heatmap.png"), width = 600, height = 720)
            ComplexHeatmap::draw(heatmap_isoform)
            dev.off()
        # }
    }
    # polt GOKEGG
    res_gene %>% build_enrichment_gene_1(., organism = species) %>% 
        GOKEGG_enrishment_1(., prefix =paste0(prefix, "/gene"))
}
# 2.run DEA

load_data <- one_step_load_data_fun()

one_step_de_fun(
    gene_matrix = load_data$gene_matrix, 
    isoform_matrix = load_data$isoform_matrix, 
    species = species, 
    prefix = output_)

input_path <- paste0(output_, "/2.gene&isoform_DE/gene_deseq2_p0.05.csv")
output_path <- paste0(output_, "/3.GO&KEGG&GSEA")
species <- "mmu"
auto_enrichment(input_path, output_path, species)

