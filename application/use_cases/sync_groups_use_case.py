import asyncio
from typing import List

from domain.interfaces.repositories import GroupDataRepository as IGroupDataRepository
from domain.interfaces.repositories import GroupRepository as IGroupRepository
from domain.interfaces.use_cases import SyncGroupsUseCase as ISyncGroupsUseCase
from domain.entities import Group
from domain.services import GroupValidationService
from domain.exceptions import (
    ValidationException, 
    ExternalServiceException, 
    RateLimitException,
    CaptchaRequiredException
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

class SyncGroupsUseCase(ISyncGroupsUseCase):    
    def __init__(
        self,
        group_data_repository: IGroupDataRepository,
        group_repository: IGroupRepository,
        dry_run: bool = False
    ):
        self.group_data_repository = group_data_repository
        self.group_repository = group_repository
        self.dry_run = dry_run
    
    async def execute(self) -> None:        
        try:
            logging.info("📥 Получение групп из Google Sheets...")
            groups = await self.group_data_repository.get_all_groups()
            if not groups:
                logging.info("ℹ️  Нет групп для синхронизации")
                return
            
            groups_after_creating: List[Group] = []
            logging.info(f"📥 Получено {len(groups)} групп")
            logging.info("📥 Запущен процесс создания")
            for i, group in enumerate(groups):
                if not group.is_created_in_vk() and group.needs_update():
                    logging.info(f"\t{i}/{len(groups)} Создание: {group.title}")
                    created_group = await self._process_group_creation(group)
                    groups_after_creating.append(created_group)
                else:
                    logging.info(f"\t{i}/{len(groups)} Группа не требует создания: {group.title}")
                    groups_after_creating.append(group)

            groups_after_updating: List[Group] = []
            logging.info("📥 Запущен процесс редактирования")
            for i, group in enumerate(groups_after_creating):
                if group.is_created_in_vk() and group.needs_update():
                    logging.info(f"\t{i}/{len(groups)} Редактирование: {group.title}")
                    updated_group = await self._process_group_updating(group)
                    groups_after_updating.append(updated_group)
                else:
                    logging.info(f"\t{i}/{len(groups)} Группа не требует редактирования: {group.title}")
                    groups_after_updating.append(group)

            logging.info('📥 Запущен процесс актуализации данных')
            if self.dry_run:
                logging.info(f"    [DRY RUN] Группы были бы актуализированы")
            else:
                await self.group_data_repository.actialize_group_data(groups_after_updating)
                logging.info(f"    ✅ Актуализация завершена")

        except Exception as e:
            logging.info(f"❌ Критическая ошибка: {e}", exc_info=True)
        
    async def _process_group_creation(self, group: Group) -> Group:    
        try:
            if self.dry_run:
                logging.info(f"    [DRY RUN] Группа была бы создана")
                group.vk_id = 1000
            else:
                GroupValidationService.validate_for_creation(group)
                vk_id = await self.group_repository.create_group(group)
                group.vk_id = vk_id
                logging.info(f"    ✅ Создана с VK ID: {vk_id}")

        except ValidationException as e:
            logging.info(f"    ⚠️  Пропущена: {e}")
            
        except (RateLimitException, CaptchaRequiredException) as e:
            logging.info(f"    ⏸️  Требует внимания: {e}")
            
        except ExternalServiceException as e:
            logging.info(f"    ❌ Ошибка API: {e}")
            
        except Exception as e:
            logging.info(f"    💥 Неожиданная ошибка: {e}")
        
        finally:
            if not self.dry_run:
                await asyncio.sleep(0.5)
            return group

        
    async def _process_group_updating(self, group: Group) -> Group:
        try:
            if self.dry_run:
                logging.info(f"    [DRY RUN] Группа была бы обновлена")
            else:
                GroupValidationService.validate_for_update(group)
                await self.group_repository.update_group(group)
                logging.info(f"    ✅ Обновлена")

        except ValidationException as e:
            logging.info(f"    ⚠️  Пропущена: {e}")
            
        except (RateLimitException, CaptchaRequiredException) as e:
            logging.info(f"    ⏸️  Требует внимания: {e}")
            
        except ExternalServiceException as e:
            logging.info(f"    ❌ Ошибка API: {e}")
            
        except Exception as e:
            logging.info(f"    💥 Неожиданная ошибка: {e}")
        
        finally:
            if not self.dry_run:
                await asyncio.sleep(0.5)
            return group