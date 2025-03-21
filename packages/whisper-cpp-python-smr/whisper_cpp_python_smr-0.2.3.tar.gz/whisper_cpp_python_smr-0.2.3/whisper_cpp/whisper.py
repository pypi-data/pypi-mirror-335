# SPDX-License-Identifier: Apache-2.0
import ctypes
import functools
import os
import multiprocessing
import sys
from collections import namedtuple

class whisper_aheads(ctypes.Structure):
    _fields_ = [
        ('n_heads', ctypes.c_size_t),
        ('heads', ctypes.c_void_p)
    ]

class whisper_context_params(ctypes.Structure):
    _fields_ = [
        ('use_gpu', ctypes.c_bool),
        ('flash_attn', ctypes.c_bool),
        ('gpu_device', ctypes.c_int),
        ('dtw_token_timestamps', ctypes.c_bool),
        ('dtw_aheads_preset', ctypes.c_int),
        ('dtw_n_top', ctypes.c_int),
        ('dtw_aheads', whisper_aheads),
        ('dtw_mem_size', ctypes.c_size_t)
    ]

class whisper_full_params_greedy(ctypes.Structure):
    _fields_ = [
        ('best_of', ctypes.c_int)
    ]
class whisper_full_params_beam_search(ctypes.Structure):
    _fields_ = [
        ('beam_size', ctypes.c_int),
        ('patience', ctypes.c_float)
    ]
class whisper_full_params(ctypes.Structure):
    _fields_ = [
        ('strategy', ctypes.c_int),
        ('n_threads', ctypes.c_int),
        ('n_max_text_ctx', ctypes.c_int),
        ('offset_ms', ctypes.c_int),
        ('duration_ms', ctypes.c_int),
        ('translate', ctypes.c_bool),
        ('no_context', ctypes.c_bool),
        ('no_timestamps', ctypes.c_bool),
        ('single_segment', ctypes.c_bool),
        ('print_special', ctypes.c_bool),
        ('print_progress', ctypes.c_bool),
        ('print_realtime', ctypes.c_bool),
        ('print_timestamps', ctypes.c_bool),
        ('token_timestamps', ctypes.c_bool),
        ('thold_pt', ctypes.c_float),
        ('thold_ptsum', ctypes.c_float),
        ('max_len', ctypes.c_int),
        ('split_on_word', ctypes.c_bool),
        ('max_tokens', ctypes.c_int),
        ('debug_mode', ctypes.c_bool),
        ('audio_ctx', ctypes.c_int),
        ('tdrz_enable', ctypes.c_bool),
        ('suppress_regex', ctypes.c_char_p),
        ('initial_prompt', ctypes.c_char),
        ('prompt_tokens', ctypes.c_void_p),
        ('prompt_n_tokens', ctypes.c_int),
        ('language', ctypes.c_char_p),
        ('detect_language', ctypes.c_bool),
        ('suppress_blank', ctypes.c_bool),
        ('suppress_nst', ctypes.c_bool),
        ('temperature', ctypes.c_float),
        ('max_initial_ts', ctypes.c_float),
        ('length_penalty', ctypes.c_float),
        ('temperature_inc', ctypes.c_float),
        ('entropy_thold', ctypes.c_float),
        ('logprob_thold', ctypes.c_float),
        ('no_speech_thold', ctypes.c_float),
        ('greeedy', whisper_full_params_greedy),
        ('beam_search', whisper_full_params_beam_search),
        ('new_segment_callback', ctypes.c_void_p),
        ('new_segment_callback_user_data', ctypes.c_void_p),
        ('progress_callback', ctypes.c_void_p),
        ('progress_callback_user_data', ctypes.c_void_p),
        ('encoder_begin_callback', ctypes.c_void_p),
        ('encoder_begin_callback_user_data', ctypes.c_void_p),
        ('abort_callback', ctypes.c_void_p),
        ('abort_callback_user_data', ctypes.c_void_p),
        ('logits_filter_callback', ctypes.c_void_p),
        ('logits_filter_callback_user_data', ctypes.c_void_p),
        ('grammar_rules', ctypes.c_void_p),
        ('n_grammar_rules', ctypes.c_size_t),
        ('i_start_rule', ctypes.c_size_t),
        ('grammar_penalty', ctypes.c_float),
    ]

ggml_log_callback = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)

def ctypes_function_for_shared_library(lib):
    def ctypes_function(name, argtypes, restype):
        def decorator(f):
            func = getattr(lib, name)
            func.argtypes = argtypes
            func.restype = restype
            functools.wraps(f)(func)
            return func

        return decorator

    return ctypes_function


def lib_name(base):
    if sys.platform == 'darwin':
        return f'lib{base}.dylib'
    if sys.platform == 'linux':
        return f'lib{base}.so'
    if sys.platform == 'win32':
        return f'{base}.dll'

lib = ctypes.CDLL(f'{os.path.dirname(__file__)}/{lib_name("whisper")}')

ctypes_function = ctypes_function_for_shared_library(lib)

WHISPER_AHEADS_NONE = 0
WHISPER_AHEADS_N_TOP_MOST = 1
WHISPER_AHEADS_CUSTOM = 2
WHISPER_AHEADS_TINY_EN = 3
WHISPER_AHEADS_TINY = 4
WHISPER_AHEADS_BASE_EN = 5
WHISPER_AHEADS_BASE = 6
WHISPER_AHEADS_SMALL_EN = 7
WHISPER_AHEADS_SMALL = 8
WHISPER_AHEADS_MEDIUM_EN = 9
WHISPER_AHEADS_MEDIUM = 10
WHISPER_AHEADS_LARGE_V1 = 11
WHISPER_AHEADS_LARGE_V2 = 12
WHISPER_AHEADS_LARGE_V3 = 13

WHISPER_SAMPLING_GREEDY = 0

@ctypes_function(
    'ggml_backend_load',
    [ctypes.c_char_p],
    ctypes.c_void_p
)
def ggml_backend_load():
    pass

@ctypes_function(
    'whisper_context_default_params',
    [],
    whisper_context_params
)
def whisper_context_default_params():
    pass


@ctypes_function(
    'whisper_init_from_file_with_params',
    [ctypes.c_char_p, whisper_context_params],
    ctypes.c_void_p
)
def whisper_init_from_file_with_params():
    pass

@ctypes_function(
    'whisper_free',
    [ctypes.c_void_p],
    None
)
def whisper_free():
    pass

@ctypes_function(
    'whisper_full_default_params',
    [ctypes.c_int],
    whisper_full_params
)
def whisper_full_default_params():
    pass

@ctypes_function(
    'whisper_full_parallel',
    [ctypes.c_void_p, whisper_full_params, ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_int],
    ctypes.c_int
)
def whisper_full_parallel():
    pass

@ctypes_function(
    'whisper_full_n_segments',
    [ctypes.c_void_p],
    ctypes.c_int
)
def whisper_full_n_segments():
    pass

@ctypes_function(
    'whisper_full_get_segment_t0',
    [ctypes.c_void_p, ctypes.c_int],
    ctypes.c_int64
)
def whisper_full_get_segment_t0():
    pass

@ctypes_function(
    'whisper_full_get_segment_t1',
    [ctypes.c_void_p, ctypes.c_int],
    ctypes.c_int64
)
def whisper_full_get_segment_t1():
    pass

@ctypes_function(
    'whisper_full_get_segment_text',
    [ctypes.c_void_p, ctypes.c_int],
    ctypes.c_char_p
)
def whisper_full_get_segment_text():
    pass

@ctypes_function(
    "whisper_log_set",
    [ggml_log_callback, ctypes.c_void_p],
    None
)
def whisper_log_set():
    pass

def py_log_callback(level, text, userdata):
    pass
c_log_callback = ggml_log_callback(py_log_callback)

Segment = namedtuple('Segment', ['start', 'end', 'text'])

class Whisper(object):
    def __init__(self, model_path, aheads, verbose):
        if not verbose:
            whisper_log_set(c_log_callback, None)
        ggml_backend_load(f'{os.path.dirname(__file__)}/{lib_name("ggml-cpu")}'.encode())
        if sys.platform == 'darwin':
            ggml_backend_load(f'{os.path.dirname(__file__)}/{lib_name("ggml-metal")}'.encode())
        if sys.platform == 'linux':
            ggml_backend_load(f'{os.path.dirname(__file__)}/{lib_name("ggml-opencl")}'.encode())

        dp = whisper_context_default_params()
        dp.dtw_aheads_preset = aheads
        self.ctx = whisper_init_from_file_with_params(model_path.encode(), dp)
        if self.ctx is None:
            raise Exception("failed to load model")

    def __del__(self):
        whisper_free(self.ctx)

    def transcribe(self, samples):
        params = whisper_full_default_params(WHISPER_SAMPLING_GREEDY)
        params.n_threads = multiprocessing.cpu_count()
        params.suppress_non_speech_tokens = True
        params.suppress_blank = True
        whisper_full_parallel(self.ctx, params, samples.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), len(samples), 1)
        n_segments = whisper_full_n_segments(self.ctx)
        segments = []
        for i in range(n_segments):
            start = whisper_full_get_segment_t0(self.ctx, i)
            end = whisper_full_get_segment_t1(self.ctx, i)
            text = whisper_full_get_segment_text(self.ctx, i)
            segments.append(Segment(start // 100, end // 100, text.decode()))
        return segments
