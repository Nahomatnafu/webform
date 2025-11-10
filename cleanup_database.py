#!/usr/bin/env python
"""
Cleanup script to fix orphaned links and forms in the database
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Link, Form
import sqlalchemy as sa

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("DATABASE CLEANUP")
    print("="*80)
    
    # Find orphaned links (marked as used but no form)
    all_links = db.session.scalars(sa.select(Link)).all()
    orphaned_links = []
    
    for link in all_links:
        if link.used:
            form = db.session.scalars(sa.select(Form).where(Form.link_id == link.id)).first()
            if not form:
                orphaned_links.append(link)
    
    print(f"\n📊 Found {len(orphaned_links)} orphaned links (marked as used but no form)")
    
    if orphaned_links:
        print("\nOrphaned links:")
        for link in orphaned_links:
            print(f"  - {link.id[:15]}... (created: {link.created_at})")
        
        response = input("\nDo you want to mark these links as unused? (y/n): ")
        if response.lower() == 'y':
            for link in orphaned_links:
                link.used = False
            db.session.commit()
            print(f"✅ Marked {len(orphaned_links)} links as unused")
        else:
            print("❌ Skipped marking links as unused")
    
    # Find orphaned forms (no link_id or link doesn't exist)
    all_forms = db.session.scalars(sa.select(Form)).all()
    orphaned_forms = []
    
    for form in all_forms:
        if form.link_id is None:
            orphaned_forms.append(form)
        else:
            link = db.session.get(Link, form.link_id)
            if not link:
                orphaned_forms.append(form)
    
    print(f"\n📊 Found {len(orphaned_forms)} orphaned forms (no link or link doesn't exist)")
    
    if orphaned_forms:
        print("\nOrphaned forms:")
        for form in orphaned_forms:
            print(f"  - {form.first_name} {form.last_name} (ID: {form.id[:15]}...)")
        
        response = input("\nDo you want to DELETE these orphaned forms? (y/n): ")
        if response.lower() == 'y':
            for form in orphaned_forms:
                # Delete the image file if it exists
                image_path = os.path.join(os.path.dirname(__file__), 'uploads', form.id)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"  Deleted image: {form.id}")
                db.session.delete(form)
            db.session.commit()
            print(f"✅ Deleted {len(orphaned_forms)} orphaned forms")
        else:
            print("❌ Skipped deleting orphaned forms")
    
    print("\n" + "="*80)
    print("CLEANUP COMPLETE")
    print("="*80 + "\n")

