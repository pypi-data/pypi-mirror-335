import json
import numpy as np

json_filename = '/home/pawel/Code/chemistry/cfour/xsim/db/sroph_at_pvdz/normal_coordinates.json'

def collect_xsim_nmode_json(json_filename):
    with open(json_filename) as json_file:
        nmodes = json.load(json_file)

    for mode in nmodes:
        cooridnate = mode['coordinate'] 
        natoms = len(cooridnate)
        print(natoms)
        vector = np.zeros(shape=(3*natoms), dtype=float)
        for atom_idx, xyz in enumerate(cooridnate):
            vector[3*atom_idx:3*atom_idx+3] = xyz

        norm = np.linalg.norm(vector)
        print(
            f'Wavenumber = {mode['frequency, cm-1']:8.2f}',
            'cm-1.',
            f'Norm = {norm:.4f}',
        )
        for xyz in cooridnate:
            print(' '*2, ' '.join(f'{i:6.3f}' for i in xyz))



def main():
    collect_xsim_nmode_json(json_filename=json_filename)

if __name__ == "__main__":
    main()
