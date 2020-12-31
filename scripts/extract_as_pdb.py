import argparse, os
import pandas as pd
import sidechainnet as scn


# Read the arguments

parser = argparse.ArgumentParser(description='Converts SidechainNet to PDB files.')
parser.add_argument('-i', '--indir', type=str, default='./sidechainnet_data',
                    help='The directory containing a SidechainNet dataset')
parser.add_argument('-o', '--outdir', type=str, default='./sidechainnet_pdb',
                    help='The directory in which the PDB files will be saved')
parser.add_argument('-v', '--casp_version', type=int, default=12,
                    help='The CASP version of the dataset')
parser.add_argument('-t', '--thinning', type=int, default=30,
                    help='The thinning percentage of the dataset')
parser.add_argument('--raw_names', type=bool, default=False,
                    help='Drop split info in ID')
args = parser.parse_args()


# Define keys

ds_keys = ["train","valid-10","valid-20","valid-30","valid-40",
           "valid-50","valid-70","valid-90","test"]

aa_code = {'A':'Ala','C':'Cys','D':'Asp','E':'Glu','F':'Phe',
           'G':'Gly','H':'His','I':'Ile','K':'Lys','L':'Leu',
           'M':'Met','N':'Asn','P':'Pro','Q':'Gln','R':'Arg',
           'S':'Ser','T':'Thr','V':'Val','W':'Trp','Y':'Tyr'}

col_names = [k for k in aa_code.keys()] + ['ic']


# Create directories

subdir = 'sidechainnet_casp'+str(args.casp_version)+'_'+str(args.thinning)
os.makedirs(os.path.join(args.outdir,subdir), exist_ok = True)
os.makedirs(os.path.join(args.outdir,subdir,'structures'), exist_ok = True)
os.makedirs(os.path.join(args.outdir,subdir,'evo-info'), exist_ok = True)


# Load SidechainNet data

data = scn.load(casp_version = args.casp_version, 
                thinning = args.thinning, 
                scn_dir = args.indir)


# Go through the datasets and process them

for ds in ds_keys: 
    seq = data[ds]["seq"] # Sequences
    crd = data[ds]["crd"] # Coordinates
    evo = data[ds]["evo"] # PSSMs and Information Content
    ids = data[ds]["ids"] # Corresponding ProteinNet IDs

    # Extract the name of each structure
    if args.raw_names:
        names = [ idi.split('#')[-1] for idi in ids ]
    else:
        names = ids

    # Write the names to a file that defines the split
    with open(os.path.join(args.outdir,subdir,ds+'.txt'), 'w') as f:
        for n in names:
            f.write("%s\n" % n)

    for i, n in enumerate(names):
        print(ds, '%d/%d'%(i,len(names)), '-', n, flush=True)
        # File names
        pdb_fn = os.path.join(args.outdir,subdir,'structures',n+'.pdb')
        csv_fn = os.path.join(args.outdir,subdir,'evo-info',n+'.csv')
        # Extract the structure and write it to a pdb file
        sb = scn.StructureBuilder(seq[i], crd=crd[i])
        sb.to_pdb(pdb_fn)
        # Extract PSSM and information content and write them to a csv file
        evo_df = pd.DataFrame(evo[i],columns=col_names)
        evo_df.to_csv(csv_fn,index=False)

