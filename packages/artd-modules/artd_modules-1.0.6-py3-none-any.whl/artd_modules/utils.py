from artd_modules.models import Module


def create_or_update_module_row(slug, name, description, version, is_plugin):
    if Module.objects.filter(slug=slug).count() == 0:
        Module.objects.create(
            slug=slug,
            name=name,
            description=description,
            version=version,
            is_plugin=is_plugin,
        )
        print(f"Module {name} created on version {version}")
    else:
        module = Module.objects.get(slug=slug)
        if module.version >= version:
            print(f"Module {name} is already up to date with version {module.version}")
            return
        else:
            module.name = name
            module.description = description
            module.version = version
            module.is_plugin = is_plugin
            module.save()
            print(f"Module {name} updated on version {version}")
