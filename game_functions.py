import sys
import pygame

from bullet import Bullet
from alien import Alien
from time import sleep

def check_keydown_events(event,ai_settings,screen,ship,bullets):
    """响应按键"""
    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        # 按下空格，创建子弹，并且加入编组bullets中
        fire_bullet(ai_settings,screen,ship,bullets)
    elif event.key == pygame.K_ESCAPE:
        sys.exit()


def check_keyup_events(event,ship):
    """响应松开"""
    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        ship.moving_left = False

def check_events(ai_settings,screen,stats, sb, play_button, ship, aliens, bullets):
    """响应按键和鼠标事件，将循环事件分离"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen,ship,bullets)

        elif event.type == pygame.KEYUP:
            check_keyup_events(event,ship)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y)

def check_play_button(ai_settings,screen,stats, sb, play_button,ship,aliens,bullets, mouse_x, mouse_y):
    """在玩家单击play按钮时开始新游戏"""
    if play_button.rect.collidepoint(mouse_x, mouse_y):
        # 重置游戏统计信息
        if not stats.game_active:
            # 重置游戏设置
            ai_settings.initialize_dynamic_settings()

            # 游戏开始后隐藏光标
            pygame.mouse.set_visible(False)

            stats.reset_stats()
            stats.game_active = True

            # 重置记分牌图像
            sb.prep_score()
            sb.prep_high_score()
            sb.prep_level()
            sb.prep_ships()

            # 清空外星人列表和子弹列表
            aliens.empty()
            bullets.empty()

            # 创建一群新的外星人，并且让飞船居中
            create_fleet(ai_settings, screen, ship, aliens)
            ship.center_ship()

def update_screen(ai_settings, screen, stats , sb, ship, alien, bullets, play_button):
    """更新屏幕上的图像，并切换到新屏幕"""
    # 每次循环都重绘屏幕
    screen.fill(ai_settings.bg_color)
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    alien.draw(screen) # 画在screen上面
    ship.blitme()
    sb.show_score()

    # 如果游戏处于非活动状态，就会绘制play按钮
    if not stats.game_active:
        play_button.draw_button()

    # 让最近绘制的屏幕可见
    pygame.display.flip()

def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """更新子弹的位置，并且删除已经消失的子弹"""
    # 更新子弹的位置
    bullets.update()

    #删除已经消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    # 检查是否有子弹击中了外星人
    check_bullt_alien_coliisions(ai_settings, screen, stats, sb, ship, aliens, bullets)

def check_bullt_alien_coliisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """相应子弹和外星人的碰撞"""
    # 删除发生碰撞的子弹和外星人
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points*len(aliens)
            sb.prep_score( )
        check_high_score(stats,sb)

    if len(aliens) == 0:
        # 删除现有的子弹并且新建立一群外星人,加快节奏
        # 如果整群外星人都被消灭，就提高一个等级
        bullets.empty()
        ai_settings.increase_speed()

        stats.level += 1
        sb.prep_level()
        create_fleet(ai_settings,screen,ship,aliens)

def fire_bullet(ai_settings,screen,ship,bullets):
    """如果还没有到达限制，就发射一颗子弹"""
    if len(bullets) < ai_settings.bullets_allowed: #子弹数目不超过允许的个数
        new_bullet = Bullet(ai_settings,screen,ship)
        bullets.add(new_bullet)

def get_number_aliens_x(ai_settings,alien_width):
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def get_number_aliens_y(ai_settings,ship_height, alien_height):
    """计算屏幕可以容纳多少行外星人"""
    available_space_y = (ai_settings.screen_height - (4*alien_height) - ship_height)
    number_aliens_y = int(available_space_y/(2*alien_height))

    return number_aliens_y

def create_alien(ai_settings, screen,aliens, alien_number, row_number):
    """创建一个外星人并且将其放在当前行"""

    alien = Alien(ai_settings,screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2*alien_width*alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 1.5*alien.rect.height*row_number + 45
    aliens.add(alien) # 加入编组，编组里面有外星人的参数信息，能够表现出外星人

def create_fleet(ai_settings, screen, ship, aliens):
    """创建外星人群"""

    alien = Alien(ai_settings,screen)
    number_aliens_x = get_number_aliens_x(ai_settings,alien.rect.width)
    number_aliens_y = get_number_aliens_y(ai_settings,ship.rect.height,alien.rect.height)

    # 创建第一行外星人

    for row_number in range (number_aliens_y):
        for alien_number in range(number_aliens_x):
            # 创建一个外星人并且将它加入当前这一行
            create_alien(ai_settings, screen, aliens, alien_number, row_number)

def check_fleet_edges(ai_settings,aliens):
    """有外星人到达边缘时采取相应的措施"""
    for alien in aliens.sprites():
        if alien.check_edges(): # 检查是否到达边缘，到达改变方向
            change_fleet_direction(ai_settings,aliens)
            break

def change_fleet_direction(ai_settings,aliens):
    """将整群外星人下移，并且改变它们的方向"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def ship_hit(ai_settings, stats,sb, screen, ship, aliens, bullets):
    """响应被外星人撞到的飞船"""
    # 将ships_left减1
    if stats.ships_left > 0:
        stats.ships_left -= 1

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人，并且将飞船放到屏幕底端中央
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # 暂停
        sleep(0.5)

    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

def update_aliens(ai_settings,stats, sb, screen, ship, aliens, bullets):
    """更新外星人群中所有外星人,这是外星人的总函数"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # 检查外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship,aliens):
        ship_hit(ai_settings, screen, stats ,sb, screen, ship, aliens, bullets)

    # 检查是否有外星人到达屏幕底部
    check_aliens_bottom(ai_settings, stats,sb,  screen, ship, aliens, bullets)

def check_aliens_bottom(ai_settings, stats,sb,  screen, ship, aliens, bullets):
    """检查是否有外星人达到了屏幕底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >=screen_rect.bottom:
            # 外星人到达底部
            ship_hit(ai_settings,stats,sb,screen,ship,aliens, bullets)
            break

def check_high_score(stats,sb):
    """检查是否诞生了新的最高分"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()

