import cloudinary
import cloudinary.api
import cloudinary.uploader

from flask import current_app

class CloudinaryUtil:
    def __init__(self):
        # Configure Cloudinary using current_app's configuration
        cloudinary.config(
            cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=current_app.config['CLOUDINARY_API_KEY'],
            api_secret=current_app.config['CLOUDINARY_API_SECRET']
        )

    def upload_image(self, file):
        """Uploads a file-like object directly to Cloudinary and returns asset_id and URL."""
        try:
            result = cloudinary.uploader.upload(file)
            # print(result)
            # Extract asset_id and URL
            asset_id = result.get("asset_id")
            url = result.get("url")
            return {"asset_id": asset_id, "url": url}
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            return None

    def list_resources(self, page=1, page_size=10,next_cursor=None):
        """Lists uploaded resources from Cloudinary with pagination."""
        try:
            resources = cloudinary.api.resources(
                pages=True,
                type='upload',
                max_results=page_size,
                next_cursor=next_cursor
            )
            #print(resources)
            # Extract necessary information
            file_list = [{'public_id': res['public_id'], 'url': res['secure_url']} for res in resources['resources']]
            
            # Prepare pagination info
            total_count = resources.get('total_count', 0)
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages
            
            return {
                'files': file_list,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'next_cursor':resources['next_cursor']
                }
            }
        except cloudinary.exceptions.Error as e:
            print(f"Cloudinary error: {e}")
            return {'error': str(e)}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {'error': 'An unexpected error occurred: ' + str(e)}
