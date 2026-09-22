from django.db import migrations, models


class Migration(migrations.Migration):
    """Xabardagi e-pochta maydoni erkin “bog'lanish uchun” maydoniga aylandi."""

    dependencies = [
        ("core", "0003_slideitem_blur_width_slideitem_image_blur_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="message",
            old_name="email",
            new_name="contact",
        ),
        migrations.AlterField(
            model_name="message",
            name="contact",
            field=models.CharField(
                help_text=(
                    "Telefon raqam, Telegram username yoki e-pochta — "
                    "qaysi biri qulay bo'lsa."
                ),
                max_length=140,
                verbose_name="Bog'lanish uchun",
            ),
        ),
    ]
