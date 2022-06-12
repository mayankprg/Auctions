from django.template.defaulttags import register



def usd(value):
    """Format value as USD."""
    float(value)
    return f"${value:,.2f}"

    
register.filter('usd', usd)