# -*- coding: utf-8 -*-
"""
太乙AGI 6.0 - Pygame图形界面
Pygame Graphical User Interface

版本: v1.0
日期: 2026-05-13
"""

import pygame
import sys
import math
import time
from typing import Dict, List, Optional

# 初始化pygame
pygame.init()

# 颜色定义 - 赛博朋克风格
COLORS = {
    'bg_dark': (10, 10, 25),
    'bg_panel': (20, 20, 40),
    'cyan': (0, 255, 255),
    'purple': (138, 43, 226),
    'pink': (255, 20, 147),
    'green': (0, 255, 128),
    'yellow': (255, 255, 0),
    'white': (255, 255, 255),
    'gray': (128, 128, 128),
    'red': (255, 50, 50),
    'orange': (255, 165, 0),
}

# 字体
pygame.font.init()
FONT_TITLE = None
FONT_MAIN = None
FONT_SMALL = None

def get_fonts():
    global FONT_TITLE, FONT_MAIN, FONT_SMALL
    try:
        FONT_TITLE = pygame.font.SysFont('microsoftyahei', 28)
        FONT_MAIN = pygame.font.SysFont('microsoftyahei', 18)
        FONT_SMALL = pygame.font.SysFont('microsoftyahei', 14)
    except:
        FONT_TITLE = pygame.font.SysFont('arial', 28)
        FONT_MAIN = pygame.font.SysFont('arial', 18)
        FONT_SMALL = pygame.font.SysFont('arial', 14)

get_fonts()


class SpringWormParticle:
    """弹簧虫粒子"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = (math.random() - 0.5) * 2
        self.vy = (math.random() - 0.5) * 2
        self.radius = 3 + math.random() * 3
        self.hue = int(time.time() * 100) % 360
        self.life = 1.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.98
        self.vy *= 0.98
        self.life -= 0.005
        self.hue = (self.hue + 1) % 360

    def draw(self, screen):
        if self.life > 0:
            r = int(255 * self.life)
            g = int(100 + 155 * (math.sin(self.hue * 0.1) * 0.5 + 0.5))
            b = int(200 * self.life)
            alpha = int(255 * self.life)
            # 简化的圆形绘制
            try:
                pygame.draw.circle(screen, (r, g, b), (int(self.x), int(self.y)), int(self.radius * self.life))
            except:
                pygame.draw.circle(screen, (255, 100, 200), (int(self.x), int(self.y)), 3)


class CurvatureOrb:
    """曲率球体 - 意图流形可视化"""
    def __init__(self, x, y, curvature, intent_type):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.curvature = curvature
        self.intent_type = intent_type
        self.radius = 30 + curvature * 50
        self.rotation = 0
        self.particles = []
        self.rings = []
        for i in range(3):
            self.rings.append({
                'radius': self.radius + i * 20,
                'alpha': 1.0 - i * 0.3,
                'rotation': i * 0.5
            })

    def update(self):
        # 平滑移动
        self.x += (self.target_x - self.x) * 0.05
        self.y += (self.target_y - self.y) * 0.05
        self.rotation += 0.02

        # 更新光环
        for ring in self.rings:
            ring['rotation'] += 0.01
            ring['alpha'] = 0.3 + 0.2 * math.sin(time.time() * 2 + ring['rotation'])

        # 粒子效果
        if math.random() < 0.3:
            angle = math.random() * 2 * math.pi
            dist = self.radius + math.random() * 30
            self.particles.append({
                'x': self.x + math.cos(angle) * dist,
                'y': self.y + math.sin(angle) * dist,
                'vx': math.cos(angle) * 0.5,
                'vy': math.sin(angle) * 0.5,
                'life': 1.0
            })

        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 0.02
            if p['life'] <= 0:
                self.particles.remove(p)

    def draw(self, screen):
        # 绘制光环
        for ring in self.rings:
            rect = pygame.Rect(
                int(self.x - ring['radius']),
                int(self.y - ring['radius']),
                int(ring['radius'] * 2),
                int(ring['radius'] * 2)
            )
            try:
                pygame.draw.ellipse(screen, COLORS['cyan'], rect, 2)
            except:
                pass

        # 绘制中心球
        base_color = self._get_color()
        try:
            pygame.draw.circle(screen, base_color, (int(self.x), int(self.y)), int(self.radius))
            # 内部高光
            highlight_x = int(self.x - self.radius * 0.3)
            highlight_y = int(self.y - self.radius * 0.3)
            pygame.draw.circle(screen, (200, 200, 255), (highlight_x, highlight_y), int(self.radius * 0.2))
        except:
            pass

        # 绘制粒子
        for p in self.particles:
            try:
                alpha = int(255 * p['life'])
                color = (0, int(255 * p['life']), int(255 * p['life']))
                pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), 2)
            except:
                pass

        # 绘制意图文字
        text = FONT_SMALL.render(self.intent_type, True, COLORS['white'])
        text_rect = text.get_rect(center=(int(self.x), int(self.y + self.radius + 20)))
        screen.blit(text, text_rect)

        # 曲率数值
        curv_text = FONT_SMALL.render(f"κ={self.curvature:.2f}", True, COLORS['yellow'])
        curv_rect = curv_text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(curv_text, curv_rect)

    def _get_color(self):
        colors = {
            'task': COLORS['cyan'],
            'query': COLORS['green'],
            'analysis': COLORS['purple'],
            'learning': COLORS['orange'],
            'creative': COLORS['pink'],
        }
        return colors.get(self.intent_type, COLORS['cyan'])


class DIKWPBar:
    """DIKWP状态条"""
    def __init__(self, x, y, width, height, label, value, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.value = value
        self.target_value = value
        self.color = color
        self.glow = 0

    def set_value(self, value):
        self.target_value = max(0, min(1, value))

    def update(self):
        self.value += (self.target_value - self.value) * 0.1
        self.glow = (math.sin(time.time() * 3) * 0.3 + 0.7)

    def draw(self, screen):
        # 背景
        pygame.draw.rect(screen, COLORS['bg_panel'], (self.x, self.y, self.width, self.height), border_radius=3)

        # 填充
        fill_width = int((self.width - 4) * self.value)
        if fill_width > 0:
            glow_intensity = int(100 * self.glow)
            fill_color = (
                min(255, self.color[0] + glow_intensity),
                min(255, self.color[1] + glow_intensity),
                min(255, self.color[2] + glow_intensity)
            )
            pygame.draw.rect(screen, fill_color, (self.x + 2, self.y + 2, fill_width, self.height - 4), border_radius=2)

        # 标签
        label_text = FONT_SMALL.render(f"{self.label} {int(self.value * 100)}%", True, COLORS['white'])
        screen.blit(label_text, (self.x + 5, self.y + 5))


class InputBox:
    """输入框"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.x <= event.pos[0] <= self.x + self.width and self.y <= event.pos[1] <= self.y + self.height
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True  # 返回文本
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.unicode and len(self.text) < 100:
                    self.text += event.unicode
        return False

    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        # 边框
        border_color = COLORS['cyan'] if self.active else COLORS['gray']
        pygame.draw.rect(screen, border_color, (self.x, self.y, self.width, self.height), 2, border_radius=5)

        # 提示文字
        if not self.text:
            hint = FONT_MAIN.render("输入您的请求... (回车发送)", True, COLORS['gray'])
            screen.blit(hint, (self.x + 10, self.y + 10))
        else:
            text_surface = FONT_MAIN.render(self.text, True, COLORS['white'])
            screen.blit(text_surface, (self.x + 10, self.y + 10))

        # 光标
        if self.active and self.cursor_visible:
            cursor_x = self.x + 10 + FONT_MAIN.size(self.text)[0] + 2
            pygame.draw.line(screen, COLORS['white'], (cursor_x, self.y + 5), (cursor_x, self.y + self.height - 5), 2)


class ChatMessage:
    """聊天消息"""
    def __init__(self, text, is_user=True, intent_type="", curvature=0):
        self.text = text
        self.is_user = is_user
        self.intent_type = intent_type
        self.curvature = curvature
        self.timestamp = time.time()
        self.alpha = 0

    def update(self):
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + 15)

    def draw(self, screen, y_pos, width):
        if self.alpha == 0:
            return 0

        # 背景
        if self.is_user:
            bg_color = (30, 60, 90)
            x = width - 400
        else:
            bg_color = (60, 30, 60)
            x = 50

        # 消息气泡
        try:
            pygame.draw.rect(screen, bg_color, (x, y_pos, 350, 60), border_radius=10)

            # 发送者标签
            label = "你" if self.is_user else f"AGI ({self.intent_type}, κ={self.curvature:.2f})"
            label_color = COLORS['cyan'] if self.is_user else COLORS['pink']
            label_text = FONT_SMALL.render(label, True, label_color)
            screen.blit(label_text, (x + 10, y_pos + 5))

            # 内容
            content = self.text[:50] + "..." if len(self.text) > 50 else self.text
            content_text = FONT_SMALL.render(content, True, COLORS['white'])
            screen.blit(content_text, (x + 10, y_pos + 25))
        except:
            pass

        return 70  # 消息高度


class AGIGUI:
    """太乙AGI 6.0 图形界面"""
    def __init__(self, agi_system):
        self.agi = agi_system
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("太乙AGI 6.0 - 革命性人机交互系统")
        self.clock = pygame.time.Clock()

        # 组件
        self.input_box = InputBox(50, 720, 800, 50)
        self.messages = []

        # 曲率球
        self.curvature_orb = CurvatureOrb(200, 200, 0.5, "task")

        # DIKWP条
        self.dikwp_bars = {
            'D': DIKWPBar(850, 100, 300, 25, "Data", 0.9, COLORS['cyan']),
            'I': DIKWPBar(850, 140, 300, 25, "Info", 0.88, COLORS['green']),
            'K': DIKWPBar(850, 180, 300, 25, "Know", 0.75, COLORS['purple']),
            'W': DIKWPBar(850, 220, 300, 25, "Wisdom", 0.85, COLORS['pink']),
            'P': DIKWPBar(850, 260, 300, 25, "Purpose", 0.95, COLORS['orange']),
        }

        # 人格信息
        self.persona = self.agi.persona

        # 粒子效果
        self.particles = []

        # 运行状态
        self.running = True
        self.last_update = time.time()

    def add_message(self, user_text, agi_response, intent_type, curvature):
        """添加对话"""
        self.messages.append(ChatMessage(user_text, True))
        self.messages.append(ChatMessage(agi_response[:100], False, intent_type, curvature))
        # 只保留最近10条
        self.messages = self.messages[-10:]

    def handle_input(self, text):
        """处理用户输入"""
        if text.strip():
            # 调用AGI系统
            result = self.agi.process_input(text)

            # 更新曲率球
            if result.intent:
                self.curvature_orb = CurvatureOrb(
                    200, 250,
                    result.intent.curvature,
                    result.intent.intent_type.value
                )

            # 更新DIKWP
            if result.dikwp_panel:
                state = result.dikwp_panel.get_current_state()
                self.dikwp_bars['D'].set_value(state['layers'].get('D', {}).get('value', 0.9))
                self.dikwp_bars['I'].set_value(state['layers'].get('I', {}).get('value', 0.88))
                self.dikwp_bars['K'].set_value(state['layers'].get('K', {}).get('value', 0.75))
                self.dikwp_bars['W'].set_value(state['layers'].get('W', {}).get('value', 0.85))
                self.dikwp_bars['P'].set_value(state['layers'].get('P', {}).get('value', 0.95))

            # 生成响应
            response_text = self._generate_response(result)

            # 添加消息
            self.add_message(
                text,
                response_text,
                result.intent.intent_type.value if result.intent else 'task',
                result.intent.curvature if result.intent else 0.5
            )

    def _generate_response(self, ctx):
        """生成响应文本"""
        if not ctx.intent:
            return "正在处理您的请求..."

        intent_type = ctx.intent.intent_type.value
        curvature = ctx.intent.curvature
        complexity = ctx.intent.complexity

        responses = {
            'task': f"已识别任务类型请求 (复杂度: {complexity:.0%})。正在调用DIKWP处理管道...",
            'query': f"查询请求已接收。曲率 κ={curvature:.2f}，信息密度适中。",
            'analysis': f"分析请求 - 检测到高曲率 {curvature:.2f}，启用深度分析模式。",
            'learning': f"学习请求已识别。认知负荷: {complexity:.0%}，调整知识获取策略。",
            'creative': f"创意生成模式。曲率 {curvature:.2f}，发散度较高。",
        }

        return responses.get(intent_type, "请求已处理完成。")

    def update(self):
        """更新状态"""
        # 更新输入框
        self.input_box.update()

        # 更新DIKWP条
        for bar in self.dikwp_bars.values():
            bar.update()

        # 更新曲率球
        self.curvature_orb.update()

        # 更新消息
        for msg in self.messages:
            msg.update()

        # 粒子效果
        if math.random() < 0.2:
            self.particles.append(SpringWormParticle(
                400 + math.random() * 400,
                300 + math.random() * 300
            ))
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def draw(self):
        """绘制界面"""
        # 背景
        self.screen.fill(COLORS['bg_dark'])

        # 背景网格
        self._draw_grid()

        # 粒子背景
        for p in self.particles:
            p.draw(self.screen)

        # 标题
        title = FONT_TITLE.render("太乙AGI 6.0", True, COLORS['cyan'])
        self.screen.blit(title, (50, 30))

        subtitle = FONT_SMALL.render("基于复合体理学 · 意图流形 · 全息投影", True, COLORS['gray'])
        self.screen.blit(subtitle, (50, 65))

        # 曲率球区域
        orb_title = FONT_MAIN.render("意图流形可视化", True, COLORS['white'])
        self.screen.blit(orb_title, (50, 100))
        pygame.draw.rect(self.screen, COLORS['bg_panel'], (40, 95, 320, 350), border_radius=10)
        self.curvature_orb.draw(self.screen)

        # 曲率说明
        curv_info = FONT_SMALL.render(f"曲率: {self.curvature_orb.curvature:.3f}", True, COLORS['yellow'])
        self.screen.blit(curv_info, (50, 460))

        # DIKWP面板
        dikwp_title = FONT_MAIN.render("DIKWP 状态仪表盘", True, COLORS['white'])
        self.screen.blit(dikwp_title, (850, 50))
        pygame.draw.rect(self.screen, COLORS['bg_panel'], (840, 45, 320, 250), border_radius=10)
        for bar in self.dikwp_bars.values():
            bar.draw(self.screen)

        # 人格面板
        self._draw_persona_panel()

        # 聊天区域
        self._draw_chat_area()

        # 输入框
        self.input_box.draw(self.screen)

        # 发送按钮
        self._draw_send_button()

        pygame.display.flip()

    def _draw_grid(self):
        """绘制背景网格"""
        for i in range(0, 1200, 50):
            pygame.draw.line(self.screen, (20, 20, 40), (i, 0), (i, 800), 1)
        for i in range(0, 800, 50):
            pygame.draw.line(self.screen, (20, 20, 40), (0, i), (1200, i), 1)

    def _draw_persona_panel(self):
        """绘制人格面板"""
        pygame.draw.rect(self.screen, COLORS['bg_panel'], (40, 470, 320, 200), border_radius=10)

        if self.persona:
            # 名称
            name = FONT_MAIN.render(f"虚拟人格体: {self.persona.name}", True, COLORS['cyan'])
            self.screen.blit(name, (50, 480))

            # MBTI
            mbti = FONT_MAIN.render(f"MBTI: {self.persona.mbti_type}", True, COLORS['purple'])
            self.screen.blit(mbti, (50, 510))

            # 情绪
            emotion = FONT_MAIN.render(f"情绪: {self.persona.emotion.state.value}", True, COLORS['pink'])
            self.screen.blit(emotion, (50, 540))

            # CQ
            cq = self.persona._compute_cq_score()
            cq_text = FONT_MAIN.render(f"认知商数: {cq:.3f}", True, COLORS['green'])
            self.screen.blit(cq_text, (50, 570))

    def _draw_chat_area(self):
        """绘制聊天区域"""
        pygame.draw.rect(self.screen, COLORS['bg_panel'], (400, 95, 400, 550), border_radius=10)

        title = FONT_MAIN.render("对话历史", True, COLORS['white'])
        self.screen.blit(title, (410, 100))

        # 绘制消息
        y = 140
        for msg in self.messages:
            h = msg.draw(self.screen, y, 1200)
            y += h
            if y > 600:
                break

    def _draw_send_button(self):
        """绘制发送按钮"""
        mouse_pos = pygame.mouse.get_pos()
        btn_x, btn_y, btn_w, btn_h = 870, 720, 100, 50
        hovered = btn_x <= mouse_pos[0] <= btn_x + btn_w and btn_y <= mouse_pos[1] <= btn_y + btn_h

        color = COLORS['cyan'] if hovered else COLORS['gray']
        pygame.draw.rect(self.screen, color, (btn_x, btn_y, btn_w, btn_h), border_radius=8)

        text = FONT_MAIN.render("发送", True, COLORS['white'])
        text_rect = text.get_rect(center=(btn_x + btn_w // 2, btn_y + btn_h // 2))
        self.screen.blit(text, text_rect)

        return hovered

    def run(self):
        """运行主循环"""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                # 处理输入
                if self.input_box.handle_event(event):
                    text = self.input_box.text
                    self.input_box.text = ""
                    self.handle_input(text)

                # 发送按钮点击
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 870 <= x <= 970 and 720 <= y <= 770:
                        if self.input_box.text.strip():
                            text = self.input_box.text
                            self.input_box.text = ""
                            self.handle_input(text)

            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def run_gui_mode(agi_system):
    """运行图形界面模式"""
    gui = AGIGUI(agi_system)
    gui.run()


if __name__ == "__main__":
    # 测试用
    from agi_main_window import CompositeAGI6
    agi = CompositeAGI6("INTJ")
    run_gui_mode(agi)
