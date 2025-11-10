#!/usr/bin/env python
"""
Test script to verify photo export functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Form, Group
import sqlalchemy as sa
import zipfile
import io
import filetype

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("TESTING PHOTO EXPORT")
    print("="*80)
    
    # Get group 1
    group = db.session.get(Group, 1)
    if not group:
        print("❌ Group 1 not found!")
        sys.exit(1)
    
    print(f"\n📊 Group: {group.name}")
    print(f"   Current Count: {group.current_count}")
    
    # Get all forms for this group
    query = sa.select(Form).where(Form.group_id == 1).order_by(Form.submitted_at.desc())
    forms = db.session.scalars(query).all()
    
    print(f"\n📊 Forms found: {len(forms)}")
    
    if not forms:
        print("❌ No forms found for this group!")
        sys.exit(1)
    
    # Check which forms have images
    upload_path = app.config['UPLOAD_PATH']
    print(f"\n📁 Upload path: {upload_path}")
    
    forms_with_images = 0
    forms_without_images = 0
    
    for form in forms:
        image_path = os.path.join(upload_path, form.id)
        if os.path.exists(image_path):
            forms_with_images += 1
            file_size = os.path.getsize(image_path)
            kind = filetype.guess(image_path)
            ext = kind.extension if kind else "unknown"
            print(f"   ✅ {form.first_name} {form.last_name}: {file_size} bytes ({ext})")
        else:
            forms_without_images += 1
            print(f"   ❌ {form.first_name} {form.last_name}: IMAGE NOT FOUND at {image_path}")
    
    print(f"\n📊 Summary:")
    print(f"   Forms with images: {forms_with_images}")
    print(f"   Forms without images: {forms_without_images}")
    
    if forms_with_images == 0:
        print("\n❌ No images found! Cannot create ZIP file.")
        sys.exit(1)
    
    # Try to create ZIP file
    print("\n📦 Creating ZIP file...")
    zip_buffer = io.BytesIO()
    files_added = 0
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for form in forms:
                image_path = os.path.join(upload_path, form.id)
                
                if os.path.exists(image_path):
                    # Create filename
                    filename = f"{form.first_name}_{form.last_name}_{form.id[:8]}"
                    
                    # Get file extension
                    kind = filetype.guess(image_path)
                    if kind:
                        filename += f".{kind.extension}"
                    else:
                        filename += ".png"
                    
                    # Add file to ZIP
                    with open(image_path, 'rb') as f:
                        data = f.read()
                        zip_file.writestr(filename, data)
                        files_added += 1
                        print(f"   ✅ Added: {filename} ({len(data)} bytes)")
        
        zip_buffer.seek(0)
        zip_size = len(zip_buffer.getvalue())
        
        print(f"\n✅ ZIP file created successfully!")
        print(f"   Files added: {files_added}")
        print(f"   ZIP size: {zip_size} bytes")
        
        # Save ZIP file for testing
        test_zip_path = os.path.join(os.path.dirname(__file__), 'test_export.zip')
        with open(test_zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        print(f"\n💾 Test ZIP saved to: {test_zip_path}")
        print("   You can open this file to verify it works!")
        
    except Exception as e:
        print(f"\n❌ Error creating ZIP file: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)

