from typing import List
from domain.interfaces.repositories import GroupDataRepository
from domain.entities import Group
from domain.exceptions import ExternalServiceException
from infrastructure.google_sheets.client import GoogleSheetsClient
from infrastructure.dto.google_sheets_record import GoogleSheetsRecord
from infrastructure.google_sheets.google_sheets_adapter import GoogleSheetsAdapter


class GoogleSheetsGroupDataRepository(GroupDataRepository):
    """
    Реализация GroupDataRepository для чтения и актуализации данных из Google Sheets
    
    Читает данные групп из таблицы и преобразует их в доменные сущности
    Актуализирует нужные данные в таблице после выполнения операций
    """
    
    def __init__(
        self,
        client: GoogleSheetsClient,
        spreadsheet_id: str,
        sheet_name: str = "Sheet1",
        start_row: int = 2,  # Пропускаем заголовок
        end_row: int = 1000,
        start_literal: str = 'D',
        end_literal: str = 'I',
        adapter: GoogleSheetsAdapter = None
    ):
        """
        Инициализация источника данных
        
        Args:
            client: Клиент Google Sheets API
            spreadsheet_id: ID таблицы Google Sheets
            sheet_name: Название листа
            start_row: Номер первой строки с данными (1-based)
            adapter: Адаптер для преобразования данных
        """
        self.client = client
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.start_row = start_row
        self.end_row = end_row
        self.start_literal = start_literal
        self.end_literal = end_literal
        self.adapter = adapter or GoogleSheetsAdapter()
    
    async def get_all_groups(self) -> List[Group]:
        """
        Получить все группы из Google Sheets
        
        Returns:
            List[Group]: Список всех валидных групп из таблицы
        """
        try:
            range_name = f"{self.sheet_name}!{self.start_literal}{self.start_row}:{self.end_literal}{self.end_row}"
            rows = await self.client.read_range(self.spreadsheet_id, range_name)
            
            sheets_records = []
            for row in rows:
                if not row or not any(str(cell).strip() for cell in row):
                    continue

                try:
                    record = GoogleSheetsRecord.from_sheet_row(row)
                    if record.is_valid():
                        sheets_records.append(record)
                except Exception as e:
                    print(f"Предупреждение: не удалось обработать строку {row}: {e}")
                    continue
            
            groups = self.adapter.to_domain_list(sheets_records)
            
            return groups
            
        except ExternalServiceException:
            raise
        except Exception as e:
            raise ExternalServiceException(
                f"Ошибка чтения групп из Google Sheets: {e}",
                "Google Sheets"
            )
    
    async def get_sheet_info(self) -> dict:
        """
        Получить информацию о таблице для диагностики
        
        Returns:
            dict: Информация о таблице
        """
        try:
            info = await self.client.get_sheet_info(self.spreadsheet_id)
            
            return {
                "title": info.get("properties", {}).get("title", "Unknown"),
                "sheets": [
                    sheet.get("properties", {}).get("title", "Unknown")
                    for sheet in info.get("sheets", [])
                ],
                "spreadsheet_id": self.spreadsheet_id,
                "configured_sheet": self.sheet_name,
                "start_row": self.start_row
            }
        except Exception as e:
            raise ExternalServiceException(
                f"Ошибка получения информации о таблице: {e}",
                "Google Sheets"
            )

    async def actialize_group_data(self, data: List[Group]) -> None:
        """
        Занести актуализированные данные о группах после их создания/редактирования в таблицу
                    
        Raises:
            ExternalServiceException: Если не удалось актуализировать данные
        """
        try:
            range_name = f"{self.sheet_name}!{self.start_literal}{self.start_row}:{self.end_literal}{self.end_row}"
            dtos = self.adapter.to_infrastructure_list(data)
            rows = [dto.to_sheet_row() for dto in dtos]
            await self.client.write_range(self.spreadsheet_id, range_name, rows)

        except ExternalServiceException:
            raise
        except Exception as e:
            raise ExternalServiceException(
                f"Ошибка актуализации данных в Google Sheets: {e}",
                "Google Sheets"
            )        