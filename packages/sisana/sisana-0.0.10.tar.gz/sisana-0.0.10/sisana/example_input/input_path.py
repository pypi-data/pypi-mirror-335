import os

def find_example_paths():
    '''
    Description:
        This code finds the paths to the files in this folder so files can be copied to user's current working directory
     
    Parameters:
    -----------
        - None
    
    Returns:
    -----------
        - list of paths to be copied in main sisana script
    '''
    
    fnames = ["BRCA_TCGA_20_LumA_LumB_samps_5000_genes_exp.tsv",
              "BRCA_TCGA_20_LumA_LumB_samps_mapping.csv",
              "BRCA_TCGA_400_LumA_LumB_samps_mapping.csv",
              "BRCA_TCGA_400_LumA_LumB_samps_survival_data.csv",
              "lioness_df_indegree_3_decimal_places_400_LumA_LumB_samps.csv",
              "genes.txt",
              "motif_tcga_brca.tsv",
              "params.yml",
              "ppi_tcga_brca.tsv",
              "c2.cp.kegg_medicus.v2023.2.Hs.symbols.gmt",
              "c2.cp.reactome.v2023.2.Hs.symbols.gmt",
              "Hallmark.v2023.2.Hs.symbols.gmt",
              "top_50_genes_heatmap.txt"]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    files = [dir_path + "/" + x for x in fnames]
    return(files)