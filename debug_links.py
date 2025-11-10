#!/usr/bin/env python
"""
Debug script to check links and forms in the database
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Link, Form, User
import sqlalchemy as sa

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("DATABASE DEBUG INFO")
    print("="*80)
    
    # Get all users
    users = db.session.scalars(sa.select(User)).all()
    print(f"\n📊 Total Users: {len(users)}")
    for user in users:
        print(f"   - {user.email} (ID: {user.id})")
    
    # Get all links
    links = db.session.scalars(sa.select(Link)).all()
    print(f"\n📊 Total Links: {len(links)}")
    
    used_links = [link for link in links if link.used]
    unused_links = [link for link in links if not link.used]
    
    print(f"   - Used links: {len(used_links)}")
    print(f"   - Unused links: {len(unused_links)}")
    
    # Get all forms
    forms = db.session.scalars(sa.select(Form)).all()
    print(f"\n📊 Total Forms: {len(forms)}")
    
    # Check for orphaned links (used but no form)
    print("\n" + "="*80)
    print("USED LINKS (should have forms)")
    print("="*80)
    
    for link in used_links:
        form = db.session.scalars(sa.select(Form).where(Form.link_id == link.id)).first()
        if form:
            print(f"\n✅ Link: {link.id[:10]}...")
            print(f"   Form: {form.first_name} {form.last_name}")
            print(f"   Created: {link.created_at}")
        else:
            print(f"\n❌ Link: {link.id[:10]}... (ORPHANED - marked as used but no form!)")
            print(f"   Created: {link.created_at}")
            print(f"   This link should be marked as used=False or deleted")
    
    # Check for forms without links
    print("\n" + "="*80)
    print("FORMS")
    print("="*80)
    
    for form in forms:
        link = db.session.get(Link, form.link_id)
        if link:
            print(f"\n✅ Form: {form.first_name} {form.last_name}")
            print(f"   Link: {form.link_id[:10]}...")
            print(f"   Link used: {link.used}")
        else:
            print(f"\n❌ Form: {form.first_name} {form.last_name} (ORPHANED - no link!)")
            print(f"   Link ID: {form.link_id[:10]}...")
    
    print("\n" + "="*80)

