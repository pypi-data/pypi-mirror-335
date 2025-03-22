import random

# Sample data for WebGL properties
vendors = ["Intel", "NVIDIA", "AMD", "Apple", "Mesa"]

renderers = [
    'Data Center GPU Max 1550', 'GeForce GT 330M', 'GeForce GTS 360M',
    'Quadro 1000M', 'GeForce GT 430', 'Quadro 2000M', 'GeForce GTS 450',
    'GeForce GTX 460 SE', 'Quadro 4000M', 'GeForce GTX 460', 'GeForce GTX 580M',
    'GeForce GTX 465', 'GeForce GTX 470', 'GeForce GTX 480', 'NVS 4200M',
    'GeForce GT 530', 'GeForce GTX 560M', 'GeForce GTX 550 Ti', 'GeForce GTX 560 SE',
    'GeForce GTX 560', 'GeForce GTX 560 Ti', 'GeForce GTX 560 Ti', 'GeForce GTX 560 Ti 448 Cores',
    'GeForce GTX 570', 'GeForce GTX 580', 'GeForce GTX 590', 'Quadro K1100M',
    'Quadro K610M', 'Quadro K2100M', 'GeForce GTX 650', 'GeForce GTX 650',
    'GeForce GTX 650 Ti', 'GeForce GTX 650 Ti Boost', 'GeForce GTX 660',
    'GeForce GTX 760 192-bit', 'GeForce GTX 660 Ti', 'GeForce GTX 670', 'GeForce GTX 680',
    'GeForce GTX 690', 'GeForce GT 710', 'GeForce GT 720', 'GeForce GTX 745',
    'GeForce GTX 750', 'GeForce GTX 750 Ti', 'GeForce GTX 760', 'Quadro K5100M',
    'GeForce GTX 770', 'GeForce GTX 780', 'GeForce GTX 780 Ti', 'GeForce GTX TITAN',
    'GeForce GTX TITAN Black', 'GeForce GTX TITAN Z', 'Quadro M520 Mobile',
    'GeForce GTX 950', 'Quadro M2200 Mobile', 'GeForce GTX 960', 'Quadro M5500 Mobile',
    'GeForce GTX 970', 'GeForce GTX 980', 'GeForce GTX 980 Ti', 'GeForce GTX TITAN X',
    'GeForce GT 1010', 'GeForce GT 1030', 'GeForce GT 1030', 'GeForce GTX 1050',
    'GeForce GTX 1050', 'GeForce GTX 1050 Ti', 'GeForce GTX 1060', 'GeForce GTX 1060',
    'GeForce GTX 1060', 'GeForce GTX 1060', 'GeForce GTX 1060', 'GeForce GTX 1060',
    'GeForce GTX 1060', 'GeForce GTX 1070 Ti', 'GeForce GTX 1080', 'GeForce GTX 1080',
    'GeForce GTX 1080 Ti', 'TITAN X Pascal', 'TITAN Xp', 'Nvidia TITAN V',
    'Nvidia TITAN V CEO Edition', 'GeForce GTX 1630', 'GeForce GTX 1650',
    'GeForce GTX 1650', 'GeForce GTX 1650 Super', 'GeForce GTX 1660 Super',
    'GeForce GTX 1660 Ti', 'GeForce RTX 2060', 'GeForce RTX 2060',
    'GeForce RTX 2060', 'GeForce RTX 2060 Super', 'GeForce RTX 2070', 'GeForce RTX 2070 Super',
    'GeForce RTX 2080', 'GeForce RTX 2080 Super', 'GeForce RTX 2080 Ti', 'Nvidia TITAN RTX',
    'GeForce RTX 3050', 'GeForce RTX 3050', 'GeForce RTX 3050', 'GeForce RTX 3050',
    'GeForce RTX 3060', 'GeForce RTX 3060', 'GeForce RTX 3060 Ti', 'GeForce RTX 3060 Ti',
    'GeForce RTX 3070', 'GeForce RTX 3070 Ti', 'GeForce RTX 3080', 'GeForce RTX 3080',
    'GeForce RTX 3080 Ti', 'GeForce RTX 3090', 'GeForce RTX 3090 Ti', 'GeForce RTX 4060',
    'GeForce RTX 4060 Ti', 'GeForce RTX 4060 Ti', 'GeForce RTX 4070', 'GeForce RTX 4070 Super',
    'GeForce RTX 4070 Ti Super', 'GeForce RTX 4080', 'GeForce RTX 4080 Super', 'GeForce RTX 4090 D',
    'GeForce RTX 4090', 'GeForce RTX 5070', 'GeForce RTX 5070 Ti', 'GeForce RTX 5080',
    'GeForce RTX 5090', 'GeForce 320M', 'Quadro 5000M', 'GeForce GT 550M', 'GeForce GT 555M',
    'GeForce 610M', 'GeForce GT 625M', 'GeForce GT 630M', 'GeForce GT 635M',
    'GeForce GT 640M LE', 'GeForce GT 645M', 'GeForce GT 650M', 'GeForce GTX 660M',
    'GeForce GTX 670M', 'GeForce GTX 670MX', 'GeForce GTX 675M', 'GeForce GTX 675MX',
    'GeForce GTX 680M', 'GeForce 820M', 'Quadro M1200 Mobile', 'GeForce 910M',
    'GeForce GTX 1050 (Notebook)', 'GeForce GTX 1050 Ti (Notebook)', 'Quadro P3000 Mobile',
    'Quadro T2000 Max-Q', 'RTX A1000 Mobile 6 GB', 'Quadro RTX 3000 Max-Q',
    'Quadro RTX 5000 Max-Q', 'RTX A2000 Mobile', 'GeForce RTX 3070 Mobile/ Laptop',
    'GeForce RTX 3070 Ti Mobile/ Laptop', 'GeForce RTX 3080 Mobile/ Laptop',
    'GeForce RTX 3080 Ti Mobile/ Laptop', 'GeForce RTX 4050 Mobile/ Laptop', 'GeForce RTX 4060 Mobile/ Laptop',
    'GeForce RTX 4070 Mobile/ Laptop', 'GeForce RTX 4080 Mobile/ Laptop', 'GeForce RTX 4090 Mobile/ Laptop',
    'Quadro 400', 'Quadro 600', 'Quadro 2000', 'Quadro 5010M', 'Quadro K6000', 'Quadro K620',
    'Quadro K1200', 'Quadro K2200', 'Quadro K5200', 'Quadro M2000', 'Quadro M4000',
    'Quadro M5000', 'Quadro M6000', 'Quadro P400', 'Quadro P600', 'Quadro P620',
    'Quadro P1000', 'Quadro P2000', 'Quadro P2200', 'Quadro P4000', 'Quadro P5000',
    'Quadro P6000', 'Quadro GP100', 'Quadro GV100', 'Quadro RTX 4000', 'Quadro RTX 5000',
    'Quadro RTX 8000', 'RTX 2000 Ada Generation', 'RTX 4000 Mobile Ada Generation',
    'RTX 5000 Mobile Ada Generation', 'NVS 3100M', 'NVS 5100M', 'Quadro P500 Mobile',
    'Quadro P600 Mobile', 'Quadro P1000 Mobile', 'Quadro P2000 Mobile', 'Quadro P5200 Max-Q',
    'Quadro T1000 Mobile', 'Quadro T2000 Mobile', 'Quadro RTX 3000 Mobile', 'Quadro RTX 4000 Mobile',
    'Quadro RTX 5000 Mobile', 'RTX A500 Mobile', 'RTX A5000 Mobile', 'RTX A5500 Mobile',
    'RTX 2000 Mobile Ada Generation', 'RTX 3000 Mobile Ada Generation', 'NVS 5400M',
    'NX-SoC (Nintendo Switch)', 'Radeon HD 3570', 'Radeon HD 4580',
    'Radeon HD 4250 Graphics (880G Chipset)', 'Radeon HD 4290 Graphics (890GX Chipset)',
    'Radeon HD 5450', 'Radeon HD 5550', 'Radeon HD 5610', 'Radeon HD 5670', 'Radeon HD 5830',
    'Radeon HD 7340', 'Radeon HD 7540D', 'Radeon HD 7660D', 'Mobility Radeon HD 4270',
    'FirePro 3D V3800', 'FirePro 3D V4800', 'FirePro 3D V5800', 'FirePro 3D V7800',
    'FirePro 3D V9800', 'FirePro V3900', 'FirePro V4900', 'FirePro V5900', 'FirePro V7900',
    'FirePro W600', 'FirePro W5000', 'FirePro D300', 'FirePro S9050', 'FirePro D700',
    'FirePro D500', 'FirePro W2100', 'FirePro W4100', 'FirePro W5100', 'FirePro W7100',
    'FirePro S9100', 'FirePro W9100', 'FirePro W4300', 'FirePro RG220', 'FirePro R5000',
    'FirePro S4000x', 'Radeon Sky 500', 'FirePro S7100X', 'FirePro S7150', 'FirePro S7150 X2',
    'FirePro S9150', 'FirePro S9170', 'FirePro S9300 x2', 'FirePro S10000', 'FirePro S10000 passive',
    'Radeon Sky 700', 'Radeon Sky 900'
]

versions = ["WebGL 1.0", "WebGL 2.0"]

extensions = [
    "ANGLE_instanced_arrays",
    "EXT_blend_minmax",
    "EXT_clip_control",
    "EXT_color_buffer_half_float",
    "EXT_depth_clamp",
    "EXT_disjoint_timer_query",
    "EXT_float_blend",
    "EXT_frag_depth",
    "EXT_polygon_offset_clamp",
    "EXT_shader_texture_lod",
    "EXT_texture_compression_bptc",
    "EXT_texture_compression_rgtc",
    "EXT_texture_filter_anisotropic",
    "EXT_texture_mirror_clamp_to_edge",
    "EXT_sRGB",
    "KHR_parallel_shader_compile",
    "OES_element_index_uint",
    "OES_fbo_render_mipmap",
    "OES_standard_derivatives",
    "OES_texture_float",
    "OES_texture_float_linear",
    "OES_texture_half_float",
    "OES_texture_half_float_linear",
    "OES_vertex_array_object",
    "WEBGL_blend_func_extended",
    "WEBGL_color_buffer_float",
    "WEBGL_compressed_texture_s3tc",
    "WEBGL_compressed_texture_s3tc_srgb",
    "WEBGL_debug_renderer_info",
    "WEBGL_debug_shaders",
    "WEBGL_depth_texture",
    "WEBGL_draw_buffers",
    "WEBGL_lose_context",
    "WEBGL_multi_draw",
    "WEBGL_polygon_mode"
]

def get_vendor():
    """Return a random vendor."""
    return random.choice(vendors)

def get_renderer():
    """Return a random renderer."""
    return random.choice(renderers)

def get_version():
    """Return a random WebGL version."""
    return random.choice(versions)

def get_extensions():
    """Return a random selection of one or more extensions."""
    extension_count = random.randint(1, len(extensions))
    return random.sample(extensions, extension_count)

def full_fingerprint():
    """Generate and return a fingerprint dictionary combining all parts."""
    fingerprint = {
        "vendor": get_vendor(),
        "renderer": get_renderer(),
        "version": get_version(),
        "extensions": get_extensions()
    }
    return fingerprint

# Example usage:
if __name__ == "__main__":
    fp = full_fingerprint()
    print(fp)
