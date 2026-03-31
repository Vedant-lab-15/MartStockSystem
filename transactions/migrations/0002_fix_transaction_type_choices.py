from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(
                choices=[
                    ('IN', 'Stock In (Restock)'),
                    ('OUT', 'Stock Out (Sale)'),
                    ('ADJ+', 'Adjustment (Increase)'),
                    ('ADJ-', 'Adjustment (Decrease)'),
                ],
                default='IN',
                max_length=4,
            ),
        ),
        # Migrate existing 'ADJ' rows to 'ADJ+' (increase is the safer default)
        migrations.RunSQL(
            sql="UPDATE transactions_transaction SET transaction_type = 'ADJ+' WHERE transaction_type = 'ADJ';",
            reverse_sql="UPDATE transactions_transaction SET transaction_type = 'ADJ' WHERE transaction_type IN ('ADJ+', 'ADJ-');",
        ),
    ]
