from django.core.management import (
    BaseCommand,
    call_command,
    get_commands,
    load_command_class,
)


class Command(BaseCommand):
    """Точка входа для запуска периодических ночных скриптов.

    Более подробную информацию можно найти по ссылке https://conf.bars.group/pages/viewpage.action?pageId=312294857
    """

    help = 'Выполнение ночных скриптов'

    def handle(self, *args, **options):
        commands = get_commands()

        for command_name, package in commands.items():
            if isinstance(package, BaseCommand):
                command = package
            else:
                try:
                    command = load_command_class(package, command_name)
                except Exception as e:
                    print(
                        f'Возникла ошибка "{e}" при обработке команды "{command_name}" из пакета "{package}". '
                        f'Команда пропущена'
                    )
                    continue

            if getattr(command, 'nightly_script', False):
                print(f'Запуск скрипта "{command.help}"')

                try:
                    call_command(command)
                except Exception:
                    print(f'Скрипт "{command.help}" завершен с ошибкой')
                else:
                    print(f'Скрипт "{command.help}" завершен успешно')
