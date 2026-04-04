from django import template

register = template.Library()

@register.filter(name='category_color')
def category_color(value):
    if not value:
        return 'secondary'
        
    colors = {
        'Electronics': 'primary',       # Blue
        'Fashion': 'danger',            # Red
        'Home & Garden': 'success',     # Green
        'Toys & Games': 'warning',      # Yellow
        'Sports & Outdoors': 'info',    # Light blue
        'Vehicles': 'dark',             # Black
        'Books & Media': 'secondary',   # Gray
        'Collectibles': 'primary',      # Blue
        'Other': 'secondary'            # Gray
    }
    return colors.get(value, 'secondary')
