#!/bin/bash
#SBATCH --partition rondror
#SBATCH --mail-type=FAIL
#SBATCH --ntasks-per-socket=1
##SBATCH --gres-flags=enforce-binding
##SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH --time=48:00:00

source ~/miniconda3/etc/profile.d/conda.sh
conda deactivate
conda deactivate
conda activate /oak/stanford/groups/rondror/users/mvoegele/envs/sidechainnet
module load cuda/10.1.168

CASP_VER=12

SCN_DIR='/oak/stanford/groups/rondror/projects/gert/data/sidechainnet_data'
PDB_DIR='/oak/stanford/groups/rondror/projects/gert/data/sidechainnet_pdb'


for THINNING in 30 70 90; do 

	DATASET=sidechainnet_casp${CASP_VER}_${THINNING}
	echo "Processing $DATASET"

	# Download the SidechainNet dataset and extract PDB+CSV files
	python extract_pdb.py -i $SCN_DIR \
	                      -o $PDB_DIR \
	                      -t $THINNING \
	                      -v $CASP_VER

	# Concatenate the IDs for the joint validation set
	cat $PDB_DIR/$DATASET/valid-??.txt > $PDB_DIR/$DATASET/valid.txt

done

