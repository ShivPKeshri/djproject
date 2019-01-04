from django.contrib import admin

# Register your models here.
from .models import UserTableModel
admin.site.register(UserTableModel)

from .models import DdmSlTable
admin.site.register(DdmSlTable)



# class DdmSlTableAdmin(admin.ModelAdmin):
# 	list_display = ['sl_tables_id','original_table_name', 'mapped_table_name', 'original_column_name', 'mapped_column_name']
# 	list_display_links = ['original_table_name']
	# class Meta:
	# 	model = DdmSlTable


# admin.site.register(DdmSlTable, DdmSlTableAdmin)