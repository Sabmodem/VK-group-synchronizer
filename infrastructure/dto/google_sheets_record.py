from dataclasses import dataclass
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


@dataclass 
class GoogleSheetsRecord:
    """
    DTO для записи из Google Sheets
    
    Представляет одну строку таблицы с данными группы
    """
    vk_id: Optional[str] 
    updating: bool
    title: str
    description: str
    screen_name: str
    avatar_url: Optional[str]
    
    @classmethod
    def from_sheet_row(cls, row_values: list, has_header: bool = True) -> 'GoogleSheetsRecord':
        """
        Создает запись из строки Google Sheets
        
        Args:
            row_values: Значения ячеек строки [A, B, C, D, E, F, G, H, I]
            has_header: Есть ли заголовки в таблице
            
        Returns:
            GoogleSheetsRecord: Созданная запись
        """
        vk_id = str(row_values[0]).strip() if row_values[0] else None
        
        # Обработка булевого поля updating
        updating_str = str(row_values[1]).strip().lower()
        updating = updating_str in ('true', '1', 'да', 'yes', 'on')
        
        title = str(row_values[2]).strip() if row_values[2] else ""
        description = str(row_values[3]).strip() if row_values[3] else ""
        screen_name = str(row_values[4]).strip() if row_values[4] else ""
        avatar_url = str(row_values[5]).strip() if row_values[5] else None
        
        return cls(
            vk_id=vk_id,
            updating=updating,
            title=title,
            description=description,
            screen_name=screen_name,
            avatar_url=avatar_url
        )
    
    def to_sheet_row(self) -> list:
        """
        Преобразует запись в строку для Google Sheets
        
        Returns:
            list: Значения для записи в строку [A, B, C, D, E, F, G, H, I]
        """
        return [
            f'=HYPERLINK("https://vk.com/club{self.vk_id}"; "{self.vk_id}")' if self.vk_id else "-",
            "=TRUE" if self.updating else "=FALSE",
            self.title or "-",
            self.description or "-",
            self.screen_name or "-",
            self.avatar_url or "-"
        ]
    
    def is_valid(self) -> bool:
        """Проверяет валидность записи"""
        return bool(
            self.title and self.title.strip() and
            self.description and self.description.strip() and
            self.screen_name and self.screen_name.strip()
        )
