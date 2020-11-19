from django.apps import apps
from django.contrib import admin
from django.contrib.admin import ModelAdmin

app_list = ["blog"]

for app_name in app_list:
    application = apps.get_app_config(app_name)

    for model in application.get_models():
        attr = {}
        attr["list_display"] = [
            name.name
            for name in model._meta.get_fields()
            if not name.many_to_many and name.concrete and not name.name == "password"
        ]
        modeladmin = type("Model", (ModelAdmin,), attr)

        admin.site.register(model, modeladmin)
