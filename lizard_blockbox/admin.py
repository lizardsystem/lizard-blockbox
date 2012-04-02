from django.contrib import admin

from lizard_blockbox import models


class ReachAdmin(admin.ModelAdmin)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Reach, ReachAdmin)
