#!/usr/bin/env python3

import pandas as pd
from pathlib import Path
import os
from PIL import Image
from datetime import datetime
import re

class ParenteralMetadataGenerator:
    def __init__(self, image_dir):
        self.image_dir = Path(image_dir)
        self.metadata_dir = Path("./metadata")
        self.metadata_dir.mkdir(exist_ok=True)
        
    def scan_directory(self):
        """Recursively scan directory and collect image information"""
        image_data = []
        total_files = 0
        processed_files = 0
        error_files = 0

        # Walk through directory
        for root, _, files in os.walk(self.image_dir):
            for filename in files:
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    total_files += 1
                    filepath = Path(root) / filename
                    try:
                        if filepath.is_file():  # Verify it's actually a file
                            with Image.open(filepath) as img:
                                # Extract directory name as category
                                category = Path(root).relative_to(self.image_dir).parts[0] if len(Path(root).relative_to(self.image_dir).parts) > 0 else "uncategorized"
                                
                                # Basic image properties
                                record = {
                                    'category': category,
                                    'file_name': filename,
                                    'relative_path': str(filepath.relative_to(self.image_dir)),
                                    'image_width': img.size[0],
                                    'image_height': img.size[1],
                                    'image_format': img.format,
                                    'file_size_kb': round(os.path.getsize(filepath) / 1024, 2),
                                    'date_added': datetime.now().strftime('%Y-%m-%d'),
                                    'last_modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d'),
                                    'notes': ''
                                }
                                
                                # Parse filename for additional info
                                concentration_match = re.search(r'(\d+(?:\.\d+)?(?:mg|ml))', filename)
                                if concentration_match:
                                    record['concentration'] = concentration_match.group(1)
                                else:
                                    record['concentration'] = ''
                                
                                image_data.append(record)
                                processed_files += 1
                                print(f"Processed: {filepath.relative_to(self.image_dir)}")
                            
                    except Exception as e:
                        error_files += 1
                        print(f"Error processing {filepath}: {str(e)}")
        
        print(f"\nProcessing Summary:")
        print(f"Total files found: {total_files}")
        print(f"Successfully processed: {processed_files}")
        print(f"Errors encountered: {error_files}")
        
        return image_data

    def save_metadata(self, filename='parenteral_metadata.csv'):
        """Save metadata to CSV file"""
        metadata_records = self.scan_directory()
        if not metadata_records:
            print("No files were processed successfully.")
            return None
            
        metadata_df = pd.DataFrame(metadata_records)
        output_path = self.metadata_dir / filename
        metadata_df.to_csv(output_path, index=False)
        print(f"\nMetadata saved to {output_path}")
        print(f"Total images processed: {len(metadata_df)}")
        return metadata_df
    
    def create_excel_template(self, filename='parenteral_metadata.xlsx'):
        """Create an Excel template with data validation and formatting"""
        metadata_records = self.scan_directory()
        if not metadata_records:
            print("No files were processed successfully.")
            return None
            
        metadata_df = pd.DataFrame(metadata_records)
        output_path = self.metadata_dir / filename
        
        # Create Excel writer object
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Metadata']
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'bg_color': '#D9E1F2',
            'border': 1
        })
        
        # Format headers
        for col_num, value in enumerate(metadata_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
        
        # Save the Excel file
        writer.close()
        print(f"Excel template saved to {output_path}")
        return metadata_df

if __name__ == "__main__":
    # Initialize generator with your image directory
    generator = ParenteralMetadataGenerator("./Parenterals")
    
    # Generate both CSV and Excel files
    metadata_df = generator.save_metadata()
    template_df = generator.create_excel_template()
    
    print("\nMetadata generation complete!")
    print(f"Files have been saved to: {generator.metadata_dir.absolute()}")