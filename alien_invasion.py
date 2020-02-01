"""主程序，创建游戏窗口，以及总的输入，主干部分"""
import pygame

from pygame.sprite import Group
from settings import Settings
from ship import Ship
from alien import Alien
from game_stats import GameStats
import game_functions as gf
from button import Button
from scoreboard import Scoreboard

def run_game():
    # 初始化游戏并且创造一个屏幕对象

    # 检查硬件
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode(
        (ai_settings.screen_width,ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")

    # 设置背景色
    bg_color = ai_settings.bg_color

    # 创建一艘飞船
    ship = Ship(ai_settings,screen)

    # 创建一个用于存储游戏统计信息的实例,并且创建记分牌
    stats = GameStats(ai_settings)
    sb = Scoreboard(ai_settings, screen, stats)

    # 创建一个用于存储子弹的编组
    bullets = Group()

    # 创建一个外星人
    aliens = Group()

    # 创建外星人群，外星人群不移动
    gf.create_fleet(ai_settings,screen,ship,aliens)

    # 创建Play按钮
    play_button = Button(ai_settings, screen , "Play")

    # 开始游戏的主循环
    while True:
    # 自动循环
        # 监视键盘和鼠标事件
        gf.check_events(ai_settings,screen,stats, sb, play_button, ship, aliens, bullets)

        if stats.game_active:

            ship.update()

            # 更新子弹
            gf.update_bullets(ai_settings, screen, stats, sb, ship,  aliens, bullets)

            # 更新外星人数据
            gf.update_aliens(ai_settings, stats,sb, screen, ship, aliens,bullets
                         )

    # 每次循环都重新绘制屏幕,飞船，子弹
        gf.update_screen(ai_settings,screen,stats, sb, ship,aliens,bullets, play_button)

        #让最近绘制的屏幕可见
        pygame.display.flip()

run_game()