from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from io import BytesIO
from datetime import datetime
from app.database import get_db
from app.models import Transaction, Vente, User
from app.auth import get_current_user, role_required

router = APIRouter(prefix="/api/reports", tags=["Reports"])

def create_pdf_report(title, data, headers):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30)
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Table
    table_data = [headers]
    for row in data:
        table_data.append(row)
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

@router.get("/transactions")
def download_transactions_report(
    current_user = Depends(role_required(["DG", "DAF", "COMPTABLE"])),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).order_by(Transaction.date.desc()).limit(500).all()
    
    data = []
    for t in transactions:
        data.append([
            t.date.strftime('%d/%m/%Y'),
            t.type.upper(),
            f"{t.montant:,.0f} €",
            t.libelle[:30],
            t.statut
        ])
    
    pdf_buffer = create_pdf_report(
        "Rapport des Transactions",
        data,
        ["Date", "Type", "Montant", "Libellé", "Statut"]
    )
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=transactions.pdf"}
    )

@router.get("/financial")
def download_financial_report(
    current_user = Depends(role_required(["DG", "DAF"])),
    db: Session = Depends(get_db)
):
    total_entrees = db.query(func.sum(Transaction.montant)).filter(Transaction.type == "entree").scalar() or 0
    total_sorties = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type == "sortie",
        Transaction.statut == "APPROUVE"
    ).scalar() or 0
    solde = total_entrees - total_sorties
    
    data = [
        ["Total des Entrées", f"{total_entrees:,.0f} €"],
        ["Total des Sorties (approuvées)", f"{total_sorties:,.0f} €"],
        ["Solde Disponible", f"{solde:,.0f} €"],
        ["", ""],
        ["Rapport généré le", datetime.now().strftime('%d/%m/%Y %H:%M')]
    ]
    
    pdf_buffer = create_pdf_report("Rapport Financier", data, ["Description", "Montant"])
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=financial_report.pdf"}
    )

@router.get("/sales")
def download_sales_report(
    current_user = Depends(role_required(["DG", "DIRECTEUR_COMMERCIAL"])),
    db: Session = Depends(get_db)
):
    ventes = db.query(Vente).order_by(Vente.date.desc()).limit(500).all()
    
    data = []
    for v in ventes:
        data.append([
            v.date.strftime('%d/%m/%Y'),
            v.produit,
            str(v.quantite),
            f"{v.prix_unitaire:,.0f} €",
            f"{v.montant_total:,.0f} €"
        ])
    
    pdf_buffer = create_pdf_report(
        "Rapport des Ventes",
        data,
        ["Date", "Produit", "Quantité", "Prix Unitaire", "Total"]
    )
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sales_report.pdf"}
    )
