import click
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

@click.group()
def cli():
    """
    Консольный интерфейс для управления группами VK.com.
    """
    click.echo(f"Welcome to VK Group Manager!")

@cli.command()
def sync():
    '''
    Полная синхронизация групп из Google Sheets в VK
    '''
    from application.use_cases import SyncGroupsUseCase
    from infrastructure.google_sheets import GoogleSheetsGroupDataRepository, GoogleSheetsClient, GoogleSheetsAdapter
    from infrastructure.vk_api import VKAPIClient, VKGroupRepository
    from infrastructure.captcha_solvers import ConsoleCaptchaSolver
    import config
    import asyncio
    google_sheets_client = GoogleSheetsClient(credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE)
    google_sheets_adapter = GoogleSheetsAdapter()
    group_data_repository = GoogleSheetsGroupDataRepository(
        client=google_sheets_client, 
        spreadsheet_id=config.GOOGLE_SHEETS_SPREADSHEET_ID,
        sheet_name=config.GOOGLE_SHEETS_SHEET_NAME,
        start_row=config.GOOGLE_SHEETS_START_ROW,
        end_row=config.GOOGLE_SHEETS_END_ROW,
        start_literal=config.GOOGLE_SHEETS_START_LITERAL,
        end_literal=config.GOOGLE_SHEETS_END_ROW,
        adapter=google_sheets_adapter
    )
    console_captcha_solver = ConsoleCaptchaSolver()
    vk_api_client = VKAPIClient(
        access_token=config.VK_ACCESS_TOKEN_GROUPS_OWNER,
        captcha_solver=console_captcha_solver
    )
    vk_group_repository = VKGroupRepository(client=vk_api_client)
    sync_groups_use_case = SyncGroupsUseCase(
        group_data_repository=group_data_repository, 
        group_repository=vk_group_repository, 
        dry_run=config.DRY_RUN
    )

    asyncio.run(sync_groups_use_case.execute())

@cli.command()
def create():
    '''
    Создание групп с данными из Google Sheets
    '''
    from application.use_cases import CreateGroupsUseCase
    from infrastructure.google_sheets import GoogleSheetsGroupDataRepository, GoogleSheetsClient, GoogleSheetsAdapter
    from infrastructure.vk_api import VKAPIClient, VKGroupRepository
    from infrastructure.captcha_solvers import ConsoleCaptchaSolver
    import config
    import asyncio
    google_sheets_client = GoogleSheetsClient(credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE)
    google_sheets_adapter = GoogleSheetsAdapter()
    group_data_repository = GoogleSheetsGroupDataRepository(
        client=google_sheets_client, 
        spreadsheet_id=config.GOOGLE_SHEETS_SPREADSHEET_ID,
        sheet_name=config.GOOGLE_SHEETS_SHEET_NAME,
        start_row=config.GOOGLE_SHEETS_START_ROW,
        end_row=config.GOOGLE_SHEETS_END_ROW,
        start_literal=config.GOOGLE_SHEETS_START_LITERAL,
        end_literal=config.GOOGLE_SHEETS_END_ROW,
        adapter=google_sheets_adapter
    )
    console_captcha_solver = ConsoleCaptchaSolver()
    vk_api_client = VKAPIClient(
        access_token=config.VK_ACCESS_TOKEN_GROUPS_OWNER,
        captcha_solver=console_captcha_solver
    )
    vk_group_repository = VKGroupRepository(client=vk_api_client)
    sync_groups_use_case = CreateGroupsUseCase(
        group_data_repository=group_data_repository, 
        group_repository=vk_group_repository, 
        dry_run=config.DRY_RUN
    )

    asyncio.run(sync_groups_use_case.execute())    


@cli.command()
def update():
    '''
    Обновление уже созданных групп
    '''
    from application.use_cases import UpdateGroupsUseCase
    from infrastructure.google_sheets import GoogleSheetsGroupDataRepository, GoogleSheetsClient, GoogleSheetsAdapter
    from infrastructure.vk_api import VKAPIClient, VKGroupRepository
    from infrastructure.captcha_solvers import ConsoleCaptchaSolver
    import config
    import asyncio
    google_sheets_client = GoogleSheetsClient(credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE)
    google_sheets_adapter = GoogleSheetsAdapter()
    group_data_repository = GoogleSheetsGroupDataRepository(
        client=google_sheets_client, 
        spreadsheet_id=config.GOOGLE_SHEETS_SPREADSHEET_ID,
        sheet_name=config.GOOGLE_SHEETS_SHEET_NAME,
        start_row=config.GOOGLE_SHEETS_START_ROW,
        end_row=config.GOOGLE_SHEETS_END_ROW,
        start_literal=config.GOOGLE_SHEETS_START_LITERAL,
        end_literal=config.GOOGLE_SHEETS_END_ROW,
        adapter=google_sheets_adapter
    )
    console_captcha_solver = ConsoleCaptchaSolver()
    vk_api_client = VKAPIClient(
        access_token=config.VK_ACCESS_TOKEN_GROUPS_OWNER,
        captcha_solver=console_captcha_solver
    )
    vk_group_repository = VKGroupRepository(client=vk_api_client)
    sync_groups_use_case = UpdateGroupsUseCase(
        group_data_repository=group_data_repository, 
        group_repository=vk_group_repository, 
        dry_run=config.DRY_RUN
    )

    asyncio.run(sync_groups_use_case.execute()) 

'''
Эти две команды запускать СТРОГО ПОСЛЕДОВАТЕЛЬНО - сначала subscribe, потом grant_admin
'''
@cli.command()
def subscribe():
    '''
    Подписаться на все группы с аккаута, которому нужно дать доступ к ним
    '''
    from application.use_cases import JoinGroupsUseCase
    from infrastructure.google_sheets import GoogleSheetsGroupDataRepository, GoogleSheetsClient, GoogleSheetsAdapter
    from infrastructure.vk_api import VKAPIClient, GroupSettingsInteractor
    from infrastructure.captcha_solvers import ConsoleCaptchaSolver
    import config
    import asyncio
    google_sheets_client = GoogleSheetsClient(credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE)
    google_sheets_adapter = GoogleSheetsAdapter()
    group_data_repository = GoogleSheetsGroupDataRepository(
        client=google_sheets_client,
        spreadsheet_id=config.GOOGLE_SHEETS_SPREADSHEET_ID,
        sheet_name=config.GOOGLE_SHEETS_SHEET_NAME,
        start_row=config.GOOGLE_SHEETS_START_ROW,
        end_row=config.GOOGLE_SHEETS_END_ROW,
        start_literal=config.GOOGLE_SHEETS_START_LITERAL,
        end_literal=config.GOOGLE_SHEETS_END_ROW,
        adapter=google_sheets_adapter
    )
    console_captcha_solver = ConsoleCaptchaSolver()
    vk_api_client = VKAPIClient(
        access_token=config.VK_ACCESS_TOKEN_CHATUS_ACCOUNT,
        captcha_solver=console_captcha_solver
    )
    group_settings_interactor = GroupSettingsInteractor(client=vk_api_client)
    sync_groups_use_case = JoinGroupsUseCase(
        group_data_repository=group_data_repository, 
        group_settings_interactor=group_settings_interactor,
        dry_run=config.DRY_RUN
    )

    asyncio.run(sync_groups_use_case.execute())
@cli.command()
def grant_admin():
    '''
    Дать права админа аккаунту из config.py
    '''
    from application.use_cases import GiveAdminPrivilegeUseCase
    from infrastructure.google_sheets import GoogleSheetsGroupDataRepository, GoogleSheetsClient, GoogleSheetsAdapter
    from infrastructure.vk_api import VKAPIClient, GroupSettingsInteractor
    from infrastructure.captcha_solvers import ConsoleCaptchaSolver
    import config
    import asyncio
    google_sheets_client = GoogleSheetsClient(credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE)
    google_sheets_adapter = GoogleSheetsAdapter()
    group_data_repository = GoogleSheetsGroupDataRepository(
        client=google_sheets_client,
        spreadsheet_id=config.GOOGLE_SHEETS_SPREADSHEET_ID,
        sheet_name=config.GOOGLE_SHEETS_SHEET_NAME,
        start_row=config.GOOGLE_SHEETS_START_ROW,
        end_row=config.GOOGLE_SHEETS_END_ROW,
        start_literal=config.GOOGLE_SHEETS_START_LITERAL,
        end_literal=config.GOOGLE_SHEETS_END_ROW,
        adapter=google_sheets_adapter
    )
    console_captcha_solver = ConsoleCaptchaSolver()
    vk_api_client = VKAPIClient(
        access_token=config.VK_ACCESS_TOKEN_GROUPS_OWNER,
        captcha_solver=console_captcha_solver
    )
    group_settings_interactor = GroupSettingsInteractor(client=vk_api_client)
    sync_groups_use_case = GiveAdminPrivilegeUseCase(
        group_data_repository=group_data_repository, 
        group_settings_interactor=group_settings_interactor,
        chatus_user_id=config.VK_ADMIN_ACCOUNT_USER_ID,
        dry_run=config.DRY_RUN
    )

    asyncio.run(sync_groups_use_case.execute())    

if __name__ == '__main__':
    cli()