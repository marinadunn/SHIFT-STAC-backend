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
    dataset_date = '20220228'
    x_chunk = 100
    y_chunk = 100
    wavelength_chunk = 100
    # 20220228 flight paths
    aviris_data = [
                'ang20220228t183924',
                'ang20220228t185150',
                'ang20220228t18572',
                'ang20220228t190702',
                'ang20220228t192104',
                'ang20220228t193333',
                'ang20220228t194708',
                'ang20220228t195958',
                'ang20220228t201833',
                'ang20220228t202944',
                'ang20220228t204228',
                'ang20220228t205624',
                'ang20220228t210940'
                ]
    for item in aviris_data:
        slurm_path = make_slurm_script(username, folder_name, dataset_date,
                                        x_chunk, y_chunk, wavelength_chunk, item)
        call(["sbatch", slurm_path])

if __name__ == '__main__':
    main()
