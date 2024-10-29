import cloudinary
# Import the cloudinary.api for managing assets
import cloudinary.api
# Import the cloudinary.uploader for uploading assets
import cloudinary.uploader

result = cloudinary.api.resource_by_asset_id("5a6c6623531728db1713f77cf302f966")
print(result)