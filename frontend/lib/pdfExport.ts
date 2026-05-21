import jsPDF from "jspdf";
import html2canvas from "html2canvas";

export async function exportReviewToPDF(elementId: string, filename = "ResearchMate_Literature_Review.pdf") {
  const el = document.getElementById(elementId);
  if (!el) {
    console.error(`Export failed: Element ID '${elementId}' not resolved.`);
    return;
  }
  
  try {
    // Canvas conversion with scale multiplier to maintain high DPI printing quality
    const canvas = await html2canvas(el, {
      scale: 2,
      useCORS: true,
      backgroundColor: "#090d16", // match theme
      logging: false
    });
    
    const imgData = canvas.toDataURL("image/png");
    
    // Create A4 sized document
    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "mm",
      format: "a4"
    });
    
    const imgProps = pdf.getImageProperties(imgData);
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
    
    // Support multi-page splitting by iterating height increments if required
    let heightLeft = pdfHeight;
    let position = 0;
    const pageHeight = pdf.internal.pageSize.getHeight();
    
    pdf.addImage(imgData, "PNG", 0, position, pdfWidth, pdfHeight);
    heightLeft -= pageHeight;
    
    while (heightLeft >= 0) {
      position = heightLeft - pdfHeight;
      pdf.addPage();
      pdf.addImage(imgData, "PNG", 0, position, pdfWidth, pdfHeight);
      heightLeft -= pageHeight;
    }
    
    pdf.save(filename);
  } catch (error) {
    console.error("Client-side PDF generation failed: ", error);
  }
}
