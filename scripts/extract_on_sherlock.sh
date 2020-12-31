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

python extract_as_pdb.py -i '/oak/stanford/groups/rondror/projects/gert/data/sidechainnet_data' \
                         -o '/oak/stanford/groups/rondror/projects/gert/data/sidechainnet_pdb'

