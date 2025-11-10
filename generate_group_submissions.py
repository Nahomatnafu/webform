#!/usr/bin/env python
"""
Generate fake form submissions for a group.
This script creates fake people with realistic data for testing purposes.

Usage:
    python generate_group_submissions.py <group_id> <count>
    python generate_group_submissions.py --list-groups
    python generate_group_submissions.py --create-link <group_id>

Examples:
    # List all available groups
    python generate_group_submissions.py --list-groups
    
    # Generate 10 fake submissions for group ID 1
    python generate_group_submissions.py 1 10
    
    # Create a new link for group ID 1
    python generate_group_submissions.py --create-link 1
"""

import os
import sys
import random
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw, ImageFont
import io

# Add the app to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, create_app
from app.models import Form, Link, Group, User
import secrets

# Sample data for realistic fake people
FIRST_NAMES_MALE = [
    'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph',
    'Thomas', 'Charles', 'Christopher', 'Daniel', 'Matthew', 'Anthony', 'Donald',
    'Mark', 'Paul', 'Steven', 'Andrew', 'Kenneth', 'Joshua', 'Kevin', 'Brian', 'George'
]

FIRST_NAMES_FEMALE = [
    'Mary', 'Patricia', 'Jennifer', 'Linda', 'Barbara', 'Elizabeth', 'Susan', 'Jessica',
    'Sarah', 'Karen', 'Nancy', 'Lisa', 'Betty', 'Margaret', 'Sandra', 'Ashley',
    'Dorothy', 'Kimberly', 'Emily', 'Donna', 'Michelle', 'Carol', 'Amanda', 'Melissa'
]

MIDDLE_NAMES = [
    'Lee', 'Ann', 'Marie', 'Lynn', 'Rose', 'Grace', 'Jane', 'Mae', 'Ray', 'James',
    'Michael', 'David', 'Joseph', 'Thomas', 'Allen', 'Wayne', 'Edward', 'Paul'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker'
]

STREET_NAMES = [
    'Main', 'Oak', 'Maple', 'Cedar', 'Elm', 'Washington', 'Lake', 'Hill', 'Park',
    'River', 'Pine', 'Sunset', 'First', 'Second', 'Third', 'Broadway', 'Church'
]

STREET_TYPES = ['St', 'Ave', 'Blvd', 'Dr', 'Ln', 'Rd', 'Way', 'Ct']

EYE_COLORS = ['Brown', 'Blue', 'Green', 'Hazel', 'Gray', 'Amber']
HAIR_COLORS = ['Black', 'Brown', 'Blonde', 'Red', 'Gray', 'Auburn', 'Chestnut']

US_STATES = {
    'MN': ['Minneapolis', 'St. Paul', 'Rochester', 'Duluth', 'Bloomington'],
    'CA': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'San Jose'],
    'TX': ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth'],
    'FL': ['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Fort Lauderdale'],
    'NY': ['New York', 'Buffalo', 'Rochester', 'Albany', 'Syracuse'],
    'IL': ['Chicago', 'Aurora', 'Naperville', 'Joliet', 'Rockford'],
    'PA': ['Philadelphia', 'Pittsburgh', 'Allentown', 'Erie', 'Reading'],
    'OH': ['Columbus', 'Cleveland', 'Cincinnati', 'Toledo', 'Akron'],
    'GA': ['Atlanta', 'Augusta', 'Columbus', 'Savannah', 'Athens'],
    'NC': ['Charlotte', 'Raleigh', 'Greensboro', 'Durham', 'Winston-Salem']
}

def generate_fake_image(first_name, last_name, gender):
    """Generate a simple fake ID photo with the person's name"""
    # Create image with gradient background
    img = Image.new('RGB', (300, 400), color=(240, 240, 245))
    draw = ImageDraw.Draw(img)
    
    # Draw background gradient effect
    for i in range(400):
        color_val = 240 - int(i * 0.1)
        draw.line([(0, i), (300, i)], fill=(color_val, color_val, color_val + 10))
    
    # Draw head (circle)
    head_color = (255, 220, 177) if gender != 'Female' else (255, 228, 196)
    draw.ellipse([75, 50, 225, 200], fill=head_color, outline=(200, 180, 150), width=2)
    
    # Draw body (rectangle)
    shirt_colors = [(70, 130, 180), (220, 20, 60), (34, 139, 34), (255, 140, 0), (128, 0, 128)]
    shirt_color = random.choice(shirt_colors)
    draw.rectangle([50, 200, 250, 400], fill=shirt_color)
    
    # Draw text at bottom
    try:
        # Try to use a default font, fall back to default if not available
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add name
    name_text = f"{first_name} {last_name}"
    draw.rectangle([0, 350, 300, 400], fill=(255, 255, 255, 200))
    draw.text((150, 365), name_text, fill=(0, 0, 0), anchor="mm", font=font_large)
    draw.text((150, 385), "ID PHOTO", fill=(100, 100, 100), anchor="mm", font=font_small)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def generate_fake_person(link_id, group_id=None):
    """Generate a single fake person with realistic data"""
    # Randomly select gender
    gender = random.choice(['Male', 'Female'])
    
    # Select name based on gender
    if gender == 'Male':
        first_name = random.choice(FIRST_NAMES_MALE)
    else:
        first_name = random.choice(FIRST_NAMES_FEMALE)
    
    middle_name = random.choice(MIDDLE_NAMES) if random.random() > 0.3 else None
    last_name = random.choice(LAST_NAMES)
    
    # Select state and corresponding city
    state = random.choice(list(US_STATES.keys()))
    city = random.choice(US_STATES[state])
    
    # Generate address
    street_number = random.randint(100, 9999)
    street_name = random.choice(STREET_NAMES)
    street_type = random.choice(STREET_TYPES)
    address = f"{street_number} {street_name} {street_type}"
    
    # Generate zip code based on state (simplified)
    zip_code = f"{random.randint(10000, 99999)}"
    
    # Generate date of birth (18-80 years old)
    age_days = random.randint(18*365, 80*365)
    date_of_birth = datetime.now() - timedelta(days=age_days)
    
    # Generate height (in cm) - realistic ranges
    if gender == 'Male':
        height = random.uniform(165, 195)  # 5'5" to 6'5"
    else:
        height = random.uniform(152, 180)  # 5'0" to 5'11"
    
    # Generate weight (in kg) - realistic ranges
    if gender == 'Male':
        weight = random.uniform(60, 110)  # 132 to 242 lbs
    else:
        weight = random.uniform(50, 90)   # 110 to 198 lbs
    
    # Generate form ID
    form_id = secrets.token_urlsafe(16)
    
    # Create form object
    form = Form(
        id=form_id,
        link_id=link_id,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        eye_color=random.choice(EYE_COLORS),
        hair_color=random.choice(HAIR_COLORS),
        address=address,
        date_of_birth=date_of_birth,
        height=height,
        weight=weight,
        gender=gender,
        state=state,
        city=city,
        zip_code=zip_code,
        organ_donor=random.choice([True, False]),
        restrictions_corrective_lenses=random.choice([True, False]),
        group_id=group_id,
        submitted_at=datetime.now(timezone.utc)
    )
    
    # Generate and save fake image
    img_bytes = generate_fake_image(first_name, last_name, gender)
    upload_path = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(upload_path, exist_ok=True)
    
    with open(os.path.join(upload_path, form_id), 'wb') as f:
        f.write(img_bytes.getvalue())
    
    return form

def list_groups():
    """List all available groups"""
    app = create_app()
    with app.app_context():
        groups = db.session.query(Group).all()
        
        if not groups:
            print("No groups found in the database.")
            return
        
        print("\n" + "="*80)
        print("AVAILABLE GROUPS")
        print("="*80)
        
        for group in groups:
            print(f"\nGroup ID: {group.id}")
            print(f"  Name: {group.name}")
            print(f"  Description: {group.description or 'N/A'}")
            print(f"  Current Count: {group.current_count}")
            print(f"  Max Capacity: {group.max_capacity if group.max_capacity > 0 else 'Unlimited'}")
            print(f"  Created: {group.created_at}")
        
        print("\n" + "="*80)

def create_link_for_group(group_id):
    """Create a new link for a group"""
    app = create_app()
    with app.app_context():
        group = db.session.get(Group, group_id)
        if not group:
            print(f"Error: Group with ID {group_id} not found!")
            sys.exit(1)
        
        # Get the first user (admin)
        user = db.session.query(User).first()
        if not user:
            print("Error: No users found in database!")
            sys.exit(1)
        
        # Create link that expires in 24 hours
        link = Link(
            created_at=datetime.now(timezone.utc),
            end_at=datetime.now(timezone.utc) + timedelta(hours=24),
            user_id=user.id,
            group_id=group_id,
            used=False
        )
        
        db.session.add(link)
        db.session.commit()
        
        print(f"\n✅ Created new link for group '{group.name}'")
        print(f"Link ID: {link.id}")
        print(f"URL: http://127.0.0.1:5000/form/{link.id}")
        print(f"Expires: {link.end_at}")

def generate_submissions(group_id, count):
    """Generate fake submissions for a group"""
    app = create_app()
    
    with app.app_context():
        # Get the group
        group = db.session.get(Group, group_id)
        if not group:
            print(f"Error: Group with ID {group_id} not found!")
            print("Use --list-groups to see available groups.")
            sys.exit(1)
        
        # Get or create a link for this group
        link = db.session.query(Link).filter_by(group_id=group_id).first()
        
        if not link:
            print(f"No link found for group '{group.name}'. Creating one...")
            user = db.session.query(User).first()
            if not user:
                print("Error: No users found in database!")
                sys.exit(1)
            
            link = Link(
                created_at=datetime.now(timezone.utc),
                end_at=datetime.now(timezone.utc) + timedelta(hours=24),
                user_id=user.id,
                group_id=group_id,
                used=False
            )
            db.session.add(link)
            db.session.commit()
            print(f"✅ Created link: {link.id}\n")
        
        print(f"Generating {count} fake submissions for group '{group.name}'...")
        print("="*80)
        
        for i in range(count):
            form = generate_fake_person(link.id, group_id)
            db.session.add(form)
            
            age = (datetime.now() - form.date_of_birth).days // 365
            height_ft = int(form.height / 30.48)
            height_in = int((form.height % 30.48) / 2.54)
            weight_lbs = int(form.weight * 2.20462)
            
            print(f"  [{i+1}/{count}] {form.first_name} {form.last_name}")
            print(f"         Age: {age} | Gender: {form.gender} | {height_ft}'{height_in}\" | {weight_lbs} lbs")
            print(f"         {form.city}, {form.state} {form.zip_code}")
        
        # Update group count
        group.current_count += count
        
        db.session.commit()
        
        print("="*80)
        print(f"\n✅ Successfully generated {count} fake submissions!")
        print(f"Group '{group.name}' now has {group.current_count} total submissions.")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == '--list-groups':
        list_groups()
    elif command == '--create-link':
        if len(sys.argv) < 3:
            print("Error: Please provide a group ID")
            print("Usage: python generate_group_submissions.py --create-link <group_id>")
            sys.exit(1)
        group_id = int(sys.argv[2])
        create_link_for_group(group_id)
    else:
        # Generate submissions
        if len(sys.argv) < 3:
            print("Error: Please provide both group ID and count")
            print("Usage: python generate_group_submissions.py <group_id> <count>")
            sys.exit(1)
        
        group_id = int(sys.argv[1])
        count = int(sys.argv[2])
        
        if count <= 0:
            print("Error: Count must be greater than 0")
            sys.exit(1)
        
        generate_submissions(group_id, count)

if __name__ == '__main__':
    main()

