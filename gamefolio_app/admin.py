from typing import Any
from django.contrib import admin
from django.db.models import Avg, Count
from gamefolio_app.models import Author, Game, Review, List, ListEntry


class ListsInLine(admin.TabularInline):
    model = List
    classes = ['collapse']

class ReviewInLine(admin.TabularInline):
    model = Review
    classes = ['collapse']

#Shows list entrys on list page in admin
class ListEntry(admin.TabularInline):
    model = ListEntry
    classes = ['collapse']

class ListAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "List Information",
            {
                "fields": ["title", "description", "slug"],
            }
        ),
    ]
    readonly_fields = ('slug',)
    inlines = (ListEntry,)

class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'average_rating', 'total_reviews')
    readonly_fields = ('average_rating', 'total_reviews',)

    def average_rating(self, obj):
        return obj.average_rating()
    
    def total_reviews(self, obj):
        return obj.total_reviews()
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _average_rating = Avg('review__rating'),
            _total_rating = Count('review', distinct = True)
        ).order_by('_average_rating')
        return queryset
    
    average_rating.admin_order_field = "_average_rating"
    total_reviews.admin_order_field = "_total_rating"
    inlines = [ReviewInLine]

class AuthorAdmin(admin.ModelAdmin):
    inlines = (ReviewInLine, ListsInLine)

admin.site.register(Author, AuthorAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Review)
admin.site.register(List, ListAdmin)