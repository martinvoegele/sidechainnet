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
# Needs ATOM3D installed
conda activate /oak/stanford/groups/rondror/users/mvoegele/envs/sidechainnet
module load cuda/10.1.168

CASP_VER=12

PDB_DIR='/oak/stanford/groups/rondror/projects/gert/data/sidechainnet_pdb'
OUT_DIR='/oak/stanford/groups/rondror/projects/gert/data/sidechainnet_lmdb'

for THINNING in 30 70 90; do 

	DATASET=sidechainnet_casp${CASP_VER}_${THINNING}
	echo "Processing $DATASET"

	# Convert PDB+CSV files to LMDB dataset
	python create_lmdb.py -i $PDB_DIR -o $OUT_DIR \
	                      -t $THINNING -v $CASP_VER
	# Convert PDB+CSV files to LMDB dataset with splits
        python create_lmdb.py -i $PDB_DIR -o $OUT_DIR \
                              -t $THINNING -v $CASP_VER \
	                      --split

done

