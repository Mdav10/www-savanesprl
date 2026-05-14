from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from datetime import datetime
from app.database import get_db
from app.models import Transaction, SaleReport, StockMovement, Product, User
from app.deps import get_current_user, role_required

router = APIRouter(prefix="/api/reports", tags=["Reports"])

def create_pdf(title, data, headers):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30)
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    if not data:
        elements.append(Paragraph("Aucune donnée disponible", styles['Normal']))
    else:
        table_data = [headers] + data
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

@router.get("/transactions")
def download_transactions(
    current_user = Depends(role_required(["COMPTABLE", "DG", "DAF"])),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).order_by(Transaction.date.desc()).all()
    data = [[t.date.strftime('%d/%m/%Y'), t.type, f"{t.montant:,.0f}", t.libelle, t.statut] for t in transactions]
    pdf = create_pdf("Rapport des Transactions", data, ["Date", "Type", "Montant(FBU)", "Libellé", "Statut"])
    return Response(content=pdf.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=transactions.pdf"})

@router.get("/financial")
def download_financial(
    current_user = Depends(role_required(["DG", "DAF"])),
    db: Session = Depends(get_db)
):
    total_entrees = db.query(func.sum(Transaction.montant)).filter(Transaction.type == "entree").scalar() or 0
    total_sorties = db.query(func.sum(Transaction.montant)).filter(Transaction.type == "sortie", Transaction.statut == "APPROUVE").scalar() or 0
    data = [["Total Entrées", f"{total_entrees:,.0f} FBU"], ["Total Sorties", f"{total_sorties:,.0f} FBU"], ["Solde", f"{(total_entrees - total_sorties):,.0f} FBU"]]
    pdf = create_pdf("Rapport Financier", data, ["Description", "Montant"])
    return Response(content=pdf.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=financial.pdf"})

@router.get("/sales")
def download_sales(
    current_user = Depends(role_required(["DG", "DIRECTEUR_COMMERCIAL"])),
    db: Session = Depends(get_db)
):
    sales = db.query(SaleReport).order_by(SaleReport.date.desc()).all()
    data = []
    for s in sales:
        product = db.query(Product).filter(Product.id == s.product_id).first()
        agent = db.query(User).filter(User.id == s.agent_id).first()
        data.append([s.date.strftime('%d/%m/%Y'), agent.nom if agent else "?", product.nom if product else "?", str(s.quantite), f"{s.montant_total:,.0f} FBU"])
    pdf = create_pdf("Rapport des Ventes", data, ["Date", "Agent", "Produit", "Quantité", "Total"])
    return Response(content=pdf.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=sales.pdf"})

@router.get("/stock")
def download_stock(
    current_user = Depends(role_required(["DG", "DT"])),
    db: Session = Depends(get_db)
):
    movements = db.query(StockMovement).order_by(StockMovement.date.desc()).all()
    data = []
    for m in movements:
        product = db.query(Product).filter(Product.id == m.product_id).first()
        data.append([m.date.strftime('%d/%m/%Y'), product.nom if product else "?", str(m.quantite_entree), str(m.quantite_sortie), str(m.quantite_disponible)])
    pdf = create_pdf("Rapport des Mouvements de Stock", data, ["Date", "Produit", "Entrée", "Sortie", "Disponible"])
    return Response(content=pdf.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=stock.pdf"})
