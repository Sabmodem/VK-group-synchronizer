import asyncio

from domain.interfaces.repositories import GroupDataRepository as IGroupDataRepository
from domain.interfaces.use_cases import GiveAdminPrivilegeUseCase as IGiveAdminPrivilegeUseCase
from domain.interfaces import GroupSettingsInteractor
from domain.entities import Group
from domain.dto import SetGroupAdminDto, Role
from domain.exceptions import (
    ExternalServiceException, 
    RateLimitException,
    CaptchaRequiredException
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

class GiveAdminPrivilegeUseCase(IGiveAdminPrivilegeUseCase):    
    def __init__(
        self,
        group_data_repository: IGroupDataRepository,
        group_settings_interactor: GroupSettingsInteractor,
        chatus_user_id: int,
        dry_run: bool = False
    ):
        self.group_data_repository = group_data_repository
        self.group_settings_interactor = group_settings_interactor
        self.chatus_user_id = chatus_user_id
        self.dry_run = dry_run
    
    async def execute(self) -> None:
        try:            
            logging.info("📥 Получение групп из Google Sheets...")
            groups = await self.group_data_repository.get_all_groups()
            if not groups:
                logging.info("ℹ️  Нет групп для назначения администратора")
                return
            
            logging.info(f"📥 Получено {len(groups)} групп")
            logging.info("📥 Запущен процесс назначения администратора в группах")
            for i, group in enumerate(groups):
                if group.is_created_in_vk() and group.needs_update():
                    logging.info(f"\t{i}/{len(groups)} обработка группы: {group.title}")
                    await self._process_giving_privelige(group)
        except Exception as e:
            logging.info(f"❌ Критическая ошибка: {e}")


    async def _process_giving_privelige(self, group: Group) -> None:
        try:
            if self.dry_run:
                logging.info(f"    [DRY RUN] Группа была обработана")
                group.vk_id = 1000
            else:
                set_group_admin_dto = SetGroupAdminDto(
                    group_id=group.vk_id,
                    user_id=self.chatus_user_id,
                    role=Role.administrator
                )
                await self.group_settings_interactor.set_group_admin(set_group_admin_dto)
                logging.info(f"    ✅ Права администратора выданы")
        except (RateLimitException, CaptchaRequiredException) as e:
            logging.info(f"    ⏸️  Требует внимания: {e}")
            
        except ExternalServiceException as e:
            logging.info(f"    ❌ Ошибка API: {e}")
            
        except Exception as e:
            logging.info(f"    💥 Неожиданная ошибка: {e}")
        
        finally:
            if not self.dry_run:
                await asyncio.sleep(0.5)