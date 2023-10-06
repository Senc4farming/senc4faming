-- Table: public.hgmd_gen_to_check
 DROP TABLE IF EXISTS public.hdmd_gen_to_check;

CREATE TABLE IF NOT EXISTS public.gen_to_check
(
    id serial NOT NULL ,
    genid character(30) COLLATE pg_catalog."default" NOT NULL,
    check_for_update integer NOT NULL,
    date_insert date NOT NULL,
    date_update date NOT NULL,
    origin character(255) NOT NULL,
    CONSTRAINT gen_to_check_pkey PRIMARY KEY (genid,origin)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.hgmd_gen_to_check
    OWNER to tm;
	
-- Table: public.hgmd_mutation

DROP TABLE IF EXISTS public.hdmd_mutation;

CREATE TABLE IF NOT EXISTS public.hgmd_mutation
(
    id  serial NOT NULL ,
    genid character(30) COLLATE pg_catalog."default" NOT NULL,
    mutation character(30) COLLATE pg_catalog."default" NOT NULL,
    json_info json,
    date_insert date NOT NULL,
    date_update date NOT NULL,
    CONSTRAINT hgmd_mutation_pkey PRIMARY KEY (genid, mutation)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.hgmd_mutation
    OWNER to tm;

-- Table: public.hgmd_mutation_detail

DROP TABLE IF EXISTS public.hgmd_mutation_detail;

CREATE TABLE IF NOT EXISTS public.hgmd_mutation_detail
(
    id serial NOT NULL ,
    id_mutation integer NOT NULL,
    accession_number character(30) COLLATE pg_catalog."default" NOT NULL,
    mutation_type character(30) COLLATE pg_catalog."default" NOT NULL,
	search_id character(30),
    json_info json,
    date_insert date NOT NULL,
    date_update date NOT NULL,
    CONSTRAINT hgmd_mutation_detail_pkey PRIMARY KEY (search_id,id_mutation,accession_number, mutation_type)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.hgmd_mutation_detail
    OWNER to tm;
ALTER TABLE hgmd_mutation_detail
  
  ADD CONSTRAINT hgmd_mutation_detail_pkey PRIMARY KEY (id,id_mutation,accession_number, mutation_type)
-- Table: public.loginuser

DROP TABLE IF EXISTS public.loginuser;

CREATE TABLE IF NOT EXISTS public.loginuser
(
     id serial NOT NULL ,
    user_name character(30) COLLATE pg_catalog."default" NOT NULL,
    password character(30) COLLATE pg_catalog."default" NOT NULL,
    date_insert date NOT NULL,
    date_update date NOT NULL,
    CONSTRAINT loginuser_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.loginuser
    OWNER to tm;


DROP TABLE IF EXISTS public.lovd_basic_info;

CREATE TABLE IF NOT EXISTS public.lovd_basic_info
(
    id serial not null,
    title character(200),
    link_href character(200),
    lovd_id  character(200),
    author character(200),
    contributor character(200),
    date_published   date NOT NULL,
    date_updated_lovd date NOT NULL,
    content_gene_id character(200),
    content_entrez_id character(200),
    content_symbol character(200),
    content_name character(200),
    content_chromosome_location character(200),
    content_position_start character(200),
    content_position_end character(200),
    content_refseq_genomic character(200),
    content_refseq_mrna character(200),
    content_refseq_build character(200),
    date_insert date NOT NULL,
    date_update date NOT NULL,
    CONSTRAINT lovd_basic_info_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.lovd_basic_info
    OWNER to tm;


DROP TABLE IF EXISTS public.lovd_variant_info;

CREATE TABLE IF NOT EXISTS public.lovd_variant_info
(
    id serial not null,
    basic_info_id integer,
    Effect  character(200),
    Reported  character(200),
    Exon  character(200),
    cDNA character(200),
    RNA_change  character(200),
    Protein  character(200),
    Classification_method  character(200),
    Clinical_classification  character(200),
    DNA_change_hg19 character(200),
    DNA_change_hg38  character(200),
    Published_as  character(200),
    ISCN  character(200),
    DB_ID character(200),
    Variant_remarks  character(200),
    Reference  character(200),
    ClinVar_ID  character(200),
    dbSNP_ID  character(200),
    Origin  character(200),
    Segregation  character(200),
    Frequency  character(200),
    Re_site  character(200),
    VIP  character(200),
    Methylation  character(200),
    data_Owner  character(200),
    date_insert date NOT NULL,
    date_update date NOT NULL,
    CONSTRAINT lovd_variant_info_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.lovd_variant_info
    OWNER to tm;


DROP TABLE IF EXISTS public.brca_basic_info;

CREATE TABLE IF NOT EXISTS public.brca_basic_info
(
    id serial not null,
    title character(200),
    date_insert date NOT NULL,
    date_update date NOT NULL,
    CONSTRAINT brca_basic_info_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.brca_basic_info
    OWNER to tm;

DROP TABLE IF EXISTS public.brca_main_info;

CREATE TABLE IF NOT EXISTS public.brca_main_info
( 
	id serial not null,
	basic_info_id integer, 
	id_brca integer, 
	Gene_Symbol varchar(100), 
	Reference_Sequence varchar(100), 
	HGVS_cDNA varchar(100), 
	BIC_Nomenclature varchar(100), 
	HGVS_Protein varchar(100), 
	HGVS_RNA varchar(100), 
	Protein_Change varchar(100), 
	Allele_Frequency varchar(100), 
	Max_Allele_Frequency varchar(100), 
	Genomic_Coordinate_hg38 varchar(100), 
	Hg38_Start varchar(100), 
	Hg38_End varchar(100), 
	Hg37_Start varchar(100), 
	Hg37_End varchar(100), 
	Genomic_Coordinate_hg37 varchar(100), 
	Genomic_HGVS_38 varchar(100), 
	Genomic_HGVS_37 varchar(100), 
	Source_URL varchar(2000), 
	Discordant varchar(100), 
	Synonyms varchar(2000), 
	Pathogenicity_expert varchar(100), 
	Pathogenicity_all varchar(100), 
	Chr varchar(100), 
	Pos varchar(100), 
	Ref varchar(100), 
	Alt varchar(100), 
	Polyphen_Prediction varchar(100), 
	Polyphen_Score varchar(100), 
	Sift_Score varchar(100), 
	Sift_Prediction varchar(100), 
	BX_ID_ENIGMA_BRCA12_Functional_Assays varchar(100), 
	BX_ID_ENIGMA varchar(100), 
	BX_ID_LOVD varchar(1000), 
	BX_ID_ESP varchar(100), 
	BX_ID_BIC varchar(1000), 
	BX_ID_ClinVar varchar(1000), 
	BX_ID_1000_Genomes varchar(100), 
	BX_ID_ExAC varchar(100), 
	BX_ID_exLOVD varchar(100), 
	BX_ID_GnomAD varchar(100), 
	BX_ID_Findlay_BRCA1_Ring_Function_Scores varchar(100), 
	BX_ID_GnomADv3 varchar(100), 
	VR_ID varchar(100), 
	Mupit_Structure_id varchar(100), 
	CA_ID varchar(100), 
	BayesDel_nsfp33a_noAF varchar(100), 
	Data_Release_id varchar(100), 
	Variant_in_ENIGMA boolean, 
	Variant_in_ClinVar boolean, 
	Variant_in_1000_Genomes boolean, 
	Variant_in_ExAC boolean, 
	Variant_in_LOVD boolean, 
	Variant_in_BIC boolean, 
	Variant_in_ESP boolean, 
	Variant_in_exLOVD boolean, 
	Variant_in_Findlay_BRCA1_Ring_Function_Scores boolean, 
	Variant_in_ENIGMA_BRCA12_Functional_Assays boolean, 
	Variant_in_GnomAD boolean, 
	Variant_in_GnomADv3 boolean,
	Source varchar(100), 
	URL_ENIGMA varchar(100), 
	Condition_ID_type_ENIGMA varchar(100), 
	Condition_ID_value_ENIGMA varchar(100), 
	Condition_category_ENIGMA varchar(100), 
	Clinical_significance_ENIGMA varchar(100), 
	Date_last_evaluated_ENIGMA varchar(100), 
	Assertion_method_ENIGMA varchar(100), 
	Assertion_method_citation_ENIGMA varchar(100), 
	Clinical_significance_citations_ENIGMA varchar(100), 
	Comment_on_clinical_significance_ENIGMA varchar(100), 
	Collection_method_ENIGMA varchar(100), 
	Allele_origin_ENIGMA varchar(100), 
	ClinVarAccession_ENIGMA varchar(100), 
	Clinical_Significance_ClinVar varchar(100), 
	Date_Last_Updated_ClinVar varchar(100), 
	Submitter_ClinVar varchar(2000), 
	SCV_ClinVar varchar(100), 
	Allele_Origin_ClinVar varchar(100), 
	Method_ClinVar varchar(100), 
	Functional_analysis_technique_LOVD varchar(100), 
	Functional_analysis_result_LOVD varchar(100), 
	Variant_frequency_LOVD varchar(100), 
	Variant_haplotype_LOVD varchar(100), 
	HGVS_cDNA_LOVD varchar(100), 
	HGVS_protein_LOVD varchar(100), 
	Individuals_LOVD varchar(100), 
	Variant_effect_LOVD varchar(100), 
	Genetic_origin_LOVD varchar(100), 
	RNA_LOVD varchar(100), 
	Submitters_LOVD varchar(2000), 
	Created_date_LOVD varchar(100), 
	Edited_date_LOVD varchar(100), 
	DBID_LOVD varchar(100), 
	Remarks_LOVD varchar(100), 
	Classification_LOVD varchar(100),
	date_insert date NOT NULL, 
	date_update date NOT NULL, 
 CONSTRAINT brca_main_info_pkey PRIMARY KEY (id)
) 
 
TABLESPACE pg_default; 
CREATE UNIQUE INDEX idx_brca_main_info_b_idbr
ON brca_main_info(basic_info_id, id_brca);
ALTER TABLE IF EXISTS public.brca_main_info 
 OWNER to tm; 




DROP TABLE IF EXISTS public.pandrugs_basic_info;

CREATE TABLE IF NOT EXISTS public.pandrugs_basic_info
(
    id serial not null,
    title character(200),
    date_insert date NOT NULL,
    date_update date NOT NULL,
    CONSTRAINT pandrugs_basic_info_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.pandrugs_basic_info
    OWNER to tm;

DROP TABLE IF EXISTS public.pandrugs_gene_interaction_info;

CREATE TABLE IF NOT EXISTS public.pandrugs_gene_interaction_info
(
    id serial not null,
    basic_info_id integer, 
    gene character(200),
    date_insert date NOT NULL,
    date_update date NOT NULL,
    CONSTRAINT pandrugs_gene_interaction_info_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.pandrugs_gene_interaction_info
    OWNER to tm;

DROP TABLE IF EXISTS public.pandrugs_drugInteraction_info;

CREATE TABLE IF NOT EXISTS public.pandrugs_drugInteraction_info
( 
	id serial not null,
	basic_info_id integer, 
	standardDrugName varchar(200),
    showDrugName varchar(200),
    target_value varchar(200), 
 CONSTRAINT pandrugs_drugInteraction_info_pkey PRIMARY KEY (id)
) 
 
TABLESPACE pg_default; 
CREATE UNIQUE INDEX idx_pandrugs_drugInteraction_info
ON pandrugs_drugInteraction_info(standardDrugName, showDrugName,target_value);
ALTER TABLE IF EXISTS public.pandrugs_drugInteraction_info_pkey 
 OWNER to tm; 

DROP TABLE IF EXISTS public.pandrugs_indirectGene_info;

CREATE TABLE IF NOT EXISTS public.pandrugs_indirectGene_info
(
    id serial not null,
	drugInteraction_id integer, 
    gene character(200),
    date_insert date NOT NULL,
    date_update date NOT NULL,
    CONSTRAINT pandrugs_indirectGene_info_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.pandrugs_indirectGene_info
    OWNER to tm;

DROP TABLE IF EXISTS public.pharmgkb_genes;     
                                                               
CREATE TABLE IF NOT EXISTS public.pharmgkb_genes
(                                                              
	id serial not null,   
	PharmGKBAccessionId      varchar(50) ,  
	NCBIGeneID               varchar(30) ,  
	HGNCID                   varchar(40) ,  
	EnsemblId                varchar(300),  
	Name_val                     varchar(300),  
	Symbol                   varchar(40) ,  
	AlternateNames           varchar(600),  
	AlternateSymbols                varchar(200),  
	IsVIP                    varchar(100) , 
	HasVariantAnnotation     varchar(100) ,   
	Crossreferences         text,
	HasCPICDosingGuideline          varchar(30),    
	Chromosome               varchar(50),    
	ChromosomalStartGRCh37   varchar(90),    
	ChromosomalStopGRCh37   varchar(90),    
        ChromosomalStartGRCh38         varchar(90),    
        ChromosomalStopGRCh38          varchar(90),    
        CONSTRAINT pharmgkb_genes_info_pkey PRIMARY KEY (id)
        )
                                                                                                                                           
       TABLESPACE pg_default;                                                        
       CREATE INDEX idx_pharmgkb_genes_PharmGKBAccessionId                         
       ON pharmgkb_genes(PharmGKBAccessionId);
       ALTER TABLE IF EXISTS public.pharmgkb_genes_info_pkey               
        OWNER to tm;                                                                 
DROP TABLE IF EXISTS public.pharmgkb_relationships;     
                                                               
CREATE TABLE IF NOT EXISTS public.pharmgkb_relationships
(                                                              
	id serial not null,   
	Entity1_id varchar(20),
	Entity1_name  varchar(100),
	Entity1_type  varchar(20),
	Entity2_id  varchar(20),
	Entity2_name  varchar(100),
	Entity2_type  varchar(20),
	Evidence  varchar(200),
	Association  varchar(20),
	PK  varchar(20),
	PD  varchar(20),
	PMIDs  text,
        CONSTRAINT pharmgkb_relationships_info_pkey PRIMARY KEY (id)
        )
                                                                                                                                           
       TABLESPACE pg_default;                                                        
       CREATE INDEX idx_pharmgkb_relationships_Entity1_id                       
       ON pharmgkb_relationships(Entity1_id);
       ALTER TABLE IF EXISTS public.pharmgkb_relationships_info_pkey               
        OWNER to tm;   
		
DROP TABLE IF EXISTS public.pharmgkb_phenotypes;     
                                                               
CREATE TABLE IF NOT EXISTS public.pharmgkb_phenotypes
(                                                              
	id serial not null,   
	PharmGKBAccessionId varchar(100),
	Name_val varchar(300),  
	AlternateNames text,
	Cross_references text,
	ExternalVocabulary text,     
        CONSTRAINT pharmgkb_phenotypes_info_pkey PRIMARY KEY (id)
        )
                                                                                                                                           
       TABLESPACE pg_default;                                                        
       CREATE INDEX idx_pharmgkb_phenotypes_PharmGKBAccessionId                       
       ON pharmgkb_phenotypes(PharmGKBAccessionId);
       ALTER TABLE IF EXISTS public.pharmgkb_phenotypes_info_pkey               
        OWNER to tm;   

DROP TABLE IF EXISTS public.pharmgkb_chemicals;     
                                                               
CREATE TABLE IF NOT EXISTS public.pharmgkb_chemicals
(                                                              
	id serial not null,   
	PharmGKBAccessionId varchar(100),
	Name_val varchar(300),
	GenericNames text,
	TradeNames text,
	BrandMixtures text,
	Type_val varchar(50),
	Cross_references text,
	SMILES text,
	InChI text,
	DosingGuideline varchar(20),
	ExternalVocabulary text,
	ClinicalAnnotationCount varchar(50),
	VariantAnnotationCount varchar(50),
	PathwayCount varchar(50),
	VIPCount varchar(50),
	DosingGuidelineSources varchar(50),
	TopClinicalAnnotationLevel varchar(50),
	TopFDALabelTestingLevel varchar(50),
	TopAnyDrugLabelTestingLevel varchar(50),
	LabelHasDosingInfo varchar(50),
	HasRxAnnotation varchar(50),
	RxNormIdentifiers varchar(50),
	ATCIdentifiers text,
	PubChemCompoundIdentifiers   varchar(50),    
        CONSTRAINT pharmgkb_chemicals_info_pkey PRIMARY KEY (id)
        )
                                                                                                                                           
       TABLESPACE pg_default;                                                        
       CREATE INDEX idx_pharmgkb_chemicals_PharmGKBAccessionId                       
       ON pharmgkb_chemicals(PharmGKBAccessionId);
       ALTER TABLE IF EXISTS public.pharmgkb_chemicals_info_pkey               
        OWNER to tm;   


DROP TABLE IF EXISTS public.pharmgkb_drugs;     
                                                               
CREATE TABLE IF NOT EXISTS public.pharmgkb_drugs
(                                                              
	id serial not null,   
	PharmGKBAccessionId varchar(100),
	Name_val varchar(300),
	GenericNames text,
	TradeNames text,
	BrandMixtures text,
	Type_val varchar(50),
	Cross_references text,
	SMILES text,
	InChI text,
	DosingGuideline varchar(20),
	ExternalVocabulary text,
	ClinicalAnnotationCount varchar(50),
	VariantAnnotationCount varchar(50),
	PathwayCount varchar(50),
	VIPCount varchar(50),
	DosingGuidelineSources varchar(50),
	TopClinicalAnnotationLevel varchar(50),
	TopFDALabelTestingLevel varchar(50),
	TopAnyDrugLabelTestingLevel varchar(50),
	LabelHasDosingInfo varchar(50),
	HasRxAnnotation varchar(50),
	RxNormIdentifiers varchar(50),
	ATCIdentifiers text,
	PubChemCompoundIdentifiers   varchar(50),    
        CONSTRAINT pharmgkb_drugs_info_pkey PRIMARY KEY (id)
        )
                                                                                                                                           
       TABLESPACE pg_default;                                                        
       CREATE INDEX idx_pharmgkb_drugs_PharmGKBAccessionId                       
       ON pharmgkb_drugs(PharmGKBAccessionId);
       ALTER TABLE IF EXISTS public.pharmgkb_drugs_info_pkey               
        OWNER to tm;   
		


DROP TABLE IF EXISTS public.pharmgkb_variant;     
                                                               
CREATE TABLE IF NOT EXISTS public.pharmgkb_variant
(                                                              
	id serial not null,   
	VariantID varchar(100),
	VariantName varchar(20),
	GeneIDs varchar(100),
	GeneSymbols varchar(100),
	Location varchar(50),
	VariantAnnotationcount varchar(50),
	ClinicalAnnotationcount varchar(50),
	Level1_2ClinicalAnnotationcount varchar(50),
	GuidelineAnnotationcount varchar(50),
	LabelAnnotationcount varchar(50),
	Synonyms text,
 
        CONSTRAINT pharmgkb_variant_info_pkey PRIMARY KEY (id)
        )
                                                                                                                                           
       TABLESPACE pg_default;                                                        
       CREATE INDEX idx_pharmgkb_variant_VariantID                       
       ON pharmgkb_variant(VariantID);
       ALTER TABLE IF EXISTS public.pharmgkb_variant_info_pkey               
        OWNER to tm;   


CREATE TYPE type_user_role AS ENUM (
        'disabled',
        'readonly',
        'editor',
        'admin',
        'superuser')

CREATE TABLE users (

        id serial not null,   

        created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,

        email text UNIQUE,
        password text,
        first_name text,
        last_name text,
        role type_user_role DEFAULT 'readonly',
        tags text[]
    )

