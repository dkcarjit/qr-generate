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

Dimensions:

Label size: 16 mm × 27 mm
QR size: 12 mm × 12 mm
Internal padding: 1 mm on all sides
Left border → QR: 2 mm
Right border → QR: 2 mm
Bottom border → QR: 4.5 mm
Top border → QR: 10.5 mm
Text gap above QR: 1 mm
Label-to-label gap: 0 mm horizontally and vertically
Page margin: 2 mm on all sides
