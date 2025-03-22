import os
import sys
import json
import base64

def convert_image_to_base64(image_path):
    """
    Convert image file to base64 string
    """
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_lottie_json(input_json_path, output_json_path):
    """
    Process Lottie JSON file to inline image resources as base64
    """
    
    # Read input JSON
    with open(input_json_path, 'r', encoding='utf-8') as file:
        lottie_data = json.load(file)
    
    # Get directory of input JSON to resolve relative paths
    json_dir = os.path.dirname(input_json_path)
    
    # Process assets
    if 'assets' in lottie_data:
        for asset in lottie_data['assets']:
            if 'u' in asset and 'p' in asset:
                # Construct full image path
                image_path = os.path.join(json_dir, asset['u'], asset['p'])
                
                if os.path.exists(image_path):
                    # Convert image to base64
                    base64_data = convert_image_to_base64(image_path)
                    
                    # Replace path with base64 data
                    asset['u'] = ""
                    asset['p'] = "data:image/png;base64," + base64_data
                    # Set the asset to be embedded
                    asset['e'] = 1
                else:
                    print(f"Warning: Image not found at {image_path}")
    
    # Write output JSON
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(lottie_data, file)

def main():
    args = sys.argv[1:]
    
    if len(args) < 2:
        print('Usage: python main.py <input> <output>', file=sys.stderr)
        sys.exit(1)
    
    process_lottie_json(args[0], args[1])

if __name__ == '__main__':
    main()
