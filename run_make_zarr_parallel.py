from subprocess import call

def make_slurm_script(username, folder_name, dataset_date,
                      x_chunk, y_chunk, wavelength_chunk, item):
    slurm_path = "run_template.sh"
    with open(slurm_path, "w") as outfile:
    # Alternatively to sbatch, can use 'salloc', an interactive batch for monitoring memory
        outfile.write(f'#!/usr/bin/env bash\n')
        outfile.write(f'#SBATCH --account=s3673\n')
        outfile.write(f'#SBATCH --mem-per-cpu=2048\n')
        outfile.write(f'#SBATCH --mem=150G\n') # May need to increase this to accomodate full zarr
        outfile.write(f'#SBATCH --time=12:00:00\n')
        outfile.write(f'#SBATCH --constraint="sky|hasw"\n')
        outfile.write(f'#SBATCH --output=outfiles/job_%j.out\n')
        outfile.write(f'#SBATCH --error=outfiles/job_%j.err\n')
        outfile.write(f'set -e\n')
        outfile.write(f'echo "*** Start time: $(date) ***"\n')
        outfile.write(f'module load python/GEOSpyD/Min4.10.3_py3.9\n')
        outfile.write(f'echo "Using Python: $(which python)"\n')
        outfile.write(f'python make_zarr.py --username {username} --folder_name {folder_name} --dataset_date {dataset_date} ')
        outfile.write(f'--x_chunk {x_chunk} --y_chunk {y_chunk} --wavelength_chunk {wavelength_chunk} --item {item}\n')
        outfile.write(f'echo "*** End time: $(date) ***"\n')
    return slurm_path

def main():
    username = 'mdunn'
    folder_name = 'aviris_data'
    dataset_date = '20220308'
    x_chunk = 100
    y_chunk = 100
    wavelength_chunk = 100
<<<<<<< HEAD
=======
    # 20220308 flight paths
>>>>>>> 238c93e5fc51d5f0c311cddce6bf2a1642bdca89
    aviris_data = ['ang20220308t183206',
                    'ang20220308t184127',
                    'ang20220308t185140',
                    'ang20220308t190523',
                    'ang20220308t191151',
                    'ang20220308t192816',
                    'ang20220308t194253',
                    'ang20220308t195648',
                    'ang20220308t201508',
                    'ang20220308t202617',
                    'ang20220308t204043',
                    'ang20220308t205512',
                    'ang20220308t211733',
                    'ang20220308t213310',
                    'ang20220308t214629'
                    ]
    for item in aviris_data:
        slurm_path = make_slurm_script(username, folder_name, dataset_date,
                                        x_chunk, y_chunk, wavelength_chunk, item)
        call(["sbatch", slurm_path])

if __name__ == '__main__':
    main()
