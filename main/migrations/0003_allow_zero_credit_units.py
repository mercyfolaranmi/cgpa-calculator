from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_academicsession_semester_course_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='course',
            name='course_credit_units_1_to_6',
        ),
        migrations.AddConstraint(
            model_name='course',
            constraint=models.CheckConstraint(
                condition=models.Q(('credit_units__gte', 0), ('credit_units__lte', 6)),
                name='course_credit_units_0_to_6',
            ),
        ),
    ]