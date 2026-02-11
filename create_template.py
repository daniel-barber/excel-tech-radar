#!/usr/bin/env python3
"""
Create Excel template for Radar Studio import.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

def create_template():
    """Create Excel template with sample data and instructions."""
    wb = Workbook()
    
    # Set document properties
    wb.properties.title = "Radar Template"
    wb.properties.subject = "Template for importing radar projects"
    wb.properties.creator = "Radar Studio"
    
    # ===== DATA SHEET =====
    ws_data = wb.active
    ws_data.title = "Sheet1"
    
    # Headers
    headers = ["name", "ring", "quadrant", "status", "description", "tags", "link", "linkName"]
    ws_data.append(headers)
    
    # Style headers
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    for col_num, header in enumerate(headers, 1):
        cell = ws_data.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Sample data rows
    sample_data = [
        [
            "Cloud Migration Strategy",
            "Ready",
            "Infrastructure",
            "On Track",
            "<p>Comprehensive strategy for migrating legacy applications to cloud infrastructure. Includes assessment, planning, and execution phases.</p>",
            "cloud, migration, infrastructure",
            "https://example.com/cloud-strategy",
            "View Strategy Doc"
        ],
        [
            "AI-Powered Analytics Platform",
            "Less Than 1 Year",
            "Applications",
            "New",
            "<p>Next-generation analytics platform leveraging <strong>machine learning</strong> and AI to provide predictive insights.</p>",
            "AI, analytics, machine-learning",
            "https://example.com/ai-analytics",
            "Platform Overview"
        ],
        [
            "Quantum Computing Research",
            "3+ Years",
            "Emerging Tech",
            "Blocked",
            "<p>Long-term research initiative exploring quantum computing applications for optimization problems.</p>",
            "quantum, research, innovation",
            "",
            ""
        ]
    ]
    
    for row_data in sample_data:
        ws_data.append(row_data)
    
    # Add data validation for ring column (column B)
    ring_values = '"Ready,Less Than 1 Year,1-3 Years,3+ Years"'
    ring_validation = DataValidation(type="list", formula1=ring_values, allow_blank=False)
    ring_validation.error = 'Please select a valid ring value'
    ring_validation.errorTitle = 'Invalid Ring'
    ws_data.add_data_validation(ring_validation)
    ring_validation.add(f'B2:B1000')  # Apply to ring column for rows 2-1000
    
    # Quadrant column (C) is free text - no validation needed
    
    # Add data validation for status column (column D)
    status_values = '"On Track,At Risk,Blocked,New,Moved In,Moved Out"'
    status_validation = DataValidation(type="list", formula1=status_values, allow_blank=True)
    status_validation.error = 'Please select a valid status value'
    status_validation.errorTitle = 'Invalid Status'
    ws_data.add_data_validation(status_validation)
    status_validation.add(f'D2:D1000')  # Apply to status column for rows 2-1000
    
    # Auto-adjust column widths
    for col_num, header in enumerate(headers, 1):
        column_letter = get_column_letter(col_num)
        if header == "description":
            ws_data.column_dimensions[column_letter].width = 60
        elif header == "name":
            ws_data.column_dimensions[column_letter].width = 30
        elif header in ["link", "linkName"]:
            ws_data.column_dimensions[column_letter].width = 25
        else:
            ws_data.column_dimensions[column_letter].width = 20
    
    # ===== INSTRUCTIONS SHEET =====
    ws_instructions = wb.create_sheet("Instructions")
    
    # Title
    ws_instructions.append(["Radar Studio - Import Template Instructions"])
    ws_instructions["A1"].font = Font(size=16, bold=True, color="4472C4")
    ws_instructions.merge_cells("A1:D1")
    
    ws_instructions.append([])  # Empty row
    
    # Overview
    ws_instructions.append(["Overview"])
    ws_instructions["A3"].font = Font(size=14, bold=True)
    ws_instructions.append(["This template helps you import radar projects into Radar Studio."])
    ws_instructions.append(["Fill in the 'Sheet1' tab with your radar entries, then import the file."])
    ws_instructions.append([])
    
    # Column descriptions
    ws_instructions.append(["Column Descriptions"])
    ws_instructions["A7"].font = Font(size=14, bold=True)
    ws_instructions.append([])
    
    column_descriptions = [
        ["Column", "Required", "Description", "Example"],
        ["name", "Yes", "Unique name for the radar entry", "Cloud Migration Strategy"],
        ["ring", "Yes", "Time horizon: Ready, Less Than 1 Year, 1-3 Years, 3+ Years", "Ready"],
        ["quadrant", "Yes", "Category/domain (flexible, can be any text)", "Infrastructure"],
        ["status", "No", "Current status: On Track, At Risk, Blocked, New, Moved In, Moved Out", "On Track"],
        ["description", "No", "HTML description (supports <p>, <strong>, <em>, <a>, <ul>, <li>)", "<p>Detailed description...</p>"],
        ["tags", "No", "Comma-separated tags for filtering", "cloud, migration, infrastructure"],
        ["link", "No", "URL for external reference", "https://example.com/doc"],
        ["linkName", "No", "Display text for the link", "View Documentation"]
    ]
    
    for row_data in column_descriptions:
        ws_instructions.append(row_data)
        row_num = ws_instructions.max_row
        if row_num == 9:  # Header row
            for col_num in range(1, 5):
                cell = ws_instructions.cell(row=row_num, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    
    # Column widths for instructions
    ws_instructions.column_dimensions["A"].width = 15
    ws_instructions.column_dimensions["B"].width = 12
    ws_instructions.column_dimensions["C"].width = 60
    ws_instructions.column_dimensions["D"].width = 30
    
    ws_instructions.append([])
    
    # Import steps
    ws_instructions.append(["How to Import"])
    ws_instructions[f"A{ws_instructions.max_row}"].font = Font(size=14, bold=True)
    ws_instructions.append([])
    
    import_steps = [
        "1. Fill in your radar entries in the 'Sheet1' tab",
        "2. Use the dropdown menus for Ring and Status columns",
        "3. Type any value you want for Quadrant (free text)",
        "4. Delete the sample rows (rows 2-4) or replace them with your data",
        "5. Save the file with your desired project name (e.g., 'My Project.xlsx')",
        "6. In Radar Studio, click 'Import' and drag-and-drop your file",
        "7. Your project will be uploaded and appear automatically in the project list"
    ]
    
    for step in import_steps:
        ws_instructions.append([step])
    
    ws_instructions.append([])
    
    # Tips
    ws_instructions.append(["Tips"])
    ws_instructions[f"A{ws_instructions.max_row}"].font = Font(size=14, bold=True)
    ws_instructions.append([])
    
    tips = [
        "• Use HTML in descriptions for rich formatting (bold, italic, links, lists)",
        "• Tags help with searching and filtering - use consistent tag names",
        "• Quadrants are required and flexible - create your own categories as needed",
        "• Leave optional fields empty if not needed",
        "• Ensure 'name' and 'quadrant' values are not empty",
        "• Ring values must match: Ready, Less Than 1 Year, 1-3 Years, or 3+ Years"
    ]
    
    for tip in tips:
        ws_instructions.append([tip])
    
    # Save template
    output_path = "templates/radar_template.xlsx"
    wb.save(output_path)
    print(f"✅ Template created: {output_path}")

if __name__ == "__main__":
    create_template()

# Made with Bob
