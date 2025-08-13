from domain.entities import Group
from infrastructure.dto.google_sheets_record import GoogleSheetsRecord


class GoogleSheetsAdapter:
    """
    Адаптер для преобразования между доменными сущностями и DTO Google Sheets
    """
    
    def to_domain(self, sheets_record: GoogleSheetsRecord) -> Group:
        """
        Преобразует запись Google Sheets в доменную сущность Group
        
        Args:
            sheets_record: DTO запись из Google Sheets
            
        Returns:
            Group: Доменная сущность группы
        """
        return Group(
            title=sheets_record.title,
            description=sheets_record.description,
            screen_name=sheets_record.screen_name,
            updating=sheets_record.updating,
            vk_id=sheets_record.vk_id,
            avatar_url=sheets_record.avatar_url
        )
    
    def to_infrastructure(self, group: Group) -> GoogleSheetsRecord:
        """
        Преобразует доменную сущность Group в DTO для Google Sheets
        
        Args:
            group: Доменная сущность группы
            
        Returns:
            GoogleSheetsRecord: DTO для записи в Google Sheets
        """
        return GoogleSheetsRecord(
            vk_id=group.vk_id,
            updating=group.updating,
            title=group.title,
            description=group.description,
            screen_name=group.screen_name,
            avatar_url=group.avatar_url
        )
    
    def to_domain_list(self, sheets_records: list[GoogleSheetsRecord]) -> list[Group]:
        """
        Преобразует список DTO в список доменных сущностей
        
        Args:
            sheets_records: Список DTO записей
            
        Returns:
            list[Group]: Список доменных сущностей
        """
        return [self.to_domain(record) for record in sheets_records if record.is_valid()]
    
    def to_infrastructure_list(self, groups: list[Group]) -> list[GoogleSheetsRecord]:
        """
        Преобразует список доменных сущностей в список DTO
        
        Args:
            groups: Список доменных сущностей
            
        Returns:
            list[GoogleSheetsRecord]: Список DTO записей
        """
        return [self.to_infrastructure(group) for group in groups]
