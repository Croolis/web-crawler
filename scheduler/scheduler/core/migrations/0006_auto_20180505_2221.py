# Generated by Django 2.0.4 on 2018-05-05 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20180505_1735'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrawlLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('stage', models.IntegerField()),
                ('user', models.CharField(max_length=32)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crawl_links', to='core.Task')),
            ],
        ),
        migrations.CreateModel(
            name='SecurityBreach',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('stage', models.IntegerField()),
                ('owner', models.CharField(max_length=32)),
                ('intruder', models.CharField(max_length=32)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='security_breaches', to='core.Task')),
            ],
            options={
                'ordering': ['stage', 'owner', 'intruder'],
            },
        ),
        migrations.AddIndex(
            model_name='securitybreach',
            index=models.Index(fields=['task', 'stage'], name='core_securi_task_id_db596c_idx'),
        ),
        migrations.AddIndex(
            model_name='crawllink',
            index=models.Index(fields=['task', 'stage', 'user'], name='core_crawll_task_id_9231b5_idx'),
        ),
    ]