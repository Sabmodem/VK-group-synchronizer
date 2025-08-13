from typing import List, Optional, Dict, Any
import asyncio
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from domain.exceptions import ExternalServiceException


class GoogleSheetsClient:
    """
    Клиент для работы с Google Sheets API
    
    Обеспечивает базовые операции чтения и записи данных в таблицы
    """
    
    def __init__(self, credentials_file: str):
        """
        Инициализация клиента
        
        Args:
            credentials_file: Путь к файлу с service account credentials
        """
        self.credentials_file = credentials_file
        self._service = None
        self._credentials = None
    
    async def _get_service(self):
        """Получает сервис Google Sheets API с ленивой инициализацией"""
        if self._service is None:
            try:
                self._credentials = Credentials.from_service_account_file(
                    self.credentials_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                
                self._service = build('sheets', 'v4', credentials=self._credentials)
                
            except Exception as e:
                raise ExternalServiceException(
                    f"Не удалось инициализировать Google Sheets API: {e}",
                    "Google Sheets"
                )
        
        return self._service
    
    async def read_range(self, spreadsheet_id: str, range_name: str) -> List[List[str]]:
        """
        Читает данные из указанного диапазона таблицы
        
        Args:
            spreadsheet_id: ID Google Sheets таблицы
            range_name: Диапазон для чтения (например, "Sheet1!A1:I100")
            
        Returns:
            List[List[str]]: Двумерный массив значений ячеек
            
        Raises:
            ExternalServiceException: При ошибке чтения данных
        """
        try:
            service = await self._get_service()
            
            def _read():
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueRenderOption='UNFORMATTED_VALUE',
                    dateTimeRenderOption='FORMATTED_STRING'
                ).execute()
                return result.get('values', [])
            
            loop = asyncio.get_event_loop()
            values = await loop.run_in_executor(None, _read)
            
            return values
            
        except HttpError as e:
            error_details = e.error_details[0] if e.error_details else {}
            
            if e.resp.status == 403:
                raise ExternalServiceException(
                    f"Нет доступа к таблице {spreadsheet_id}. Проверьте права service account",
                    "Google Sheets"
                )
            elif e.resp.status == 404:
                raise ExternalServiceException(
                    f"Таблица {spreadsheet_id} не найдена",
                    "Google Sheets" 
                )
            else:
                raise ExternalServiceException(
                    f"Ошибка Google Sheets API: {e}",
                    "Google Sheets"
                )
                
        except Exception as e:
            raise ExternalServiceException(
                f"Неожиданная ошибка при чтении Google Sheets: {e}",
                "Google Sheets"
            )
    
    async def write_range(
        self, 
        spreadsheet_id: str, 
        range_name: str, 
        values: List[List[Any]],
        value_input_option: str = 'USER_ENTERED'
    ) -> None:
        """
        Записывает данные в указанный диапазон таблицы
        
        Args:
            spreadsheet_id: ID Google Sheets таблицы
            range_name: Диапазон для записи (например, "Sheet1!A2:I10")
            values: Двумерный массив значений для записи
            value_input_option: Как интерпретировать значения ('USER_ENTERED' или 'RAW')
            
        Raises:
            ExternalServiceException: При ошибке записи данных
        """
        try:
            service = await self._get_service()
            
            def _write():
                body = {
                    'values': values,
                    'majorDimension': 'ROWS'
                }
                
                return service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body
                ).execute()
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _write)
            
        except HttpError as e:
            if e.resp.status == 403:
                raise ExternalServiceException(
                    f"Нет прав на запись в таблицу {spreadsheet_id}",
                    "Google Sheets"
                )
            else:
                raise ExternalServiceException(
                    f"Ошибка записи в Google Sheets: {e}",
                    "Google Sheets"
                )
                
        except Exception as e:
            raise ExternalServiceException(
                f"Неожиданная ошибка при записи в Google Sheets: {e}",
                "Google Sheets"
            )
    
    async def get_sheet_info(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Получает информацию о таблице
        
        Args:
            spreadsheet_id: ID Google Sheets таблицы
            
        Returns:
            Dict: Информация о таблице (название, листы и т.д.)
        """
        try:
            service = await self._get_service()
            
            def _get_info():
                return service.spreadsheets().get(
                    spreadsheetId=spreadsheet_id,
                    fields='properties.title,sheets.properties'
                ).execute()
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _get_info)
            
        except Exception as e:
            raise ExternalServiceException(
                f"Ошибка получения информации о таблице: {e}",
                "Google Sheets"
            )
