# 表・裏PDFを1つにまとめ、仕上がり(TrimBox)と塗り足し(BleedBox)を正確に設定する
import pymupdf
MM = 72 / 25.4
out = pymupdf.open()
for side in ['omote', 'ura']:
    out.insert_pdf(pymupdf.open(f'nyuko/a5-{side}.pdf'))
for page in out:
    page.set_mediabox(pymupdf.Rect(0, 0, 216 * MM, 154 * MM))
    page.set_bleedbox(page.mediabox)
    page.set_trimbox(pymupdf.Rect(3 * MM, 3 * MM, 213 * MM, 151 * MM))
out.save('nyuko/tsunagu-a5-nyuko.pdf', garbage=3, deflate=True)
