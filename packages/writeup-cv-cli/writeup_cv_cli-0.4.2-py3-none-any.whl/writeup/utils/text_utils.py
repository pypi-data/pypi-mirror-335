import textwrap
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

def draw_wrapped_text(c, text, x, y, max_width, line_height):
    """
    Helper function to draw wrapped text with page break handling.
    """
    wrapper = textwrap.TextWrapper(width=int(max_width / 7))
    lines = wrapper.wrap(text)
    for line in lines:
        if y < inch:
            c.showPage()
            y = letter[1] - inch  # reset to top margin on new page
            c.setFont("Helvetica", 12)
        c.drawString(x, y, line)
        y -= line_height
    return y
