from dataclasses import dataclass
from enum import Enum
import io
import qrcode

from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm, inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4, A3, LETTER

from sample_qrs import sample_qrs


class Orientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@dataclass
class PageConfig:
    width: float
    height: float
    margin_x: float = 10 * mm
    margin_y: float = 10 * mm


@dataclass
class LabelConfig:
    width: float
    height: float
    gap_x: float = 0
    gap_y: float = 0

    show_border: bool = True
    border_width: float = 0.2

    inner_padding_x: float = 1 * mm
    inner_padding_y: float = 1 * mm


@dataclass
class QRConfig:
    width: float = 12 * mm
    height: float = 12 * mm

    offset_y: float = 3.5 * mm

    border: int = 0

    fit: bool = True


@dataclass
class TextConfig:
    enabled: bool = True

    font_name: str = "Helvetica"
    font_size: float = 5.8

    offset_y: float = 1 * mm


def detect_best_orientation(page: PageConfig, label: LabelConfig) -> Orientation:

    portrait_cols = int((page.width - (2 * page.margin_x)) // (label.width + label.gap_x))

    portrait_rows = int((page.height - (2 * page.margin_y)) // (label.height + label.gap_y))

    portrait_total = portrait_cols * portrait_rows

    landscape_cols = int((page.width - (2 * page.margin_x)) // (label.height + label.gap_x))

    landscape_rows = int((page.height - (2 * page.margin_y)) // (label.width + label.gap_y))

    landscape_total = landscape_cols * landscape_rows

    return (
        Orientation.PORTRAIT
        if portrait_total >= landscape_total
        else Orientation.LANDSCAPE
    )


def compute_grid(page: PageConfig, label: LabelConfig, orientation: Orientation):

    if orientation == Orientation.LANDSCAPE:
        label_width = label.height
        label_height = label.width
    else:
        label_width = label.width
        label_height = label.height

    usable_width = page.width - (2 * page.margin_x)
    usable_height = page.height - (2 * page.margin_y)

    step_x = label_width + label.gap_x
    step_y = label_height + label.gap_y

    cols = int(usable_width // step_x)
    rows = int(usable_height // step_y)

    total_grid_width = cols * step_x
    total_grid_height = rows * step_y

    start_x = page.margin_x + ((usable_width - total_grid_width) / 2)

    start_y = page.margin_y + ((usable_height - total_grid_height) / 2)

    return {
        "rows": rows,
        "cols": cols,
        "step_x": step_x,
        "step_y": step_y,
        "start_x": start_x,
        "start_y": start_y,
        "label_width": label_width,
        "label_height": label_height,
    }


def iter_grid(rows, cols):

    for row in range(rows):

        for col in range(cols):

            yield row, col


def generate_qr_image(value: str, border: int = 0, fit: bool = True):

    qr = qrcode.QRCode(version=1, box_size=10, border=border)

    qr.add_data(value)

    qr.make(fit=fit)

    qr_img = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = io.BytesIO()

    qr_img.save(buffer, format="PNG")

    buffer.seek(0)

    return ImageReader(buffer)


def draw_qr(canvas, qr_image, x, y, width, height):

    canvas.drawImage(
        qr_image,
        x,
        y,
        width=width,
        height=height,
        preserveAspectRatio=True,
        mask='auto',
    )


def draw_label(canvas, x, y, value, label_width, label_height, label_cfg: LabelConfig, qr_cfg: QRConfig, text_cfg: TextConfig):

    if label_cfg.show_border:

        canvas.setLineWidth(label_cfg.border_width)

        canvas.rect(
            x,
            y,
            label_width,
            label_height,
        )

    inner_x = x + label_cfg.inner_padding_x
    inner_y = y + label_cfg.inner_padding_y

    inner_width = (label_width - (2 * label_cfg.inner_padding_x))

    inner_height = (label_height - (2 * label_cfg.inner_padding_y))

    qr_x = inner_x + ((inner_width - qr_cfg.width) / 2)

    qr_y = inner_y + qr_cfg.offset_y

    qr_image = generate_qr_image(value=value, border=qr_cfg.border, fit=qr_cfg.fit)

    draw_qr(canvas=canvas, qr_image=qr_image, x=qr_x, y=qr_y, width=qr_cfg.width, height=qr_cfg.height)

    if text_cfg.enabled:

        canvas.setFont(
            text_cfg.font_name,
            text_cfg.font_size,
        )

        text_x = inner_x + (inner_width / 2)

        text_y = inner_y + text_cfg.offset_y

        canvas.drawCentredString(
            text_x,
            text_y,
            value,
        )


def render_pdf(filename: str, data: list, page_cfg: PageConfig, label_cfg: LabelConfig, qr_cfg: QRConfig, text_cfg: TextConfig):

    pdf = Canvas(
        filename,
        pagesize=(
            page_cfg.width,
            page_cfg.height,
        ),
    )

    orientation = detect_best_orientation(
        page_cfg,
        label_cfg,
    )

    grid = compute_grid(
        page_cfg,
        label_cfg,
        orientation,
    )

    rows = grid["rows"]
    cols = grid["cols"]

    step_x = grid["step_x"]
    step_y = grid["step_y"]

    start_x = grid["start_x"]
    start_y = grid["start_y"]

    label_width = grid["label_width"]
    label_height = grid["label_height"]

    qr_index = 0

    while qr_index < len(data):

        for row, col in iter_grid(rows, cols):

            if qr_index >= len(data):
                break

            x = start_x + (col * step_x)

            y = start_y + (
                (rows - 1 - row)
                * step_y
            )

            draw_label(
                canvas=pdf,
                x=x,
                y=y,
                value=data[qr_index],
                label_width=label_width,
                label_height=label_height,
                label_cfg=label_cfg,
                qr_cfg=qr_cfg,
                text_cfg=text_cfg,
            )

            qr_index += 1

        if qr_index < len(data):

            pdf.showPage()

    pdf.save()

    print(
        f"Generated {filename} "
        f"with {qr_index} QR codes"
    )


def main():

    page_cfg = PageConfig(

        # A4
        # width=A4[0],
        # height=A4[1],

        # A3
        # width=A3[0],
        # height=A3[1],

        # LETTER
        # width=LETTER[0],
        # height=LETTER[1],

        # CUSTOM 8 x 11
        # width=8 * inch,
        # height=11 * inch,

        # margin_x=10 * mm,
        # margin_y=10 * mm,

        width=8 * inch,
        height=11 * inch,

        margin_x=2 * mm,
        margin_y=2 * mm,
    )

    label_cfg = LabelConfig(

        width=16 * mm,
        height=27 * mm,

        gap_x=0,
        gap_y=0,

        show_border=True,

        border_width=0.2,

        inner_padding_x=1 * mm,
        inner_padding_y=1 * mm,
    )

    qr_cfg = QRConfig(

        width=12 * mm,
        height=12 * mm,

        offset_y=3.5 * mm,

        border=0,

        fit=True,
    )

    text_cfg = TextConfig(

        enabled=True,

        font_name="Helvetica",

        font_size=5.8,

        offset_y=1 * mm,
    )

    render_pdf(
        filename="result.pdf",

        data=sample_qrs,

        page_cfg=page_cfg,

        label_cfg=label_cfg,

        qr_cfg=qr_cfg,

        text_cfg=text_cfg,
    )


if __name__ == "__main__":
    main()
