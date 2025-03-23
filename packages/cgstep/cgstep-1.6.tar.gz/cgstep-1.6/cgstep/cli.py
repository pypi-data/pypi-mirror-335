description = """
Raspberry Pi用 高機能ステッピングモータードライバーRPZ-Stepper コマンドラインツール
Indoor Corgi, https://www.indoorcorgielec.com
GitHub: https://github.com/IndoorCorgi/cgstep
使い方: https://www.indoorcorgielec.com/products/rpz-stepper#usage
"""

from argparse import ArgumentParser, RawTextHelpFormatter, RawDescriptionHelpFormatter
from .tmc5240 import TMC5240


def cli():
  """
  コマンドラインツールを実行
  """

  class CustomFormatter(RawTextHelpFormatter, RawDescriptionHelpFormatter):

    def __init__(self, prog, indent_increment=2, max_help_position=30, width=None):
      super().__init__(prog, indent_increment, max_help_position, width)

  parser = ArgumentParser(description=description, formatter_class=CustomFormatter)
  parser.add_argument('command', help='パラメーター名 / レジスターアドレス / オペレーション名')
  parser.add_argument('--write', '-w', help='パラメーター, レジスターに書き込む値')
  parser.add_argument('--board', '-b', type=int, choices=range(0, 2), help='指定した値のBD_IDの基板を選択')
  parser.add_argument('--device', '-d', type=int, choices=range(0, 2), help='指定した値のSPIデバイスを選択')
  parser.add_argument('--hex', '-x', action='store_true', help='結果を16進数で表示')
  parser.add_argument('--steps-per-rev', '-s', type=int, default=200, help='モーター1回転あたりのフルステップ数')
  args = parser.parse_args()

  board_id = None
  device = 0
  if args.device is not None:
    device = args.device
  if args.board is not None:
    board_id = args.board
  motor = TMC5240(board_id=board_id, device=device)

  if operation(motor, args):
    return
  if param(motor, args):
    return
  if register(motor, args):
    return

  print('Not supported command: ' + args.command)


def val2str(value, args):
  """
  値を文字列に変換して返す
  --hexオプションが指定されていれば16進数表記にする

  Args:
    value: 数値
    args: オプション
  """
  if args.hex:
    return hex(value)
  else:
    return int(value)


def print_val(value, args):
  """
  値を出力
  --hexオプションが指定されていれば16進数表記にする

  Args:
    value: 数値
    args: オプション
  """
  print(val2str(value, args))


def register(motor, args):
  """
  レジスター読み書きを行うコマンドなら処理
  Args:
    motor: TMC5240クラス
    args: argparseでパースされた引数
  
  Returns: 処理したらTrue, 無関係なコマンドならFalse
  """
  try:
    addr = int(args.command, 0)
  except:
    return False

  if args.write is None:
    print_val(motor.read_register(addr), args)
  else:
    motor.write_register(addr, int(args.write, 0))

  return True


def operation(motor, args):
  """
  パラメーター/レジスター読み書き以外のコマンドなら処理
  Args:
    motor: TMC5240クラス
    args: argparseでパースされた引数
  
  Returns: 処理したらTrue, 無関係なコマンドならFalse
  """
  if args.command == 'enable':
    motor.enable()
  elif args.command == 'disable':
    motor.disable()
  elif args.command == 'moveto':
    motor.moveto(int(args.write))
  elif args.command == 'board_current':
    print(motor.board_current, '[A]')
  elif args.command == 'supported_param':
    motor.supported_param()
  else:
    return False
  return True


def param(motor, args):
  """
  パラメーター設定を行うコマンドなら処理
  Args:
    motor: TMC5240クラス
    args: argparseでパースされた引数
  
  Returns: 処理したらTrue, 無関係なコマンドならFalse
  """
  ##############################################
  # Global Configuration Registers
  if args.command == 'fast_standstill':
    if args.write is None:
      print_val(motor.fast_standstill, args)
    else:
      motor.fast_standstill = int(args.write, 0)

  elif args.command == 'en_pwm_mode':
    if args.write is None:
      print_val(motor.en_pwm_mode, args)
    else:
      motor.en_pwm_mode = int(args.write, 0)

  elif args.command == 'shaft':
    if args.write is None:
      print_val(motor.shaft, args)
    else:
      motor.shaft = int(args.write, 0)

  elif args.command == 'stop_enable':
    if args.write is None:
      print_val(motor.stop_enable, args)
    else:
      motor.stop_enable = int(args.write, 0)

  elif args.command == 'direct_mode':
    if args.write is None:
      print_val(motor.direct_mode, args)
    else:
      motor.direct_mode = int(args.write, 0)

  ###################
  # GSTAT 0x1
  elif args.command == 'reset':
    if args.write is None:
      print_val(motor.reset, args)
    else:
      motor.reset = int(args.write, 0)

  elif args.command == 'drv_err':
    if args.write is None:
      print_val(motor.drv_err, args)
    else:
      motor.drv_err = int(args.write, 0)

  elif args.command == 'register_reset':
    if args.write is None:
      print_val(motor.register_reset, args)
    else:
      motor.register_reset = int(args.write, 0)

  elif args.command == 'vm_uvlo':
    if args.write is None:
      print_val(motor.vm_uvlo, args)
    else:
      motor.vm_uvlo = int(args.write, 0)

  ###################
  # IOIN 0x4
  elif args.command == 'ext_clk':
    if args.write is None:
      print_val(motor.ext_clk, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'adc_err':
    if args.write is None:
      print_val(motor.adc_err, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'silicon_rv':
    if args.write is None:
      print_val(motor.silicon_rv, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'version':
    if args.write is None:
      print_val(motor.version, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  ###################
  # DRV_CONF 0xA
  elif args.command == 'current_range':
    if args.write is None:
      print_val(motor.current_range, args)
    else:
      motor.current_range = int(args.write, 0)

  elif args.command == 'slope_control':
    if args.write is None:
      print_val(motor.slope_control, args)
    else:
      motor.slope_control = int(args.write, 0)

  ###################
  # GLOBAL_SCALER 0xB
  elif args.command == 'global_scaler':
    if args.write is None:
      print_val(motor.global_scaler, args)
    else:
      motor.global_scaler = int(args.write, 0)

  ##############################################
  # Velocity Dependent Configuration Registers
  ###################
  # IHOLD_IRUN 0x10
  elif args.command == 'ihold':
    if args.write is None:
      print_val(motor.ihold, args)
    else:
      motor.ihold = int(args.write, 0)

  elif args.command == 'irun':
    if args.write is None:
      print_val(motor.irun, args)
    else:
      motor.irun = int(args.write, 0)

  elif args.command == 'iholddelay':
    if args.write is None:
      print_val(motor.iholddelay, args)
    else:
      motor.iholddelay = int(args.write, 0)

  elif args.command == 'irundelay':
    if args.write is None:
      print_val(motor.irundelay, args)
    else:
      motor.irundelay = int(args.write, 0)

  ###################
  # TPOWERDOWN 0x11
  elif args.command == 'tpowerdown':
    if args.write is None:
      print_val(motor.tpowerdown, args)
    else:
      motor.tpowerdown = int(args.write, 0)

  ###################
  # TSTEP 0x12
  elif args.command == 'tstep':
    if args.write is None:
      print_val(motor.tstep, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  ###################
  # TPWMTHRS 0x13
  elif args.command == 'tpwmthrs':
    if args.write is None:
      print_val(motor.tpwmthrs, args)
    else:
      motor.tpwmthrs = int(args.write, 0)

  ###################
  # TCOOLTHRS 0x14
  elif args.command == 'tcoolthrs':
    if args.write is None:
      print_val(motor.tcoolthrs, args)
    else:
      motor.tcoolthrs = int(args.write, 0)

  ###################
  # THIGH 0x15
  elif args.command == 'thigh':
    if args.write is None:
      print_val(motor.thigh, args)
    else:
      motor.thigh = int(args.write, 0)

  ##############################################
  # Ramp Generator Registers
  ###################
  # RAMPMODE 0x20
  elif args.command == 'rampmode':
    if args.write is None:
      print_val(motor.rampmode, args)
    else:
      motor.rampmode = int(args.write, 0)

  ###################
  # XACTUAL 0x21
  elif args.command == 'xactual':
    if args.write is None:
      print_val(motor.xactual, args)
    else:
      motor.xactual = int(args.write, 0)

  ###################
  # VACTUAL 0x22
  elif args.command == 'vactual':
    if args.write is None:
      print_val(motor.vactual, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  ###################
  # VSTART 0x23
  elif args.command == 'vstart':
    if args.write is None:
      print_val(motor.vstart, args)
    else:
      motor.vstart = int(args.write, 0)

  ###################
  # A1 0x24
  elif args.command == 'a1':
    if args.write is None:
      print_val(motor.a1, args)
    else:
      motor.a1 = int(args.write, 0)

  ###################
  # V1 0x25
  elif args.command == 'v1':
    if args.write is None:
      print_val(motor.v1, args)
    else:
      motor.v1 = int(args.write, 0)

  ###################
  # AMAX 0x26
  elif args.command == 'amax':
    if args.write is None:
      print_val(motor.amax, args)
    else:
      motor.amax = int(args.write, 0)

  ###################
  # VMAX 0x27
  elif args.command == 'vmax':
    if args.write is None:
      print_val(motor.vmax, args)
    else:
      motor.vmax = int(args.write, 0)

  ###################
  # DMAX 0x28
  elif args.command == 'dmax':
    if args.write is None:
      print_val(motor.dmax, args)
    else:
      motor.dmax = int(args.write, 0)

  ###################
  # TVMAX 0x29
  elif args.command == 'tvmax':
    if args.write is None:
      print_val(motor.tvmax, args)
    else:
      motor.tvmax = int(args.write, 0)

  ###################
  # D1 0x2A
  elif args.command == 'd1':
    if args.write is None:
      print_val(motor.d1, args)
    else:
      motor.d1 = int(args.write, 0)

  ###################
  # VSTOP 0x2B
  elif args.command == 'vstop':
    if args.write is None:
      print_val(motor.vstop, args)
    else:
      motor.vstop = int(args.write, 0)

  ###################
  # TZEROWAIT 0x2C
  elif args.command == 'tzerowait':
    if args.write is None:
      print_val(motor.tzerowait, args)
    else:
      motor.tzerowait = int(args.write, 0)

  ###################
  # XTARGET 0x2D
  elif args.command == 'xtarget':
    if args.write is None:
      print_val(motor.xtarget, args)
    else:
      motor.xtarget = int(args.write, 0)

  elif args.command == 'direct_a':
    if args.write is None:
      print_val(motor.direct_a, args)
    else:
      motor.direct_a = int(args.write, 0)

  elif args.command == 'direct_b':
    if args.write is None:
      print_val(motor.direct_b, args)
    else:
      motor.direct_b = int(args.write, 0)

  ###################
  # V2 0x2E
  elif args.command == 'v2':
    if args.write is None:
      print_val(motor.v2, args)
    else:
      motor.v2 = int(args.write, 0)

  ###################
  # A2 0x2F
  elif args.command == 'a2':
    if args.write is None:
      print_val(motor.a2, args)
    else:
      motor.a2 = int(args.write, 0)

  ###################
  # D2 0x30
  elif args.command == 'd2':
    if args.write is None:
      print_val(motor.d2, args)
    else:
      motor.d2 = int(args.write, 0)

  ##############################################
  # Ramp Generator Driver Feature Control Registers
  ###################
  # VDCMIN 0x33
  elif args.command == 'vdcmin':
    if args.write is None:
      print_val(motor.vdcmin, args)
    else:
      motor.vdcmin = int(args.write, 0)

  ###################
  # SW_MODE 0x34
  elif args.command == 'sg_stop':
    if args.write is None:
      print_val(motor.sg_stop, args)
    else:
      motor.sg_stop = int(args.write, 0)

  elif args.command == 'en_softstop':
    if args.write is None:
      print_val(motor.en_softstop, args)
    else:
      motor.en_softstop = int(args.write, 0)

  elif args.command == 'en_virtual_stop_l':
    if args.write is None:
      print_val(motor.en_virtual_stop_l, args)
    else:
      motor.en_virtual_stop_l = int(args.write, 0)

  elif args.command == 'en_virtual_stop_r':
    if args.write is None:
      print_val(motor.en_virtual_stop_r, args)
    else:
      motor.en_virtual_stop_r = int(args.write, 0)

  ###################
  # RAMP_STAT 0x35
  elif args.command == 'velocity_reached':
    if args.write is None:
      print_val(motor.velocity_reached, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'position_reached':
    if args.write is None:
      print_val(motor.position_reached, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'vzero':
    if args.write is None:
      print_val(motor.vzero, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  ###################
  # VIRTUAL_STOP_L 0x3E
  elif args.command == 'virtual_stop_l':
    if args.write is None:
      print_val(motor.virtual_stop_l, args)
    else:
      motor.virtual_stop_l = int(args.write, 0)

  ###################
  # VIRTUAL_STOP_R 0x3F
  elif args.command == 'virtual_stop_r':
    if args.write is None:
      print_val(motor.virtual_stop_r, args)
    else:
      motor.virtual_stop_r = int(args.write, 0)

  ##############################################
  # ADC Registers
  ###################
  # ADC_VSUPPLY_AIN 0x50
  elif args.command == 'adc_ain':
    if args.write is None:
      print_val(motor.adc_ain, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'adc_vsupply':
    if args.write is None:
      print_val(motor.adc_vsupply, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  ###################
  # ADC_TEMP 0x51
  elif args.command == 'adc_temp':
    if args.write is None:
      print_val(motor.adc_temp, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  ##############################################
  # Motor Driver Registers
  ###################
  # CHOPCONF 0x6C
  elif args.command == 'toff':
    if args.write is None:
      print_val(motor.toff, args)
    else:
      motor.toff = int(args.write, 0)

  elif args.command == 'disfdcc':
    if args.write is None:
      print_val(motor.disfdcc, args)
    else:
      motor.disfdcc = int(args.write, 0)

  elif args.command == 'chm':
    if args.write is None:
      print_val(motor.chm, args)
    else:
      motor.chm = int(args.write, 0)

  elif args.command == 'vhighfs':
    if args.write is None:
      print_val(motor.vhighfs, args)
    else:
      motor.vhighfs = int(args.write, 0)

  elif args.command == 'vhighchm':
    if args.write is None:
      print_val(motor.vhighchm, args)
    else:
      motor.vhighchm = int(args.write, 0)

  elif args.command == 'mres':
    if args.write is None:
      print_val(motor.mres, args)
    else:
      motor.mres = int(args.write, 0)

  elif args.command == 'intpol':
    if args.write is None:
      print_val(motor.intpol, args)
    else:
      motor.intpol = int(args.write, 0)

  elif args.command == 'diss2g':
    if args.write is None:
      print_val(motor.diss2g, args)
    else:
      motor.diss2g = int(args.write, 0)

  elif args.command == 'diss2vs':
    if args.write is None:
      print_val(motor.diss2vs, args)
    else:
      motor.diss2vs = int(args.write, 0)

  ###################
  # COOLCONF 0x6D
  elif args.command == 'semin':
    if args.write is None:
      print_val(motor.semin, args)
    else:
      motor.semin = int(args.write, 0)

  elif args.command == 'seup':
    if args.write is None:
      print_val(motor.seup, args)
    else:
      motor.seup = int(args.write, 0)

  elif args.command == 'semax':
    if args.write is None:
      print_val(motor.semax, args)
    else:
      motor.semax = int(args.write, 0)

  elif args.command == 'sedn':
    if args.write is None:
      print_val(motor.sedn, args)
    else:
      motor.sedn = int(args.write, 0)

  elif args.command == 'seimin':
    if args.write is None:
      print_val(motor.seimin, args)
    else:
      motor.seimin = int(args.write, 0)

  elif args.command == 'sgt':
    if args.write is None:
      print_val(motor.sgt, args)
    else:
      motor.sgt = int(args.write, 0)

  elif args.command == 'sfilt':
    if args.write is None:
      print_val(motor.sfilt, args)
    else:
      motor.sfilt = int(args.write, 0)

  ###################
  # DCCTRL 0x6E
  elif args.command == 'dc_time':
    if args.write is None:
      print_val(motor.dc_time, args)
    else:
      motor.dc_time = int(args.write, 0)

  elif args.command == 'dc_sg':
    if args.write is None:
      print_val(motor.dc_sg, args)
    else:
      motor.dc_sg = int(args.write, 0)

  ###################
  # DRV_STATUS 0x6F
  elif args.command == 'sg_result':
    if args.write is None:
      print_val(motor.sg_result, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 's2vsa':
    if args.write is None:
      print_val(motor.s2vsa, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 's2vsb':
    if args.write is None:
      print_val(motor.s2vsb, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'stealth':
    if args.write is None:
      print_val(motor.stealth, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'fsactive':
    if args.write is None:
      print_val(motor.fsactive, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'cs_actual':
    if args.write is None:
      print_val(motor.cs_actual, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'stallguard':
    if args.write is None:
      print_val(motor.stallguard, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'ot':
    if args.write is None:
      print_val(motor.ot, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'otpw':
    if args.write is None:
      print_val(motor.otpw, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 's2ga':
    if args.write is None:
      print_val(motor.s2ga, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 's2gb':
    if args.write is None:
      print_val(motor.s2gb, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'ola':
    if args.write is None:
      print_val(motor.ola, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'olb':
    if args.write is None:
      print_val(motor.olb, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'stst':
    if args.write is None:
      print_val(motor.stst, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  ###################
  # PWMCONF 0x70
  elif args.command == 'pwm_grad':
    if args.write is None:
      print_val(motor.pwm_grad, args)
    else:
      motor.pwm_grad = int(args.write, 0)

  elif args.command == 'pwm_freq':
    if args.write is None:
      print_val(motor.pwm_freq, args)
    else:
      motor.pwm_freq = int(args.write, 0)

  elif args.command == 'pwm_autoscale':
    if args.write is None:
      print_val(motor.pwm_autoscale, args)
    else:
      motor.pwm_autoscale = int(args.write, 0)

  elif args.command == 'pwm_autograd':
    if args.write is None:
      print_val(motor.pwm_autograd, args)
    else:
      motor.pwm_autograd = int(args.write, 0)

  elif args.command == 'freewheel':
    if args.write is None:
      print_val(motor.freewheel, args)
    else:
      motor.freewheel = int(args.write, 0)

  elif args.command == 'pwm_meas_sd_enable':
    if args.write is None:
      print_val(motor.pwm_meas_sd_enable, args)
    else:
      motor.pwm_meas_sd_enable = int(args.write, 0)

  elif args.command == 'pwm_dis_reg_stst':
    if args.write is None:
      print_val(motor.pwm_dis_reg_stst, args)
    else:
      motor.pwm_dis_reg_stst = int(args.write, 0)

  elif args.command == 'pwm_reg':
    if args.write is None:
      print_val(motor.pwm_reg, args)
    else:
      motor.pwm_reg = int(args.write, 0)

  elif args.command == 'pwm_lim':
    if args.write is None:
      print_val(motor.pwm_lim, args)
    else:
      motor.pwm_lim = int(args.write, 0)

  ###################
  # PWM_SCALE 0x71
  elif args.command == 'pwm_scale_sum':
    if args.write is None:
      print_val(motor.pwm_scale_sum, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'pwm_scale_auto':
    if args.write is None:
      print_val(motor.pwm_scale_auto, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  ###################
  # PWM_AUTO 0x72
  elif args.command == 'pwm_ofs_auto':
    if args.write is None:
      print_val(motor.pwm_ofs_auto, args)
    else:
      motor.pwm_ofs_auto = int(args.write, 0)

  elif args.command == 'pwm_grad_auto':
    if args.write is None:
      print_val(motor.pwm_grad_auto, args)
    else:
      motor.pwm_grad_auto = int(args.write, 0)

  ###################
  # SG4_THRS 0x74
  elif args.command == 'sg4_thrs':
    if args.write is None:
      print_val(motor.sg4_thrs, args)
    else:
      motor.sg4_thrs = int(args.write, 0)

  elif args.command == 'sg4_filt_en':
    if args.write is None:
      print_val(motor.sg4_filt_en, args)
    else:
      motor.sg4_filt_en = int(args.write, 0)

  ###################
  # SG4_RESULT 0x75
  elif args.command == 'sg4_result':
    if args.write is None:
      print_val(motor.sg4_result, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  ###################
  # SG4_IND 0x76
  elif args.command == 'sg4_ind_0':
    if args.write is None:
      print_val(motor.sg4_ind_0, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'sg4_ind_1':
    if args.write is None:
      print_val(motor.sg4_ind_1, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'sg4_ind_2':
    if args.write is None:
      print_val(motor.sg4_ind_2, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'sg4_ind_3':
    if args.write is None:
      print_val(motor.sg4_ind_3, args)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  ##############################################
  # Converted parameters
  elif args.command == 'ifs':
    motor.steps_per_rev = args.steps_per_rev
    if args.write is None:
      print(motor.ifs)
    else:
      motor.ifs = float(args.write)

  elif args.command == 'vactual_rpm':
    motor.steps_per_rev = args.steps_per_rev
    if args.write is None:
      print(motor.vactual_rpm)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'vmax_rpm':
    motor.steps_per_rev = args.steps_per_rev
    if args.write is None:
      print(motor.vmax_rpm)
    else:
      motor.vmax_rpm = float(args.write)

  elif args.command == 'v1_rpm':
    motor.steps_per_rev = args.steps_per_rev
    if args.write is None:
      print(motor.v1_rpm)
    else:
      motor.v1_rpm = float(args.write)

  elif args.command == 'v2_rpm':
    motor.steps_per_rev = args.steps_per_rev
    if args.write is None:
      print(motor.v2_rpm)
    else:
      motor.v2_rpm = float(args.write)

  elif args.command == 'tstep_rpm':
    motor.steps_per_rev = args.steps_per_rev
    if args.write is None:
      print(motor.tstep_rpm)
    else:
      raise ValueError('{} is not writable parameter'.format(args.command))

  elif args.command == 'tpwmthrs_rpm':
    motor.steps_per_rev = args.steps_per_rev
    if args.write is None:
      print(motor.tpwmthrs_rpm)
    else:
      motor.tpwmthrs_rpm = float(args.write)

  elif args.command == 'thigh_rpm':
    motor.steps_per_rev = args.steps_per_rev
    if args.write is None:
      print(motor.thigh_rpm)
    else:
      motor.thigh_rpm = float(args.write)

  else:
    return False
  return True
