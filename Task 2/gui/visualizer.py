"""Canvas-based visualizer for Fibonacci spirals, bar distributions, and Golden Ratio convergence."""

import math
import tkinter as tk
from typing import List, Optional, Tuple
from .theme import PALETTE, FONTS


class FibonacciVisualizer(tk.Canvas):
    """Interactive visualizer supporting Golden Spiral and ratio convergence rendering."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        kwargs.setdefault("bg", PALETTE["bg_card"])
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightbackground", PALETTE["border_subtle"])
        super().__init__(parent, **kwargs)
        
        self.step_index = 0
        self.max_steps = 10
        self.is_animating = False
        self.animation_job: Optional[str] = None
        self.animation_speed_ms = 400
        self.mode = "spiral"  # 'spiral' or 'convergence'

        self.bind("<Configure>", lambda e: self.redraw())

    def set_mode(self, mode: str) -> None:
        """Sets visualization mode: 'spiral' or 'convergence'."""
        self.mode = mode
        self.redraw()

    def set_speed(self, speed_ms: int) -> None:
        """Sets animation tick delay in milliseconds."""
        self.animation_speed_ms = max(50, speed_ms)

    def reset(self) -> None:
        """Resets animation to initial step."""
        self.stop_animation()
        self.step_index = 1
        self.redraw()

    def start_animation(self, max_steps: int = 12) -> None:
        """Begins animated step-by-step rendering."""
        self.max_steps = max_steps
        self.is_animating = True
        self._animate_step()

    def stop_animation(self) -> None:
        """Pauses animation."""
        self.is_animating = False
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None

    def step_forward(self) -> None:
        """Advances one step."""
        if self.step_index < self.max_steps:
            self.step_index += 1
            self.redraw()

    def step_backward(self) -> None:
        """Goes back one step."""
        if self.step_index > 1:
            self.step_index -= 1
            self.redraw()

    def _animate_step(self) -> None:
        if not self.is_animating:
            return
        if self.step_index < self.max_steps:
            self.step_index += 1
            self.redraw()
            self.animation_job = self.after(self.animation_speed_ms, self._animate_step)
        else:
            self.is_animating = False

    def redraw(self) -> None:
        """Clears and re-renders active visualization."""
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 50 or height < 50:
            return

        if self.mode == "spiral":
            self._draw_golden_spiral(width, height)
        else:
            self._draw_ratio_convergence(width, height)

    def _draw_golden_spiral(self, width: int, height: int) -> None:
        """Draws Fibonacci squares and logarithmic spiral arcs."""
        # Calculate Fibonacci sequence up to step_index
        fibs = [1, 1]
        for _ in range(max(0, self.step_index - 1)):
            fibs.append(fibs[-1] + fibs[-2])
        
        display_fibs = fibs[:self.step_index + 1]
        
        # Header text
        self.create_text(
            20, 20,
            text=f"Fibonacci Golden Spiral (Step {self.step_index}/{self.max_steps})",
            fill=PALETTE["accent_cyan"],
            font=FONTS["title_md"],
            anchor="nw"
        )
        self.create_text(
            20, 42,
            text=f"Current Term F({self.step_index}) = {display_fibs[-1]:,} | Golden Ratio φ ≈ 1.6180339887",
            fill=PALETTE["text_secondary"],
            font=FONTS["body_sm"],
            anchor="nw"
        )

        cx, cy = width * 0.48, height * 0.52
        scale = min(width, height) / (display_fibs[-1] * 2.8 if display_fibs[-1] > 1 else 100)
        scale = max(scale, 1.2)

        # Directions: 0: right, 1: top, 2: left, 3: bottom
        directions = [(1, 0), (0, -1), (-1, 0), (0, 1)]
        cur_x, cur_y = cx, cy

        # Calculate square positions
        squares = []
        # Precomputed coordinates for canonical spiral winding
        # [ (side, x_min, y_min, x_max, y_max, arc_bbox, start_angle) ]
        x, y = cur_x, cur_y
        
        # Standard winding offsets for Fibonacci squares
        # Start with F(1)=1 at origin
        w_x, w_y = cx - 20, cy - 20
        dx_dir = [ (0, 1), (-1, 0), (0, -1), (1, 0) ]
        
        # Let's use clean parametric logarithmic spiral for smooth rendering
        # Draw background grid lines
        grid_step = 40
        for gx in range(0, width, grid_step):
            self.create_line(gx, 0, gx, height, fill="#131D31", dash=(2, 4))
        for gy in range(0, height, grid_step):
            self.create_line(0, gy, width, gy, fill="#131D31", dash=(2, 4))

        # Draw spiral curve using logarithmic spiral formula: r = a * e^(b * theta)
        phi = (1 + math.sqrt(5)) / 2
        b = math.log(phi) / (math.pi / 2)
        
        max_theta = min(self.step_index * (math.pi / 2), 12 * math.pi / 2)
        points = []
        num_points = int(max_theta * 40)
        
        initial_radius = 8.0 * scale * 0.3
        
        for i in range(max(1, num_points)):
            theta = (i / num_points) * max_theta
            r = initial_radius * math.exp(b * theta * 0.45)
            px = cx + r * math.cos(theta)
            py = cy - r * math.sin(theta)  # flip y for canvas coords
            points.append((px, py))

        # Draw glowing spiral line
        if len(points) > 1:
            flattened = [coord for pt in points for coord in pt]
            # Outer glow
            self.create_line(flattened, fill="#0E7490", width=6, smooth=True, capstyle="round")
            # Core neon line
            self.create_line(flattened, fill=PALETTE["accent_emerald"], width=2.5, smooth=True, capstyle="round")

            # Draw glowing nodes at each quarter turn
            for step in range(1, self.step_index + 1):
                theta_step = step * (math.pi / 2)
                if theta_step <= max_theta:
                    r_step = initial_radius * math.exp(b * theta_step * 0.45)
                    nx = cx + r_step * math.cos(theta_step)
                    ny = cy - r_step * math.sin(theta_step)
                    
                    color = PALETTE["spiral_colors"][(step - 1) % len(PALETTE["spiral_colors"])]
                    self.create_oval(nx - 7, ny - 7, nx + 7, ny + 7, fill=color, outline="#FFFFFF", width=1.5)
                    self.create_text(
                        nx + 10, ny - 8,
                        text=f"F{step}={display_fibs[step-1]}",
                        fill=PALETTE["text_primary"],
                        font=FONTS["tag"],
                        anchor="w"
                    )

    def _draw_ratio_convergence(self, width: int, height: int) -> None:
        """Plots convergence of ratio F(n)/F(n-1) to the Golden Ratio Phi (1.618033...)."""
        pad_x, pad_y = 60, 60
        plot_w = width - 2 * pad_x
        plot_h = height - 2 * pad_y
        
        # Header
        self.create_text(
            20, 20,
            text="Golden Ratio Convergence: lim(n→∞) F(n) / F(n-1) = φ",
            fill=PALETTE["accent_emerald"],
            font=FONTS["title_md"],
            anchor="nw"
        )

        # Axes
        self.create_line(pad_x, height - pad_y, width - pad_x, height - pad_y, fill=PALETTE["text_muted"], width=1.5)
        self.create_line(pad_x, pad_y, pad_x, height - pad_y, fill=PALETTE["text_muted"], width=1.5)

        phi = (1 + math.sqrt(5)) / 2  # 1.6180339887...
        
        # Y range: 1.0 to 2.2
        y_min, y_max = 1.0, 2.2
        
        def to_canvas(step: int, val: float) -> Tuple[float, float]:
            cx = pad_x + (step / max(1, self.max_steps)) * plot_w
            cy = (height - pad_y) - ((val - y_min) / (y_max - y_min)) * plot_h
            return cx, cy

        # Draw Phi asymptote line
        _, phi_y = to_canvas(0, phi)
        self.create_line(pad_x, phi_y, width - pad_x, phi_y, fill=PALETTE["accent_amber"], dash=(4, 4), width=1.5)
        self.create_text(
            width - pad_x - 5, phi_y - 12,
            text=f"φ ≈ {phi:.10f}",
            fill=PALETTE["accent_amber"],
            font=FONTS["mono_sm"],
            anchor="e"
        )

        # Calculate Fibonacci ratios
        fibs = [0, 1]
        for _ in range(self.max_steps + 2):
            fibs.append(fibs[-1] + fibs[-2])

        ratios = []
        for i in range(2, min(len(fibs), self.step_index + 2)):
            r = fibs[i] / fibs[i - 1]
            ratios.append((i - 1, r))

        # Plot points and connecting lines
        points = []
        for idx, r in ratios:
            px, py = to_canvas(idx, min(max(r, y_min), y_max))
            points.append((px, py))

        if len(points) > 1:
            flattened = [coord for pt in points for coord in pt]
            self.create_line(flattened, fill=PALETTE["accent_cyan"], width=2.5)

        for i, (idx, r) in enumerate(ratios):
            px, py = points[i]
            self.create_oval(px - 5, py - 5, px + 5, py + 5, fill=PALETTE["accent_indigo"], outline=PALETTE["text_primary"], width=1.5)
            self.create_text(
                px, py - 12,
                text=f"{r:.4f}",
                fill=PALETTE["text_primary"],
                font=FONTS["mono_sm"]
            )
            # X-axis label
            self.create_text(px, height - pad_y + 15, text=f"n={idx}", fill=PALETTE["text_secondary"], font=FONTS["mono_sm"])
