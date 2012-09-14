from django.contrib import admin

from lizard_blockbox import models


class WaterLevelDifferenceAdmin(admin.ModelAdmin):
    list_display = ('riversegment', 'measure', 'reference', 'level_difference')
    list_filter = ('measure',)


class ReferenceValueAdmin(admin.ModelAdmin):
    list_display = ('riversegment', 'reference')


class VertexValueInline(admin.TabularInline):
    model = models.VertexValue


class VertexAdmin(admin.ModelAdmin):
    list_display = ('id', 'header', 'name', 'named_reaches_string')


class VertexValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'vertex', 'riversegment', 'value')
    list_filter = ('vertex',)


admin.site.register(models.Reach)
admin.site.register(models.RiverSegment)
admin.site.register(models.NamedReach)
admin.site.register(models.Measure)
admin.site.register(models.WaterLevelDifference, WaterLevelDifferenceAdmin)
admin.site.register(models.SubsetReach)
admin.site.register(models.ReferenceValue, ReferenceValueAdmin)
admin.site.register(models.Vertex, VertexAdmin)
admin.site.register(models.VertexValue, VertexValueAdmin)
# admin.site.register(models.CityLocation)
