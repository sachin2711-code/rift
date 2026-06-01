"""
Report Service
Generates PDF reports for agent runs
"""

import os
from datetime import datetime
from typing import Any, Dict, List

from fpdf import FPDF

from utils.logger import get_logger

logger = get_logger(__name__)


class PDFReport(FPDF):
    """Custom PDF report class"""
    
    def header(self):
        # Logo or title
        self.set_font('Arial', 'B', 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, 'RIFT DevOps Agent - Run Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(33, 37, 41)
        self.multi_cell(0, 6, body)
        self.ln()
    
    def add_info_row(self, label, value):
        self.set_font('Arial', 'B', 11)
        self.set_text_color(33, 37, 41)
        self.cell(50, 8, label + ':', 0, 0)
        
        self.set_font('Arial', '', 11)
        self.set_text_color(33, 37, 41)
        self.cell(0, 8, str(value), 0, 1)
    
    def add_status_badge(self, status):
        if status == 'passed':
            self.set_fill_color(40, 167, 69)  # Green
            self.set_text_color(255, 255, 255)
        elif status == 'failed':
            self.set_fill_color(220, 53, 69)  # Red
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(108, 117, 125)  # Gray
            self.set_text_color(255, 255, 255)
        
        self.set_font('Arial', 'B', 12)
        self.cell(40, 10, status.upper(), 0, 1, 'C', True)
        self.ln(5)


class ReportService:
    """
    Service for generating reports
    """
    
    def __init__(self):
        self.reports_dir = "/tmp/rift-reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    async def generate_pdf_report(self, run_id: str, run_data: Dict[str, Any]) -> str:
        """
        Generate PDF report for a run
        
        Args:
            run_id: Run ID
            run_data: Run data
            
        Returns:
            Path to generated PDF
        """
        pdf = PDFReport()
        pdf.add_page()
        
        # Run Summary
        pdf.chapter_title('Run Summary')
        pdf.add_info_row('Run ID', run_id)
        pdf.add_info_row('Repository', run_data.get('repository_url', 'N/A'))
        pdf.add_info_row('Team', run_data.get('team_name', 'N/A'))
        pdf.add_info_row('Team Leader', run_data.get('team_leader_name', 'N/A'))
        pdf.add_info_row('Branch', run_data.get('branch_name', 'N/A'))
        pdf.add_info_row('Status', run_data.get('status', 'N/A').upper())
        pdf.ln(5)
        
        # CI/CD Status
        pdf.chapter_title('CI/CD Status')
        pdf.add_status_badge(run_data.get('final_cicd_status', 'unknown'))
        pdf.add_info_row('Iterations', str(run_data.get('cicd_iterations', 0)))
        pdf.ln(5)
        
        # Score
        score = run_data.get('score', {})
        pdf.chapter_title('Score Breakdown')
        pdf.add_info_row('Base Score', str(score.get('base_score', 100)))
        pdf.add_info_row('Speed Bonus', f"+{score.get('speed_bonus', 0)}")
        pdf.add_info_row('Efficiency Penalty', f"-{score.get('efficiency_penalty', 0)}")
        pdf.add_info_row('Success Bonus', f"+{score.get('success_bonus', 0)}")
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(0, 123, 255)
        pdf.cell(0, 10, f"TOTAL SCORE: {score.get('total_score', 0)}", 0, 1)
        pdf.ln(5)
        
        # Fixes Summary
        pdf.chapter_title('Fixes Summary')
        pdf.add_info_row('Total Failures', str(run_data.get('total_failures', 0)))
        pdf.add_info_row('Total Fixes', str(run_data.get('total_fixes', 0)))
        pdf.add_info_row('Duration', f"{run_data.get('duration_seconds', 0):.2f} seconds")
        pdf.ln(5)
        
        # Fixes Table
        fixes = run_data.get('fixes', [])
        if fixes:
            pdf.add_page()
            pdf.chapter_title('Fixes Applied')
            
            # Table header
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(50, 8, 'File', 1, 0, 'C', True)
            pdf.cell(30, 8, 'Bug Type', 1, 0, 'C', True)
            pdf.cell(20, 8, 'Line', 1, 0, 'C', True)
            pdf.cell(40, 8, 'Status', 1, 0, 'C', True)
            pdf.cell(50, 8, 'Description', 1, 1, 'C', True)
            
            # Table rows
            pdf.set_font('Arial', '', 8)
            for fix in fixes[:50]:  # Limit to 50 fixes
                file_path = fix.get('file_path', '')[:25]
                bug_type = fix.get('bug_type', '')[:12]
                line = str(fix.get('line_number', ''))
                status = fix.get('status', '')[:10]
                desc = fix.get('description', '')[:30]
                
                # Status color
                if status == 'verified':
                    pdf.set_text_color(40, 167, 69)
                elif status == 'failed':
                    pdf.set_text_color(220, 53, 69)
                else:
                    pdf.set_text_color(33, 37, 41)
                
                pdf.cell(50, 6, file_path, 1)
                pdf.cell(30, 6, bug_type, 1)
                pdf.cell(20, 6, line, 1, 0, 'C')
                pdf.cell(40, 6, status, 1)
                pdf.cell(50, 6, desc, 1, 1)
            
            pdf.set_text_color(33, 37, 41)
        
        # Links
        pdf.ln(10)
        pdf.chapter_title('Links')
        if run_data.get('pull_request_url'):
            pdf.add_info_row('Pull Request', run_data.get('pull_request_url'))
        if run_data.get('commit_sha'):
            pdf.add_info_row('Commit SHA', run_data.get('commit_sha')[:12])
        
        # Footer
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 10, f"Generated by RIFT DevOps Agent on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", 0, 1, 'C')
        
        # Save PDF
        output_path = os.path.join(self.reports_dir, f"rift_report_{run_id}.pdf")
        pdf.output(output_path)
        
        logger.info(f"Generated PDF report: {output_path}")
        return output_path
    
    async def generate_json_report(self, run_id: str, run_data: Dict[str, Any]) -> str:
        """Generate JSON report for a run"""
        import json
        
        output_path = os.path.join(self.reports_dir, f"rift_report_{run_id}.json")
        
        with open(output_path, 'w') as f:
            json.dump(run_data, f, indent=2, default=str)
        
        return output_path
