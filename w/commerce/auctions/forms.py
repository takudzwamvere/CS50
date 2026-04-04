from django import forms
from .models import Listing, Bid, Comment

CATEGORY_CHOICES = [
    ('', '-- No Category --'),
    ('Electronics', 'Electronics'),
    ('Fashion', 'Fashion'),
    ('Home & Garden', 'Home & Garden'),
    ('Toys & Games', 'Toys & Games'),
    ('Sports & Outdoors', 'Sports & Outdoors'),
    ('Vehicles', 'Vehicles'),
    ('Books & Media', 'Books & Media'),
    ('Collectibles', 'Collectibles'),
    ('Other', 'Other'),
]


class ListingForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Listing title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your item...'}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...  (optional)'}),
        }


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Your bid amount'
            })
        }
        labels = {
            'amount': 'Your Bid ($)'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Leave a comment...'
            })
        }
        labels = {
            'content': 'Comment'
        }
