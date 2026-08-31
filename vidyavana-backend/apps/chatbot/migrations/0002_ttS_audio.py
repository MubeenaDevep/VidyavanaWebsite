from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chatbot", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TTSAudio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("filename", models.CharField(max_length=255, unique=True)),
                ("status", models.CharField(choices=[("processing", "Processing"), ("ready", "Ready"), ("error", "Error")], default="processing", max_length=20)),
                ("error_message", models.CharField(blank=True, max_length=255)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]