import numpy as np
import torch
from torch.nn.utils.rnn import pad_sequence

def flatten_with_structure(data, delimiter=-9999):
    """Flattens a nested list while preserving the structure with delimiters."""
    flattened_list = []
    
    def recursive_flatten(sublist):
        if isinstance(sublist, list):
            # Add delimiter to mark the start of a sublist
            flattened_list.append(delimiter)
            for item in sublist:
                recursive_flatten(item)
            # Add delimiter to mark the end of a sublist
            flattened_list.append(delimiter)
        else:
            # If it's not a list, just append the value
            flattened_list.append(sublist)
    
    recursive_flatten(data)
    return flattened_list

def flatten_and_pad_sequences(input_data):
    """
    Flattens and pads nested sequences to ensure they have the same length.

    Args:
        input_data (list): A nested list of sequences.

    Returns:
        torch.Tensor: A padded tensor of sequences.
    """
    # Flatten the nested structure
    flattened_input = [flatten_with_structure(sequence) for sequence in input_data]

    # Convert to tensors
    tensor_sequences = [torch.tensor(seq, dtype=torch.float32) for seq in flattened_input]

    # Pad the sequences
    padded_sequences = pad_sequence(tensor_sequences, batch_first=True)

    return padded_sequences

# Example usage
input_data = [
    [[[0, [0, 0, 5]],[3, [1, 3, 5]],[2, [1, 3, 1]]], [[2, [1, 3, 1,3,2]],[2, [6, 3, 2,3,0]],[4, [1, 0, 1,3,2]]], [0,3,2,1,4,5,7,4]],
    [[[1, [4, 2, 5]],[2, [1, 3, 5]]], [[0, [4, 2, 1,3,2]],[3, [0, 0, 0,3,2]]], [0,0,2,1,3,6,5,7,4,3,2,1]]
]

padded_sequences = flatten_and_pad_sequences(input_data)
print("Padded Sequences:\n", padded_sequences)