# SPDX-License-Identifier: GPL-2.0 Only
# (c) 2021 , Michael John Sakellaropoulos

# Prerequisites : smbus2, pysdl2, sdl2(system library)
# Read touch coords from KC1 ilitek ili210x touch controller and draw as SDL2 Rect

import sys
import sdl2
import sdl2.ext
from smbus2 import SMBus, i2c_msg
# import gpio


class IlitekPanelInfo:
    def __init__(self, max_touch, max_btn, max_x, max_y, ch_x, ch_y, fwver, protover):
        self.max_touch = max_touch
        self.max_btn = max_btn
        self.max_x = max_x
        self.max_y = max_y
        self.ch_x = ch_x
        self.ch_y = ch_y
        self.fwver = fwver
        self.protover = protover


X_RES = 1024
Y_RES = 600

I2C_BUS_NUMBER = 1
I2C_CHIP_ADDR = 0x41

ILI210X_DATA_SIZE = 64
ILI210X_CMD_READ_TOUCHDATA = 0x10
ILI210X_CMD_PANEL_INFO = 0x20
ILI210X_CMD_CALIBRATE = 0xcc
ILI210X_CMD_GET_FIRMWARE_VERSION = 0x40
ILI210X_CMD_GET_PROTOCOL_VERSION = 0x42


def reset_ili210x():
    print("Not implemented")


def init_i2c():
    return SMBus(I2C_BUS_NUMBER)


def ili210x_read_reg(bus, cmd, size):
    write = i2c_msg.write(I2C_CHIP_ADDR, [cmd])
    read = i2c_msg.read(I2C_CHIP_ADDR, size)
    bus.i2c_rdwr(write, read)
    return list(read)


def ili210x_read_panel_info(bus):
    return ili210x_read_reg(bus, ILI210X_CMD_PANEL_INFO, ILI210X_DATA_SIZE)


def ili210x_read_firmware_ver(bus):
    return ili210x_read_reg(bus, ILI210X_CMD_GET_FIRMWARE_VERSION, 4*8)


def ili210x_read_protocol_ver(bus):
    return ili210x_read_reg(bus, ILI210X_CMD_GET_PROTOCOL_VERSION, 2*8)


def ili210x_get_info(bus):
    panelinfo_data = ili210x_read_panel_info(bus)
    fwver_data = ili210x_read_firmware_ver(bus)
    protover_data = ili210x_read_protocol_ver(bus)
    max_touch = panelinfo_data[6]
    max_btn = panelinfo_data[7]
    max_x = int.from_bytes([panelinfo_data[0], panelinfo_data[1]], byteorder="little", signed=False)
    max_y = int.from_bytes([panelinfo_data[2], panelinfo_data[3]], byteorder="little", signed=False)
    ch_x = panelinfo_data[5]
    ch_y = panelinfo_data[4]
    fwver = f'{fwver_data[0]}.{fwver_data[1]}.{fwver_data[2]}.{fwver_data[3]}'
    protover = f'{protover_data[0]}.{protover_data[1]}'
    return IlitekPanelInfo(max_touch, max_btn, max_x, max_y, ch_x, ch_y, fwver, protover)


def ili210x_read_touch_data(bus):
    return ili210x_read_reg(bus, ILI210X_CMD_READ_TOUCHDATA, ILI210X_DATA_SIZE)


def ili210x_touchdata_to_coords(touchdata, finger):
    # coords are uint16 , little endian
    x = int.from_bytes([touchdata[1 + (finger * 4) + 0],touchdata[1 + (finger * 4) + 1]], byteorder="little", signed=False)
    y = int.from_bytes([touchdata[1 + (finger * 4) + 2],touchdata[1 + (finger * 4) + 3]], byteorder="little", signed=False)
    return (x, y)


def draw_rect(renderer, x, y, color):
    width = 5
    height = 5
    x1 = int(x-width/2)
    y1 = int(y-height/2)
    renderer.fill(rects=[[x1, y1, width, height]], color=color)
    # print(f'draw_rect {x1} {y1} {width} {height}')


def draw_touch(touchdata, finger, renderer, max_x, max_y, x_res, y_res):
    (x, y) = ili210x_touchdata_to_coords(touchdata, finger)
    x = x*x_res/max_x
    y = y*y_res/max_y
    color = sdl2.ext.Color(0, 0, 255, 0) if finger == 0 else sdl2.ext.Color(0, 255, 0, 0)
    draw_rect(renderer, x, y, color)
    # print(f'draw_touch: X: {x} , Y: {y}')


def main():
    sdl2.ext.init()

    i2c = init_i2c()
    panel = ili210x_get_info(i2c)

    window = sdl2.ext.Window(
        title="Hello World!", size=(X_RES, Y_RES),
        flags=sdl2.SDL_WINDOW_SHOWN,
        position=(sdl2.SDL_WINDOWPOS_CENTERED,
                  sdl2.SDL_WINDOWPOS_CENTERED)
    )

    window.show()

    renderer = sdl2.ext.Renderer(window)

    running = True
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            # elif event.type == sdl2.SDL_MOUSEMOTION:
                # motion = event.motion
        touchdata = ili210x_read_touch_data(i2c)
        draw_touch(touchdata, 0, renderer, panel.max_x, panel.max_y, X_RES, Y_RES)
        draw_touch(touchdata, 1, renderer, panel.max_x, panel.max_y, X_RES, Y_RES)
        renderer.present()

    print("Closing!")
    i2c.close()
    sdl2.ext.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())

