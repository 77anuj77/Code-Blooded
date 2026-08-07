#!/usr/bin/env python3
"""Create data/orpha.sqlite with schema and sample data for local development."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "packages" / "ingest"))
sys.path.insert(0, str(ROOT / "packages" / "scoring"))

from sqlmodel import Session, SQLModel, create_engine

from ingest.models import (
    ClinVarGeneDisease,
    CrossRef,
    Disease,
    DiseaseGene,
    DiseasePhenotype,
    FacialDiseasePhenotype,
    HPOAncestor,
    HPOTerm,
    Prevalence,
)

DB_PATH = ROOT / "data" / "orpha.sqlite"


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as s:
        diseases = [
            Disease(
                orpha_code=280,
                name="Bardet-Biedl syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=778,
                name="Marfan syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=166,
                name="Cystic fibrosis",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=644,
                name="Rett syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=98,
                name="Angelman syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=79314,
                name="Noonan syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=558,
                name="Prader-Willi syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=137,
                name="Tuberous sclerosis",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=869,
                name="Williams-Beuren syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=784,
                name="Turner syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=221068,
                name="Kabuki syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=169146,
                name="Ehlers-Danlos syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=94093,
                name="CHARGE syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=124,
                name="Down syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
            Disease(
                orpha_code=168541,
                name="Kleefstra syndrome",
                disorder_type="Disease",
                disorder_group="Disorder",
            ),
        ]
        s.add_all(diseases)
        s.commit()

        hpo_terms = [
            HPOTerm(
                hpo_id="HP:0001250",
                name="Seizures",
                definition="Seizures resulting from abnormal excessive synchronous neuronal activity.",
                ic=8.5,
            ),
            HPOTerm(
                hpo_id="HP:0001249",
                name="Intellectual disability",
                definition="Degree of intellectual limitation.",
                ic=9.1,
            ),
            HPOTerm(
                hpo_id="HP:0001252",
                name="Hypotonia",
                definition="Muscular hypotonia.",
                ic=6.2,
            ),
            HPOTerm(
                hpo_id="HP:0000252",
                name="Microcephaly",
                definition="Occipitofrontal head circumference more than 2 standard deviations below the mean.",
                ic=7.8,
            ),
            HPOTerm(
                hpo_id="HP:0001263",
                name="Global developmental delay",
                definition="Delay in the acquisition of cognitive and motor developmental milestones.",
                ic=8.9,
            ),
            HPOTerm(
                hpo_id="HP:0000256",
                name="Macrocephaly",
                definition="Occipitofrontal head circumference more than 2 standard deviations above the mean.",
                ic=5.1,
            ),
            HPOTerm(
                hpo_id="HP:0001166",
                name="Clinodactyly",
                definition="Deflection of the finger.",
                ic=3.2,
            ),
            HPOTerm(
                hpo_id="HP:0000593",
                name="Brachydactyly",
                definition="Shortness of fingers or toes.",
                ic=3.8,
            ),
            HPOTerm(
                hpo_id="HP:0001382",
                name="Joint hypermobility",
                definition="The ability of a joint to move beyond its normal range of motion.",
                ic=2.9,
            ),
            HPOTerm(
                hpo_id="HP:0000965",
                name="Scoliosis",
                definition="The presence of an abnormal lateral curvature of the spine.",
                ic=5.5,
            ),
            HPOTerm(
                hpo_id="HP:0000482",
                name="Arachnodactyly",
                definition="Abnormally long and slender fingers and toes.",
                ic=4.3,
            ),
            HPOTerm(
                hpo_id="HP:0000518",
                name="Cataract",
                definition="An opacity of the lens of the eye.",
                ic=5.9,
            ),
            HPOTerm(
                hpo_id="HP:0001167",
                name="Brachycephaly",
                definition="Anteroposteriorly shortened head.",
                ic=3.5,
            ),
            HPOTerm(
                hpo_id="HP:0000568",
                name="Microphthalmia",
                definition="One or both eyeballs are abnormally small.",
                ic=5.7,
            ),
            HPOTerm(
                hpo_id="HP:0001332",
                name="Hypoplasia of the optic nerve",
                definition="Underdevelopment of the optic nerve.",
                ic=4.6,
            ),
            HPOTerm(
                hpo_id="HP:0000545",
                name="Myopia",
                definition="Nearsightedness.",
                ic=2.8,
            ),
            HPOTerm(
                hpo_id="HP:0002383",
                name="Deeply set eye",
                definition="Deep-set eyes.",
                ic=2.5,
            ),
            HPOTerm(
                hpo_id="HP:0001254",
                name="Hyperreflexia",
                definition="A higher than normal response of deep tendon reflexes.",
                ic=5.3,
            ),
            HPOTerm(
                hpo_id="HP:0001260",
                name="Dystonia",
                definition="Sustained muscle contractions causing twisting and repetitive movements.",
                ic=6.1,
            ),
            HPOTerm(
                hpo_id="HP:0000750",
                name="Failure to thrive",
                definition="Deceleration of linear growth.",
                ic=5.8,
            ),
            HPOTerm(
                hpo_id="HP:0001596",
                name="Abnormality of cardiovascular system",
                definition="Any functional abnormality of the cardiovascular system.",
                ic=5.2,
            ),
            HPOTerm(
                hpo_id="HP:0001510",
                name="Congenital heart defect",
                definition="A structural anomaly of the heart that is present at birth.",
                ic=7.0,
            ),
            HPOTerm(
                hpo_id="HP:0001629",
                name="Pulmonic stenosis",
                definition="A narrowing of the right ventricular outflow tract.",
                ic=4.8,
            ),
            HPOTerm(
                hpo_id="HP:0000826",
                name="Ataxia",
                definition="Motor clumsiness with failure of voluntary movement.",
                ic=6.5,
            ),
            HPOTerm(
                hpo_id="HP:0001268",
                name="Mental deterioration",
                definition="Loss of previously established cognitive abilities.",
                ic=7.3,
            ),
            HPOTerm(
                hpo_id="HP:0000717",
                name="Autism",
                definition="Autism spectrum disorder.",
                ic=7.1,
            ),
            HPOTerm(
                hpo_id="HP:0000722",
                name="Obsessive-compulsive behavior",
                definition="Repetitive, persistent thoughts or behaviors.",
                ic=4.2,
            ),
            HPOTerm(
                hpo_id="HP:0001264",
                name="Short stature",
                definition="Short body height.",
                ic=5.6,
            ),
            HPOTerm(
                hpo_id="HP:0001165",
                name="Clinodactyly of the 5th finger",
                definition="Bending or curvature of the 5th finger.",
                ic=2.4,
            ),
            HPOTerm(
                hpo_id="HP:0000501",
                name="Glaucoma",
                definition="Increased pressure within the eye.",
                ic=4.7,
            ),
            HPOTerm(
                hpo_id="HP:0000365",
                name="Hearing impairment",
                definition="A decreased severity of hearing.",
                ic=5.4,
            ),
            HPOTerm(
                hpo_id="HP:0000407",
                name="Sensorineural hearing loss",
                definition="Hearing loss due to inner ear pathology.",
                ic=5.0,
            ),
            HPOTerm(
                hpo_id="HP:0000939",
                name="Acanthosis nigricans",
                definition="Velvety hyperpigmentation of the skin.",
                ic=3.0,
            ),
            HPOTerm(
                hpo_id="HP:0000819",
                name="Diabetes mellitus",
                definition="A metabolic disorder characterized by hyperglycemia.",
                ic=4.4,
            ),
            HPOTerm(
                hpo_id="HP:0000098",
                name="Obesity",
                definition="Abnormally increased adipose tissue.",
                ic=4.1,
            ),
            HPOTerm(
                hpo_id="HP:0000316",
                name="Cone-shaped epiphysis",
                definition="Cone-shaped epiphysis of phalanges.",
                ic=3.1,
            ),
            HPOTerm(
                hpo_id="HP:0002015",
                name="Brachydactyly type A1",
                definition="Brachydactyly with short metacarpals and phalanges.",
                ic=2.7,
            ),
            HPOTerm(
                hpo_id="HP:0000543",
                name="Strabismus",
                definition="Misalignment of the visual axes.",
                ic=3.3,
            ),
            HPOTerm(
                hpo_id="HP:0000175",
                name="Ptosis",
                definition="Drooping of the upper eyelid.",
                ic=3.6,
            ),
            HPOTerm(
                hpo_id="HP:0000400",
                name="Cleft palate",
                definition="A congenital fissure in the roof of the mouth.",
                ic=5.1,
            ),
            HPOTerm(
                hpo_id="HP:0000347",
                name="Talipes equinovarus",
                definition="Foot deformity with plantar flexion and inversion.",
                ic=3.4,
            ),
            HPOTerm(
                hpo_id="HP:0000369",
                name="Orchidopexy",
                definition="Failure of testicular descent.",
                ic=2.6,
            ),
            HPOTerm(
                hpo_id="HP:0000595",
                name="Umbilical hernia",
                definition="Protrusion of the abdominal contents through the umbilicus.",
                ic=2.2,
            ),
            HPOTerm(
                hpo_id="HP:0002616",
                name="Aortic root aneurysm",
                definition="Aneurysmatic dilation of the aortic root.",
                ic=4.5,
            ),
            HPOTerm(
                hpo_id="HP:0001302",
                name="Mitral valve prolapse",
                definition="Bowing of leaflets into the left atrium.",
                ic=4.0,
            ),
            HPOTerm(
                hpo_id="HP:0001744",
                name="Splenomegaly",
                definition="Enlargement of the spleen.",
                ic=3.9,
            ),
            HPOTerm(
                hpo_id="HP:0002280",
                name="Hepatomegaly",
                definition="Enlargement of the liver.",
                ic=3.7,
            ),
            HPOTerm(
                hpo_id="HP:0002019",
                name="Conductive hearing loss",
                definition="Hearing loss due to conduction abnormalities.",
                ic=3.5,
            ),
        ]
        s.add_all(hpo_terms)
        s.commit()

        ancestors = [
            HPOAncestor(hpo_id="HP:0001250", ancestor_id="HP:0000448"),
            HPOAncestor(hpo_id="HP:0001250", ancestor_id="HP:0002190"),
            HPOAncestor(hpo_id="HP:0001250", ancestor_id="HP:0000707"),
            HPOAncestor(hpo_id="HP:0001249", ancestor_id="HP:0000707"),
            HPOAncestor(hpo_id="HP:0001249", ancestor_id="HP:0001268"),
            HPOAncestor(hpo_id="HP:0001252", ancestor_id="HP:0001252"),
            HPOAncestor(hpo_id="HP:0000252", ancestor_id="HP:0001188"),
            HPOAncestor(hpo_id="HP:0000252", ancestor_id="HP:0005484"),
            HPOAncestor(hpo_id="HP:0001263", ancestor_id="HP:0000707"),
            HPOAncestor(hpo_id="HP:0001263", ancestor_id="HP:0001249"),
            HPOAncestor(hpo_id="HP:0000256", ancestor_id="HP:0001188"),
            HPOAncestor(hpo_id="HP:0000256", ancestor_id="HP:0005484"),
            HPOAncestor(hpo_id="HP:0000965", ancestor_id="HP:0002828"),
            HPOAncestor(hpo_id="HP:0001510", ancestor_id="HP:0001596"),
            HPOAncestor(hpo_id="HP:0001510", ancestor_id="HP:0001629"),
        ]
        s.add_all(ancestors)
        s.commit()

        phenotypes = [
            DiseasePhenotype(
                orpha_code=280,
                hpo_id="HP:0001250",
                hpo_term="Seizures",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=280,
                hpo_id="HP:0001249",
                hpo_term="Intellectual disability",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=280,
                hpo_id="HP:0000256",
                hpo_term="Macrocephaly",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=280,
                hpo_id="HP:0000819",
                hpo_term="Diabetes mellitus",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=280,
                hpo_id="HP:0000098",
                hpo_term="Obesity",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=280,
                hpo_id="HP:0000518",
                hpo_term="Cataract",
                frequency_label="Occasional (29-5%)",
                frequency_weight=0.17,
            ),
            DiseasePhenotype(
                orpha_code=280,
                hpo_id="HP:0000501",
                hpo_term="Glaucoma",
                frequency_label="Occasional (29-5%)",
                frequency_weight=0.17,
            ),
            DiseasePhenotype(
                orpha_code=280,
                hpo_id="HP:0000369",
                hpo_term="Orchidopexy",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=778,
                hpo_id="HP:0001382",
                hpo_term="Joint hypermobility",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=778,
                hpo_id="HP:0001166",
                hpo_term="Clinodactyly",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=778,
                hpo_id="HP:0000482",
                hpo_term="Arachnodactyly",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=778,
                hpo_id="HP:0000965",
                hpo_term="Scoliosis",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=778,
                hpo_id="HP:0002616",
                hpo_term="Aortic root aneurysm",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=778,
                hpo_id="HP:0001302",
                hpo_term="Mitral valve prolapse",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=778,
                hpo_id="HP:0000543",
                hpo_term="Strabismus",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=644,
                hpo_id="HP:0001263",
                hpo_term="Global developmental delay",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=644,
                hpo_id="HP:0001252",
                hpo_term="Hypotonia",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=644,
                hpo_id="HP:0001260",
                hpo_term="Dystonia",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=644,
                hpo_id="HP:0001249",
                hpo_term="Intellectual disability",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=644,
                hpo_id="HP:0000750",
                hpo_term="Failure to thrive",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=644,
                hpo_id="HP:0000365",
                hpo_term="Hearing impairment",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=98,
                hpo_id="HP:0001250",
                hpo_term="Seizures",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=98,
                hpo_id="HP:0001249",
                hpo_term="Intellectual disability",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=98,
                hpo_id="HP:0001167",
                hpo_term="Brachycephaly",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=98,
                hpo_id="HP:0001252",
                hpo_term="Hypotonia",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=98,
                hpo_id="HP:0000717",
                hpo_term="Autism",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=558,
                hpo_id="HP:0000098",
                hpo_term="Obesity",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=558,
                hpo_id="HP:0001249",
                hpo_term="Intellectual disability",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=558,
                hpo_id="HP:0000819",
                hpo_term="Diabetes mellitus",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=558,
                hpo_id="HP:0000717",
                hpo_term="Autism",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=558,
                hpo_id="HP:0000369",
                hpo_term="Orchidopexy",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=137,
                hpo_id="HP:0001250",
                hpo_term="Seizures",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=137,
                hpo_id="HP:0001249",
                hpo_term="Intellectual disability",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=137,
                hpo_id="HP:0000256",
                hpo_term="Macrocephaly",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=869,
                hpo_id="HP:0001249",
                hpo_term="Intellectual disability",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=869,
                hpo_id="HP:0001510",
                hpo_term="Congenital heart defect",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=869,
                hpo_id="HP:0000365",
                hpo_term="Hearing impairment",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=869,
                hpo_id="HP:0001264",
                hpo_term="Short stature",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=784,
                hpo_id="HP:0001264",
                hpo_term="Short stature",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=784,
                hpo_id="HP:0001510",
                hpo_term="Congenital heart defect",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=784,
                hpo_id="HP:0000400",
                hpo_term="Cleft palate",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=221068,
                hpo_id="HP:0001249",
                hpo_term="Intellectual disability",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=221068,
                hpo_id="HP:0001264",
                hpo_term="Short stature",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=221068,
                hpo_id="HP:0001166",
                hpo_term="Clinodactyly",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=94093,
                hpo_id="HP:0001263",
                hpo_term="Global developmental delay",
                frequency_label="Very frequent (99-80%)",
                frequency_weight=0.895,
            ),
            DiseasePhenotype(
                orpha_code=94093,
                hpo_id="HP:0000568",
                hpo_term="Microphthalmia",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=94093,
                hpo_id="HP:0001332",
                hpo_term="Hypoplasia of the optic nerve",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=94093,
                hpo_id="HP:0001510",
                hpo_term="Congenital heart defect",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
            DiseasePhenotype(
                orpha_code=94093,
                hpo_id="HP:0001629",
                hpo_term="Pulmonic stenosis",
                frequency_label="Frequent (79-30%)",
                frequency_weight=0.545,
            ),
        ]
        s.add_all(phenotypes)
        s.commit()

        genes = [
            DiseaseGene(
                orpha_code=280,
                gene_symbol="BBS1",
                gene_name="Bardet-Biedl syndrome 1",
                ensembl_id="ENSG00000125166",
            ),
            DiseaseGene(
                orpha_code=280,
                gene_symbol="BBS2",
                gene_name="Bardet-Biedl syndrome 2",
                ensembl_id="ENSG00000125166",
            ),
            DiseaseGene(
                orpha_code=280,
                gene_symbol="BBS4",
                gene_name="Bardet-Biedl syndrome 4",
                ensembl_id="ENSG00000125166",
            ),
            DiseaseGene(
                orpha_code=778,
                gene_symbol="FBN1",
                gene_name="Fibrillin 1",
                ensembl_id="ENSG00000166147",
            ),
            DiseaseGene(
                orpha_code=166,
                gene_symbol="CFTR",
                gene_name="Cystic fibrosis transmembrane conductance regulator",
                ensembl_id="ENSG00000001626",
            ),
            DiseaseGene(
                orpha_code=644,
                gene_symbol="MECP2",
                gene_name="Methyl-CpG binding protein 2",
                ensembl_id="ENSG00000169057",
            ),
            DiseaseGene(
                orpha_code=98,
                gene_symbol="UBE3A",
                gene_name="Ubiquitin protein ligase E3A",
                ensembl_id="ENSG00000112062",
            ),
            DiseaseGene(
                orpha_code=79314,
                gene_symbol="PTPN11",
                gene_name="Protein tyrosine phosphatase non-receptor type 11",
                ensembl_id="ENSG00000179295",
            ),
            DiseaseGene(
                orpha_code=558,
                gene_symbol="SNRPN",
                gene_name="Small nuclear ribonucleoprotein polypeptide N",
                ensembl_id="ENSG00000128739",
            ),
            DiseaseGene(
                orpha_code=137,
                gene_symbol="TSC1",
                gene_name="Tuberous sclerosis 1",
                ensembl_id="ENSG00000165699",
            ),
            DiseaseGene(
                orpha_code=137,
                gene_symbol="TSC2",
                gene_name="Tuberous sclerosis 2",
                ensembl_id="ENSG00000103197",
            ),
            DiseaseGene(
                orpha_code=869,
                gene_symbol="LIMK1",
                gene_name="LIM domain kinase 1",
                ensembl_id="ENSG00000106683",
            ),
            DiseaseGene(
                orpha_code=784,
                gene_symbol="XIST",
                gene_name="X inactive specific transcript",
                ensembl_id="ENSG00000229807",
            ),
            DiseaseGene(
                orpha_code=221068,
                gene_symbol="KMT2D",
                gene_name="Lysine methyltransferase 2D",
                ensembl_id="ENSG00000167548",
            ),
            DiseaseGene(
                orpha_code=169146,
                gene_symbol="COL5A1",
                gene_name="Collagen type V alpha 1 chain",
                ensembl_id="ENSG00000130635",
            ),
            DiseaseGene(
                orpha_code=94093,
                gene_symbol="CHD7",
                gene_name="Chromodomain helicase DNA binding protein 7",
                ensembl_id="ENSG00000171316",
            ),
            DiseaseGene(
                orpha_code=168541,
                gene_symbol="EHMT1",
                gene_name="Histone-lysine N-methyltransferase EHMT1",
                ensembl_id="ENSG00000181090",
            ),
        ]
        s.add_all(genes)
        s.commit()

        cross_refs = [
            CrossRef(
                orpha_code=280,
                source="ICD-10",
                reference="Q87.2",
                mapping_relation="included",
            ),
            CrossRef(
                orpha_code=280,
                source="OMIM",
                reference="209900",
                mapping_relation="included",
            ),
            CrossRef(
                orpha_code=778,
                source="ICD-10",
                reference="Q87.4",
                mapping_relation="included",
            ),
            CrossRef(
                orpha_code=778,
                source="OMIM",
                reference="154700",
                mapping_relation="included",
            ),
            CrossRef(
                orpha_code=166,
                source="ICD-10",
                reference="E84.0",
                mapping_relation="included",
            ),
            CrossRef(
                orpha_code=166,
                source="OMIM",
                reference="219700",
                mapping_relation="included",
            ),
            CrossRef(
                orpha_code=644,
                source="ICD-10",
                reference="F84.1",
                mapping_relation="included",
            ),
            CrossRef(
                orpha_code=644,
                source="OMIM",
                reference="312750",
                mapping_relation="included",
            ),
            CrossRef(
                orpha_code=98,
                source="ICD-10",
                reference="F84.0",
                mapping_relation="included",
            ),
            CrossRef(
                orpha_code=98,
                source="OMIM",
                reference="105830",
                mapping_relation="included",
            ),
        ]
        s.add_all(cross_refs)
        s.commit()

        prevalence = [
            Prevalence(
                orpha_code=280,
                prevalence_type="Point prevalence",
                prevalence_class="1-9 / 100 000",
                val_moy=None,
                geographic="Europe",
            ),
            Prevalence(
                orpha_code=778,
                prevalence_type="Point prevalence",
                prevalence_class="1-9 / 100 000",
                val_moy=None,
                geographic="Europe",
            ),
            Prevalence(
                orpha_code=166,
                prevalence_type="Point prevalence",
                prevalence_class="1-9 / 100 000",
                val_moy=0.000005,
                geographic="Europe",
            ),
            Prevalence(
                orpha_code=644,
                prevalence_type="Point prevalence",
                prevalence_class="1-9 / 100 000",
                val_moy=None,
                geographic="Europe",
            ),
            Prevalence(
                orpha_code=98,
                prevalence_type="Point prevalence",
                prevalence_class="1-9 / 100 000",
                val_moy=None,
                geographic="Europe",
            ),
        ]
        s.add_all(prevalence)
        s.commit()

    print(
        f"Created {DB_PATH} with {len(diseases)} diseases, {len(hpo_terms)} HPO terms, {len(phenotypes)} phenotypes, {len(genes)} genes"
    )


if __name__ == "__main__":
    main()
