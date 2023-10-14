import requests
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import argparse

logging.basicConfig(level=logging.DEBUG)

BASE_URL = 'https://www.tng-project.org/api/'

def fetch_simulations(api_key):
    #logging.debug("Fetching simulations...")
    """Fetch the list of all available simulations."""
    headers = {"api-key": api_key}
    response = requests.get(BASE_URL, headers=headers)
    #print("Fetching simulations:")
    #print(f"Request URL: {response.url}")
    #print(f"Status Code: {response.status_code}")
    #print(f"Response Content: {response.content.decode()}")
    #logging.debug(f"Request URL: {response.url}")
    #logging.debug(f"Status Code: {response.status_code}")
    return response.json().get('simulations', [])


def fetch_data_types():
    """Return the types of data that can be downloaded."""
    return [
        "PartType0 (Gas)",
        "PartType1 (Halo)",
        "PartType2 (Disk)",
        "PartType3 (Bulge)",
        "PartType4 (Stars)",
        "PartType5 (Black Holes)"
    ]


def download_cutout(api_key, simulation_name, snapshot_id, object_id, datatypes, is_subhalo=True, cube_size=None):
    #logging.debug(f"Initiating download for {datatypes}...")

    headers = {"api-key": api_key}
    object_type = "subhalos" if is_subhalo else "halos"
    endpoint = f"{simulation_name}/snapshots/{snapshot_id}/{object_type}/{object_id}/cutout.hdf5"

    # Properties for each particle type
    all_params = {
        'Gas': 'Coordinates,Velocities,ParticleIDs,Masses,InternalEnergy,Density,ElectronAbundance,NeutralHydrogenAbundance,SmoothingLength,StarFormationRate,Metallicity',
        'Halo': 'Coordinates,Velocities,ParticleIDs,Masses',
        'Disk': 'Coordinates,Velocities,ParticleIDs,Masses',
        'Bulge': 'Coordinates,Velocities,ParticleIDs,Masses',
        'Stars': 'Coordinates,Velocities,ParticleIDs,Masses,StellarFormationTime,Metallicity',
        'Black Holes': 'Coordinates,Velocities,ParticleIDs,Masses,BlackHoleMass,BlackHoleAccretionRate'
    }

    # Filter the parameters based on the selected datatypes
    params = {key: value for key, value in all_params.items() if key in datatypes}

    if cube_size:
        params['size'] = cube_size  # Setting the size of the cutout in megaparsecs

    response = requests.get(BASE_URL + endpoint, headers=headers, params=params, stream=True)

    #logging.debug("Downloading cutout data:")
    #logging.debug(f"Request URL: {response.url}")
    #logging.debug(f"Status Code: {response.status_code}")
    #logging.debug(f"Response Headers: {response.headers}")
    if response.status_code == 200:
        object_prefix = "subhalo" if is_subhalo else "halo"
        filename = f"{object_prefix}_{object_id}_cutout.hdf5"
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        messagebox.showinfo("Success", f"Data downloaded successfully! Check the file {filename}")
        print(f"Data downloaded successfully! Check the file {filename}")  # <-- Add this line
    else:
        messagebox.showerror("Error", f"An error occurred: {response.content.decode()}")
        print(f"An error occurred: {response.content.decode()}")  # <-- Add this line
def main():
    root = tk.Tk()
    root.title("IllustrisTNG Data Fetcher")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Entry for API key
    ttk.Label(frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    api_key_entry = ttk.Entry(frame)
    api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

    # Fetch and display available simulations
    simulations_combobox = ttk.Combobox(frame, state="readonly")
    simulations_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
    ttk.Label(frame, text="Select Simulation:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

    # Input fields for snapshot ID and object ID (either halo or subhalo)
    ttk.Label(frame, text="Snapshot ID:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    snapshot_id_entry = ttk.Entry(frame)
    snapshot_id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

    ttk.Label(frame, text="Object ID (Halo/Subhalo):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
    object_id_entry = ttk.Entry(frame)
    object_id_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

    # Entry for specifying cube size in megaparsecs
    ttk.Label(frame, text="Cube Size (Mpc, optional):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
    cube_size_entry = ttk.Entry(frame)
    cube_size_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

    # Listbox to display and select data types
    ttk.Label(frame, text="Data Types:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
    data_types_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE)
    data_types_listbox.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
    for datatype in fetch_data_types():
        data_types_listbox.insert(tk.END, datatype)

    # Checkbox to specify if the object is a subhalo (default) or halo
    is_subhalo_var = tk.BooleanVar(value=True)
    is_subhalo_checkbox = ttk.Checkbutton(frame, text="Is Subhalo?", variable=is_subhalo_var)
    is_subhalo_checkbox.grid(row=6, column=0, columnspan=2, padx=5, pady=5)


  
    def fetch_data():
        #logging.debug("Fetching data...")
        api_key = api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your API key.")
            return

        simulation_name = simulations_combobox.get()
        snapshot_id = snapshot_id_entry.get()
        object_id = object_id_entry.get()
        cube_size = cube_size_entry.get().strip()
        if cube_size:
            cube_size = f"{cube_size}Mpc"
        selected_data_types = data_types_listbox.curselection()
        datatypes = [data_types_listbox.get(i) for i in selected_data_types]
        is_subhalo = is_subhalo_var.get()
        download_cutout(api_key, simulation_name, snapshot_id, object_id, datatypes, is_subhalo, cube_size)


    def populate_simulations():
        #logging.debug("Populating simulations...")
        api_key = api_key_entry.get().strip()
        simulations = fetch_simulations(api_key)
        simulations_combobox['values'] = [sim['name'] for sim in simulations]

    # Button to populate simulations
    populate_button = ttk.Button(frame, text="Load Simulations", command=populate_simulations)
    populate_button.grid(row=1, column=2, padx=5)

    # Fetch data button
    fetch_button = ttk.Button(frame, text="Fetch Data", command=fetch_data)
    fetch_button.grid(row=7, column=0, columnspan=2, pady=20)

    root.mainloop()

def list_simulations(api_key):
    """List available simulations in the terminal."""
    simulations = fetch_simulations(api_key)
    print("Available Simulations:")
    for sim in simulations:
        print(f"- {sim['name']}")

def read_params_from_file(filename):
    """Read multiple parameter sets from a file, with improved error handling."""
    param_sets = []
    try:
        with open(filename, 'r') as f:
            param_set = {}
            for line in f:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                if line == '---':
                    param_sets.append(param_set)
                    param_set = {}
                    continue
                
                # Split by colon and ensure there are two parts
                parts = line.split(":")
                if len(parts) != 2:
                    print(f"Unexpected format in line: {line}")
                    continue
                
                key, value = parts
                param_set[key.strip()] = value.strip()
            if param_set:  # Add the last set if not empty
                param_sets.append(param_set)
        return param_sets
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

        
if __name__ == "__main__":


    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Download data from the TNG API.")
    parser.add_argument("--param_file", type=str, help="Path to the parameter file.")
    parser.add_argument("--GUI", type=bool, default=False, help="Launch the GUI.")
    parser.add_argument("--api_key", type=str, help="Your API key.")
    parser.add_argument("--simulation", type=str, help="Name of the simulation (e.g., TNG50-1).")
    parser.add_argument("--snapshot", type=int, help="Snapshot number.")
    parser.add_argument("--subhalo_id", type=int, help="ID of the subhalo.")
    parser.add_argument("--parts", type=str, help="Comma-separated list of parts to download (e.g., PartType0,PartType4).")

    args = parser.parse_args()

    if args.GUI or len(sys.argv) == 1:
        main()

    elif args.param_file:
        param_sets = read_params_from_file(args.param_file)
        if param_sets:
            api_key = param_sets[0].get('api_key')  # Assuming API key is in the first set
            for param_set in param_sets:
                param_set['api_key'] = api_key  # Set API key for all sets
                set_args = argparse.Namespace(**param_set)
                if all([set_args.api_key, set_args.simulation, set_args.snapshot, set_args.subhalo_id, set_args.parts]):
                    parts = set_args.parts.split(",")
                    download_cutout(set_args.api_key, set_args.simulation, set_args.snapshot, set_args.subhalo_id, parts)

    # If individual command line arguments are provided
    elif any([args.api_key, args.simulation, args.snapshot, args.subhalo_id, args.parts]):
        if args.api_key and not any([args.simulation, args.snapshot, args.subhalo_id, args.parts]):
            list_simulations(args.api_key)
            sys.exit(0)  # Exit after listing simulations

        elif all([args.api_key, args.simulation, args.snapshot, args.subhalo_id, args.parts]):
            parts = args.parts.split(",")
            download_cutout(args.api_key, args.simulation, args.snapshot, args.subhalo_id, parts)
            sys.exit(0)  # Exit the script after terminal usage