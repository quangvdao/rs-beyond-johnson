use std::env;

use zisk_common::{Proof, ProofBody, VadcopKind};

const SOURCE_QUERIES: usize = 54;
const TARGET_QUERIES: usize = 51;

fn copy_fixed(source: &[u64], cursor: &mut usize, output: &mut Vec<u64>, words: usize) {
    output.extend_from_slice(&source[*cursor..*cursor + words]);
    *cursor += words;
}

fn copy_query_prefix(
    source: &[u64],
    cursor: &mut usize,
    output: &mut Vec<u64>,
    words_per_query: usize,
) {
    output.extend_from_slice(&source[*cursor..*cursor + TARGET_QUERIES * words_per_query]);
    *cursor += SOURCE_QUERIES * words_per_query;
}

fn truncate_query_arrays(source: &[u64]) -> Vec<u64> {
    let mut cursor = 0;
    let mut output = Vec::with_capacity(source.len() - (SOURCE_QUERIES - TARGET_QUERIES) * 490);

    // Three stage roots and 135 cubic-extension evaluations.
    copy_fixed(source, &mut cursor, &mut output, 3 * 4 + 135 * 3);

    // Fixed-polynomial values and paths, followed by their shared partial-tree table.
    copy_query_prefix(source, &mut cursor, &mut output, 45);
    copy_query_prefix(source, &mut cursor, &mut output, (19 - 6) * 4);
    copy_fixed(source, &mut cursor, &mut output, (1 << 6) * 4);

    // Three committed stages: query values, paths, then shared partial-tree table.
    for width in [48, 12, 21] {
        copy_query_prefix(source, &mut cursor, &mut output, width);
        copy_query_prefix(source, &mut cursor, &mut output, (19 - 6) * 4);
        copy_fixed(source, &mut cursor, &mut output, (1 << 6) * 4);
    }

    // FRI roots.
    copy_fixed(source, &mut cursor, &mut output, 3 * 4);

    // Three FRI query layers: folded values, paths, then shared partial-tree table.
    for next_bits in [16, 13, 10] {
        copy_query_prefix(source, &mut cursor, &mut output, (1 << 3) * 3);
        copy_query_prefix(source, &mut cursor, &mut output, (next_bits - 6) * 4);
        copy_fixed(source, &mut cursor, &mut output, (1 << 6) * 4);
    }

    // Final cubic-extension polynomial and proof-of-work nonce.
    copy_fixed(source, &mut cursor, &mut output, (1 << 10) * 3 + 1);

    assert_eq!(cursor, source.len(), "unexpected source proof layout");
    assert_eq!(source.len() - output.len(), (SOURCE_QUERIES - TARGET_QUERIES) * 490);
    output
}

fn main() {
    let mut args = env::args_os().skip(1);
    let input = args.next().expect("usage: truncate_fri_queries INPUT OUTPUT");
    let output = args.next().expect("usage: truncate_fri_queries INPUT OUTPUT");
    assert!(args.next().is_none(), "usage: truncate_fri_queries INPUT OUTPUT");

    let mut proof = Proof::load(&input).expect("load input proof");
    match &mut proof.body {
        ProofBody::Vadcop { proof: words, kind, hash, publics_full, zisk_vk } => {
            assert_eq!(*kind, VadcopKind::Minimal, "input is not a compressed final proof");
            assert_eq!(hash, "Poseidon1", "input is not a Poseidon1 proof");
            assert_eq!(publics_full.len(), 68, "unexpected public-vector length");
            assert_eq!(zisk_vk.len(), 4, "unexpected ZisK verification-key length");
            assert_eq!(words.len() * 8, 254_032, "unexpected Q54 raw proof size");
            println!(
                "input metadata: kind={kind:?}, hash={hash}, publics={}, zisk_vk_words={}, raw_proof_bytes={}",
                publics_full.len(),
                zisk_vk.len(),
                words.len() * 8
            );
            *words = truncate_query_arrays(words);
            assert_eq!(words.len() * 8, 242_272, "unexpected Q51 raw proof size");
            println!("output metadata: kind={kind:?}, hash={hash}, raw_proof_bytes={}", words.len() * 8);
        }
        ProofBody::Plonk { .. } => panic!("input is a Plonk proof"),
    }

    proof.verify().expect("matching Q51 verifier rejected converted proof");
    proof.save(&output).expect("save output proof");
    let saved = Proof::load(&output).expect("reload saved output proof");
    saved.verify().expect("matching Q51 verifier rejected reloaded saved proof");
    println!("Q51 Minimal Poseidon1 proof verified, saved, reloaded, and verified again");
}
