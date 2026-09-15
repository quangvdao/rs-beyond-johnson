#!/usr/bin/env python3
"""Reproduce the full shipped ZisK v1.2 beyond-Johnson scope audit.

The embedded inventory was streamed from every starkinfo.json in the public
v1.2.0-alpha proving-key archive. Checks use exact integer/rational arithmetic
and the repository's finite MCA engine. Security is checked phase by phase,
matching Proofman's convention; no whole-protocol security claim is made.
"""
from fractions import Fraction as F
import json
import math
from pathlib import Path

from tune_powers_mca import certificate

P = 2**64 - 2**32 + 1
Q = P**3
TARGET_BITS = 128
SOURCE = {
    "audit_date": "2026-09-07",
    "zisk_main_observed_commit": "b08d856c0f72b21d94fc49151deefaf8e7419b79",
    "proofman_main_observed_commit": "0f3fef8cd1897df469532996e72e0c84ef69d6fb",
    "zisk_release": "v1.2.0-alpha",
    "zisk_commit": "fbbc69bcd2ea9a78d1a438b4a897bc48ff0b00a3",
    "proofman_release": "v1.2.0-alpha",
    "proofman_commit": "0f3fef8cd1897df469532996e72e0c84ef69d6fb",
    "artifact_url": "https://storage.googleapis.com/zisk-setup/zisk-provingkey-1.2.0-alpha.tar.gz",
    "artifact_metadata_url": "https://storage.googleapis.com/storage/v1/b/zisk-setup/o/zisk-provingkey-1.2.0-alpha.tar.gz",
    "artifact_hash_url": "https://storage.googleapis.com/zisk-setup/zisk-provingkey-1.2.0-alpha.hash",
    "artifact_md5_url": "https://storage.googleapis.com/zisk-setup/zisk-provingkey-1.2.0-alpha.tar.gz.md5",
    "artifact_size_bytes": 3834146324,
    "artifact_updated": "2026-08-26T10:12:30.073Z",
    "artifact_etag": "-CPKe8KeHvpYDEAE=",
    "artifact_crc32c_base64": "I/G+IA==",
    "artifact_md5": "51e142e7217b807bec25af465b7eeb71",
    "setup_input_hash": "8a3874e32de9f44e999ff91f06df618efe44ba0606a7c5c592e3fe59feb58e76",
}
SUPPORT_BANK = [
    (13, 3, 18), (12, 3, 16), (12, 3, 24), (9, 3, 17),
    (8, 4, 28), (7, 3, 19), (7, 3, 26), (6, 3, 21),
    (6, 3, 16), (5, 2, 19), (5, 2, 14), (2, 0, 10),
    (2, 0, 6), (15, 0, 62), (20, 0, 58), (2, 0, 11),
]

ARTIFACT_METADATA = json.loads(r'''
[{"name":"Add256","artifact_name":"Add256","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Add256/air/Add256.starkinfo.json","n_bits":20,"n_bits_ext":21,"steps":[21,18,15,12,9,6],"pow_bits":16,"queries":228,"batch_size":69,"opening_group_sizes":[1,67,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[47,51,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Arith","artifact_name":"Arith","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Arith/air/Arith.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":66,"opening_group_sizes":[1,64,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[45,46,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Arith256","artifact_name":"Arith256","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Arith256/air/Arith256.starkinfo.json","n_bits":20,"n_bits_ext":21,"steps":[21,18,15,12,9,6],"pow_bits":16,"queries":228,"batch_size":173,"opening_group_sizes":[1,3,3,3,3,3,3,5,7,7,7,9,9,9,11,24,10,7,7,7,5,6,6,6,3,3,3,3],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[11,23,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Arith256/compressor","artifact_name":"Zisk_Arith256_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/Arith256/compressor/compressor.starkinfo.json","n_bits":18,"n_bits_ext":20,"steps":[20,17,14,11,8,5],"pow_bits":20,"queries":120,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"Arith256X","artifact_name":"Arith256X","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Arith256X/air/Arith256X.starkinfo.json","n_bits":20,"n_bits_ext":21,"steps":[21,18,15,12,9,6],"pow_bits":16,"queries":228,"batch_size":265,"opening_group_sizes":[4,6,6,6,6,6,6,8,11,11,11,12,12,12,17,34,12,9,9,9,8,8,8,8,5,5,5,5,2,2,2],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[19,29,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Arith256X/compressor","artifact_name":"Zisk_Arith256X_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/Arith256X/compressor/compressor.starkinfo.json","n_bits":18,"n_bits_ext":20,"steps":[20,17,14,11,8,5],"pow_bits":20,"queries":120,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"ArithBn254Complex","artifact_name":"ArithBn254Complex","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/ArithBn254Complex/air/ArithBn254Complex.starkinfo.json","n_bits":20,"n_bits_ext":21,"steps":[21,18,15,12,9,6],"pow_bits":16,"queries":228,"batch_size":263,"opening_group_sizes":[3,5,5,5,5,5,5,7,13,13,13,13,13,13,19,41,13,9,9,9,9,9,9,9,3,2,2,2],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[24,35,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"ArithBn254Complex/compressor","artifact_name":"Zisk_ArithBn254Complex_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/ArithBn254Complex/compressor/compressor.starkinfo.json","n_bits":18,"n_bits_ext":20,"steps":[20,17,14,11,8,5],"pow_bits":20,"queries":120,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"ArithBn254Ec","artifact_name":"ArithBn254Ec","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/ArithBn254Ec/air/ArithBn254Ec.starkinfo.json","n_bits":20,"n_bits_ext":21,"steps":[21,18,15,12,9,6],"pow_bits":16,"queries":228,"batch_size":281,"opening_group_sizes":[2,4,4,4,4,4,4,6,13,13,13,14,14,14,20,46,16,11,11,11,11,11,11,11,3,2,2,2],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[27,39,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"ArithBn254Ec/compressor","artifact_name":"Zisk_ArithBn254Ec_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/ArithBn254Ec/compressor/compressor.starkinfo.json","n_bits":18,"n_bits_ext":20,"steps":[20,17,14,11,8,5],"pow_bits":20,"queries":120,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"ArithEq","artifact_name":"ArithEq","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/ArithEq/air/ArithEq.starkinfo.json","n_bits":20,"n_bits_ext":21,"steps":[21,18,15,12,9,6],"pow_bits":16,"queries":228,"batch_size":479,"opening_group_sizes":[13,15,15,15,15,15,15,17,23,23,23,23,23,23,38,64,16,11,11,11,11,11,11,11,5,5,5,5,2,2,2],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[45,39,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"ArithEq/compressor","artifact_name":"Zisk_ArithEq_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/ArithEq/compressor/compressor.starkinfo.json","n_bits":18,"n_bits_ext":20,"steps":[20,17,14,11,8,5],"pow_bits":20,"queries":120,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"ArithEq384","artifact_name":"ArithEq384","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/ArithEq384/air/ArithEq384.starkinfo.json","n_bits":20,"n_bits_ext":21,"steps":[21,18,15,12,9,6],"pow_bits":16,"queries":228,"batch_size":551,"opening_group_sizes":[9,9,9,10,10,10,10,10,10,10,10,12,18,18,18,18,18,18,18,18,18,18,28,54,15,11,11,11,11,11,11,11,11,11,11,11,4,4,4,4,4,4,2,2,2,2,2],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[35,39,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"ArithEq384/compressor","artifact_name":"Zisk_ArithEq384_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/ArithEq384/compressor/compressor.starkinfo.json","n_bits":18,"n_bits_ext":20,"steps":[20,17,14,11,8,5],"pow_bits":20,"queries":120,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"ArithSecp256K1","artifact_name":"ArithSecp256K1","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/ArithSecp256K1/air/ArithSecp256K1.starkinfo.json","n_bits":20,"n_bits_ext":21,"steps":[21,18,15,12,9,6],"pow_bits":16,"queries":228,"batch_size":281,"opening_group_sizes":[2,4,4,4,4,4,4,6,13,13,13,14,14,14,20,46,16,11,11,11,11,11,11,11,3,2,2,2],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[27,39,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"ArithSecp256K1/compressor","artifact_name":"Zisk_ArithSecp256K1_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/ArithSecp256K1/compressor/compressor.starkinfo.json","n_bits":18,"n_bits_ext":20,"steps":[20,17,14,11,8,5],"pow_bits":20,"queries":120,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"Binary","artifact_name":"Binary","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Binary/air/Binary.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":16,"queries":228,"batch_size":49,"opening_group_sizes":[1,47,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[39,15,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"BinaryAdd","artifact_name":"BinaryAdd","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/BinaryAdd/air/BinaryAdd.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":16,"queries":228,"batch_size":18,"opening_group_sizes":[1,16,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[10,9,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"BinaryAddHi","artifact_name":"BinaryAddHi","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/BinaryAddHi/air/BinaryAddHi.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":16,"queries":228,"batch_size":25,"opening_group_sizes":[1,23,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[15,15,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"BinaryExtension","artifact_name":"BinaryExtension","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/BinaryExtension/air/BinaryExtension.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":16,"queries":228,"batch_size":39,"opening_group_sizes":[1,37,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[28,18,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"BinaryExtensionFull","artifact_name":"BinaryExtensionFull","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/BinaryExtensionFull/air/BinaryExtensionFull.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":16,"queries":228,"batch_size":45,"opening_group_sizes":[1,43,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[34,18,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Blake2br","artifact_name":"Blake2br","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Blake2br/air/Blake2br.starkinfo.json","n_bits":18,"n_bits_ext":19,"steps":[19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":248,"opening_group_sizes":[12,10,10,10,12,10,13,165,2,1,1,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":3,"stage_widths":[119,109,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Blake2br/compressor","artifact_name":"Zisk_Blake2br_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/Blake2br/compressor/compressor.starkinfo.json","n_bits":18,"n_bits_ext":20,"steps":[20,17,14,11,8,5],"pow_bits":20,"queries":120,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"Dma","artifact_name":"Dma","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Dma/air/Dma.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":46,"opening_group_sizes":[1,44,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[34,21,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Dma64Aligned","artifact_name":"Dma64Aligned","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Dma64Aligned/air/Dma64Aligned.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":62,"opening_group_sizes":[11,50,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[35,36,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Dma64AlignedInputCpy","artifact_name":"Dma64AlignedInputCpy","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Dma64AlignedInputCpy/air/Dma64AlignedInputCpy.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":44,"opening_group_sizes":[6,37,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[25,27,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Dma64AlignedMem","artifact_name":"Dma64AlignedMem","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Dma64AlignedMem/air/Dma64AlignedMem.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":46,"opening_group_sizes":[10,35,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[26,18,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Dma64AlignedMemCpy","artifact_name":"Dma64AlignedMemCpy","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Dma64AlignedMemCpy/air/Dma64AlignedMemCpy.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":52,"opening_group_sizes":[7,44,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[31,30,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Dma64AlignedMemSet","artifact_name":"Dma64AlignedMemSet","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Dma64AlignedMemSet/air/Dma64AlignedMemSet.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":30,"opening_group_sizes":[7,22,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[14,15,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"DmaInputCpy","artifact_name":"DmaInputCpy","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/DmaInputCpy/air/DmaInputCpy.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":27,"opening_group_sizes":[1,25,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[16,18,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"DmaMemCpy","artifact_name":"DmaMemCpy","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/DmaMemCpy/air/DmaMemCpy.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":33,"opening_group_sizes":[1,31,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[22,18,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"DmaPrePost","artifact_name":"DmaPrePost","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/DmaPrePost/air/DmaPrePost.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":83,"opening_group_sizes":[1,81,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[66,32,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"DmaPrePostInputCpy","artifact_name":"DmaPrePostInputCpy","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/DmaPrePostInputCpy/air/DmaPrePostInputCpy.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":44,"opening_group_sizes":[1,42,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[32,21,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"DmaPrePostMemCpy","artifact_name":"DmaPrePostMemCpy","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/DmaPrePostMemCpy/air/DmaPrePostMemCpy.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":70,"opening_group_sizes":[1,68,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[55,30,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"DmaUnaligned","artifact_name":"DmaUnaligned","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/DmaUnaligned/air/DmaUnaligned.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":52,"opening_group_sizes":[13,31,8],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[24,12,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"InputData","artifact_name":"InputData","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/InputData/air/InputData.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":25,"opening_group_sizes":[6,18,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[9,14,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"JumpDest","artifact_name":"JumpDest","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/JumpDest/air/JumpDest.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":63,"opening_group_sizes":[3,2,12,45,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[32,25,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Keccakf","artifact_name":"Keccakf","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Keccakf/air/Keccakf.starkinfo.json","n_bits":18,"n_bits_ext":19,"steps":[19,16,13,10,7,5],"pow_bits":21,"queries":217,"batch_size":5408,"opening_group_sizes":[1,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1604,2170,1602,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[1925,721,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Keccakf/compressor","artifact_name":"Zisk_Keccakf_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/Keccakf/compressor/compressor.starkinfo.json","n_bits":20,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":20,"queries":110,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"Main","artifact_name":"Main","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Main/air/Main.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":16,"queries":228,"batch_size":59,"opening_group_sizes":[8,50,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[38,24,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Mem","artifact_name":"Mem","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Mem/air/Mem.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":16,"queries":228,"batch_size":27,"opening_group_sizes":[7,19,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[13,9,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"MemAlign","artifact_name":"MemAlign","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/MemAlign/air/MemAlign.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":63,"opening_group_sizes":[14,39,10],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[32,12,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"MemAlignByte","artifact_name":"MemAlignByte","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/MemAlignByte/air/MemAlignByte.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":16,"queries":228,"batch_size":25,"opening_group_sizes":[1,23,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[16,12,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"MemAlignReadByte","artifact_name":"MemAlignReadByte","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/MemAlignReadByte/air/MemAlignReadByte.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":16,"queries":228,"batch_size":18,"opening_group_sizes":[1,16,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[10,9,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"MemAlignWriteByte","artifact_name":"MemAlignWriteByte","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/MemAlignWriteByte/air/MemAlignWriteByte.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":16,"queries":228,"batch_size":23,"opening_group_sizes":[1,21,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[14,12,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Poseidon","artifact_name":"Poseidon","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Poseidon/air/Poseidon.starkinfo.json","n_bits":17,"n_bits_ext":18,"steps":[18,15,12,9,6],"pow_bits":16,"queries":228,"batch_size":534,"opening_group_sizes":[2,2,2,2,2,1,1,1,1,1,18,18,69,316,66,16,16],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[84,302,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Poseidon/compressor","artifact_name":"Zisk_Poseidon_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/Poseidon/compressor/compressor.starkinfo.json","n_bits":18,"n_bits_ext":20,"steps":[20,17,14,11,8,5],"pow_bits":20,"queries":120,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"Rom","artifact_name":"Rom","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Rom/air/Rom.starkinfo.json","n_bits":22,"n_bits_ext":23,"steps":[23,20,17,14,11,8,5],"pow_bits":20,"queries":219,"batch_size":21,"opening_group_sizes":[1,19,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[1,9,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"RomData","artifact_name":"RomData","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/RomData/air/RomData.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":14,"opening_group_sizes":[4,9,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":1,"stage_widths":[5,3,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Sha256f","artifact_name":"Sha256f","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/Sha256f/air/Sha256f.starkinfo.json","n_bits":18,"n_bits_ext":19,"steps":[19,16,13,10,7,5],"pow_bits":16,"queries":228,"batch_size":1266,"opening_group_sizes":[1,1,1,65,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,34,34,2,2,2,2,2,2,2,34,2,2,66,66,98,68,114,66,65,65,33,33,32,32,32,32,32,32,64,32,32,32],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":2,"stage_widths":[102,14,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"Sha256f/compressor","artifact_name":"Zisk_Sha256f_compressor","category":"compressor","artifact_path":"provingKey/zisk/Zisk/airs/Sha256f/compressor/compressor.starkinfo.json","n_bits":19,"n_bits_ext":21,"steps":[21,18,15,12,9,6],"pow_bits":20,"queries":110,"batch_size":181,"opening_group_sizes":[2,2,2,2,19,134,18,1,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":51,"stage_widths":[46,49,12],"n_publics":472,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.49666666666666665},{"name":"VirtualTableZisk0","artifact_name":"VirtualTableZisk0","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/VirtualTableZisk0/air/VirtualTableZisk0.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":20,"queries":219,"batch_size":77,"opening_group_sizes":[1,75,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":54,"stage_widths":[12,21,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"VirtualTableZisk1","artifact_name":"VirtualTableZisk1","category":"base_air","artifact_path":"provingKey/zisk/Zisk/airs/VirtualTableZisk1/air/VirtualTableZisk1.starkinfo.json","n_bits":21,"n_bits_ext":22,"steps":[22,19,16,13,10,7,5],"pow_bits":23,"queries":213,"batch_size":84,"opening_group_sizes":[1,82,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":48,"stage_widths":[21,33,6],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.2895598854801191},{"name":"recursive2","artifact_name":"Zisk_Main_recursive1","category":"recursive2","artifact_path":"provingKey/zisk/Zisk/recursive2/recursive2.starkinfo.json","n_bits":17,"n_bits_ext":20,"steps":[20,17,14,11,8,5],"pow_bits":20,"queries":73,"batch_size":135,"opening_group_sizes":[2,3,104,25,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":45,"stage_widths":[48,12,21],"n_publics":476,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.643113276073393},{"name":"vadcop_final","artifact_name":"vadcop_final","category":"final_stark","artifact_path":"provingKey/zisk/vadcop_final/vadcop_final.starkinfo.json","n_bits":16,"n_bits_ext":20,"steps":[20,16,12,8,5],"pow_bits":22,"queries":54,"batch_size":135,"opening_group_sizes":[2,3,104,25,1],"arity":4,"transcript_arity":4,"last_level_verification":2,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":45,"stage_widths":[48,12,21],"n_publics":69,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.7466666666666667},{"name":"vadcop_final_compressed","artifact_name":"compressed_final","category":"final_stark","artifact_path":"provingKey/zisk/vadcop_final_compressed/vadcop_final_compressed.starkinfo.json","n_bits":15,"n_bits_ext":19,"steps":[19,16,13,10],"pow_bits":22,"queries":54,"batch_size":135,"opening_group_sizes":[2,3,104,25,1],"arity":2,"transcript_arity":4,"last_level_verification":6,"verification_hash_type":"GL","hash_commits":true,"merkle_tree_custom":true,"n_stages":2,"n_constants":45,"stage_widths":[48,12,21],"n_publics":68,"security_regime":"JBR","proximity_gap":0.0033333333333333335,"proximity_parameter":0.7466666666666667}]
''' )

POWERS_ALTERNATIVES = [
    ("vadcop_final_compressed", 52, [(8,4,28),(8,4,28),(6,3,21)]),
    ("vadcop_final", 52, [(8,4,28),(7,3,26),(5,2,19),(2,0,10)]),
    ("recursive2", 71, [(7,3,19),(7,3,18),(7,3,18),(5,2,14),(2,0,6)]),
]

# Actual evMap grouping for the three aggregation configurations.  vf2 powers
# batch within each opening point; vf1 powers batch the five resulting groups.
NESTED_OPENING_GROUP_SIZES = [2, 3, 104, 25, 1]


def bits(error):
    return math.log2(error.denominator) - math.log2(error.numerator)


def compact(c):
    keep = ["m","M","mu","support","height","dimension","local_rank_upper",
            "L","exact_exceptional_bound","exceptional_count_upper","list_size_upper",
            "joint_degree_upper","generic_fiber_degree_upper"]
    return {k: c[k] for k in keep}


def exact_threshold(n, k, queries, pow_bits):
    """Largest integral A satisfying query target and strict finite Johnson."""
    hi, lo = min(n, math.isqrt(n * (k - 1) - 1)), k + 1
    if lo > hi:
        return None
    scale, nt = 2 ** (TARGET_BITS - pow_bits), n**queries
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid**queries * scale <= nt:
            lo = mid
        else:
            hi = mid - 1
    return lo


def best_certificate(n, k, A, ell, denominator):
    choices = []
    for support in SUPPORT_BANK:
        try:
            c = certificate(n, k, A, *support, ell)
        except ValueError:
            continue
        if c:
            error = F(c["exceptional_count_upper"], denominator)
            choices.append((error, support, c))
    if not choices:
        return None
    error, support, c = min(choices, key=lambda x: x[0])
    return {"support":list(support), "error":str(error), "bits":bits(error),
            "certificate":compact(c)}


def nested_powers_batch(n, k, A, group_sizes):
    """Joint inner interleaved-curve bound followed by the outer powers curve.

    The shared inner challenge is charged once at the maximum group degree.
    Padding to that degree preserves the actual nested batching transcript.
    """
    degrees = [size-1 for size in group_sizes]
    components=[]
    total=F(0)
    for role, degree in [("inner_groups",max(degrees)),("outer_groups",len(degrees)-1)]:
        if degree == 0:
            components.append({"role":role,"degree":0,"error":"0","bits":None,"certificate":None})
            continue
        c=best_certificate(n,k,A,degree,Q)
        if c is None:
            return None
        total += F(c["error"])
        components.append({"role":role,"degree":degree,**c})
    return {"opening_group_sizes":group_sizes,
            "inner_degrees":degrees,"outer_degree":len(degrees)-1,
            "charged_degrees":[max(degrees),len(degrees)-1],
            "components":components,"error":str(total),"bits":bits(total)}


def raw_proof_bytes(meta, queries):
    """Exact Proofman verifier::expected_proof_size_bytes raw-u64 layout."""
    arity = meta["arity"]
    log_arity = arity.bit_length() - 1
    llv = meta["last_level_verification"]
    siblings = max(0, (meta["n_bits_ext"] + log_arity - 1)//log_arity - llv)
    per_level = (arity - 1) * 4
    last = arity**llv * 4 if llv else 0
    words = 4*(meta["n_stages"]+1) + 3*meta["batch_size"]
    words += queries*meta["n_constants"] + queries*siblings*per_level + last
    for width in meta["stage_widths"]:
        words += queries*width + queries*siblings*per_level + last
    steps = meta["steps"]
    words += 4*(len(steps)-1)
    for before, after in zip(steps, steps[1:]):
        words += queries*(2**(before-after)*3)
        fri_siblings = max(0, (after+log_arity-1)//log_arity - llv)
        words += queries*fri_siblings*per_level + last
    words += 3*2**steps[-1] + 1
    return words*8


def johnson_query_floor(meta):
    """Exact query floor at the finite Johnson agreement sqrt((k-1)/n)."""
    n, k = 2**meta["n_bits_ext"], 2**meta["n_bits"]
    queries = 1
    # Square the comparison to avoid representing the Johnson square root.
    rhs = F(1, 2**(2*(TARGET_BITS-meta["pow_bits"])))
    while F(k-1,n)**queries > rhs:
        queries += 1
    return queries


def affine_geometry(meta, queries):
    n, k = 2**meta["n_bits_ext"], 2**meta["n_bits"]
    A = exact_threshold(n, k, queries, meta["pow_bits"])
    if A is None:
        return {"status":"no threshold above dimension", "queries":queries,
                "minimum_phase_bits":0.0}
    initial = best_certificate(n, k, A, 1, Q-1)
    qe = F(A,n)**queries / 2**meta["pow_bits"]
    folds, nn, kk = [], n, k
    for before, after in zip(meta["steps"],meta["steps"][1:]):
        factor = 2**(before-after)
        nn //= factor; kk //= factor
        aa = (A*nn+n-1)//n
        fc = best_certificate(nn,kk,aa,factor-1,Q)
        folds.append({"n":nn,"k":kk,"A":aa,"powers_degree":factor-1,**(fc or {})})
    levels = [bits(qe)]
    if initial: levels.append(initial["bits"])
    levels.extend(f["bits"] for f in folds if "bits" in f)
    ok = bool(initial) and all("bits" in f for f in folds) and min(levels)>=TARGET_BITS
    return {"status":"certified" if ok else "bounded certificate below target",
            "queries":queries,"A":A,"agreement":str(F(A,n)),
            "finite_johnson_strict":A*A<n*(k-1),"query_error":str(qe),
            "query_bits":bits(qe),"initial_affine":initial,"folds":folds,
            "minimum_phase_bits":min(levels)}


def affine_groups():
    grouped = {}
    for meta in ARTIFACT_METADATA:
        key=(meta["category"],meta["n_bits"],meta["n_bits_ext"],tuple(meta["steps"]),
             meta["pow_bits"],meta["queries"])
        grouped.setdefault(key,[]).append(meta)
    out=[]
    for members in grouped.values():
        ex=members[0]; floor=johnson_query_floor(ex)
        attempts=[affine_geometry(ex,t) for t in range(floor-1,max(0,floor-9),-1)]
        good=[a for a in attempts if a["status"]=="certified"]
        chosen=good[-1] if good else None
        rows=[]
        for meta in members:
            old=raw_proof_bytes(meta,meta["queries"])
            row={"name":meta["name"],"batch_size":meta["batch_size"],
                 "raw_proof_bytes_current":old}
            if chosen and meta["queries"]>chosen["queries"]:
                new=raw_proof_bytes(meta,chosen["queries"])
                row.update(new_queries=chosen["queries"],raw_proof_bytes_new=new,
                           raw_proof_bytes_saved=old-new,
                           raw_bytes_per_query=(old-new)//(meta["queries"]-chosen["queries"]),
                           affine_extension_coefficients=meta["batch_size"]-1,
                           additional_extension_challenges_over_current_two=max(0,meta["batch_size"]-3))
            rows.append(row)
        out.append({"category":ex["category"],"n_bits":ex["n_bits"],
                    "n_bits_ext":ex["n_bits_ext"],
                    "rate":str(F(2**ex["n_bits"],2**ex["n_bits_ext"])),
                    "steps":ex["steps"],"pow_bits":ex["pow_bits"],
                    "current_queries":ex["queries"],
                    "continuous_finite_johnson_boundary_query_floor":floor,
                    "best_bounded_affine_candidate":chosen,
                    "first_below_johnson_attempt":attempts[0],
                    "bounded_query_scan":[floor-1,max(1,floor-8)],"members":rows})
    return sorted(out,key=lambda x:(x["category"],x["n_bits_ext"],x["pow_bits"],x["current_queries"]))


def powers_no_new_hook():
    """Pareto points using the shipped nested batching and query PoW hook."""
    by_name={m["name"]:m for m in ARTIFACT_METADATA}
    meta=by_name["vadcop_final_compressed"]
    requested=[(52,22)]
    out=[]
    for queries,pow_bits in requested:
        n,k=2**meta["n_bits_ext"],2**meta["n_bits"]
        A=exact_threshold(n,k,queries,pow_bits)
        batch=nested_powers_batch(n,k,A,meta["opening_group_sizes"])
        folds=[]; nn=n; kk=k
        for before,after in zip(meta["steps"],meta["steps"][1:]):
            factor=2**(before-after); nn//=factor; kk//=factor
            aa=(A*nn+n-1)//n
            fc=best_certificate(nn,kk,aa,factor-1,Q)
            folds.append({"n":nn,"k":kk,"A":aa,"powers_degree":factor-1,**fc})
        qe=F(A,n)**queries/2**pow_bits
        assert F(batch["error"]) <= F(1,2**TARGET_BITS)
        assert all(F(f["error"]) <= F(1,2**TARGET_BITS) for f in folds)
        assert qe <= F(1,2**TARGET_BITS)
        old=raw_proof_bytes(meta,meta["queries"]); new=raw_proof_bytes(meta,queries)
        out.append({"name":meta["name"],"old_queries":meta["queries"],"new_queries":queries,
                    "old_query_grinding_bits":meta["pow_bits"],"new_query_grinding_bits":pow_bits,
                    "expected_grinding_work_multiplier":2**(pow_bits-meta["pow_bits"]),
                    "A":A,"agreement":str(F(A,n)),"finite_johnson_strict":A*A<n*(k-1),
                    "continuous_finite_johnson_boundary_query_floor":johnson_query_floor({**meta,"pow_bits":pow_bits}),
                    "nested_batch":batch,"folds":folds,"query_error":str(qe),"query_bits":bits(qe),
                    "minimum_phase_bits":min([batch["bits"],bits(qe)]+[f["bits"] for f in folds]),
                    "raw_proof_bytes_old":old,"raw_proof_bytes_new":new,
                    "raw_proof_bytes_saved":old-new,
                                        "change_surface":"nQueries only" if pow_bits==meta["pow_bits"] else "nQueries and existing powBits threshold"})
    blockers=[]
    for name,attempt_queries in [("vadcop_final",53),("recursive2",71)]:
        m=by_name[name]; n,k=2**m["n_bits_ext"],2**m["n_bits"]
        A=math.isqrt(n*(k-1)-1)
        batch=nested_powers_batch(n,k,A,m["opening_group_sizes"])
        if F(batch["error"]) <= F(1,2**TARGET_BITS):
            continue
        blockers.append({"name":name,"attempt_queries":attempt_queries,
                         "maximum_strict_beyond_johnson_A":A,
                         "nested_batch_bits_at_maximum_A":batch["bits"],
                         "nested_batch":batch,
                         "reason":"initial nested-powers batching remains below 128 bits even at the largest strict beyond-Johnson agreement; query grinding cannot reduce this earlier error"})
    return {"feasible":out,"blocked":blockers}


def powers_geometry(meta, queries):
    """Check actual nested powers batching, shipped query PoW, and all folds."""
    n,k=2**meta["n_bits_ext"],2**meta["n_bits"]
    A=exact_threshold(n,k,queries,meta["pow_bits"])
    if A is None:
        return {"status":"no threshold above dimension","queries":queries,"minimum_phase_bits":0.0}
    batch=nested_powers_batch(n,k,A,meta["opening_group_sizes"])
    folds=[]; nn=n; kk=k
    for before,after in zip(meta["steps"],meta["steps"][1:]):
        factor=2**(before-after);nn//=factor;kk//=factor
        aa=(A*nn+n-1)//n
        fc=best_certificate(nn,kk,aa,factor-1,Q)
        folds.append({"n":nn,"k":kk,"A":aa,"powers_degree":factor-1,**(fc or {})})
    qe=F(A,n)**queries/2**meta["pow_bits"]
    levels=[batch["bits"],bits(qe)]+[f["bits"] for f in folds if "bits" in f]
    ok=all("bits" in f for f in folds) and min(levels)>=TARGET_BITS
    return {"status":"certified" if ok else "bounded certificate below target",
            "queries":queries,"A":A,"agreement":str(F(A,n)),
            "finite_johnson_strict":A*A<n*(k-1),"nested_batch":batch,
            "folds":folds,"query_error":str(qe),"query_bits":bits(qe),
            "minimum_phase_bits":min(levels)}


def powers_full_scope():
    """No-new-hook screen for every shipped base AIR and compressor."""
    out=[]
    for meta in ARTIFACT_METADATA:
        if meta["category"] not in {"base_air","compressor"}:
            continue
        floor=johnson_query_floor(meta)
        attempts=[powers_geometry(meta,floor-1)]
        if attempts[0]["status"]=="certified":
            for queries in range(floor-2,max(0,floor-9),-1):
                attempt=powers_geometry(meta,queries); attempts.append(attempt)
                if attempt["status"]!="certified":
                    break
        good=[a for a in attempts if a["status"]=="certified"]
        chosen=good[-1] if good else None
        old=raw_proof_bytes(meta,meta["queries"])
        row={"name":meta["name"],"category":meta["category"],
             "n_bits":meta["n_bits"],"n_bits_ext":meta["n_bits_ext"],
             "batch_size":meta["batch_size"],"opening_group_sizes":meta["opening_group_sizes"],
             "current_queries":meta["queries"],"query_grinding_bits":meta["pow_bits"],
             "continuous_finite_johnson_boundary_query_floor":floor,
             "first_below_johnson_attempt":attempts[0],"bounded_attempts":attempts,
             "best_bounded_candidate":chosen,"raw_proof_bytes_current":old}
        if chosen and meta["queries"]>chosen["queries"]:
            new=raw_proof_bytes(meta,chosen["queries"])
            row.update(raw_proof_bytes_new=new,raw_proof_bytes_saved=old-new,
                       raw_bytes_per_query=(old-new)//(meta["queries"]-chosen["queries"]))
        out.append(row)
    return out


def powers_alternatives():
    by_name={m["name"]:m for m in ARTIFACT_METADATA}; out=[]
    for name,t,fold_supports in POWERS_ALTERNATIVES:
        meta=by_name[name]; n,k=2**meta["n_bits_ext"],2**meta["n_bits"]
        A=exact_threshold(n,k,t,meta["pow_bits"])
        nested=nested_powers_batch(n,k,A,meta["opening_group_sizes"])
        raw=F(nested["error"])
        grinding=max(0,math.ceil(TARGET_BITS-bits(raw)))
        grounded=raw/2**grinding
        folds=[]; nn=n; kk=k
        for (before,after),support in zip(zip(meta["steps"],meta["steps"][1:]),fold_supports):
            factor=2**(before-after); nn//=factor; kk//=factor
            aa=(A*nn+n-1)//n
            fc=certificate(nn,kk,aa,*support,factor-1); fe=F(fc["exceptional_count_upper"],Q)
            assert bits(fe)>=TARGET_BITS
            folds.append({"n":nn,"k":kk,"A":aa,"support":list(support),
                          "error":str(fe),"bits":bits(fe),"certificate":compact(fc)})
        qe=F(A,n)**t/2**meta["pow_bits"]
        assert bits(qe)>=TARGET_BITS and bits(grounded)>=TARGET_BITS
        old=raw_proof_bytes(meta,meta["queries"]); before_nonce=raw_proof_bytes(meta,t)
        new=before_nonce+(8 if grinding else 0)
        out.append({"name":name,"n_bits":meta["n_bits"],"n_bits_ext":meta["n_bits_ext"],
                    "batch_size":meta["batch_size"],"batch_degree":meta["batch_size"]-1,
                    "old_queries":meta["queries"],"new_queries":t,
                    "continuous_finite_johnson_boundary_query_floor":johnson_query_floor(meta),
                    "below_johnson_floor_by_queries":johnson_query_floor(meta)-t,
                    "A":A,"agreement":str(F(A,n)),"finite_johnson_strict":A*A<n*(k-1),
                    "nested_batch":nested,"batch_raw_error":str(raw),
                    "batch_raw_bits":bits(raw),"extra_batching_grinding_bits":grinding,
                    "batch_error_after_grinding":str(grounded),
                    "batch_bits_after_grinding":bits(grounded),
                    "folds":folds,"query_error":str(qe),"query_bits":bits(qe),
                    "raw_proof_bytes_old":old,
                    "raw_proof_bytes_new_before_new_nonce":before_nonce,
                    "illustrative_new_batching_nonce_bytes":8 if grinding else 0,
                    "raw_proof_bytes_new":new,"raw_proof_bytes_saved":old-new})
    return out


def markdown(data):
    candidate_by_name={}; group_rows=[]
    for g in data["affine_scope_groups"]:
        c=g["best_bounded_affine_candidate"]
        names=", ".join(f'`{m["name"]}`' for m in g["members"])
        widths=",".join(str(m["batch_size"]) for m in g["members"])
        if c:
            saves=[m.get("raw_proof_bytes_saved",0) for m in g["members"]]
            result=f'{g["current_queries"]}->{c["queries"]}; {min(saves)}'
            if min(saves)!=max(saves): result+=f'..{max(saves)}'
            result+=' B'
            status=f'certified ({c["minimum_phase_bits"]:.3f} bits min)'
            for m in g["members"]:
                if "new_queries" in m: candidate_by_name[m["name"]]=m
        else:
            a=g["first_below_johnson_attempt"]
            result="none in bounded scan"
            status=f'first below-Johnson target: {a["minimum_phase_bits"]:.3f} bits'
        group_rows.append(f'| {names} | 2^{g["n_bits_ext"]} | 2^{g["n_bits"]} | {g["pow_bits"]} | {widths} | {result} | {status} |')
    inv_rows=[]
    for m in data["artifact_inventory"]:
        cand=candidate_by_name.get(m["name"])
        result="—" if not cand else f'{m["queries"]}->{cand["new_queries"]}; {cand["raw_proof_bytes_saved"]} B'
        inv_rows.append(f'| `{m["name"]}` | {m["category"]} | 2^{m["n_bits_ext"]} | 2^{m["n_bits"]} | {m["queries"]} | {m["pow_bits"]} | {m["batch_size"]} | `{m["stage_widths"]}` | {result} |')
    pow_rows=[f'| `{p["name"]}` | {p["old_queries"]}->{p["new_queries"]} | {p["extra_batching_grinding_bits"]} | {p["raw_proof_bytes_saved"]} |' for p in data["powers_plus_batch_grinding_alternatives"]]
    by_category={category:[m for g in data["affine_scope_groups"] if g["category"]==category for m in g["members"] if "new_queries" in m] for category in ("base_air","compressor")}
    nohook_rows=[]
    for c in data["powers_preserving_existing_hook"]["feasible"]:
        nohook_rows.append(
            f'| `{c["name"]}` | {c["A"]} | {c["nested_batch"]["bits"]:.6f} '
            f'| {min(f["bits"] for f in c["folds"]):.6f} | {c["query_bits"]:.6f} '
            f'| {c["old_queries"]}->{c["new_queries"]} | {c["old_query_grinding_bits"]}->{c["new_query_grinding_bits"]} '
            f'| {c["expected_grinding_work_multiplier"]}x | {c["raw_proof_bytes_saved"]} |')
    blocker_rows=[f'| `{b["name"]}` | {b["attempt_queries"]} | {b["maximum_strict_beyond_johnson_A"]} | {b["nested_batch_bits_at_maximum_A"]:.6f} |' for b in data["powers_preserving_existing_hook"]["blocked"]]
    full_powers=data["powers_preserving_full_base_compressor_scope"]
    powers_scope_rows=[]
    for category,label in [("base_air","Base AIRs"),("compressor","Compressors")]:
        rows=[r for r in full_powers if r["category"]==category]
        good=sum(r["best_bounded_candidate"] is not None for r in rows)
        vals=[r["first_below_johnson_attempt"]["minimum_phase_bits"] for r in rows]
        powers_scope_rows.append(f'| {label} | {len(rows)} | {good} | {min(vals):.3f}..{max(vals):.3f} |')
    representative_names=["Poseidon","Keccakf","Sha256f","ArithEq","Poseidon/compressor","Sha256f/compressor","Keccakf/compressor"]
    powers_rep_rows=[]
    for name in representative_names:
        row=next(r for r in full_powers if r["name"]==name)
        a=row["first_below_johnson_attempt"]
        powers_rep_rows.append(f'| `{name}` | {row["batch_size"]} | {row["continuous_finite_johnson_boundary_query_floor"]}->{a["queries"]} | {a["nested_batch"]["bits"]:.6f} | {min(f["bits"] for f in a["folds"]):.6f} | {a["query_bits"]:.6f} |')
    primary_rows=[]
    for name in ("vadcop_final_compressed","vadcop_final","recursive2"):
        g=next(g for g in data["affine_scope_groups"] if any(m["name"]==name for m in g["members"]))
        c=g["best_bounded_affine_candidate"]
        m=next(m for m in g["members"] if m["name"]==name)
        min_fold=min(f["bits"] for f in c["folds"])
        support=tuple(c["initial_affine"]["support"])
        primary_rows.append(
            f'| `{name}` | {c["A"]} | `{support}` | {c["initial_affine"]["bits"]:.6f} '
            f'| {min_fold:.6f} | {c["query_bits"]:.6f} | '
            f'{g["continuous_finite_johnson_boundary_query_floor"]}->{c["queries"]} | '
            f'{m["raw_proof_bytes_current"]}->{m["raw_proof_bytes_new"]} ({m["raw_proof_bytes_saved"]}) |')
    return f'''# ZisK v1.2 full-configuration scope audit (2026-09-07)

## Least-invasive result: keep the shipped batching transcript

This audit covers every `starkinfo.json` in the shipped ZisK `v1.2.0-alpha` proving-key archive: 42 base AIRs, 11 compressor AIRs, `recursive2`, and both final STARKs. The largest actual batching widths are 5,408 (`Keccakf`) and 1,266 (`Sha256f`); the aggregation layers use width 135.

The parameter-only replacement keeps both existing powers challenges and the query-grinding nonce. For `vadcop_final_compressed`, changing `nQueries` from 54 to 52 saves **7,840 raw verifier-layout bytes**, with the original 22 grinding bits. It adds no transcript round or proof field. Setup and generated-verifier dimensions must reflect the new query count. The certificate uses the separate derivative-degree image bound.

The emitted FRI polynomial does not flatten all 135 terms into one challenge. Source inspection shows five opening-point groups of sizes `(2,3,104,25,1)`, powers batching inside each group with `std_vf2`, and powers batching of the five results with independent `std_vf1`. The audit reduction packages the inner groups as interleaving rows, pads them to degree 103, and applies one shared-challenge curve-MCA bound. It then conditions on the inner challenge and applies the outer degree-4 bound. This uses the same ideal independent-uniform challenge model as Proofman's security calculator; all commitments and claimed evaluations are fixed before both challenges, and the singleton has no inner batching failure. The resulting charge is E_103+E_4; no flattening to a single degree-134 challenge or change of coefficients is used. This sequential reduction is audit reasoning, not a bound stated in Proofman's source.

| Phase | A | Nested batch bits | Min fold bits | Query bits | Queries | Query PoW | Expected PoW work | Raw bytes saved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(nohook_rows)}

The 52-query certificate lies below the finite-Johnson query-only floor of 53 with the same 22 grinding bits. This is a beyond-Johnson gain even when using the finite-length boundary. The following table records aggregation cases, if any, whose earlier nested-powers term still fails at the largest strict beyond-Johnson agreement in this bounded support bank.

| Phase | Attempted queries | Maximum strict A | Nested batch bits |
|---|---:|---:|---:|
{chr(10).join(blocker_rows)}

## Full base and compressor screen with shipped powers

The same check is run on all 53 released base/compressor configurations using their exact opening-point grouping, folding schedule, field, dimensions, and unchanged grinding. The tables below report the recomputed outcomes with the refined bound. A failed bounded support search is not an impossibility result.

| Kind | Tested | Certified | First-target minimum-bit range |
|---|---:|---:|---:|
{chr(10).join(powers_scope_rows)}

| Representative | Width | Johnson boundary->attempt q | Nested batch bits | Min fold bits | Query bits |
|---|---:|---:|---:|---:|---:|
{chr(10).join(powers_rep_rows)}

The JSON contains all 53 exact attempts, including every opening-group degree and component certificate. Failure is bounded-search evidence for this support bank, not an impossibility result.

## Independent-coefficient alternative

Replacing the nested powers batching with independently derived affine coefficients gives the larger numerical scope below. This is a protocol alternative, not the preferred minimal change: it needs `batch_size-1` extension-field coefficients and may materially enlarge recursive verifiers. With exact finite affine-MCA and unchanged powers folds, compressed final reaches 52 queries, final reaches 52, and `recursive2` reaches 70.

The Johnson column evaluates the query term exactly at the continuous finite-Johnson agreement `sqrt((k-1)/n)` and shipped query grinding. It is a necessary query-only floor after discarding every algebraic error, rather than a complete Johnson-regime soundness analysis.

| Phase | A | Initial support | Affine bits | Min fold bits | Query bits | Johnson boundary->new q | Raw bytes old->new (saved) |
|---|---:|---|---:|---:|---:|---:|---:|
{chr(10).join(primary_rows)}

### Exact affine-coefficient scope by shipped geometry

The scan checks at most eight query counts below the query-only floor at the continuous finite-Johnson boundary, using the fixed support bank in the reproducer. “None” is a bounded certificate result, not an impossibility claim. Every phase is checked separately at 128 bits, matching Proofman's implementation convention.

| Shipped configurations | n | k | Query PoW | Widths | Best bounded query/byte result | Exact status |
|---|---:|---:|---:|---|---|---|
{chr(10).join(group_rows)}

Large half-rate base AIRs are the material boundary in this scan: at the first theorem-specific target, the best tested affine initial-phase certificates have about 126.5 bits for `n=2^22` and 124.5 bits for `n=2^23`. This is a bounded-search obstruction, not an impossibility result. It is independent of batching width for the affine construction. The 2^22-domain Keccak compressor remains feasible because its rate is 1/4; its optimized support `(9,3,17)` gives 128.658 bits at 107 queries.

Numerical candidates cover {len(by_category["base_air"])} of 42 base AIR configurations and all {len(by_category["compressor"])} compressors. Summing one proof of each affected configuration gives {sum(m["raw_proof_bytes_saved"] for m in by_category["base_air"]):,} raw bytes across the base rows and {sum(m["raw_proof_bytes_saved"] for m in by_category["compressor"]):,} across compressors. These are inventory totals, not end-to-end VM-proof savings: component multiplicities and recursive wrapping determine the realized total.

The affine vector needs `batch_size-1` extension-field coefficients. That is 134 coefficients for the three aggregation rows, 1,265 for SHA-256f, and 5,407 for Keccak-f, replacing the current two extension challenges. They add no proof bytes, but the transcript permutations and generated recursive-circuit constraints may be substantial; this audit does not estimate proving time or circuit size.

## Current-powers alternative

Keeping powers batching and adding a nonce before its challenge also gives theorem-specific recursion/final reductions. Proofman's calculator computes batching grinding, but emitted `starkinfo` drops it and the proof contains only the later query nonce. Each row therefore needs a new pre-batching nonce, native/recursive verification logic, and regeneration. Byte savings subtract one illustrative 8-byte `u64` nonce.

| Phase | Queries | Extra batching bits | Net raw bytes saved |
|---|---:|---:|---:|
{chr(10).join(pow_rows)}

The independent-coefficient route avoids that nonce and reaches 70 rather than 71 queries for `recursive2` in this bounded search.

## Complete shipped metadata inventory

`GL`, `hashCommits=true`, `merkleTreeCustom=true`, JBR, and the 128-bit setup target are uniform. Stage widths are the three committed stage-tree widths; powers width is exact `evMap` length.

| Name | Kind | n | k | Current q | PoW | Powers width | Stage widths | Affine result |
|---|---|---:|---:|---:|---:|---:|---|---|
{chr(10).join(inv_rows)}

## Source, artifact, and encoding evidence

The repository heads observed on {SOURCE["audit_date"]} were ZisK [`{SOURCE["zisk_main_observed_commit"]}`](https://github.com/0xPolygonHermez/zisk/tree/{SOURCE["zisk_main_observed_commit"]}) and Proofman [`{SOURCE["proofman_main_observed_commit"]}`](https://github.com/0xPolygonHermez/pil2-proofman/tree/{SOURCE["proofman_main_observed_commit"]}). The public setup is tied to ZisK [`v1.2.0-alpha`](https://github.com/0xPolygonHermez/zisk/tree/{SOURCE["zisk_commit"]}) at `{SOURCE["zisk_commit"]}`, which pins Proofman [`v1.2.0-alpha`](https://github.com/0xPolygonHermez/pil2-proofman/tree/{SOURCE["proofman_commit"]}) at `{SOURCE["proofman_commit"]}`. ZisK's [setup builder](https://github.com/0xPolygonHermez/zisk/blob/{SOURCE["zisk_commit"]}/tools/test-env/setup_build.sh) defaults to Poseidon1; its [upload script](https://github.com/0xPolygonHermez/zisk/blob/{SOURCE["zisk_commit"]}/tools/test-env/upload_setup.sh) publishes the archive.

The public [proving-key archive]({SOURCE["artifact_url"]}) is {SOURCE["artifact_size_bytes"]} bytes. Bucket [metadata]({SOURCE["artifact_metadata_url"]}) records update `{SOURCE["artifact_updated"]}`, ETag `{SOURCE["artifact_etag"]}`, and CRC32C `{SOURCE["artifact_crc32c_base64"]}`. The [MD5 sidecar]({SOURCE["artifact_md5_url"]}) gives `{SOURCE["artifact_md5"]}` and the [setup-input-hash sidecar]({SOURCE["artifact_hash_url"]}) gives `{SOURCE["setup_input_hash"]}`. The complete gzip stream was read sequentially while retaining only 2.7 MB of metadata; no key payload was stored.

Proofman's [base setup](https://github.com/0xPolygonHermez/pil2-proofman/blob/{SOURCE["proofman_commit"]}/setup/pil2-stark/src/commands/setup.rs) selects powers batching, width `evMap.len()`, Goldilocks cubic extension, JBR, and 128 target bits. [Recursive setup](https://github.com/0xPolygonHermez/pil2-proofman/blob/{SOURCE["proofman_commit"]}/setup/pil2-stark/src/proving_key/recursive.rs) builds recursive1/compressor layers and `recursive2`; [final](https://github.com/0xPolygonHermez/pil2-proofman/blob/{SOURCE["proofman_commit"]}/setup/pil2-stark/src/proving_key/final_setup.rs) and [compressed-final](https://github.com/0xPolygonHermez/pil2-proofman/blob/{SOURCE["proofman_commit"]}/setup/pil2-stark/src/proving_key/compressed_final.rs) setup fix the last schedules.

The generated [FRI polynomial](https://github.com/0xPolygonHermez/pil2-proofman/blob/{SOURCE["proofman_commit"]}/setup/pil2-stark/src/pil/fri_poly.rs) uses `std_vf1/std_vf2` powers after evaluations are fixed. The native [proof generator](https://github.com/0xPolygonHermez/pil2-proofman/blob/{SOURCE["proofman_commit"]}/pil2-stark/src/starkpil/gen_proof.hpp) already serializes one nonce and applies `powBits` when deriving query positions, so 22-to-23 changes an existing check rather than adding a protocol field. The security API models [affine batching](https://github.com/0xPolygonHermez/pil2-proofman/blob/{SOURCE["proofman_commit"]}/setup/pil2-stark/src/types/security/pcs/types.rs), but the native prover/verifier does not implement the vector. `nQueries` and `powBits` are compiled into native and Circom verifier dimensions.

Proofman's [raw proof-size function](https://github.com/0xPolygonHermez/pil2-proofman/blob/{SOURCE["proofman_commit"]}/verifier/src/verifier.rs) counts the exact `u64` buffer consumed by the verifier. The final proof is bincode over that `Vec<u64>` plus public values, a compression flag, and hash string, so deltas are exact for the raw layout; file deltas can vary with bincode lengths and values. The artifact records `verificationHashType=GL`; Poseidon1 is the build-script default rather than a literal `starkinfo` field.

Reproduce with `python3 scripts/zisk_scope_audit.py`. The JSON retains all exact finite certificates and artifact rows.
'''


def main():
    groups=affine_groups(); no_hook=powers_no_new_hook()
    full_powers=powers_full_scope(); powers=powers_alternatives()
    inventory=[]
    for meta in ARTIFACT_METADATA:
        row=dict(meta); row["raw_proof_bytes_current"]=raw_proof_bytes(meta,meta["queries"])
        inventory.append(row)
    data={"scope":"all 56 shipped ZisK v1.2 starkinfo configurations",
          "source":SOURCE,
          "security_convention":"each batching, fold, and query phase individually at least 128 bits; no union-bound claim",
          "field":{"base":"Goldilocks","characteristic":P,"extension_degree":3,"cardinality":Q},
          "hash":{"artifact_verification_hash_type":"GL","hash_commits":True,
                  "merkle_tree_custom":True,"release_builder_default":"Poseidon1"},
          "artifact_inventory":inventory,"affine_scope_groups":groups,
          "powers_batching_audit":{
              "source_evidence":"std_vf2 powers within five evMap opening-point groups, then independent std_vf1 powers across groups; both sampled after evaluation absorption",
              "opening_group_sizes":NESTED_OPENING_GROUP_SIZES,
              "audit_reduction":"one interleaved inner curve-MCA bound at the maximum group degree, then conditional outer curve-MCA; ideal independent-uniform Fiat-Shamir challenges",
              "source_calculator_abstraction":"Powers with batch_size=evMap.len(); its width-minus-one degree is numerically compatible because positive nested degrees sum to 134 for aggregation",
              "not_source_claim":"Proofman does not state the sequential nested reduction",
          },
          "powers_preserving_existing_hook":no_hook,
          "powers_preserving_full_base_compressor_scope":full_powers,
          "powers_plus_batch_grinding_alternatives":powers,
          "integration":{"affine_coefficients":"Fiat-Shamir-derived after all batched words are fixed; no proof payload",
                         "affine_requires_protocol_code":True,"requires_setup_regeneration":True,
                         "requires_native_verifier_regeneration":True,
                         "requires_recursive_circuit_regeneration":True,
                         "requires_key_republication":True,
                         "snark_wrapper_size_effect":"none: fixed outer BN254 SNARK encoding"}}
    out=Path(__file__).parent/"examples"
    (out/"zisk-full-scope-2026-09-07.json").write_text(json.dumps(data,indent=2)+"\n")
    (out/"zisk-full-scope-2026-09-07.md").write_text(markdown(data))
    certified=sum(1 for g in groups for m in g["members"] if "new_queries" in m)
    print(f"inventoried {len(inventory)} configurations; affine alternatives for {certified}")
    for c in no_hook["feasible"]:
        print("powers/no-new-hook",c["name"],f'{c["old_queries"]}->{c["new_queries"]}',
              f'pow {c["old_query_grinding_bits"]}->{c["new_query_grinding_bits"]}',
              c["raw_proof_bytes_saved"],"bytes")
    full_good=[r for r in full_powers if r["best_bounded_candidate"]]
    print(f"powers/no-new-hook base+compressor candidates {len(full_good)}/{len(full_powers)}")


if __name__=="__main__":
    main()
