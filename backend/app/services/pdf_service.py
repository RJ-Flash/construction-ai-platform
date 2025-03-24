import os
import io
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from ..db.models import Quote, QuoteItem, Project, Client, User
from ..core.config import settings

class PDFService:
    """
    Service for generating PDFs from quotes.
    
    This is a placeholder implementation that will be replaced with an actual PDF generation
    library like ReportLab, WeasyPrint, or wkhtmltopdf in a future implementation.
    """
    
    def __init__(self):
        """Initialize the PDF service."""
        # Ensure the output directory exists
        self.output_dir = Path(settings.PDF_OUTPUT_DIR)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_quote_pdf(self, db: Session, quote_id: int) -> str:
        """
        Generate a PDF for a quote and return the file path.
        """
        # Get the quote with all related data
        quote = db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            raise ValueError(f"Quote with ID {quote_id} not found")
        
        # Get project and client info
        project = db.query(Project).filter(Project.id == quote.project_id).first()
        client = db.query(Client).filter(Client.id == quote.client_id).first() if quote.client_id else None
        
        # Get quote items
        items = db.query(QuoteItem).filter(QuoteItem.quote_id == quote.id).all()
        
        # Get creator info
        created_by = db.query(User).filter(User.id == quote.created_by).first()
        
        # Format data for the PDF template
        quote_data = {
            # Quote details
            "id": quote.id,
            "title": quote.title,
            "status": quote.status.value,
            "created_at": quote.created_at.strftime("%Y-%m-%d"),
            "expiry_date": quote.expiry_date.strftime("%Y-%m-%d") if quote.expiry_date else None,
            
            # Financial details
            "subtotal": format_currency(quote.subtotal_amount),
            "discount": f"{quote.discount_percentage}% ({format_currency(quote.discount_amount)})",
            "tax": f"{quote.tax_rate}% ({format_currency(quote.tax_amount)})",
            "total": format_currency(quote.total_amount),
            
            # Project details
            "project": {
                "name": project.name,
                "description": project.description,
                "location": project.location
            } if project else {},
            
            # Client details
            "client": {
                "name": client.name if client else quote.client_name,
                "email": client.email if client else quote.client_email,
                "phone": client.phone if client else quote.client_phone,
                "address": client.address if client else None
            },
            
            # Created by
            "created_by": created_by.full_name if created_by else "Unknown",
            
            # Items
            "items": [{
                "description": item.description,
                "details": item.details,
                "quantity": item.quantity,
                "unit_price": format_currency(item.unit_price),
                "total_price": format_currency(item.total_price)
            } for item in items],
            
            # Notes
            "notes": quote.notes
        }
        
        # Generate a filename
        filename = f"quote_{quote.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        file_path = self.output_dir / filename
        
        # In a real implementation, this would use a PDF generation library
        # to render the quote_data into a PDF file
        # For this placeholder, we'll just create an empty file
        with open(file_path, 'w') as f:
            f.write(f"Quote {quote.id} - {quote.title}\n")
            f.write(f"This is a placeholder for the actual PDF content.\n")
            f.write(f"The real implementation would use a PDF generation library.\n")
        
        return str(file_path)
    
    async def render_quote_html(self, quote_data: Dict[str, Any]) -> str:
        """
        Render a quote as HTML that can be converted to a PDF.
        This is a placeholder that would use a template engine in a real implementation.
        """
        # In a real implementation, this would use a template engine like Jinja2
        # to render the quote_data into an HTML template
        # For this placeholder, we'll just return a basic HTML string
        
        items_html = ""
        for item in quote_data.get("items", []):
            items_html += f"""
            <tr>
                <td>{item.get('description', '')}</td>
                <td>{item.get('quantity', '')}</td>
                <td>{item.get('unit_price', '')}</td>
                <td>{item.get('total_price', '')}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Quote {quote_data.get('id', '')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ display: flex; justify-content: space-between; }}
                .quote-info {{ margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; border: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .totals {{ margin-top: 20px; text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div>
                    <h1>Quote #{quote_data.get('id', '')}</h1>
                    <h2>{quote_data.get('title', '')}</h2>
                </div>
                <div>
                    <p>Date: {quote_data.get('created_at', '')}</p>
                    <p>Expiry: {quote_data.get('expiry_date', 'N/A')}</p>
                    <p>Status: {quote_data.get('status', '')}</p>
                </div>
            </div>
            
            <div class="quote-info">
                <div class="project-info">
                    <h3>Project</h3>
                    <p>Name: {quote_data.get('project', {}).get('name', '')}</p>
                    <p>Location: {quote_data.get('project', {}).get('location', '')}</p>
                    <p>Description: {quote_data.get('project', {}).get('description', '')}</p>
                </div>
                
                <div class="client-info">
                    <h3>Client</h3>
                    <p>Name: {quote_data.get('client', {}).get('name', '')}</p>
                    <p>Email: {quote_data.get('client', {}).get('email', '')}</p>
                    <p>Phone: {quote_data.get('client', {}).get('phone', '')}</p>
                    <p>Address: {quote_data.get('client', {}).get('address', '')}</p>
                </div>
            </div>
            
            <h3>Items</h3>
            <table>
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <div class="totals">
                <p>Subtotal: {quote_data.get('subtotal', '')}</p>
                <p>Discount: {quote_data.get('discount', '')}</p>
                <p>Tax: {quote_data.get('tax', '')}</p>
                <p><strong>Total: {quote_data.get('total', '')}</strong></p>
            </div>
            
            <div class="notes">
                <h3>Notes</h3>
                <p>{quote_data.get('notes', '')}</p>
            </div>
            
            <div class="footer">
                <p>Created by: {quote_data.get('created_by', '')}</p>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html

    async def html_to_pdf(self, html_content: str, output_path: str):
        """
        Convert HTML content to a PDF file.
        This is a placeholder that would use a HTML-to-PDF library in a real implementation.
        """
        # In a real implementation, this would use a library like weasyprint or wkhtmltopdf
        # to convert the HTML to a PDF file
        # For this placeholder, we'll just write the HTML to a file
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        # For demonstration purposes, add a .html file alongside the PDF
        html_path = output_path.replace('.pdf', '.html')
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        return output_path


def format_currency(amount: float) -> str:
    """
    Format a currency amount with two decimal places and a dollar sign.
    """
    if amount is None:
        return "$0.00"
    return f"${amount:.2f}"
