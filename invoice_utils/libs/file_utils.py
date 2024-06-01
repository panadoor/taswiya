import os
from datetime import datetime

def get_file_name_and_extension(file_path):
    """
    Extracts the file name and extension from a given file path.
   
    Parameters:
    file_path (str): The full file name with extension.
    
    Returns:
    tuple: A tuple containing the file name and the extension.
    """
    # Extract file name and extension
    file_name_with_ext = os.path.basename(file_path)
    file_name, file_extension = os.path.splitext(file_name_with_ext)
    
    # Remove leading and trailing spaces from file name and extension
    file_name = file_name.strip()
    file_name = file_name.replace('.', '_').replace(' ', '_')
    file_extension = file_extension.strip()
    
    # Return file name and extension
    return file_name, file_extension

# Function to convert date format from YYYYMMDD to DD.MM.YYYY
def convert_date_format(date_str):
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    return date_obj.strftime("%d.%m.%Y")

def rename_files(directory, rename=False):
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        # Construct the full file path
        old_file_path = os.path.join(directory, filename)
        
        # Skip directories
        if os.path.isdir(old_file_path) or (not filename.endswith('.pdf')) \
                or (not filename.startswith('FA')):
            continue

        # Example usage
        file_path = "example.file.name with spaces .txt"
        file_name, extension = get_file_name_and_extension(filename)
        #print(f"File name: '{file_name}'")
        #print(f"File extension: '{extension}'")

        # Split the filename into parts
        parts = file_name.split('_')

        # Check if the filename starts with "Facture"
        """ if parts[0] == "Facture":
            facture_number = parts[1]
            date_str = parts[2]
            company_name = '_'.join(parts[3:-1]) + '_' + parts[-1].split('.')[0]
            extension = parts[-1].split('.')[-1]
        else:"""

        facture_number = parts[0]
        company_name = '_'.join(parts[1:-1]) #+ '_' + parts[-1].split('.')[0]
        date_str = parts[-1]
        #extension = parts[-1].split('.')[-1]

        # Convert the date to the desired format
        try:
            formatted_date = convert_date_format(date_str)
        except ValueError:
            continue

        # Construct the new filename
        new_filename = f"{facture_number}_{company_name}_{formatted_date}{extension}"
        
        # Construct the full new file path
        new_file_path = os.path.join(directory, new_filename)
        
        # Rename the file
        if rename:
            os.rename(old_file_path, new_file_path)
        
        print(f"{filename} -> {new_filename}")

    print("Renaming completed.")