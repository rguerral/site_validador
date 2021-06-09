# Generated by Django 3.1.7 on 2021-06-04 22:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('attribute_type', models.CharField(choices=[('NOMINAL', 'NOMINAL'), ('RATIO', 'RATIO')], max_length=8)),
                ('fixed', models.CharField(choices=[('NO', 'NO'), ('SI', 'SI')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('max_category_level', models.IntegerField(validators=[django.core.validators.MaxValueValidator(4), django.core.validators.MinValueValidator(1)])),
                ('max_products_alternatives', models.IntegerField(validators=[django.core.validators.MaxValueValidator(20), django.core.validators.MinValueValidator(1)])),
                ('min_products_category_level', models.IntegerField(validators=[django.core.validators.MaxValueValidator(4), django.core.validators.MinValueValidator(1)])),
                ('min_products_n', models.IntegerField(validators=[django.core.validators.MaxValueValidator(20), django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='BidAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('zone_or_global', models.CharField(choices=[('ZONA', 'ZONA'), ('NACIONAL', 'NACIONAL')], max_length=8)),
                ('global_minprice', models.IntegerField(blank=True, null=True)),
                ('global_maxprice', models.IntegerField(blank=True, null=True)),
                ('bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='catalog.bid')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('tree_name', models.CharField(max_length=200, unique=True)),
                ('position', models.CharField(max_length=16, null=True)),
                ('level', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.bid')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='catalog.category')),
            ],
            options={
                'unique_together': {('name', 'bid')},
            },
        ),
        migrations.CreateModel(
            name='Dimension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='NominalConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accept_others', models.BooleanField()),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.attribute')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='catalog.category')),
            ],
            options={
                'unique_together': {('name', 'category')},
            },
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zones', to='catalog.bid')),
            ],
            options={
                'unique_together': {('name', 'bid')},
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('abbreviation', models.CharField(max_length=8, unique=True)),
                ('is_base', models.BooleanField()),
                ('to_base', models.FloatField()),
                ('currency', models.BooleanField(default=False)),
                ('dimension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='units', to='catalog.dimension')),
            ],
        ),
        migrations.CreateModel(
            name='RatioConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minval', models.FloatField()),
                ('maxval', models.FloatField()),
                ('integer', models.BooleanField()),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.attribute')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratio_configs', to='catalog.product')),
            ],
        ),
        migrations.CreateModel(
            name='PriceBidAttributeZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minprice', models.IntegerField()),
                ('maxprice', models.IntegerField()),
                ('bidattribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.bidattribute')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.zone')),
            ],
        ),
        migrations.CreateModel(
            name='NominalValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=64)),
                ('nominal_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nominal_values', to='catalog.nominalconfig')),
            ],
        ),
        migrations.AddField(
            model_name='nominalconfig',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nominal_configs', to='catalog.product'),
        ),
        migrations.CreateModel(
            name='FixedRatioValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.attribute')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fixed_ratio_values', to='catalog.product')),
            ],
        ),
        migrations.CreateModel(
            name='FixedNominalValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=64)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.attribute')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fixed_nominal_values', to='catalog.product')),
            ],
        ),
        migrations.AddField(
            model_name='bidattribute',
            name='unit',
            field=models.ForeignKey(limit_choices_to={'currency': True}, on_delete=django.db.models.deletion.CASCADE, to='catalog.unit'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='catalog.category'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='catalog.unit'),
        ),
        migrations.AlterUniqueTogether(
            name='bidattribute',
            unique_together={('name', 'bid')},
        ),
        migrations.AlterUniqueTogether(
            name='attribute',
            unique_together={('name', 'category')},
        ),
    ]
