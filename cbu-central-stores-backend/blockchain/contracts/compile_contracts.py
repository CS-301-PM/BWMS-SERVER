import json
import os
from pathlib import Path
from solcx import compile_standard, install_solc

# Install a specific Solidity compiler version
install_solc('0.8.19')

def compile_contract():
    # Define the path to the contract
    contract_path = Path(__file__).parent / "StreamlinedStoresManager.sol"

    # Read the Solidity source code
    with open(contract_path, "r") as file:
        source_code = file.read()

    # Prepare the compilation input
    compilation_input = {
        "language": "Solidity",
        "sources": {
            "StreamlinedStoresManager.sol": {
                "content": source_code
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        }
    }

    # Compile the contract
    compiled_output = compile_standard(compilation_input)

    # Get the contract ABI and Bytecode
    contract_data = compiled_output['contracts']['StreamlinedStoresManager.sol']['StreamlinedStoresManager']
    abi = contract_data['abi']
    bytecode = contract_data['evm']['bytecode']['object']

    # Create a directory for the build artifacts if it doesn't exist
    build_dir = Path(__file__).parent / "build"
    build_dir.mkdir(exist_ok=True)

    # Save the ABI and Bytecode to a JSON file
    with open(build_dir / "StreamlinedStoresManager.json", "w") as file:
        json.dump({"abi": abi, "bytecode": bytecode}, file, indent=4)

    print("Contract compiled successfully! ABI and Bytecode saved to build/ directory.")
    return abi, bytecode

if __name__ == "__main__":
    compile_contract()