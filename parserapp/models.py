from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class DdmSlTable(models.Model):
    sl_tables_id = models.AutoField(primary_key=True)
    sl = models.CharField(max_length=10)
    original_table_name = models.CharField(max_length=80)
    mapped_table_name = models.CharField(max_length=80)
    original_column_name = ArrayField(models.TextField(max_length=100))
    mapped_column_name = ArrayField(models.TextField(max_length=100))
    

    # class Meta:
        
    #     db_table = 'ddm_sl_table'
    #     unique_together = (('sl','original_table_name'), ('sl','mapped_table_name'))


class UserTableModel(models.Model):
	sl_tables_id = models.AutoField(primary_key=True)
	sl = models.CharField(max_length=10)
	original_table_name = models.CharField(max_length=80)
	mapped_table_name = models.CharField(max_length=80)
	original_column_name = ArrayField(models.TextField(max_length=100))
	mapped_column_name = ArrayField(models.TextField(max_length=100))