import argparse, os
import pandas as pd
import atom3d.datasets as da
import atom3d.splits.splits as spl


# Read the arguments
parser = argparse.ArgumentParser(description='Converts SidechainNet to PDB files.')
parser.add_argument('-i', '--indir', type=str, default='./sidechainnet_pdb',
                    help='The directory containing a SidechainNet dataset')
parser.add_argument('-o', '--outdir', type=str, default='./sidechainnet_lmdb',
                    help='The directory in which the PDB files will be saved')
parser.add_argument('-v', '--casp_version', type=int, default=12,
                    help='The CASP version of the dataset')
parser.add_argument('-t', '--thinning', type=int, default=30,
                    help='The sequence identity threshold for thinning of the dataset')
parser.add_argument('--split', dest='split', action='store_true',
                    help='Write the split datasets instead of the full one.')
args = parser.parse_args()


# Construct directory names
subds_name = 'sidechainnet_casp'+str(args.casp_version)+'_'+str(args.thinning)
input_dir  = os.path.join(args.indir, subds_name)
output_dir = os.path.join(args.outdir,subds_name)
labels_dir = os.path.join(input_dir,'evo-info')

# Define the transformation function
def add_evo(item):
    name = item['id'][:-4]
    # Get label data
    label_file = os.path.join(labels_dir,name+'.csv')
    label_data = pd.read_csv(label_file)
    # Add PSSM and information content to the item
    item['pssm'] = label_data[['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y']]
    item['ic'] = label_data[['ic']]
    # Remove .pdb ending 
    item['atoms'].replace(item['id'], name, inplace=True)
    item['id'] = name
    return item

# Load dataset from directory of PDB files
struct_dir = os.path.join(input_dir, 'structures')
dataset = da.load_dataset(struct_dir, 'pdb', transform=add_evo)

# Create the output directory if it does not exist yet
os.makedirs(output_dir, exist_ok=True)

# Write out either the full dataset or the split datasets
if not args.split: 
    # - Full dataset -
    print('Writing the full dataset in LMDB format.')
    # Remove old MDB files if they exist
    for mdb_part in ['data.mdb','lock.mdb']:
        mdb_file = os.path.join(output_dir,mdb_part)
        try: os.remove(mdb_file)
        except OSError: pass
    # Create LMDB dataset from PDB dataset
    da.make_lmdb_dataset(dataset, output_dir,
                         filter_fn = None, 
                         serialization_format = 'json',
                         include_bonds = False)
else:  
    # - Split datasets -
    print('Splitting the dataset.')
    # Load split values
    tr_file = os.path.join(input_dir,'train.txt')
    va_file = os.path.join(input_dir,'valid.txt')
    te_file = os.path.join(input_dir,'test.txt')
    tr_values = pd.read_csv(tr_file,header=None)[0].tolist()
    va_values = pd.read_csv(va_file,header=None)[0].tolist()
    te_values = pd.read_csv(te_file,header=None)[0].tolist()
    # Create splits
    split_ds = spl.split_by_group(dataset, 
                                  value_fn = lambda x: x['id'],
                                  train_values = tr_values, 
                                  val_values   = va_values, 
                                  test_values  = te_values)
    # Write out split datasets
    print('Writing the split datasets in LMDB format.')
    for s,split_name in enumerate(['training','validation','test']):
        # Create the output directory if it does not exist yet
        split_dir = os.path.join(output_dir, split_name)
        os.makedirs(split_dir, exist_ok=True)
        # Remove old MDB files if they exist
        for mdb_part in ['data.mdb','lock.mdb']:
            mdb_file = os.path.join(split_dir,mdb_part)
            try: os.remove(mdb_file)
            except OSError: pass
        # Create LMDB dataset from PDB dataset
        da.make_lmdb_dataset(split_ds[s], split_dir,
                             filter_fn = None, 
                             serialization_format = 'json',
                             include_bonds = False)


