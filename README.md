1. Calculates best orientation (portrait/landscape) based on how many labels fit per page.

2. Uses ReportLab’s built-in units (mm, inch) for accurate print measurements.

3. Creates an 8×11 inch PDF using ReportLab Canvas.

4. Each label size is fixed at 16mm × 27mm.

5. Adds 10mm margin on all sides.

6. Grid is calculated using available space after margins and label size.

7. ReportLab canvas uses bottom-left origin (0,0).

8. QR codes are generated using the qrcode library.

9. Each QR is created in memory (BytesIO) and rendered directly onto the PDF canvas (no files saved).

10. Each label contains a centered QR code with its text placed below it inside the label.

11. Labels are placed using grid coordinates (row/column -> x, y positions), with row order inverted for correct top-to-bottom printing.
