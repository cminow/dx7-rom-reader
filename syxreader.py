#!/usr/bin/env python3

import argparse
import math

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def int_from_file(f):
	return int(f.read(1).hex(), 16)

def curve_type(value):
	if value == 0:
		return "-LIN"
	elif value == 1:
		return "-EXP"
	elif value == 2:
		return "+EXP"
	elif value == 3:
		return "+LIN"
	else:
		return "Error"	

def lfo_wave_type(value):
	if value == 0:
		return "TRIANGLE"
	elif value == 1:
		return "SAW DOWN"
	elif value == 2:
		return "SAW UP"
	elif value == 3:
		return "SQUARE"
	elif value == 4:
		return "SINE"
	elif value == 5:
		return "SAMPLE & HOLD"
	
def frequency(coarse, fine, mode):
	if mode == 0:
		if coarse > 0:
			return_frequency = coarse + (fine * 0.01 * coarse)
		else:
			return_frequency = 0.5 + fine * 0.005
		return return_frequency
	else:
		base_frequency = pow(10, coarse & 3)
		base_frequency = base_frequency * math.exp(2.30258509299404568402 * (fine / 100))
		return base_frequency

def operator_breakpoin(breakpoint_number):
	# C3 = 27
	note_name = NOTES[(breakpoint_number + 9) % 12]
	breakpoint = 3
	for octave in range(-1,8):
		if breakpoint_number < breakpoint:
			return "{}{}".format(note_name, octave)
		breakpoint += 12
	return "Unknown"

def setupArguments():
	parser = argparse.ArgumentParser(
		prog = "syxreader.py",
		description = "Read sysex ROM files for the original DX7."
	)
	parser.add_argument('-i', '--infile', dest = 'input_file', required = True)
	parser.add_argument('-n', '--voice-number', dest = 'voice_number', required = True, default = 1, type = int)
	return parser.parse_args()

if __name__ == "__main__":
	args = setupArguments()
	voice_number = args.voice_number
	if voice_number < 1 or voice_number > 32:
		print("Error: voice number must be between 1 and 32.")
		exit()
	with open(args.input_file, 'rb') as f:
		f.seek(6 + (128 * (voice_number - 1)))
		
		for operator in reversed(range(1,7)):
			for rate in range(1,5):
				operator_rate = int_from_file(f)
				print("OP {} EG Rate {}: {}".format(operator, rate, operator_rate))
			for level in range(1,5):
				operator_level = int_from_file(f)
				print("OP {} EG Level {}: {}".format(operator, level, operator_level))
			operator_scaling_break_point = int_from_file(f)
			
			print("OP {} Keyboard level scaling breakpoint: {} ({})".format(operator, operator_scaling_break_point, operator_breakpoin(operator_scaling_break_point)))
			operator_left_depth = int_from_file(f)
			print("OP {} Keyboard level scaling left depth: {}".format(operator, operator_left_depth))
			operator_right_depth = int_from_file(f)
			print("OP {} Keyboard level scaling right depth: {}".format(operator, operator_right_depth))

			curve_byte = int_from_file(f)
			# print("{:08b}".format(curve_byte))
			left_curve_byte = curve_byte >> 2
			print("OP {} left curve: {}".format(operator, curve_type(left_curve_byte)))
			right_curve_byte = curve_byte & ~(1 << 2) & ~(1 << 3)
			# print("{:08b}".format(right_curve_byte))
			print("OP {} right curve: {}".format(operator, curve_type(right_curve_byte)))
		
			osc_detune_and_rate_scale = int_from_file(f)
			# print("{:08b}".format(osc_detune_and_rate_scale))
			detune = (osc_detune_and_rate_scale >> 3) - 7
			print("OP {} oscillator detune: {}".format(operator, detune))
			rate_scale = osc_detune_and_rate_scale & ~(1 << 3) & ~(1 << 4) & ~(1 << 5) & ~(1 << 6)  & ~(1 << 7)
			print("OP {} oscillator rate scale: {}".format(operator, rate_scale))
		
			velocity_sensitivity_and_amp_mod = int_from_file(f)
			key_velocity_sensitivity = velocity_sensitivity_and_amp_mod >> 2
			print("OP {} key velocity sensitivity: {}".format(operator, key_velocity_sensitivity))
			amplitude_mod_sensitivity = velocity_sensitivity_and_amp_mod & ~(1 << 2) & ~(1 << 3) & ~(1 << 4) & ~(1 << 5) & ~(1 << 6) & ~(1 << 6)
			print("OP {} amplitude modulation sensitivity: {}".format(operator, amplitude_mod_sensitivity))
		
			output_level = int_from_file(f)
			print("OP {} output level: {}".format(operator, output_level))
		
			coarse_freq_and_oscillator_mode = int_from_file(f)
			coarse_frequency = coarse_freq_and_oscillator_mode >> 1
			print("OP {} coarse frequency: {}".format(operator, coarse_frequency))
			oscillator_mode = coarse_freq_and_oscillator_mode & ~(1 << 1) & ~(1 << 2) & ~(1 << 3) & ~(1 << 4) & ~(1 << 5)
			print("OP {} oscillator mode: {}".format(operator, "FIXED" if oscillator_mode == 1 else "RATIO"))
		
			freq_fine = int_from_file(f)
			print("OP {} fine frequency: {}".format(operator, freq_fine))
		
			combined_frequency = frequency(coarse_frequency, freq_fine, oscillator_mode)
			print("OP {} combined frequency (as displayed): {}".format(operator, combined_frequency))
		
			print("======= End OP {}".format(operator))
		
		for rate in range(1,5):
			pitch_rate = int_from_file(f)
			print("Pitch EG Rate {}: {}".format(rate, pitch_rate))
		for level in range(1,5):
			pitch_level = int_from_file(f)
			print("Pitch EG Level {}: {}".format(level, pitch_level))
		
		algorithm = int_from_file(f) + 1
		print("Algorithm: {}".format(algorithm))
	
		osc_key_sync_feedback = int_from_file(f)
		oscillator_key_sync = (osc_key_sync_feedback >> 3)
		print("Oscillator key sync: {}".format("ON" if oscillator_key_sync == 1 else "OFF"))
	
		lfo_speed = int_from_file(f)
		print("LFO Speed: {}".format(lfo_speed))
		lfo_delay = int_from_file(f)
		print("LFO Delay: {}".format(lfo_delay))
		lfo_pitch_mod_depth = int_from_file(f)
		print("LFO pitch mod depth: {}".format(lfo_pitch_mod_depth))
		lfo_amp_mod_depth = int_from_file(f)
		print("LFO amplitude mod depth: {}".format(lfo_amp_mod_depth))
		lfo_raw_block = int_from_file(f)
	
		lfo_pitch_mod_sensitivity = (lfo_raw_block >> 4)
		print("LFO pitch modulation sensitivity: {}".format(lfo_pitch_mod_sensitivity))
		lfo_wave = (lfo_raw_block >> 1) & ~(1 << 3) & ~(1 << 4) & ~(1 << 5)
		print("LFO Wave: {}".format(lfo_wave_type(lfo_wave)))
		lfo_sync = lfo_raw_block & ~(1 << 2) & ~(1 << 3) & ~(1 << 4) & ~(1 << 5) & ~(1 << 6)
		print("LFO sync: {}".format("ON" if lfo_sync == 1 else "OFF"))
	
		# print("Raw LFO LPMS, wave and sync: {}".format(lfo_raw_block))
		transpose = int_from_file(f)
		print("Transpose: {} (12 = C2)".format(transpose))
		patch_name = f.read(10).decode("utf-8")
		print("Patch name: {}".format(patch_name))
	