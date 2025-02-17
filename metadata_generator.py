import pandas as pd
from pathlib import Path
import os
from PIL import Image
from datetime import datetime
import logging

class ParenteralMetadataGenerator:
    def __init__(self, image_dir):
        self.image_dir = Path(image_dir)
        self.metadata_dir = Path("./metadata")
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Set up logging
        log_path = self.metadata_dir / 'processing.log'
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('ParenteralMetadataGenerator')
        
    def verify_images(self):
        """Verify all images in directory and return detailed counts"""
        all_image_files = list(self.image_dir.glob("*.[jJ][pP][gG]"))
        total_images = len(all_image_files)
        
        self.logger.info(f"Found {total_images} total image files")
        
        # Test opening each image
        successful = []
        failed = []
        
        for img_path in all_image_files:
            try:
                with Image.open(img_path) as img:
                    img.verify()  # Verify image integrity
                    successful.append(img_path)
                    self.logger.info(f"Successfully verified: {img_path.name}")
            except Exception as e:
                failed.append((img_path, str(e)))
                self.logger.error(f"Failed to process: {img_path.name} - Error: {str(e)}")
        
        return {
            'total_files': total_images,
            'successful': successful,
            'failed': failed
        }
        
    def generate_base_metadata(self):
        """Generate basic metadata from image files with detailed error tracking"""
        verification = self.verify_images()
        metadata_records = []
        
        print("\nImage Verification Summary:")
        print(f"Total image files found: {verification['total_files']}")
        print(f"Successfully processed: {len(verification['successful'])}")
        print(f"Failed to process: {len(verification['failed'])}")
        
        if verification['failed']:
            print("\nFailed Images:")
            for failed_img, error in verification['failed']:
                print(f"- {failed_img.name}: {error}")
        
        # Process verified images
        for img_path in verification['successful']:
            try:
                with Image.open(img_path) as img:
                    record = {
                        'file_name': img_path.name,
                        'medication_name': '',
                        'generic_name': '',
                        'concentration': '',
                        'volume_ml': '',
                        'manufacturer': '',
                        'ndc_code': '',
                        'lot_number': '',
                        'expiration_date': '',
                        'storage_requirements': '',
                        'image_width': img.size[0],
                        'image_height': img.size[1],
                        'image_format': img.format,
                        'file_size_kb': round(os.path.getsize(img_path) / 1024, 2),
                        'date_added': datetime.now().strftime('%Y-%m-%d'),
                        'last_modified': datetime.fromtimestamp(os.path.getmtime(img_path)).strftime('%Y-%m-%d'),
                        'processing_status': 'success',
                        'notes': ''
                    }
                    metadata_records.append(record)
            except Exception as e:
                self.logger.error(f"Error during metadata extraction for {img_path}: {e}")
                
        return pd.DataFrame(metadata_records)

    def save_metadata(self, filename='parenteral_metadata.csv'):
        """Save metadata to CSV file with verification report"""
        metadata_df = self.generate_base_metadata()
        output_path = self.metadata_dir / filename
        metadata_df.to_csv(output_path, index=False)
        
        # Save verification report
        verification_path = self.metadata_dir / 'verification_report.txt'
        with open(verification_path, 'w') as f:
            f.write(f"Verification Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total images in directory: {len(list(self.image_dir.glob('*.[jJ][pP][gG]')))}\n")
            f.write(f"Successfully processed images: {len(metadata_df)}\n")
            f.write(f"Processing rate: {(len(metadata_df)/len(list(self.image_dir.glob('*.[jJ][pP][gG]')))*100):.2f}%\n")
            
        return metadata_df

# Example usage
if __name__ == "__main__":
    generator = ParenteralMetadataGenerator("./Parenterals")
    metadata_df = generator.save_metadata()
    
    print("\nProcessing complete!")
    print(f"Check {generator.metadata_dir.absolute()} for:")
    print("- parenteral_metadata.csv (main metadata file)")
    print("- verification_report.txt (detailed processing report)")
    print("- processing.log (detailed processing log)")