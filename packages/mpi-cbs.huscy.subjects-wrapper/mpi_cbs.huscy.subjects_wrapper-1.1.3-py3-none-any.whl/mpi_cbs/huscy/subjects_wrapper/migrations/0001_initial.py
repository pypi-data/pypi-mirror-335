from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('subjects', '0003_auto_20211028_1133'),
    ]

    operations = [
        migrations.CreateModel(
            name='WrappedSubject',
            fields=[
                ('pseudonym', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject')),
            ],
        ),
    ]
