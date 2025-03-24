import os
import json
import torch
import matplotlib.pyplot as plt

def print_query_result(idx, data_pt, pt_expected, pt_dec):
    print(f'{pt_expected.shape=} {pt_dec.shape=}')
    print(f'{pt_dec=}')
    print(f'{pt_expected=}')

    # Visualize
    plt.figure()
    plt.imshow(data_pt.reshape(28, 28), cmap="gray")
    plt.title(f"idx={idx}\nhom prediction: {pt_dec.argmax()}")
    plt.axis("off")
    plt.show()

    # Verify similarity
    torch.testing.assert_close(
            pt_expected, pt_dec,
            rtol=1 / 2**9, atol=1 / 2**9
        )
    print("Homomorphic and clear outputs are close.\n")



def load_e2e_config() -> tuple:
    """
    Locate the e2e.json file relative to the calling script, load its content, 
    and return both the file path and the loaded configuration.
    :return: A tuple containing the config file path and the configuration dictionary.
    """
    # Get the directory of the calling script
    current_script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Construct the path to e2e.json relative to the calling script's directory
    config_path = os.path.join(current_script_dir, '../../../e2e.json')
    
    print(f'Searching for config file at: {config_path}')
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            return config_path, config
    except FileNotFoundError:
        raise FileNotFoundError(f"e2e.json file not found at: {config_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse JSON from the config file at: {config_path}")
