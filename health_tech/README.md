# Health Tech - Medical Conditions A-Z Index

A comprehensive Django app that implements an A-Z Medical Conditions Index similar to Mayo Clinic, providing detailed information about various medical conditions and diseases.

## Features

### Core Functionality
- **A-Z Index**: Browse medical conditions alphabetically
- **Search**: Full-text search across condition names, symptoms, causes, and treatments
- **Detailed Views**: Comprehensive information for each condition including symptoms, causes, and treatments
- **Department Organization**: Conditions organized by medical specialty
- **SEO-Friendly**: Semantic HTML, proper meta tags, and structured data

### Models
- **MedicalCondition**: Main model with fields for name, slug, overview, symptoms, causes, treatments, department, and images
- **Auto-generated slugs**: URL-friendly slugs automatically created from condition names
- **Department categorization**: 24+ medical departments including Cardiology, Neurology, Oncology, etc.
- **Image support**: Optional images for each condition

### Views & URLs
- `/conditions/` → A-Z index with letter counts
- `/conditions/<letter>/` → Conditions starting with specific letter (with pagination)
- `/conditions/detail/<slug>/` → Detailed condition information
- `/conditions/search/` → Search functionality

### Admin Interface
- Comprehensive admin with search, filters, and bulk actions
- Image preview in admin list view
- Department and letter filtering
- Export functionality

### Templates
- Responsive design with dark mode support
- Accessible HTML with proper semantic structure
- Pagination support
- Related conditions suggestions
- Quick navigation between letters

## Installation & Setup

1. **Add to INSTALLED_APPS**:
   ```python
   INSTALLED_APPS = [
       # ... other apps
       'health_tech',
   ]
   ```

2. **Include URLs**:
   ```python
   # In your main urls.py
   path('', include("health_tech.urls")),
   ```

3. **Run migrations**:
   ```bash
   python manage.py makemigrations health_tech
   python manage.py migrate
   ```

4. **Populate with sample data**:
   ```bash
   python manage.py populate_conditions
   ```

5. **Add to navigation** (already implemented in base.html):
   The app is automatically added to the sidebar navigation.

## Usage

### Adding Conditions
1. Access Django Admin at `/admin/`
2. Go to Health Tech > Medical Conditions
3. Click "Add Medical Condition"
4. Fill in all required fields
5. Optionally upload an image

### Managing Content
- Use the admin interface for content management
- Search and filter conditions by department, letter, or content
- Export conditions for backup or analysis

### Customization
- Modify `DEPARTMENTS` choices in `models.py` to add/remove medical specialties
- Customize templates in `health_tech/templates/health_tech/`
- Adjust pagination settings in views (default: 20 per page)

## Technical Details

### Dependencies
- Django (core framework)
- Pillow (for image handling)
- Requests (for sample data population)

### Key Features
- **Pagination**: 20 conditions per page on letter views, 15 on search
- **Filtering**: By department and search terms
- **SEO**: Structured data markup, proper meta tags
- **Performance**: Database indexes on name, department, and created_at
- **Responsive**: Mobile-first design with Tailwind CSS

### Model Fields
- `name`: Condition name (max 200 chars, unique)
- `slug`: URL-friendly version (auto-generated, unique)
- `overview`: Brief description (TextField)
- `symptoms`: Signs and symptoms (TextField)  
- `causes`: Causes and risk factors (TextField)
- `treatments`: Treatment options (TextField)
- `department`: Medical specialty (choices)
- `image`: Optional condition image
- `created_at`/`updated_at`: Timestamps

## Testing

Run the included test suite:
```bash
python manage.py test health_tech
```

Tests cover:
- Model functionality (slug generation, properties, URLs)
- View responses and content
- Search functionality
- Error handling

## Sample Data

The app includes a management command to populate the database with realistic medical conditions:

```bash
python manage.py populate_conditions
```

This creates 20+ sample conditions across different medical departments with placeholder images.

## Future Enhancements

Potential improvements:
- User favorites/bookmarks
- Condition comparison feature
- Related articles/resources
- Multi-language support
- API endpoints for mobile apps
- Advanced search filters (by severity, age group, etc.)
- User reviews/ratings
- Integration with appointment booking

## Contributing

When adding new conditions:
1. Follow the established content format
2. Include comprehensive information in all fields
3. Assign appropriate medical department
4. Add relevant images when possible
5. Test across different devices and screen sizes

## License

This app is part of the UrbanMD Health Network platform.