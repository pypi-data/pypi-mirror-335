import time
import spidev


class TMC5240:
  """
  ステッピングモータードライバーTMC5240制御クラス

  Attributes:
    signed_position: Trueなら位置情報を符号付きで返す. Falseなら符号なしで返す. 
  """

  RAMPMODE_POSITIONING = 0
  RAMPMODE_VELOCITY_POSITIVE = 1
  RAMPMODE_VELOCITY_NEGATIVE = 2
  RAMPMODE_HOLD = 3

  BOARD_SELECT_GPIO = 25  # ボード選択GPIO番号
  board_select_output = None  # ボード選択用DigitalOutputDevice. 切り替え高速化のためクラス変数を利用

  def __init__(self, bus=0, device=0, board_id=None, spi_speed_hz=1000000, steps_per_rev=200):
    """
    Args:
      bus: SPIバス. Raspberry Piでは0. 
      device: CS信号. Raspberry Piでは0か1. 
      board_id: RPZ-Stepper基板用ボード選択信号(GPIO25). 0か1. Noneで使用しない. 
      spi_speed_hz: SPI通信速度[Hz]
      steps_per_rev: モーター1回転のフルステップ数. 速度計算に使用. 
    """
    self.spi = spidev.SpiDev()
    self.spi.open(bus, device)
    self.spi.max_speed_hz = spi_speed_hz
    self.spi.mode = 3
    self.signed_position = True
    self.board_id = board_id
    self.steps_per_rev = steps_per_rev
    self.fclk = 12500000

    if board_id is not None:
      if board_id != 0 and board_id != 1:
        raise ValueError('Invalid board_id')

  ##############################################
  # Direct Register Access

  def select_board(self):
    """
    ボード選択信号を出力する
    board_idがNoneなら何もしない
    board_idが0ならboard_select_gpioをLow
    board_idが1ならboard_select_gpioをHigh
    最初の呼び出し時, board_select_outputにインスタンス作成
    """
    if self.board_id is None:
      return

    from gpiozero import DigitalOutputDevice

    if TMC5240.board_select_output is None:
      TMC5240.board_select_output = DigitalOutputDevice(self.BOARD_SELECT_GPIO)
    TMC5240.board_select_output.value = self.board_id

  def read_register(self, addr, return_status=False):
    """
    SPIで指定アドレスからデータを読み出す

    Args:
      addr: 読み出しアドレス 8bit. 
      return_status: Trueならステータスも返す
    
    Returns:
      int: 読み出したデータ 32bit. 
      int: 読み出したステータス 8bit. return_status=Trueの場合のみ
    """
    self.select_board()

    # 結果を受け取るため2回通信する
    for _ in range(2):
      spi_write_data = [addr, 0, 0, 0, 0]  # xfer, xfer2はデータが変わる場合があるので毎回設定
      spi_read_data = self.spi.xfer3(spi_write_data)

    read_data = 0
    for i in range(4):
      read_data += (spi_read_data[i + 1] << ((3 - i) * 8))

    if return_status:
      return read_data, spi_read_data[0]
    else:
      return read_data

  def write_register(self, addr, data):
    """
    SPIで指定アドレスにデータを書き込む

    Args:
      addr: 書き込みアドレス 8bit. 
      data: 書き込みデータ 32bit.
    """
    self.select_board()
    spi_write_data = [addr | 0x80]
    for i in range(4):
      spi_write_data.append((data >> ((3 - i) * 8)) & 0xFF)
    self.spi.xfer3(spi_write_data)

  def get_bits(self, data, msb, lsb):
    """
    32bit幅のdataの指定ビットの値を返す
    """
    if msb < lsb:
      raise ValueError('lsb is larger than msb')
    length = msb - lsb + 1
    data = data >> lsb
    data &= (2**length - 1)
    return data

  def set_bits(self, data, msb, lsb, value):
    """
    32bit幅のdataの指定ビットにvalueをセットした値を返す
    """
    if msb < lsb:
      raise ValueError('lsb is larger than msb')

    length = msb - lsb + 1
    if value >= 2**length:
      raise ValueError('value exceeds length')

    # 指定ビットを0にする
    for i in range(lsb, msb + 1):
      data &= (0xFFFFFFFF - (1 << i))

    data ^= (value << lsb)
    return data

  def get_register_bits(self, addr, msb, lsb):
    """
    指定レジスターの指定ビットを返す
    """
    return self.get_bits(self.read_register(addr), msb, lsb)

  def set_register_bits(self, addr, msb, lsb, value):
    """
    指定レジスターの指定ビットにvalueをセットして書き込む
    一度読み出して, レジスターの未指定ビットは変更前と同じ値を書き込む
    """
    data = self.read_register(addr)
    data = self.set_bits(data, msb, lsb, value)
    self.write_register(addr, data)

  ##############################################
  # Global Configuration Registers

  ###################
  # GCONF 0x0
  @property
  def fast_standstill(self):
    return self.get_register_bits(0x0, 1, 1)

  @fast_standstill.setter
  def fast_standstill(self, value):
    self.set_register_bits(0x0, 1, 1, value)

  @property
  def en_pwm_mode(self):
    return self.get_register_bits(0x0, 2, 2)

  @en_pwm_mode.setter
  def en_pwm_mode(self, value):
    self.set_register_bits(0x0, 2, 2, value)

  @property
  def shaft(self):
    return self.get_register_bits(0x0, 4, 4)

  @shaft.setter
  def shaft(self, value):
    self.set_register_bits(0x0, 4, 4, value)

  @property
  def stop_enable(self):
    return self.get_register_bits(0x0, 15, 15)

  @stop_enable.setter
  def stop_enable(self, value):
    self.set_register_bits(0x0, 15, 15, value)

  @property
  def direct_mode(self):
    return self.get_register_bits(0x0, 16, 16)

  @direct_mode.setter
  def direct_mode(self, value):
    self.set_register_bits(0x0, 16, 16, value)

  ###################
  # GSTAT 0x1
  @property
  def reset(self):
    return self.get_register_bits(0x1, 0, 0)

  @reset.setter
  def reset(self, value):
    """
    リセット時に立つフラグ
    1を書き込むとフラグクリア
    """
    self.set_register_bits(0x1, 0, 0, value, pre_read=False)

  @property
  def drv_err(self):
    return self.get_register_bits(0x1, 1, 1)

  @drv_err.setter
  def drv_err(self, value):
    """
    温度異常か短絡検出でドライバー動作停止時に立つフラグ
    1を書き込むとフラグクリア
    """
    self.set_register_bits(0x1, 1, 1, value, pre_read=False)

  @property
  def register_reset(self):
    return self.get_register_bits(0x1, 3, 3)

  @register_reset.setter
  def register_reset(self, value):
    """
    レジスター値がリセットされた際に立つフラグ
    1を書き込むとフラグクリア
    """
    self.set_register_bits(0x1, 3, 3, value, pre_read=False)

  @property
  def vm_uvlo(self):
    return self.get_register_bits(0x1, 4, 4)

  @vm_uvlo.setter
  def vm_uvlo(self, value):
    """
    電源電圧低下際に立つフラグ. 電源投入時にも立つ
    1を書き込むとフラグクリア
    """
    self.set_register_bits(0x1, 4, 4, value, pre_read=False)

  ###################
  # IOIN 0x4
  @property
  def ext_clk(self):
    return self.get_register_bits(0x4, 14, 14)

  @property
  def adc_err(self):
    return self.get_register_bits(0x4, 15, 15)

  @property
  def silicon_rv(self):
    return self.get_register_bits(0x4, 18, 16)

  @property
  def version(self):
    return self.get_register_bits(0x4, 31, 24)

  ###################
  # DRV_CONF 0xA
  @property
  def current_range(self):
    return self.get_register_bits(0xA, 1, 0)

  @current_range.setter
  def current_range(self, value):
    self.set_register_bits(0xA, 1, 0, value)

  @property
  def slope_control(self):
    return self.get_register_bits(0xA, 5, 4)

  @slope_control.setter
  def slope_control(self, value):
    self.set_register_bits(0xA, 5, 4, value)

  ###################
  # GLOBAL_SCALER 0xB
  @property
  def global_scaler(self):
    return self.get_register_bits(0xB, 7, 0)

  @global_scaler.setter
  def global_scaler(self, value):
    if value > 256 or (value < 32 and value != 0):
      raise ValueError('value out of range')
    if value == 256:
      value = 0
    self.set_register_bits(0xB, 7, 0, value)

  ##############################################
  # Velocity Dependent Configuration Registers

  ###################
  # IHOLD_IRUN 0x10
  @property
  def ihold(self):
    return self.get_register_bits(0x10, 4, 0)

  @ihold.setter
  def ihold(self, value):
    self.set_register_bits(0x10, 4, 0, value)

  @property
  def irun(self):
    return self.get_register_bits(0x10, 12, 8)

  @irun.setter
  def irun(self, value):
    self.set_register_bits(0x10, 12, 8, value)

  @property
  def iholddelay(self):
    return self.get_register_bits(0x10, 19, 16)

  @iholddelay.setter
  def iholddelay(self, value):
    self.set_register_bits(0x10, 19, 16, value)

  @property
  def irundelay(self):
    return self.get_register_bits(0x10, 27, 24)

  @irundelay.setter
  def irundelay(self, value):
    self.set_register_bits(0x10, 27, 24, value)

  ###################
  # TPOWERDOWN 0x11
  @property
  def tpowerdown(self):
    return self.get_register_bits(0x11, 7, 0)

  @tpowerdown.setter
  def tpowerdown(self, value):
    self.set_register_bits(0x11, 7, 0, value)

  ###################
  # TSTEP 0x12
  @property
  def tstep(self):
    return self.read_register(0x12)

  ###################
  # TPWMTHRS 0x13
  @property
  def tpwmthrs(self):
    return self.read_register(0x13)

  @tpwmthrs.setter
  def tpwmthrs(self, value):
    self.write_register(0x13, value)

  ###################
  # TCOOLTHRS 0x14
  @property
  def tcoolthrs(self):
    return self.read_register(0x14)

  @tcoolthrs.setter
  def tcoolthrs(self, value):
    self.write_register(0x14, value)

  ###################
  # THIGH 0x15
  @property
  def thigh(self):
    return self.read_register(0x15)

  @thigh.setter
  def thigh(self, value):
    self.write_register(0x15, value)

  ##############################################
  # Ramp Generator Registers

  ###################
  # RAMPMODE 0x20
  @property
  def rampmode(self):
    return self.get_register_bits(0x20, 1, 0)

  @rampmode.setter
  def rampmode(self, value):
    self.set_register_bits(0x20, 1, 0, value)

  ###################
  # XACTUAL 0x21
  @property
  def xactual(self):
    xactual = self.read_register(0x21)
    if self.signed_position:
      if xactual >= 2147483648:
        xactual -= 4294967296
    return xactual

  @xactual.setter
  def xactual(self, value):
    self.write_register(0x21, value)

  ###################
  # VACTUAL 0x22
  @property
  def vactual(self):
    vactual = self.read_register(0x22)
    if vactual >= 8388608:
      vactual -= 16777216
    return vactual

  ###################
  # VSTART 0x23
  @property
  def vstart(self):
    return self.read_register(0x23)

  @vstart.setter
  def vstart(self, value):
    self.write_register(0x23, value)

  ###################
  # A1 0x24
  @property
  def a1(self):
    return self.read_register(0x24)

  @a1.setter
  def a1(self, value):
    self.write_register(0x24, value)

  ###################
  # V1 0x25
  @property
  def v1(self):
    return self.read_register(0x25)

  @v1.setter
  def v1(self, value):
    self.write_register(0x25, value)

  ###################
  # AMAX 0x26
  @property
  def amax(self):
    return self.read_register(0x26)

  @amax.setter
  def amax(self, value):
    self.write_register(0x26, value)

  ###################
  # VMAX 0x27
  @property
  def vmax(self):
    return self.read_register(0x27)

  @vmax.setter
  def vmax(self, value):
    self.write_register(0x27, value)

  ###################
  # DMAX 0x28
  @property
  def dmax(self):
    return self.read_register(0x28)

  @dmax.setter
  def dmax(self, value):
    self.write_register(0x28, value)

  ###################
  # TVMAX 0x29
  @property
  def tvmax(self):
    return self.read_register(0x29)

  @tvmax.setter
  def tvmax(self, value):
    self.write_register(0x29, value)

  ###################
  # D1 0x2A
  @property
  def d1(self):
    return self.read_register(0x2A)

  @d1.setter
  def d1(self, value):
    self.write_register(0x2A, value)

  ###################
  # VSTOP 0x2B
  @property
  def vstop(self):
    return self.read_register(0x2B)

  @vstop.setter
  def vstop(self, value):
    self.write_register(0x2B, value)

  ###################
  # TZEROWAIT 0x2C
  @property
  def tzerowait(self):
    return self.read_register(0x2C)

  @tzerowait.setter
  def tzerowait(self, value):
    self.write_register(0x2C, value)

  ###################
  # XTARGET 0x2D
  @property
  def xtarget(self):
    xtarget = self.read_register(0x2D)
    if self.signed_position:
      if xtarget >= 2147483648:
        xtarget -= 4294967296
    return xtarget

  @xtarget.setter
  def xtarget(self, value):
    self.write_register(0x2D, value)

  @property
  def direct_a(self):
    return self.get_register_bits(0x2D, 8, 0)

  @direct_a.setter
  def direct_a(self, value):
    """
    direct mode用
    A相の出力を-256~256の範囲で指定
    XTARGETレジスターを使用するので, positioning modeに戻す際は
    XTARGETを再設定する
    """
    if value > 255 or value < -256:
      raise ValueError('value out of range')
    if value < 0:
      value += 512
    self.set_register_bits(0x2D, 8, 0, value)

  @property
  def direct_b(self):
    return self.get_register_bits(0x2D, 24, 16)

  @direct_b.setter
  def direct_b(self, value):
    """
    direct mode用
    B相の出力を-256~256の範囲で指定
    XTARGETレジスターを使用するので, positioning modeに戻す際は
    XTARGETを再設定する
    """
    if value > 255 or value < -256:
      raise ValueError('value out of range')
    if value < 0:
      value += 512
    self.set_register_bits(0x2D, 24, 16, value)

  ###################
  # V2 0x2E
  @property
  def v2(self):
    return self.read_register(0x2E)

  @v2.setter
  def v2(self, value):
    self.write_register(0x2E, value)

  ###################
  # A2 0x2F
  @property
  def a2(self):
    return self.read_register(0x2F)

  @a2.setter
  def a2(self, value):
    self.write_register(0x2F, value)

  ###################
  # D2 0x30
  @property
  def d2(self):
    return self.read_register(0x30)

  @d2.setter
  def d2(self, value):
    self.write_register(0x30, value)

  ##############################################
  # Ramp Generator Driver Feature Control Registers

  ###################
  # VDCMIN 0x33
  @property
  def vdcmin(self):
    return self.get_register_bits(0x33, 22, 8)

  @vdcmin.setter
  def vdcmin(self, value):
    self.set_register_bits(0x33, 22, 8, value)

  ###################
  # SW_MODE 0x34
  @property
  def sg_stop(self):
    return self.get_register_bits(0x34, 10, 10)

  @sg_stop.setter
  def sg_stop(self, value):
    self.set_register_bits(0x34, 10, 10, value)

  @property
  def en_softstop(self):
    return self.get_register_bits(0x34, 11, 11)

  @en_softstop.setter
  def en_softstop(self, value):
    self.set_register_bits(0x34, 11, 11, value)

  @property
  def en_virtual_stop_l(self):
    return self.get_register_bits(0x34, 12, 12)

  @en_virtual_stop_l.setter
  def en_virtual_stop_l(self, value):
    self.set_register_bits(0x34, 12, 12, value)

  @property
  def en_virtual_stop_r(self):
    return self.get_register_bits(0x34, 13, 13)

  @en_virtual_stop_r.setter
  def en_virtual_stop_r(self, value):
    self.set_register_bits(0x34, 13, 13, value)

  ###################
  # RAMP_STAT 0x35
  @property
  def velocity_reached(self):
    return self.get_register_bits(0x35, 8, 8)

  @property
  def position_reached(self):
    return self.get_register_bits(0x35, 9, 9)

  @property
  def vzero(self):
    return self.get_register_bits(0x35, 10, 10)

  ###################
  # VIRTUAL_STOP_L 0x3E
  @property
  def virtual_stop_l(self):
    virtual_stop_l = self.read_register(0x3E)
    if self.signed_position:
      if virtual_stop_l >= 2147483648:
        virtual_stop_l -= 4294967296
    return virtual_stop_l

  @virtual_stop_l.setter
  def virtual_stop_l(self, value):
    self.write_register(0x3E, value)

  ###################
  # VIRTUAL_STOP_R 0x3F
  @property
  def virtual_stop_r(self):
    return self.read_register(0x3F)

  @virtual_stop_r.setter
  def virtual_stop_r(self, value):
    self.write_register(0x3F, value)

  ##############################################
  # ADC Registers

  ###################
  # ADC_VSUPPLY_AIN 0x50
  @property
  def adc_ain(self):
    """
    AINの電圧[mV]を返す
    """
    data = self.get_register_bits(0x50, 28, 16)
    if data >= 4096:
      data -= 8192
    return round(data * 0.3052, 2)

  @property
  def adc_vsupply(self):
    """
    電源電圧[V]を返す
    """
    data = self.get_register_bits(0x50, 12, 0)
    return round(data * 9.732 / 1000, 2)

  ###################
  # ADC_TEMP 0x51
  @property
  def adc_temp(self):
    """
    温度[℃]を返す
    """
    data = self.get_register_bits(0x51, 12, 0)
    return round((data - 2038) / 7.7, 2)

  ##############################################
  # Motor Driver Registers

  ###################
  # CHOPCONF 0x6C
  @property
  def toff(self):
    return self.get_register_bits(0x6C, 3, 0)

  @toff.setter
  def toff(self, value):
    self.set_register_bits(0x6C, 3, 0, value)

  @property
  def disfdcc(self):
    return self.get_register_bits(0x6C, 12, 12)

  @disfdcc.setter
  def disfdcc(self, value):
    self.set_register_bits(0x6C, 12, 12, value)

  @property
  def chm(self):
    return self.get_register_bits(0x6C, 14, 14)

  @chm.setter
  def chm(self, value):
    self.set_register_bits(0x6C, 14, 14, value)

  @property
  def vhighfs(self):
    return self.get_register_bits(0x6C, 18, 18)

  @vhighfs.setter
  def vhighfs(self, value):
    self.set_register_bits(0x6C, 18, 18, value)

  @property
  def vhighchm(self):
    return self.get_register_bits(0x6C, 19, 19)

  @vhighchm.setter
  def vhighchm(self, value):
    self.set_register_bits(0x6C, 19, 19, value)

  @property
  def mres(self):
    return self.get_register_bits(0x6C, 27, 24)

  @mres.setter
  def mres(self, value):
    self.set_register_bits(0x6C, 27, 24, value)

  @property
  def intpol(self):
    return self.get_register_bits(0x6C, 28, 28)

  @intpol.setter
  def intpol(self, value):
    self.set_register_bits(0x6C, 28, 28, value)

  @property
  def diss2g(self):
    return self.get_register_bits(0x6C, 30, 30)

  @diss2g.setter
  def diss2g(self, value):
    self.set_register_bits(0x6C, 30, 30, value)

  @property
  def diss2vs(self):
    return self.get_register_bits(0x6C, 31, 31)

  @diss2vs.setter
  def diss2vs(self, value):
    self.set_register_bits(0x6C, 31, 31, value)

  ###################
  # COOLCONF 0x6D
  @property
  def semin(self):
    return self.get_register_bits(0x6D, 3, 0)

  @semin.setter
  def semin(self, value):
    self.set_register_bits(0x6D, 3, 0, value)

  @property
  def seup(self):
    return self.get_register_bits(0x6D, 6, 5)

  @seup.setter
  def seup(self, value):
    self.set_register_bits(0x6D, 6, 5, value)

  @property
  def semax(self):
    return self.get_register_bits(0x6D, 11, 8)

  @semax.setter
  def semax(self, value):
    self.set_register_bits(0x6D, 11, 8, value)

  @property
  def sedn(self):
    return self.get_register_bits(0x6D, 14, 13)

  @sedn.setter
  def sedn(self, value):
    self.set_register_bits(0x6D, 14, 13, value)

  @property
  def seimin(self):
    return self.get_register_bits(0x6D, 15, 15)

  @seimin.setter
  def seimin(self, value):
    self.set_register_bits(0x6D, 15, 15, value)

  @property
  def sgt(self):
    return self.get_register_bits(0x6D, 22, 16)

  @sgt.setter
  def sgt(self, value):
    self.set_register_bits(0x6D, 22, 16, value)

  @property
  def sfilt(self):
    return self.get_register_bits(0x6D, 24, 24)

  @sfilt.setter
  def sfilt(self, value):
    self.set_register_bits(0x6D, 24, 24, value)

  ###################
  # DCCTRL 0x6E
  @property
  def dc_time(self):
    return self.get_register_bits(0x6E, 9, 0)

  @dc_time.setter
  def dc_time(self, value):
    self.set_register_bits(0x6E, 9, 0, value)

  @property
  def dc_sg(self):
    return self.get_register_bits(0x6E, 23, 16)

  @dc_sg.setter
  def dc_sg(self, value):
    self.set_register_bits(0x6E, 23, 16, value)

  ###################
  # DRV_STATUS 0x6F
  @property
  def sg_result(self):
    return self.get_register_bits(0x6F, 9, 0)

  @property
  def s2vsa(self):
    return self.get_register_bits(0x6F, 12, 12)

  @property
  def s2vsb(self):
    return self.get_register_bits(0x6F, 13, 13)

  @property
  def stealth(self):
    return self.get_register_bits(0x6F, 14, 14)

  @property
  def fsactive(self):
    return self.get_register_bits(0x6F, 15, 15)

  @property
  def cs_actual(self):
    return self.get_register_bits(0x6F, 20, 16)

  @property
  def stallguard(self):
    return self.get_register_bits(0x6F, 24, 24)

  @property
  def ot(self):
    return self.get_register_bits(0x6F, 25, 25)

  @property
  def otpw(self):
    return self.get_register_bits(0x6F, 26, 26)

  @property
  def s2ga(self):
    return self.get_register_bits(0x6F, 27, 27)

  @property
  def s2gb(self):
    return self.get_register_bits(0x6F, 28, 28)

  @property
  def ola(self):
    return self.get_register_bits(0x6F, 29, 29)

  @property
  def olb(self):
    return self.get_register_bits(0x6F, 30, 30)

  @property
  def stst(self):
    return self.get_register_bits(0x6F, 31, 31)

  ###################
  # PWMCONF 0x70
  @property
  def pwm_grad(self):
    return self.get_register_bits(0x70, 7, 0)

  @pwm_grad.setter
  def pwm_grad(self, value):
    self.set_register_bits(0x70, 7, 0, value)

  @property
  def pwm_freq(self):
    return self.get_register_bits(0x70, 17, 16)

  @pwm_freq.setter
  def pwm_freq(self, value):
    self.set_register_bits(0x70, 17, 16, value)

  @property
  def pwm_autoscale(self):
    return self.get_register_bits(0x70, 18, 18)

  @pwm_autoscale.setter
  def pwm_autoscale(self, value):
    self.set_register_bits(0x70, 18, 18, value)

  @property
  def pwm_autograd(self):
    return self.get_register_bits(0x70, 19, 19)

  @pwm_autograd.setter
  def pwm_autograd(self, value):
    self.set_register_bits(0x70, 19, 19, value)

  @property
  def freewheel(self):
    return self.get_register_bits(0x70, 21, 20)

  @freewheel.setter
  def freewheel(self, value):
    self.set_register_bits(0x70, 21, 20, value)

  @property
  def pwm_meas_sd_enable(self):
    return self.get_register_bits(0x70, 22, 22)

  @pwm_meas_sd_enable.setter
  def pwm_meas_sd_enable(self, value):
    self.set_register_bits(0x70, 22, 22, value)

  @property
  def pwm_dis_reg_stst(self):
    return self.get_register_bits(0x70, 23, 23)

  @pwm_dis_reg_stst.setter
  def pwm_dis_reg_stst(self, value):
    self.set_register_bits(0x70, 23, 23, value)

  @property
  def pwm_reg(self):
    return self.get_register_bits(0x70, 27, 24)

  @pwm_reg.setter
  def pwm_reg(self, value):
    self.set_register_bits(0x70, 27, 24, value)

  @property
  def pwm_lim(self):
    return self.get_register_bits(0x70, 31, 28)

  @pwm_lim.setter
  def pwm_lim(self, value):
    self.set_register_bits(0x70, 31, 28, value)

  ###################
  # PWM_SCALE 0x71
  @property
  def pwm_scale_sum(self):
    return self.get_register_bits(0x71, 9, 0)

  @property
  def pwm_scale_auto(self):
    return self.get_register_bits(0x71, 24, 16)

  ###################
  # PWM_AUTO 0x72
  @property
  def pwm_ofs_auto(self):
    return self.get_register_bits(0x72, 7, 0)

  @pwm_ofs_auto.setter
  def pwm_ofs_auto(self, value):
    self.set_register_bits(0x72, 7, 0, value)

  @property
  def pwm_grad_auto(self):
    return self.get_register_bits(0x72, 23, 16)

  @pwm_grad_auto.setter
  def pwm_grad_auto(self, value):
    self.set_register_bits(0x72, 23, 16, value)

  ###################
  # SG4_THRS 0x74
  @property
  def sg4_thrs(self):
    return self.get_register_bits(0x74, 7, 0)

  @sg4_thrs.setter
  def sg4_thrs(self, value):
    self.set_register_bits(0x74, 7, 0, value)

  @property
  def sg4_filt_en(self):
    return self.get_register_bits(0x74, 8, 8)

  @sg4_filt_en.setter
  def sg4_filt_en(self, value):
    self.set_register_bits(0x74, 8, 8, value)

  ###################
  # SG4_RESULT 0x75
  @property
  def sg4_result(self):
    return self.get_register_bits(0x75, 9, 0)

  ###################
  # SG4_IND 0x76
  @property
  def sg4_ind_0(self):
    return self.get_register_bits(0x76, 7, 0)

  @property
  def sg4_ind_1(self):
    return self.get_register_bits(0x76, 15, 8)

  @property
  def sg4_ind_2(self):
    return self.get_register_bits(0x76, 23, 16)

  @property
  def sg4_ind_3(self):
    return self.get_register_bits(0x76, 31, 24)

  ##############################################
  # Converted parameters

  @property
  def ifs(self):
    """
    current_range, global_scalerから電流の最大値[A]を計算して返す
    """
    global_scaler = self.global_scaler
    if global_scaler == 0:
      global_scaler = 256
    return round((self.current_range + 1) * global_scaler / 256, 2)

  @ifs.setter
  def ifs(self, value):
    """
    電流の最大値[A]からcurrent_range, global_scalerを計算して設定
    
    Args:
      value: 電流の最大値(IFS) 0.125 - 3.0
    """
    if value < 0.125 or value > 3.0:
      raise ValueError('value out of range')
    if value <= 1.0:
      current_range = 0
    elif value <= 2.0:
      current_range = 1
    else:
      current_range = 2
    self.current_range = current_range
    self.global_scaler = round(value * 256 / (current_range + 1))

  @property
  def vactual_rpm(self):
    return self.v2rpm(self.vactual)

  @property
  def vmax_rpm(self):
    return self.v2rpm(self.vmax)

  @vmax_rpm.setter
  def vmax_rpm(self, value):
    self.vmax = self.rpm2v(value)

  @property
  def v1_rpm(self):
    return self.v2rpm(self.v1)

  @v1_rpm.setter
  def v1_rpm(self, value):
    self.v1 = self.rpm2v(value)

  @property
  def v2_rpm(self):
    return self.v2rpm(self.v2)

  @v2_rpm.setter
  def v2_rpm(self, value):
    self.v2 = self.rpm2v(value)

  @property
  def tstep_rpm(self):
    return self.tstep2rpm(self.tstep)

  @property
  def tpwmthrs_rpm(self):
    tpwmthrs = self.tpwmthrs
    if tpwmthrs == 0:
      return 0
    return self.tstep2rpm(tpwmthrs)

  @tpwmthrs_rpm.setter
  def tpwmthrs_rpm(self, value):
    if value == 0:
      self.tpwmthrs = 0
    else:
      self.tpwmthrs = self.rpm2tstep(value)

  @property
  def thigh_rpm(self):
    thigh = self.thigh
    if thigh == 0:
      return 0
    return self.tstep2rpm(thigh)

  @thigh_rpm.setter
  def thigh_rpm(self, value):
    if value == 0:
      self.thigh = 0
    else:
      self.thigh = self.rpm2tstep(value)

  ##############################################
  # RPZ-Stepper Functions

  def enable(self):
    """
    インバーターをONしてモーターに電圧印加
    TOFFの値をデフォルトで使用する
    """
    self.toff = 3

  def disable(self):
    """
    インバーターをOFFしてモーターに電圧を印加しない
    """
    self.toff = 0

  def moveto(self, xtarget, polling_interval=0.1):
    """
    xtargetまで移動し, 目標位置に到達したら戻る

    Args:
      xtarget: 目標位置
      polling_interval: 到達したか確認する頻度[s]
    """
    if self.vmax < 10:
      raise ValueError('vmax is too low')
    if self.amax == 0:
      raise ValueError('amax is too low')
    if self.dmax == 0:
      raise ValueError('dmax is too low')

    self.rampmode = self.RAMPMODE_POSITIONING
    self.xtarget = xtarget
    while self.position_reached == 0:
      time.sleep(polling_interval)

  def rpm2v(self, rpm):
    """
    rpmからTMC5240で指定する速度vを計算して返す
    """
    return round(rpm / 60 * self.steps_per_rev * 256 / self.fclk * 2**24)

  def v2rpm(self, v):
    """
    TMC5240で指定する速度vからrpmを計算して返す
    """
    return round(v * 60 / self.steps_per_rev / 256 * self.fclk / (2**24), 2)

  def rpm2tstep(self, rpm):
    """
    rpmからTMC5240で指定するステップ時間tstepを計算して返す
    """
    return round(self.fclk / (rpm / 60 * self.steps_per_rev * 256))

  def tstep2rpm(self, tstep):
    """
    TMC5240で指定するステップ時間tstepからrpmを計算して返す
    """
    return round(self.fclk / (tstep / 60 * self.steps_per_rev * 256), 2)

  @property
  def board_current(self, meas_count=1000):
    """
    基板の消費電流[A]を返す
    モーター制御中電流は変化しているので, meas_count回測定して平均を計算
    """
    ain_sum = 0
    for _ in range(meas_count):
      ain_sum += self.adc_ain
    return round(ain_sum / 27.9 / 7.5 / meas_count, 2)

  @classmethod
  def supported_param(self):
    """
    サポートしているパラメーター名一覧を表示
    """
    params = """fast_standstill, en_pwm_mode, shaft, stop_enable, direct_mode, reset, 
drv_err, register_reset, vm_uvlo, ext_clk, adc_err, silicon_rv, 
version, current_range, slope_control, global_scaler, ihold, irun, 
iholddelay, irundelay, tpowerdown, tstep, tpwmthrs, tcoolthrs, 
thigh, rampmode, xactual, vactual, vstart, a1, 
v1, amax, vmax, dmax, tvmax, d1, 
vstop, tzerowait, xtarget, direct_a, direct_b, v2, 
a2, d2, vdcmin, sg_stop, en_softstop, en_virtual_stop_l, 
en_virtual_stop_r, velocity_reached, position_reached, vzero, virtual_stop_l, virtual_stop_r, 
adc_ain, adc_vsupply, adc_temp, toff, disfdcc, chm, 
vhighfs, vhighchm, mres, intpol, diss2g, diss2vs, 
semin, seup, semax, sedn, seimin, sgt, 
sfilt, dc_time, dc_sg, sg_result, s2vsa, s2vsb, 
stealth, fsactive, cs_actual, stallguard, ot, otpw, 
s2ga, s2gb, ola, olb, stst, pwm_grad, 
pwm_freq, pwm_autoscale, pwm_autograd, freewheel, pwm_meas_sd_enable, pwm_dis_reg_stst, 
pwm_reg, pwm_lim, pwm_scale_sum, pwm_scale_auto, pwm_ofs_auto, pwm_grad_auto, 
sg4_thrs, sg4_filt_en, sg4_result, sg4_ind_0, sg4_ind_1, sg4_ind_2, 
sg4_ind_3, ifs, vactual_rpm, vmax_rpm, v1_rpm, v2_rpm, 
tstep_rpm, tpwmthrs_rpm, thigh_rpm"""

    print(params)

  ##############################################
  # Print Functions

  def print_register(self, addr):
    reg_data = self.read_register(addr)
    print('{:#04x}, {:#010x}'.format(addr, reg_data))

  def print_all_registers(self):
    for addr in range(0x0, 0xC):
      self.print_register(addr)
    for addr in range(0x10, 0x16):
      self.print_register(addr)
    for addr in range(0x20, 0x31):
      self.print_register(addr)
    for addr in range(0x33, 0x40):
      self.print_register(addr)
    for addr in range(0x50, 0x53):
      self.print_register(addr)
    for addr in range(0x60, 0x73):
      self.print_register(addr)
    for addr in range(0x74, 0x77):
      self.print_register(addr)

  def print_ramp_settings(self):
    rampmodes = ['POSITIONING', 'VELOCITY POSITIVE', 'VELOCITY NEGATIVE', 'HOLD']
    print('RAMPMODE: {}'.format(rampmodes[self.rampmode]))
    print('V1: {}'.format(self.v1))
    print('V2: {}'.format(self.v2))
    print('VMAX: {}'.format(self.vmax))
    print('VSTART: {}'.format(self.vstart))
    print('VSTOP: {}'.format(self.vstop))
    print('A1: {}'.format(self.a1))
    print('A2: {}'.format(self.a2))
    print('AMAX: {}'.format(self.amax))
    print('D1: {}'.format(self.d1))
    print('D2: {}'.format(self.d2))
    print('DMAX: {}'.format(self.dmax))
