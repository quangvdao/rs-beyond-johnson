//! Explain the byte-level A/B delta between two complete rkyv VM proofs.

use std::{env, fs, process::ExitCode};

use prover::{FIXED_TABLE_COUNT, ProtocolProfile, VmProof};

fn read_proof(path: &str) -> Result<(Vec<u8>, VmProof), String> {
    let bytes = fs::read(path).map_err(|e| format!("failed to read {path}: {e}"))?;
    let proof = rkyv::from_bytes::<VmProof, rkyv::rancor::Error>(&bytes)
        .map_err(|e| format!("failed to deserialize {path}: {e}"))?;
    Ok((bytes, proof))
}

fn archived_len(proof: &VmProof) -> Result<usize, String> {
    rkyv::to_bytes::<rkyv::rancor::Error>(proof)
        .map(|bytes| bytes.len())
        .map_err(|e| format!("failed to serialize counterfactual proof: {e}"))
}

fn isolated_cpu_allocation(proof: &VmProof) -> Result<(usize, usize, usize), String> {
    let cpu = proof
        .proof
        .proofs
        .get(FIXED_TABLE_COUNT)
        .ok_or_else(|| String::from("proof has no CPU sub-proof"))?
        .clone();
    let mut cpu_only = proof.clone();
    cpu_only.proof.proofs = vec![cpu];
    let cpu_only_len = archived_len(&cpu_only)?;
    cpu_only.proof.proofs.clear();
    let empty_len = archived_len(&cpu_only)?;
    Ok((cpu_only_len, empty_len, cpu_only_len - empty_len))
}

fn run() -> Result<(), String> {
    let mut args = env::args().skip(1);
    let control_path = args
        .next()
        .ok_or_else(|| String::from("usage: profile_size_breakdown CONTROL EXPERIMENTAL"))?;
    let experimental_path = args
        .next()
        .ok_or_else(|| String::from("usage: profile_size_breakdown CONTROL EXPERIMENTAL"))?;
    if args.next().is_some() {
        return Err(String::from(
            "usage: profile_size_breakdown CONTROL EXPERIMENTAL",
        ));
    }

    let (control_bytes, control) = read_proof(&control_path)?;
    let (experimental_bytes, experimental) = read_proof(&experimental_path)?;
    if control.profile != ProtocolProfile::Control
        || experimental.profile != ProtocolProfile::CpuRsAnchorsV1
    {
        return Err(String::from(
            "expected a control proof followed by a cpu-rs-anchors-v1 proof",
        ));
    }

    let experimental_cpu = experimental
        .proof
        .proofs
        .get(FIXED_TABLE_COUNT)
        .ok_or_else(|| String::from("experimental proof has no CPU sub-proof"))?;
    let control_cpu_original = control
        .proof
        .proofs
        .get(FIXED_TABLE_COUNT)
        .ok_or_else(|| String::from("control proof has no CPU sub-proof"))?;
    let control_cpu_bytes = rkyv::to_bytes::<rkyv::rancor::Error>(control_cpu_original)
        .map_err(|e| format!("failed to serialize control CPU sub-proof: {e}"))?;
    let experimental_cpu_bytes = rkyv::to_bytes::<rkyv::rancor::Error>(experimental_cpu)
        .map_err(|e| format!("failed to serialize experimental CPU sub-proof: {e}"))?;
    let (control_cpu_only_vm, control_empty_vm, control_cpu_marginal) =
        isolated_cpu_allocation(&control)?;
    let (experimental_cpu_only_vm, experimental_empty_vm, experimental_cpu_marginal) =
        isolated_cpu_allocation(&experimental)?;
    let mut fewer_queries = control.clone();
    let control_cpu = fewer_queries
        .proof
        .proofs
        .get_mut(FIXED_TABLE_COUNT)
        .ok_or_else(|| String::from("control proof has no CPU sub-proof"))?;
    control_cpu
        .query_list
        .truncate(ProtocolProfile::CPU_RS_ANCHORS_V1_CPU_QUERIES);
    control_cpu
        .deep_poly_openings
        .truncate(ProtocolProfile::CPU_RS_ANCHORS_V1_CPU_QUERIES);
    let fewer_queries_len = archived_len(&fewer_queries)?;

    let mut hybrid = fewer_queries;
    hybrid.profile = ProtocolProfile::CpuRsAnchorsV1;
    hybrid.proof.proofs[FIXED_TABLE_COUNT].early_main_trace_evaluations =
        experimental_cpu.early_main_trace_evaluations.clone();
    let hybrid_len = archived_len(&hybrid)?;

    println!("control_bytes={}", control_bytes.len());
    println!("experimental_bytes={}", experimental_bytes.len());
    println!("control_subproofs={}", control.proof.proofs.len());
    println!("experimental_subproofs={}", experimental.proof.proofs.len());
    println!("control_cpu_standalone_bytes={}", control_cpu_bytes.len());
    println!(
        "experimental_cpu_standalone_bytes={}",
        experimental_cpu_bytes.len()
    );
    println!(
        "cpu_standalone_savings={}",
        control_cpu_bytes.len() - experimental_cpu_bytes.len()
    );
    println!("control_cpu_only_vm_bytes={control_cpu_only_vm}");
    println!("control_empty_vm_bytes={control_empty_vm}");
    println!("control_cpu_marginal_bytes={control_cpu_marginal}");
    println!("experimental_cpu_only_vm_bytes={experimental_cpu_only_vm}");
    println!("experimental_empty_vm_bytes={experimental_empty_vm}");
    println!("experimental_cpu_marginal_bytes={experimental_cpu_marginal}");
    for (name, cpu) in [
        ("control", control_cpu_original),
        ("experimental", experimental_cpu),
    ] {
        let first_deep = cpu
            .deep_poly_openings
            .first()
            .ok_or_else(|| format!("{name} CPU proof has no DEEP opening"))?;
        let early_widths: Vec<_> = cpu
            .early_main_trace_evaluations
            .iter()
            .map(Vec::len)
            .collect();
        println!(
            "{name}_cpu_shape=trace:{} main_root:1 aux_root:{} precomputed_root:{} early:{:?} ood:{}x{} next_ood:{}x{} composition_root:1 composition_parts:{} fri_roots:{} final_coeffs:{} queries:{} deep:{} deep_main_width:{} deep_aux_width:{} deep_composition_width:{} nonce:{} bus_inputs:{}",
            cpu.trace_length,
            usize::from(cpu.lde_trace_aux_merkle_root.is_some()),
            usize::from(cpu.lde_trace_precomputed_merkle_root.is_some()),
            early_widths,
            cpu.trace_ood_evaluations.width,
            cpu.trace_ood_evaluations.height,
            cpu.trace_ood_next_evaluations.width,
            cpu.trace_ood_next_evaluations.height,
            cpu.composition_poly_parts_ood_evaluation.len(),
            cpu.fri_layers_merkle_roots.len(),
            cpu.fri_final_poly_coeffs.len(),
            cpu.query_list.len(),
            cpu.deep_poly_openings.len(),
            first_deep.main_trace_polys.evaluations.len(),
            first_deep
                .aux_trace_polys
                .as_ref()
                .map_or(0, |opening| opening.evaluations.len()),
            first_deep.composition_poly.evaluations.len(),
            usize::from(cpu.nonce.is_some()),
            usize::from(cpu.bus_public_inputs.is_some()),
        );
    }
    println!(
        "gross_11_query_savings={}",
        control_bytes.len() - fewer_queries_len
    );
    println!("rkyv_early_claim_cost={}", hybrid_len - fewer_queries_len);
    println!("counterfactual_hybrid_bytes={hybrid_len}");
    println!(
        "net_savings={}",
        control_bytes.len() - experimental_bytes.len()
    );
    if hybrid_len != experimental_bytes.len() {
        return Err(format!(
            "shape-only counterfactual length {hybrid_len} did not match experimental length {}",
            experimental_bytes.len()
        ));
    }
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("{error}");
            ExitCode::FAILURE
        }
    }
}
