#!/usr/bin/env python
"""
Fake data generator for testing the form submission system.
Generates fake form submissions for a given group link.
"""

import os
import sys
import random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
import io

# Add the app to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, create_app
from app.models import Form, Link
import secrets

# Sample data
FIRST_NAMES = [
    'John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'James', 'Jessica',
    'Robert', 'Jennifer', 'William', 'Linda', 'Richard', 'Barbara', 'Joseph', 'Susan',
    'Thomas', 'Jessica', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas',
    'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White'
]

EYE_COLORS = ['brown', 'blue', 'green', 'hazel', 'gray', 'black']
HAIR_COLORS = ['black', 'brown', 'blonde', 'red', 'gray', 'white']
GENDERS = ['male', 'female', 'other']
STATES = ['MN', 'CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC']
CITIES = ['Minneapolis', 'Los Angeles', 'Houston', 'Miami', 'New York', 'Philadelphia', 'Chicago', 'Columbus', 'Atlanta', 'Charlotte']

def generate_fake_image(name):
    """Generate a simple fake image with the person's name"""
    img = Image.new('RGB', (200, 250), color=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple circle for head
    draw.ellipse([50, 20, 150, 120], fill=(200, 150, 100))
    
    # Draw text
    draw.text((20, 150), f"Name: {name}", fill=(0, 0, 0))
    draw.text((20, 170), f"ID Photo", fill=(0, 0, 0))
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def generate_fake_submission(link_id, group_id=None):
    """Generate a single fake form submission"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    form_id = secrets.token_urlsafe(16)
    
    form = Form(
        id=form_id,
        link_id=link_id,
        first_name=first_name,
        middle_name=random.choice([None, random.choice(FIRST_NAMES)]),
        last_name=last_name,
        eye_color=random.choice(EYE_COLORS),
        hair_color=random.choice(HAIR_COLORS),
        address=f"{random.randint(100, 9999)} Main St",
        date_of_birth=datetime.now() - timedelta(days=random.randint(18*365, 80*365)),
        height=random.uniform(150, 200),
        weight=random.uniform(50, 120),
        gender=random.choice(GENDERS),
        state=random.choice(STATES),
        city=random.choice(CITIES),
        zip_code=f"{random.randint(10000, 99999)}",
        organ_donor=random.choice([True, False]),
        restrictions_corrective_lenses=random.choice([True, False]),
        group_id=group_id
    )
    
    # Generate and save fake image
    img_bytes = generate_fake_image(f"{first_name} {last_name}")
    upload_path = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(upload_path, exist_ok=True)
    
    with open(os.path.join(upload_path, form_id), 'wb') as f:
        f.write(img_bytes.getvalue())
    
    return form

def main():
    app = create_app()
    
    with app.app_context():
        if len(sys.argv) < 3:
            print("Usage: python generate_fake_data.py <link_id> <count>")
            print("Example: python generate_fake_data.py abc123def456 5")
            sys.exit(1)
        
        link_id = sys.argv[1]
        count = int(sys.argv[2])
        
        # Verify link exists
        link = db.session.get(Link, link_id)
        if not link:
            print(f"Error: Link '{link_id}' not found!")
            sys.exit(1)
        
        print(f"Generating {count} fake submissions for link {link_id}...")
        
        for i in range(count):
            form = generate_fake_submission(link_id, link.group_id)
            db.session.add(form)
            print(f"  [{i+1}/{count}] Created submission for {form.first_name} {form.last_name}")
        
        # Increment group count
        if link.group:
            link.group.current_count += count
        
        db.session.commit()
        print(f"\n✅ Successfully generated {count} fake submissions!")

if __name__ == '__main__':
    main()

