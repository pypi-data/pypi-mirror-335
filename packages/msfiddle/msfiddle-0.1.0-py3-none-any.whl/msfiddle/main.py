import os
import argparse
from tqdm import tqdm
import yaml
import time
import sys

import numpy as np
import pandas as pd
from collections import OrderedDict

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from .dataset import MGFDataset
from .model_tcn import MS2FNet_tcn, FDRNet
from .utils.mol_utils import vector_to_formula, formula_to_vector
from .utils.msms_utils import mass_calculator
from .utils.refine_utils import formula_refinement
from .download import get_checkpoint_dir, check_models_exist, download_models


def test_step(model, loader, device): 
    model.eval()
    spec_ids = []
    y_pred = []
    exp_precursor_mz = []
    exp_precursor_type = []
    mass_pred = []
    atomnum_pred = []
    hcnum_pred = []
    with tqdm(total=len(loader)) as bar: 
        for _, batch in enumerate(loader): 
            spec_id, exp_pre_type, x, env, neutral_add = batch
            x = x.to(device, dtype=torch.float32)
            env = env.to(device, dtype=torch.float32)
            neutral_add = neutral_add.to(device, dtype=torch.float32)
            exp_pre_mz = env[:, 0]

            with torch.no_grad(): 
                _, pred_f, pred_mass, pred_atomnum, pred_hcnum = model(x, env)
            pred_f = pred_f - neutral_add # add the neutral adduct

            bar.set_description('Eval')
            bar.update(1)

            spec_ids = spec_ids + list(spec_id)
            y_pred.append(pred_f.detach().cpu())
            exp_precursor_mz.append(exp_pre_mz.detach().cpu())
            exp_precursor_type = exp_precursor_type + list(exp_pre_type)
            mass_pred.append(pred_mass.detach().cpu())
            atomnum_pred.append(pred_atomnum.detach().cpu())
            hcnum_pred.append(pred_hcnum.detach().cpu())

    y_pred = torch.cat(y_pred, dim = 0)
    exp_precursor_mz = torch.cat(exp_precursor_mz, dim = 0)
    mass_pred = torch.cat(mass_pred, dim = 0)
    atomnum_pred = torch.cat(atomnum_pred, dim = 0)
    hcnum_pred = torch.cat(hcnum_pred, dim = 0)
    return spec_ids, y_pred, exp_precursor_mz, exp_precursor_type, mass_pred, atomnum_pred, hcnum_pred


def rerank_by_fdr(fdr_model, spec, env, refined_results, device, K): 
    fdr_model.eval()

    refine_f = [f for f in refined_results['formula'] if f != None]
    refine_m = [m for m in refined_results['mass'] if m != None]
    if len(refine_f) == 0: 
        refined_results['fdr'] = [0.] * K
        return refined_results

    # convert refine_f (formula strings) to f (formula vectors)
    f = [formula_to_vector(f_str) for f_str in refine_f]
    f = torch.from_numpy(np.array(f))

    spec = spec.to(device, dtype=torch.float32).repeat(f.size(0), 1)
    env = env.to(device, dtype=torch.float32).repeat(f.size(0), 1)
    f = f.to(device, dtype=torch.float32)
    
    with torch.no_grad(): 
        fdr = fdr_model(spec, env, f)
        fdr = torch.sigmoid(fdr).detach().cpu().numpy()
    
    # Create a list of tuples with (fdr_value, refine_f_value, mass_value) pairs
    combined_list = list(zip(fdr, refine_f, refine_m))
    # Sort the combined list based on the fdr_value
    sorted_combined_list = sorted(combined_list, key=lambda x: x[0], reverse=True)
    # Unpack the sorted lists
    sorted_fdr, sorted_refine_f, sorted_mass = zip(*sorted_combined_list)
    sorted_fdr, sorted_refine_f, sorted_mass = list(sorted_fdr), list(sorted_refine_f), list(sorted_mass)

    # Pad sorted_refine_f and sorted_fdr with None if necessary
    if len(sorted_refine_f) < K: 
        sorted_refine_f += [None] * (K - len(sorted_refine_f))
        sorted_fdr += [0.] * (K - len(sorted_fdr))
        sorted_mass += [None] * (K - len(sorted_mass))

    return {'formula': sorted_refine_f, 'mass': sorted_mass, 'fdr': sorted_fdr}


def init_random_seed(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    return


def main(): 
    parser = argparse.ArgumentParser(description='msfiddle')
    
    # Define two exclusive argument groups
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--demo', action='store_true',
                      help='Run prediction on demo data')
    mode_group.add_argument('--test_data', type=str,
                      help='Path to data (.mgf)')
    
    # Add instrument type option
    parser.add_argument('--instrument_type', type=str, choices=['qtof', 'orbitrap'], default='orbitrap',
                      help='Instrument type: qtof or orbitrap (default: orbitrap)')
    
    # Add other required arguments
    parser.add_argument('--result_path', type=str, required=True,
                      help='Path to save predicted results')
    
    # Add optional arguments
    parser.add_argument('--buddy_path', type=str, default='', 
                      help='Path to saved BUDDY\'s results')
    parser.add_argument('--sirius_path', type=str, default='', 
                      help='Path to saved SIRIUS\'s results')
    parser.add_argument('--seed', type=int, default=42,
                      help='Seed for random functions')
    parser.add_argument('--device', type=int, nargs='+', default=[0], 
                      help='Which GPUs to use if any (default: [0]). Accepts multiple values separated by space.')
    parser.add_argument('--no_cuda', action='store_true', 
                      help='Disables CUDA')
    
    # Add advanced arguments for custom configurations
    advanced_group = parser.add_argument_group('Advanced options')
    advanced_group.add_argument('--config_path', type=str,
                      help='Custom path to configuration (.yaml)')
    advanced_group.add_argument('--resume_path', type=str,
                      help='Custom path to pretrained TCN model')
    advanced_group.add_argument('--fdr_resume_path', type=str,
                      help='Custom path to pretrained FDR model')
    
    args = parser.parse_args()
    
    # Initialize random seed
    init_random_seed(args.seed)
    start_time = time.time()
    
    # Get package directory
    package_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Make sure models are downloaded
    if not check_models_exist():
        print("Pre-trained models not found. Downloading now...")
        download_models()
        print("Models downloaded successfully.")
    
    # Set default paths based on mode and instrument type
    if args.demo:
        test_data_path = os.path.join(package_dir, 'demo', 'input_msms.mgf')
        print(f"Using demo data: {test_data_path}")
    else:
        test_data_path = args.test_data
        print(f"Using custom data: {test_data_path}")
    
    # Set paths based on instrument type
    instrument_suffix = args.instrument_type
    
    # Set config path
    if args.config_path:
        config_path = args.config_path
    else:
        config_path = os.path.join(package_dir, 'config', f'fiddle_tcn_{instrument_suffix}.yml')
    print(f"Using config: {config_path}")
    
    # Set model paths
    checkpoint_dir = get_checkpoint_dir()
    
    if args.resume_path:
        resume_path = args.resume_path
    else:
        resume_path = os.path.join(checkpoint_dir, f'fiddle_tcn_{instrument_suffix}.pt')
    print(f"Using TCN model: {resume_path}")
    
    if args.fdr_resume_path:
        fdr_resume_path = args.fdr_resume_path
    else:
        fdr_resume_path = os.path.join(checkpoint_dir, f'fiddle_fdr_{instrument_suffix}.pt')
    print(f"Using FDR model: {fdr_resume_path}")
    
    # Load config
    with open(config_path, 'r') as f: 
        config = yaml.load(f, Loader=yaml.FullLoader)
    print('Loaded model & training configuration from {}'.format(config_path))

    # Set device
    device_1st = torch.device("cuda:" + str(args.device[0])) if torch.cuda.is_available() and not args.no_cuda else torch.device("cpu")
    print(f'Device(s): {args.device}')

    # 1. Data
    valid_set = MGFDataset(test_data_path, config['encoding'])
    valid_loader = DataLoader(
                    valid_set,
                    batch_size=1, 
                    shuffle=False, 
                    num_workers=0, 
                    drop_last=True)

    # 2. Model
    # 2.1 MS2F
    model = MS2FNet_tcn(config['model']).to(device_1st)
    num_params = sum(p.numel() for p in model.parameters())
    print(f'# MS2FNet_tcn Params: {num_params}')
    if len(args.device) > 1: # Wrap the model with nn.DataParallel
        model = nn.DataParallel(model, device_ids=args.device)

    print('Loading the formula prediction model...')
    state_dict = torch.load(resume_path, map_location=device_1st, weights_only=False)['model_state_dict']
    is_multi_gpu = any(key.startswith('module.') for key in state_dict.keys())
    if is_multi_gpu and len(args.device) == 1: # Convert the model to single GPU
        new_state_dict = OrderedDict()
        for key, value in state_dict.items():
            if key.startswith('module.'):
                new_key = key[7:]  # Remove the 'module.' prefix
                new_state_dict[new_key] = value
            else:
                new_state_dict[key] = value
        model.load_state_dict(new_state_dict)
    else:
        model.load_state_dict(state_dict)

    # 2.2 FDR
    fdr_model = FDRNet(config['model']).to(device_1st)
    num_params = sum(p.numel() for p in fdr_model.parameters())
    print(f'# FDRNet Params: {num_params}')    
    if len(args.device) > 1: # Wrap the model with nn.DataParallel
        fdr_model = nn.DataParallel(fdr_model, device_ids=args.device)

    print('Loading the FDR prediction model...')
    state_dict = torch.load(fdr_resume_path, map_location=device_1st, weights_only=False)['model_state_dict']
    is_multi_gpu = any(key.startswith('module.') for key in state_dict.keys())
    if is_multi_gpu and len(args.device) == 1: # Convert the fdr_model to single GPU
        new_state_dict = OrderedDict()
        for key, value in state_dict.items(): 
            if key.startswith('module.'):
                new_key = key[7:]  # Remove the 'module.' prefix
                new_state_dict[new_key] = value
            else:
                new_state_dict[key] = value
        fdr_model.load_state_dict(new_state_dict)
    else:
        fdr_model.load_state_dict(state_dict)
    
    # 3. Formula Prediction
    spec_ids, y_pred, exp_precursor_mz, exp_precursor_type, mass_pred, atomnum_pred, hcnum_pred = test_step(model, valid_loader, device_1st)

    prediction_time = time.time() - start_time
    prediction_time /= len(valid_set)

    formula_pred = [vector_to_formula(y) for y in y_pred] # calculate the formula strings
    y_pred = [';'.join(y) for y in y_pred.numpy().astype('str')]

    spectra = []
    environments = []
    for batch in valid_loader:  
        _, _, spec, env, _ = batch
        spectra.append(spec)
        environments.append(env)

    # 4. Post-processing
    if args.buddy_path != '':
        buddy_df = pd.read_csv(args.buddy_path)
    if args.sirius_path != '':
        sirius_df = pd.read_csv(args.sirius_path)

    formula_redined = {'Refined Formula ({})'.format(str(k)): [] for k in range(config['post_processing']['top_k'])}
    mass_redined = {'Refined Mass ({})'.format(str(k)): [] for k in range(config['post_processing']['top_k'])}
    fdr_refined = {'FDR ({})'.format(str(k)): [] for k in range(config['post_processing']['top_k'])}
    running_time = []
    exp_mass = []
    # Please note that here we use the experimental precursor m/z, rather than the theoretic precursor m/z. 
    for idx, pred_f, exp_pre_mz, exp_pre_type, spec, env in tqdm(zip(spec_ids, 
                                                             formula_pred, 
                                                             exp_precursor_mz, 
                                                             exp_precursor_type, spectra, environments), total=len(exp_precursor_mz), desc='Post'): 
        m = mass_calculator(exp_pre_type, exp_pre_mz) # Use experimental precursor m/z and precursor type to calculate molmass
        exp_mass.append(m.item())

        f0_list = [pred_f]
        if args.buddy_path != '' and len(buddy_df.loc[buddy_df['ID'] == idx]) > 0: 
            buddy_f = buddy_df.loc[buddy_df['ID'] == idx].iloc[0][['Pred Formula (1)', 
                                                                        'Pred Formula (2)', 
                                                                        'Pred Formula (3)',
                                                                        'Pred Formula (4)', 
                                                                        'Pred Formula (5)',]].tolist()
            buddy_fdr = buddy_df.loc[buddy_df['ID'] == idx].iloc[0][['BUDDY Score (1)', 
                                                                        'BUDDY Score (2)', 
                                                                        'BUDDY Score (3)',
                                                                        'BUDDY Score (4)', 
                                                                        'BUDDY Score (5)',]].tolist()
            buddy_f = [x for x, fdr in zip(buddy_f, buddy_fdr) if str(x) != 'nan' and fdr < config['post_processing']['buddy_fdr_thr']]
            f0_list.extend(buddy_f)
        if args.sirius_path != '': 
            sirius_f = sirius_df.loc[sirius_df['ID'] == idx].iloc[0][['Pred Formula (1)', 
                                                                        'Pred Formula (2)', 
                                                                        'Pred Formula (3)',
                                                                        'Pred Formula (4)', 
                                                                        'Pred Formula (5)',]].tolist()
            sirius_score = sirius_df.loc[sirius_df['ID'] == idx].iloc[0][['SIRIUS Score (1)', 
                                                                        'SIRIUS Score (2)', 
                                                                        'SIRIUS Score (3)',
                                                                        'SIRIUS Score (4)', 
                                                                        'SIRIUS Score (5)',]].tolist()
            sirius_f = [x for x, score in zip(sirius_f, sirius_score) if str(x) != 'nan' and score > config['post_processing']['sirius_score_thr']]
            f0_list.extend(sirius_f)

        f0_list = list(set(f0_list)) # deduplicates
        start_time = time.time()
        refined_results = formula_refinement(f0_list, m.item(), 
                                            config['post_processing']['mass_tolerance'], 
                                            config['post_processing']['ppm_mode'], 
                                            config['post_processing']['top_k'], 
                                            config['post_processing']['maxium_miss_atom_num'], 
                                            config['post_processing']['time_out'], 
                                            config['post_processing']['refine_atom_type'],
                                            config['post_processing']['refine_atom_num'],
                                            )

        # Rerank the results by predicted FDR
        refined_results = rerank_by_fdr(fdr_model, spec, env, refined_results, device_1st, config['post_processing']['top_k'])

        for i, (refined_f, refined_m, refined_fdr) in enumerate(zip(refined_results['formula'], refined_results['mass'], refined_results['fdr'])): 
            formula_redined[f'Refined Formula ({i})'].append(refined_f)
            mass_redined[f'Refined Mass ({i})'].append(refined_m)
            fdr_refined[f'FDR ({i})'].append(refined_fdr)
        refinement_time = time.time() - start_time
        running_time.append(prediction_time + refinement_time)

    # 5. Save the final results
    print('\nSaving predicted results...')
    out_dict = {'ID': spec_ids, 'Y Pred': y_pred, 'Mass': exp_mass, 
                'Pred Formula': formula_pred, 'Pred Mass': mass_pred.tolist(), 
                'Pred Atom Num': atomnum_pred.tolist(), 'Pred H/C Num': hcnum_pred.tolist(), 
                'Running Time': running_time}
    res_df = pd.DataFrame({**out_dict, **formula_redined, **mass_redined, **fdr_refined})
    res_df.to_csv(args.result_path, index=False)
    print(f'Done! Results saved to {args.result_path}')


if __name__ == "__main__":
    main()