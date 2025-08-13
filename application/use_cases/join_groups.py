import asyncio
from typing import List

from domain.interfaces.repositories import GroupDataRepository as IGroupDataRepository
from domain.interfaces.use_cases import JoinGroupsUseCase as IJoinGroupsUseCase
from domain.interfaces import GroupSettingsInteractor
from domain.entities import Group
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

class JoinGroupsUseCase(IJoinGroupsUseCase):    
    def __init__(
        self,
        group_data_repository: IGroupDataRepository,
        group_settings_interactor: GroupSettingsInteractor,
        dry_run: bool = False
    ):
        self.group_data_repository = group_data_repository
        self.group_settings_interactor = group_settings_interactor
        self.dry_run = dry_run
    
    async def execute(self) -> None:
        try:            
            logging.info("📥 Получение групп из Google Sheets...")
            groups = await self.group_data_repository.get_all_groups()
            if not groups:
                logging.info("ℹ️  Нет групп для вступления")
                return
            
            logging.info(f"📥 Получено {len(groups)} групп")
            logging.info("📥 Запущен процесс вступления в группы")
            for i, group in enumerate(groups):
                if group.is_created_in_vk() and group.needs_update():
                    logging.info(f"\t{i}/{len(groups)} Вступление в группу: {group.title}")
                    await self._process_joining_group(group)
        except Exception as e:
            logging.info(f"❌ Критическая ошибка: {e}")


    async def _process_joining_group(self, group: Group) -> None:
        try:
            if self.dry_run:
                logging.info(f"    [DRY RUN] Группа была обработана")
                group.vk_id = 1000
            else:
                await self.group_settings_interactor.join_group(group)
                logging.info(f"    ✅ Вступление выполнено")
        except (RateLimitException, CaptchaRequiredException) as e:
            logging.info(f"    ⏸️  Требует внимания: {e}")
            
        except ExternalServiceException as e:
            if 'you are already in this community' in str(e):
                logging.info(f"    ⏸️  Уже в группе")
            else:
                logging.info(f"    ❌ Ошибка API: {e}")
            
        except Exception as e:
            logging.info(f"    💥 Неожиданная ошибка: {e}")
        
        finally:
            if not self.dry_run:
                await asyncio.sleep(0.5)