# ui_base.py
# Base UI components for Dark Tamagotchi

import pygame
import pygame.freetype
from tamagotchi.utils.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, PURPLE,
    FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_HUGE
)

# Initialize pygame fonts
pygame.freetype.init()

class UIElement:
    """Base class for UI elements"""

    def __init__(self, x, y, width, height):
        """
        Initialize a UI element

        Parameters:
        -----------
        x : int
            X coordinate
        y : int
            Y coordinate
        width : int
            Width of the element
        height : int
            Height of the element
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True

    def draw(self, surface):
        """
        Draw the element

        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        if not self.visible:
            return

    def handle_event(self, event):
        """
        Handle pygame event

        Parameters:
        -----------
        event : pygame.event.Event
            The event to handle

        Returns:
        --------
        bool
            True if the event was handled, False otherwise
        """
        if not self.visible or not self.enabled:
            return False

        return False

    def update(self, dt):
        """
        Update the element

        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        pass

    def set_position(self, x, y):
        """
        Set the position of the element

        Parameters:
        -----------
        x : int
            New X coordinate
        y : int
            New Y coordinate
        """
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Button(UIElement):
    """Button UI element"""

    def __init__(self, x, y, width, height, text, callback=None,
                 bg_color=DARK_GRAY, hover_color=GRAY, text_color=WHITE,
                 font_size=FONT_MEDIUM, tooltip=None):
        """
        Initialize a button

        Parameters:
        -----------
        x : int
            X coordinate
        y : int
            Y coordinate
        width : int
            Width of the button
        height : int
            Height of the button
        text : str
            Text to display on the button
        callback : function, optional
            Function to call when the button is clicked
        bg_color : tuple, optional
            Background color
        hover_color : tuple, optional
            Background color when hovered
        text_color : tuple, optional
            Text color
        font_size : int, optional
            Font size
        tooltip : str, optional
            Tooltip text
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.tooltip = tooltip
        self.hovered = False
        self.pressed = False
        self.font = pygame.freetype.SysFont('Arial', font_size)

    def draw(self, surface):
        """
        Draw the button

        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        if not self.visible:
            return

        # Determine background color
        color = self.hover_color if self.hovered else self.bg_color

        # Draw button background
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=5)

        # Draw text
        text_surf, text_rect = self.font.render(self.text, self.text_color)
        text_x = self.x + (self.width - text_rect.width) // 2
        text_y = self.y + (self.height - text_rect.height) // 2
        surface.blit(text_surf, (text_x, text_y))

    def handle_event(self, event):
        """
        Handle pygame event

        Parameters:
        -----------
        event : pygame.event.Event
            The event to handle

        Returns:
        --------
        bool
            True if the event was handled, False otherwise
        """
        if not self.visible or not self.enabled:
            return False

        # Mouse motion
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return self.hovered

        # Mouse button down
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.pressed = True
                return True

        # Mouse button up
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False

            # If button was pressed and is still hovered, call callback
            if was_pressed and self.hovered and self.callback:
                self.callback()
                return True

        return False

    def set_text(self, text):
        """
        Set the button text

        Parameters:
        -----------
        text : str
            New text
        """
        self.text = text

class TextBox(UIElement):
    """Text box UI element for displaying text"""

    def __init__(self, x, y, width, height, text="", bg_color=None, text_color=WHITE,
                 font_size=FONT_MEDIUM, align="left", valign="top", border=False,
                 multiline=False, max_lines=None):
        """
        Initialize a text box

        Parameters:
        -----------
        x : int
            X coordinate
        y : int
            Y coordinate
        width : int
            Width of the text box
        height : int
            Height of the text box
        text : str, optional
            Text to display
        bg_color : tuple, optional
            Background color (None for transparent)
        text_color : tuple, optional
            Text color
        font_size : int, optional
            Font size
        align : str, optional
            Text alignment: 'left', 'center', 'right'
        valign : str, optional
            Vertical alignment: 'top', 'middle', 'bottom'
        border : bool, optional
            Whether to draw a border
        multiline : bool, optional
            Whether to support multiple lines
        max_lines : int, optional
            Maximum number of lines to display
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_size = font_size
        self.align = align
        self.valign = valign
        self.border = border
        self.multiline = multiline
        self.max_lines = max_lines
        self.font = pygame.freetype.SysFont('Arial', font_size)

    def draw(self, surface):
        """
        Draw the text box

        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        if not self.visible:
            return

        # Draw background if specified
        if self.bg_color:
            pygame.draw.rect(surface, self.bg_color, self.rect)

        # Draw border if specified
        if self.border:
            pygame.draw.rect(surface, WHITE, self.rect, width=1)

        # Draw text
        if self.multiline:
            self.draw_multiline_text(surface)
        else:
            self.draw_single_line_text(surface)

    def draw_single_line_text(self, surface):
        """
        Draw single line text

        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        text_surf, text_rect = self.font.render(self.text, self.text_color)

        # Horizontal alignment
        if self.align == "left":
            text_x = self.x + 5
        elif self.align == "center":
            text_x = self.x + (self.width - text_rect.width) // 2
        else:  # right
            text_x = self.x + self.width - text_rect.width - 5

        # Vertical alignment
        if self.valign == "top":
            text_y = self.y + 5
        elif self.valign == "middle":
            text_y = self.y + (self.height - text_rect.height) // 2
        else:  # bottom
            text_y = self.y + self.height - text_rect.height - 5

        surface.blit(text_surf, (text_x, text_y))

    def draw_multiline_text(self, surface):
        """
        Draw multiline text

        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        # Split text into lines
        lines = self.text.splitlines()

        # Apply max_lines limit if specified
        if self.max_lines and len(lines) > self.max_lines:
            lines = lines[:self.max_lines]

        # Calculate line height
        _, text_rect = self.font.render("Tg", self.text_color)
        line_height = text_rect.height + 2

        # Calculate starting Y position based on vertical alignment
        total_height = line_height * len(lines)
        if self.valign == "top":
            start_y = self.y + 5
        elif self.valign == "middle":
            start_y = self.y + (self.height - total_height) // 2
        else:  # bottom
            start_y = self.y + self.height - total_height - 5

        # Draw each line
        for i, line in enumerate(lines):
            text_surf, text_rect = self.font.render(line, self.text_color)

            # Horizontal alignment
            if self.align == "left":
                text_x = self.x + 5
            elif self.align == "center":
                text_x = self.x + (self.width - text_rect.width) // 2
            else:  # right
                text_x = self.x + self.width - text_rect.width - 5

            text_y = start_y + i * line_height
            surface.blit(text_surf, (text_x, text_y))

    def set_text(self, text):
        """
        Set the text box text

        Parameters:
        -----------
        text : str
            New text
        """
        self.text = text

class ProgressBar(UIElement):
    """Progress bar UI element"""

    def __init__(self, x, y, width, height, value=0, max_value=100, bg_color=DARK_GRAY,
                 fill_color=GREEN, border_color=WHITE, show_text=True, label=None):
        """
        Initialize a progress bar

        Parameters:
        -----------
        x : int
            X coordinate
        y : int
            Y coordinate
        width : int
            Width of the progress bar
        height : int
            Height of the progress bar
        value : int or float, optional
            Current value
        max_value : int or float, optional
            Maximum value
        bg_color : tuple, optional
            Background color
        fill_color : tuple, optional
            Fill color
        border_color : tuple, optional
            Border color
        show_text : bool, optional
            Whether to show the value as text
        label : str, optional
            Label to display next to the progress bar
        """
        super().__init__(x, y, width, height)
        self.value = value
        self.max_value = max_value
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.show_text = show_text
        self.label = label
        self.font = pygame.freetype.SysFont('Arial', FONT_SMALL)

    def draw(self, surface):
        """
        Draw the progress bar

        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        if not self.visible:
            return

        # Draw label if specified
        if self.label:
            label_surf, label_rect = self.font.render(self.label, WHITE)
            surface.blit(label_surf, (self.x - label_rect.width - 10, self.y + (self.height - label_rect.height) // 2))

        # Draw background
        pygame.draw.rect(surface, self.bg_color, self.rect)

        # Draw fill
        fill_width = int((self.value / self.max_value) * self.width)
        fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
        pygame.draw.rect(surface, self.fill_color, fill_rect)

        # Draw border
        pygame.draw.rect(surface, self.border_color, self.rect, width=1)

        # Draw text
        if self.show_text:
            percent = int((self.value / self.max_value) * 100)
            text = f"{percent}%"
            text_surf, text_rect = self.font.render(text, WHITE)
            text_x = self.x + (self.width - text_rect.width) // 2
            text_y = self.y + (self.height - text_rect.height) // 2
            surface.blit(text_surf, (text_x, text_y))

    def set_value(self, value):
        """
        Set the progress bar value

        Parameters:
        -----------
        value : int or float
            New value
        """
        self.value = max(0, min(value, self.max_value))

    def get_percentage(self):
        """
        Get the progress percentage

        Returns:
        --------
        float
            Progress percentage (0-100)
        """
        return (self.value / self.max_value) * 100

class IconButton(Button):
    """Button with an icon"""

    def __init__(self, x, y, width, height, icon, callback=None,
                 bg_color=DARK_GRAY, hover_color=GRAY, text=None,
                 text_color=WHITE, font_size=FONT_SMALL, tooltip=None):
        """
        Initialize an icon button

        Parameters:
        -----------
        x : int
            X coordinate
        y : int
            Y coordinate
        width : int
            Width of the button
        height : int
            Height of the button
        icon : pygame.Surface
            Icon image
        callback : function, optional
            Function to call when the button is clicked
        bg_color : tuple, optional
            Background color
        hover_color : tuple, optional
            Background color when hovered
        text : str, optional
            Text to display below the icon
        text_color : tuple, optional
            Text color
        font_size : int, optional
            Font size
        tooltip : str, optional
            Tooltip text
        """
        super().__init__(x, y, width, height, text or "", callback,
                        bg_color, hover_color, text_color, font_size, tooltip)
        self.icon = icon

    def draw(self, surface):
        """
        Draw the icon button

        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        if not self.visible:
            return

        # Draw button background
        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=5)

        # Draw icon
        icon_x = self.x + (self.width - self.icon.get_width()) // 2
        icon_y = self.y + (self.height - self.icon.get_height()) // 2

        # If there's text, adjust icon position
        if self.text:
            text_surf, text_rect = self.font.render(self.text, self.text_color)
            icon_y = self.y + (self.height - self.icon.get_height() - text_rect.height - 5) // 2

        surface.blit(self.icon, (icon_x, icon_y))

        # Draw text if specified
        if self.text:
            text_surf, text_rect = self.font.render(self.text, self.text_color)
            text_x = self.x + (self.width - text_rect.width) // 2
            text_y = icon_y + self.icon.get_height() + 5
            surface.blit(text_surf, (text_x, text_y))

class Tooltip:
    """Tooltip for UI elements"""

    def __init__(self, text, font_size=FONT_SMALL, bg_color=DARK_GRAY, text_color=WHITE, padding=5):
        """
        Initialize a tooltip

        Parameters:
        -----------
        text : str
            Tooltip text
        font_size : int, optional
            Font size
        bg_color : tuple, optional
            Background color
        text_color : tuple, optional
            Text color
        padding : int, optional
            Padding around the text
        """
        self.text = text
        self.font_size = font_size
        self.bg_color = bg_color
        self.text_color = text_color
        self.padding = padding
        self.font = pygame.freetype.SysFont('Arial', font_size)
        self.visible = False
        self.pos = (0, 0)

    def show(self, pos):
        """
        Show the tooltip at the specified position

        Parameters:
        -----------
        pos : tuple
            Position (x, y) to show the tooltip
        """
        self.pos = pos
        self.visible = True

    def hide(self):
        """Hide the tooltip"""
        self.visible = False

    def draw(self, surface):
        """
        Draw the tooltip

        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        if not self.visible:
            return

        # Render text to get size
        text_surf, text_rect = self.font.render(self.text, self.text_color)

        # Create tooltip rectangle
        tooltip_rect = pygame.Rect(
            self.pos[0],
            self.pos[1],
            text_rect.width + self.padding * 2,
            text_rect.height + self.padding * 2
        )

        # Ensure tooltip stays on screen
        if tooltip_rect.right > WINDOW_WIDTH:
            tooltip_rect.x = WINDOW_WIDTH - tooltip_rect.width
        if tooltip_rect.bottom > WINDOW_HEIGHT:
            tooltip_rect.y = WINDOW_HEIGHT - tooltip_rect.height

        # Draw background
        pygame.draw.rect(surface, self.bg_color, tooltip_rect, border_radius=3)
        pygame.draw.rect(surface, WHITE, tooltip_rect, width=1, border_radius=3)

        # Draw text
        surface.blit(text_surf, (tooltip_rect.x + self.padding, tooltip_rect.y + self.padding))

class ScrollableList(UIElement):
    """Scrollable list UI element"""

    def __init__(self, x, y, width, height, items=None, bg_color=DARK_GRAY,
                 item_height=30, selected_color=BLUE, hover_color=GRAY,
                 text_color=WHITE, font_size=FONT_SMALL, on_select=None):
        """
        Initialize a scrollable list

        Parameters:
        -----------
        x : int
            X coordinate
        y : int
            Y coordinate
        width : int
            Width of the list
        height : int
            Height of the list
        items : list, optional
            List of items to display
        bg_color : tuple, optional
            Background color
        item_height : int, optional
            Height of each item
        selected_color : tuple, optional
            Color of selected item
        hover_color : tuple, optional
            Color of hovered item
        text_color : tuple, optional
            Text color
        font_size : int, optional
            Font size
        on_select : function, optional
            Function to call when an item is selected
        """
        super().__init__(x, y, width, height)
        self.items = items or []
        self.bg_color = bg_color
        self.item_height = item_height
        self.selected_color = selected_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.on_select = on_select
        self.font = pygame.freetype.SysFont('Arial', font_size)

        self.scroll_offset = 0
        self.visible_items = height // item_height
        self.selected_index = -1
        self.hovered_index = -1
        self.dragging = False
        self.drag_start = 0

    def draw(self, surface):
        """
        Draw the scrollable list

        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        if not self.visible:
            return

        # Draw background
        pygame.draw.rect(surface, self.bg_color, self.rect)

        # Draw items
        for i in range(self.visible_items):
            item_index = i + self.scroll_offset
            if item_index >= len(self.items):
                break

            item = self.items[item_index]
            item_rect = pygame.Rect(self.x, self.y + i * self.item_height, self.width, self.item_height)

            # Determine item background color
            if item_index == self.selected_index:
                bg_color = self.selected_color
            elif item_index == self.hovered_index:
                bg_color = self.hover_color
            else:
                bg_color = self.bg_color

            # Draw item background
            pygame.draw.rect(surface, bg_color, item_rect)

            # Draw item text
            text = str(item)
            text_surf, text_rect = self.font.render(text, self.text_color)
            text_x = self.x + 5
            text_y = self.y + i * self.item_height + (self.item_height - text_rect.height) // 2
            surface.blit(text_surf, (text_x, text_y))

        # Draw border
        pygame.draw.rect(surface, WHITE, self.rect, width=1)

    def handle_event(self, event):
        """
        Handle pygame event

        Parameters:
        -----------
        event : pygame.event.Event
            The event to handle

        Returns:
        --------
        bool
            True if the event was handled, False otherwise
        """
        if not self.visible or not self.enabled:
            return False

        # Mouse motion
        if event.type == pygame.MOUSEMOTION:
            # Check if mouse is over the list
            if self.rect.collidepoint(event.pos):
                # Calculate hovered item index
                rel_y = event.pos[1] - self.y
                index = rel_y // self.item_height + self.scroll_offset
                if 0 <= index < len(self.items):
                    self.hovered_index = index
                else:
                    self.hovered_index = -1

                # Handle dragging for scrolling
                if self.dragging:
                    drag_distance = event.pos[1] - self.drag_start
                    scroll_amount = drag_distance // 10
                    if scroll_amount != 0:
                        self.scroll_offset = max(0, min(self.scroll_offset - scroll_amount,
                                                    max(0, len(self.items) - self.visible_items)))
                        self.drag_start = event.pos[1]
                    return True

                return True
            else:
                self.hovered_index = -1

        # Mouse button down
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 1:  # Left click
                    # Calculate clicked item index
                    rel_y = event.pos[1] - self.y
                    index = rel_y // self.item_height + self.scroll_offset
                    if 0 <= index < len(self.items):
                        self.selected_index = index
                        if self.on_select:
                            self.on_select(index, self.items[index])
                    return True

                elif event.button == 4:  # Scroll up
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                    return True

                elif event.button == 5:  # Scroll down
                    self.scroll_offset = min(max(0, len(self.items) - self.visible_items),
                                            self.scroll_offset + 1)
                    return True

        # Mouse button up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                self.dragging = False
                return True

        return False

    def set_items(self, items):
        """
        Set the list items

        Parameters:
        -----------
        items : list
            New list of items
        """
        self.items = items
        self.scroll_offset = 0
        self.selected_index = -1
        self.hovered_index = -1

    def get_selected_item(self):
        """
        Get the selected item

        Returns:
        --------
        object or None
            The selected item, or None if no item is selected
        """
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None