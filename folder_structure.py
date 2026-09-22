"""
Folder Structure Manager
Creates and manages the Year/Quarter/Month/Week folder hierarchy
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional
import calendar


class FolderStructureManager:
    """Manages the folder hierarchy: Year/Quarter/Month/Week"""
    
    QUARTER_MONTHS = {
        1: (1, 3),   # Q1: Jan-Mar
        2: (4, 6),   # Q2: Apr-Jun
        3: (7, 9),   # Q3: Jul-Sep
        4: (10, 12)  # Q4: Oct-Dec
    }
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.root_path.mkdir(parents=True, exist_ok=True)
    
    def get_quarter(self, month: int) -> int:
        """Get quarter number (1-4) for a given month"""
        for quarter, (start, end) in self.QUARTER_MONTHS.items():
            if start <= month <= end:
                return quarter
        return 1
    
    def get_quarter_name(self, quarter: int) -> str:
        """Get quarter folder name"""
        start_month, end_month = self.QUARTER_MONTHS[quarter]
        start_name = calendar.month_abbr[start_month]
        end_name = calendar.month_abbr[end_month]
        return f"Q{quarter}_{start_name}-{end_name}"
    
    def get_week_number(self, date: datetime) -> int:
        """Get week number within the month (1-5)"""
        first_day = date.replace(day=1)
        # Week 1 starts on the 1st
        day_of_month = date.day
        week_num = ((day_of_month - 1) // 7) + 1
        return min(week_num, 5)
    
    def get_week_folder_name(self, week_num: int) -> str:
        """Get week folder name"""
        return f"Week_{week_num:02d}"
    
    def get_month_folder_name(self, month: int) -> str:
        """Get month folder name (number + name)"""
        return f"{month:02d}_{calendar.month_name[month]}"
    
    def get_target_folder(self, date: datetime) -> Path:
        """
        Get the target folder path for a given date
        Structure: Year/Q#_MMM-MMM/MM_MonthName/Week_##
        """
        year = date.year
        month = date.month
        quarter = self.get_quarter(month)
        week = self.get_week_number(date)
        
        year_folder = self.root_path / str(year)
        quarter_folder = year_folder / self.get_quarter_name(quarter)
        month_folder = quarter_folder / self.get_month_folder_name(month)
        week_folder = month_folder / self.get_week_folder_name(week)
        
        # Create all directories
        week_folder.mkdir(parents=True, exist_ok=True)
        
        return week_folder
    
    def get_folder_info(self, date: datetime) -> dict:
        """Get detailed folder info for a date"""
        year = date.year
        month = date.month
        quarter = self.get_quarter(month)
        week = self.get_week_number(date)
        
        return {
            "year": year,
            "quarter": quarter,
            "quarter_name": self.get_quarter_name(quarter),
            "month": month,
            "month_name": calendar.month_name[month],
            "month_folder": self.get_month_folder_name(month),
            "week": week,
            "week_folder": self.get_week_folder_name(week),
            "full_path": str(self.get_target_folder(date))
        }


def get_folder_structure_manager(root_path: str) -> FolderStructureManager:
    """Factory function to create FolderStructureManager"""
    return FolderStructureManager(root_path)