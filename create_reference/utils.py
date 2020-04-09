# AUTOGENERATED! DO NOT EDIT! File to edit: 00_utils.ipynb (unless otherwise specified).

__all__ = ['get_args', 'file_exists', 'get_ffp', 'get_gfp', 'get_likely_file_from_ftp', 'get_local_files', 'get_paras']

# Cell
import os
import sys
import re
import argparse
import ftplib
from create_reference import defaults

# Cell
def get_args():
    parser = argparse.ArgumentParser(prog='fetchr',
                                     description='Fetch and Generate references for bioinformatics analysis',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                    )

    parser.add_argument('--species',nargs='+',choices=defaults.species,default=['homo_sapiens','mus_musculus'],
                       help='Reference or references from which species')
    parser.add_argument('--indexs',nargs='+',choices=defaults.softwares,default='samtools',
                       help='Using which software(s) to create indexes')
    parser.add_argument('--reference-version','-rv',default=99,type=int,
                       help='For homo_spaiens, version=75 is the last version of Grch37 reference, \
                       you can check the version in ftp://ftp.ensembl.org/pub/')
    parser.add_argument('--outdir','-o',default='./',
                       help='Reference and indexes generated direction')
    parser.add_argument('--thread','-t',default=4,
                       help='Thread number')
    return parser.parse_args()


# Cell

def file_exists(f):
    return os.path.exists(f)

# Cell

def get_ffp(species):
    return re.compile(defaults.fasta_file_pattern.format(species=species),re.IGNORECASE)

def get_gfp(species,version):
    return re.compile(defaults.gtf_file_pattern.format(species=species,version=version),re.IGNORECASE)

# Cell

def get_likely_file_from_ftp(ftp,ftp_server,version,species,ftype,dtype,pattern):
    if ftype == 'fasta':
        direction='/pub/release-{version}/{ftype}/{species}/{dtype}/'.format(
            version=version,
            species=species,
            ftype=ftype,
            dtype=dtype)
    elif ftype == 'gtf':
        direction='/pub/release-{version}/{ftype}/{species}/'.format(
            version=version,
            species=species,
            ftype=ftype)
    try:
#         print(direction)
        ftp.cwd(direction)
        files = ftp.nlst()
        for f in files:
#                 print(f)
            if len(pattern.findall(f))>0:
                return 'ftp://'+ftp_server+direction+f
        raise ValueError('No fit ' + ftype +' file in ftp://'+ftp_server+direction)
    except ftplib.all_errors as e:
        print(e)
        sys.exit(1)


# Cell

def get_local_files(outdir,species,version):
    sample_outdir='{outdir}/{species}/{version}'.format(outdir=outdir,species=species,version=version)
    local_genome_fasta='{sample_outdir}/genome.fa.gz'.format(sample_outdir=sample_outdir)
    local_transcriptome_gtf = '{sample_outdir}/transcriptome.gtf.gz'.format(sample_outdir=sample_outdir)
    os.makedirs(sample_outdir,exist_ok=True)
    return local_genome_fasta,local_transcriptome_gtf

# Cell

def get_paras(args,ftp,ftp_server):
    paras=[]
    for sp in args.species:
        para={}
        para['species']=sp
        para['version']=args.reference_version
        para['link_genome_fasta']=get_likely_file_from_ftp(ftp,
                                                           ftp_server,
                                                           args.reference_version,
                                                           sp,
                                                           'fasta',
                                                           'dna',
                                                           get_ffp(sp))
        para['link_transcriptome_gtf']=get_likely_file_from_ftp(ftp,
                                                                ftp_server,
                                                                args.reference_version,
                                                                sp,'gtf',
                                                                None,
                                                                get_gfp(sp,
                                                                        args.reference_version))
        para['local_genome_fasta'],para['local_transcriptome_gtf'] = get_local_files(args.outdir,
                                                                                     sp,
                                                                                     args.reference_version)
        paras.append(para)

    return paras