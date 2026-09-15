"""Exact local WHIR budgets with the tensor-fold bridge; exploratory search is separate.
Requires the manuscript finite-certificate engine. Models ideal uniform field challenges;
actual Goldilocks challenge codec has negligible statistical distance (see protocol audit).
No claim of global query optimality or complete Fiat-Shamir security reduction.
"""
import argparse
import sys,json
from pathlib import Path
from fractions import Fraction as F
from math import log2
from tune_first_order_mca import (
    certificate,
    LEGACY_TAYLOR_DEGREE_MODEL,
    TIGHT_TAYLOR_DEGREE_MODEL,
)

def bits(error):
    return log2(error.denominator)-log2(error.numerator)

def expected_auth_hashes(n,t):
    assert n>0 and n&(n-1)==0 and t>0
    total=F(0);size=1
    while size<n:
        total+=(n//size)*(F(n-size,n)**t-F(n-2*size,n)**t)
        size*=2
    return total
def expected_stride_auth_hashes(n,t,stride):
    """Uniform queries into indices stride*i of a binary n-leaf tree."""
    assert n>0 and n&(n-1)==0 and stride>0 and stride&(stride-1)==0
    assert stride<=n and t>0
    m=n//stride
    expected_distinct=m*(1-F(m-1,m)**t)
    return expected_auth_hashes(m,t)+(stride.bit_length()-1)*expected_distinct

Q=(2**64-2**32+1)**3
TARGET=F(1,2**128)
THRESHOLDS=[18786624067678312,55983906202016720,77984534171686272,254057177368005792]
WITNESS=[(4096,1024,127,109,1933,(96,42,174),2),(2048,128,62,55,453,(38,23,133),1),(1024,16,41,37,107,(16,16,114),1),(512,2,31,26,19,(12,12,227),1)]
BLIND=[(32,8,127,99,14,(64,28,116),1)]

def certified_schedule(spec):
 rows=[]
 for i,(n,k,old,t,A,support,u) in enumerate(spec):
  c=certificate(
      n,k,A,*support,
      taylor_degree_model=TIGHT_TAYLOR_DEGREE_MODEL)
  assert c is not None and A*A<n*(k-1)
  assert 2**64-2**32+1 > c['characteristic_strictly_greater_than']
  E,L=c['exceptional_count_upper'],c['list_size_upper']
  errors={'tensor_fold_and_identity':F(3*E+2*L,Q),'out_of_domain':F(L*(L-1),2)*F(8*k-1,Q)**u,'query_after_original_grinding':F(THRESHOLDS[i]+1,2**64)*F(A,n)**t}
  if rows:errors['incoming_combination']=F(2*(rows[-1]['queries']+u)*L,Q)
  assert all(x<=TARGET for x in errors.values())
  rows.append({'n':n,'k':k,'baseline_queries':old,'queries':t,'agreement_numerator':A,'ood':u,'pow_threshold':THRESHOLDS[i],'certificate':c,'errors':{name:str(x) for name,x in errors.items()},'bits':{name:bits(x) for name,x in errors.items()}})
 return rows

def saving(spec,element_bytes):
 return sum((old-t)*8*(element_bytes if i==0 else 24)+32*(expected_auth_hashes(n,old)-expected_auth_hashes(n,t))-(u-1)*24 for i,(n,k,old,t,A,support,u) in enumerate(spec))

def check_goldilocks():
    witness=certified_schedule(WITNESS);blind=certified_schedule(BLIND)
    # The blinding tail retains n=16,k=1,62 queries, one OOD and Johnson list160.
    blind_tail=F(2*(99+1)*160,Q)
    assert blind_tail<=TARGET
    assert F(THRESHOLDS[1]+1,2**64)*F(21,80)**62<=TARGET
    assert F(2,Q)<=TARGET
    blind_tail_ood=F(160*159,2)*F(7,Q)
    assert blind_tail_ood<=TARGET
    result={'source_commit':'6481f961fc78615811b9cbaa9aa2380f1f6703c9','whir_commit':'8804e80e8e890d01bb585f2bd5e5b564ac0fd80d','scope':__doc__,'field_cardinality':Q,'witness':witness,'blinding':blind,'blind_tail_incoming_error':str(blind_tail),'blind_tail_ood_error':str(blind_tail_ood),'expected_raw_saving':{},'baseline_schedule':[127,62,41,31],'revised_schedule':[109,55,37,26]}
    for b in (24,):
     total=2*saving(WITNESS,b)+saving(BLIND,24)
     result['expected_raw_saving'][str(b)]={'exact':str(total),'bytes':float(total)}
    # Measured canonical base-leaf size sweeps. Later witness codes stay unchanged.
    base_rows=[]
    for n,k,t,A,support in ((65536,16384,111,31354,(32,14,58)),(131072,32768,112,63123,(24,10,43)),(262144,65536,113,127065,(16,7,30))):
        row=certified_schedule([(n,k,127,t,A,support,2)])[0]
        incoming=F(2*(t+1)*160,Q)
        assert incoming<=TARGET
        row['unchanged_next_combination_error']=str(incoming)
        target_ood=F(160*159,2)*F(k-1,Q)
        assert target_ood<=TARGET
        row['unchanged_next_ood_error']=str(target_ood)
        base_rows.append(row)
    result['base_leaf_size_sweeps']=base_rows
    result['base_leaf_blind']=certified_schedule([(64,16,127,109,30,(16,7,30),1)])
    assert F(2*(109+1)*160,Q)<=TARGET
    assert F(160*159,2)*F(15,Q)<=TARGET
    result['additional_unmeasured_base_profile']=certified_schedule([(1048576,262144,127,115,514705,(11,4,21),2)])
    assert F(2*(115+1)*160,Q)<=TARGET
    return result

DATA=Path(__file__).parent/'examples/provekit-applications'

def check_passport():
    profile=json.loads((DATA/'bn254-passport-certificate.json').read_text())
    q=int(profile['field_modulus']);target=F(1,2**128);previous=None
    minimum=1000
    for row in profile['rounds']:
        n,k,t=row['n'],row['k'],row['queries']
        agreement=F(row['agreement']);A=agreement*n
        assert A.denominator==1
        A=int(A)
        historical=certificate(
            n,k,A,*row['support'],method='capped',
            taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL)
        c=certificate(
            n,k,A,*row['support'],
            taylor_degree_model=TIGHT_TAYLOR_DEGREE_MODEL)
        assert historical is not None and c is not None and A*A<n*(k-1)
        assert q>historical['characteristic_strictly_greater_than']
        assert q>c['characteristic_strictly_greater_than']
        assert historical['exceptional_count_upper']==int(row['E'])
        assert historical['list_size_upper']==int(row['L'])
        E,L=c['exceptional_count_upper'],c['list_size_upper']
        assert E<=historical['exceptional_count_upper']
        assert L<=historical['list_size_upper']
        errors=[F(L*(L-1),2)*F(8*k-1,q),F(3*E+2*L,q),F(int(row['pow_threshold'])+1,2**64)*agreement**t]
        if previous is not None:errors.append(F(2*(previous+1)*L,q))
        assert all(x<=target for x in errors)
        minimum=min(minimum,*(log2(x.denominator)-log2(x.numerator) for x in errors))
        previous=t
    # The existing outer witness form-combination and internal batch terms.
    assert all(F(x,q)<=target for x in (1,2,3,4))
    raw_saving=sum((old-row['queries'])*8*32+32*(expected_auth_hashes(row['n'],old)-expected_auth_hashes(row['n'],row['queries'])) for old,row in zip([127,62,41,31,24,20],profile['rounds']))*2
    regular_saving=raw_saving
    gamma_saving=2*((62-profile['rounds'][1]['queries'])*8*32+32*(expected_stride_auth_hashes(2**18,62,2)-expected_stride_auth_hashes(2**18,profile['rounds'][1]['queries'],2)))
    mask_saving=2*((127-profile['rounds'][0]['queries'])+(62-profile['rounds'][1]['queries']))*2*32
    raw_saving+=gamma_saving+mask_saving
    return {'regular_opening_saving':float(regular_saving),'gamma_opening_saving':float(gamma_saving),'mask_evaluation_saving':mask_saving,'minimum_changed_slot_bits':minimum,'expected_raw_saving':float(raw_saving),'expected_raw_saving_exact':str(raw_saving),'certificate':profile}

def check_passport_internal():
    """Certify both internal zkWHIR schedules, including the extra vector batch."""
    profile=json.loads((DATA/'passport-zk-certificate.json').read_text())
    q=int(profile['field_modulus'])
    previous=None
    sharp_revalidation=[]
    for i,row in enumerate(profile['blinding_rounds']):
        n,k,A=row['n'],row['k'],row['agreement_numerator']
        historical=certificate(
            n,k,A,*row['support'],method='capped',
            taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL)
        c=certificate(
            n,k,A,*row['support'],
            taylor_degree_model=TIGHT_TAYLOR_DEGREE_MODEL)
        assert historical is not None and c is not None and A*A<n*(k-1)
        assert q>historical['characteristic_strictly_greater_than']
        assert q>c['characteristic_strictly_greater_than']
        assert all(historical.get(key)==value
                   for key,value in row['certificate'].items())
        E,L=c['exceptional_count_upper'],c['list_size_upper']
        old_E=historical['exceptional_count_upper']
        old_L=historical['list_size_upper']
        assert E<=old_E and L<=old_L
        errors={'tensor_fold_and_identity':F(3*E+2*L,q),
                'one_ood_list_separation':F(L*(L-1),2)*F(8*k-1,q),
                'queries_after_unchanged_pow':F(row['pow_threshold']+1,2**64)*F(A,n)**row['queries_after']}
        historical_errors={
            'tensor_fold_and_identity':F(3*old_E+2*old_L,q),
            'one_ood_list_separation':F(old_L*(old_L-1),2)*F(8*k-1,q),
            'queries_after_unchanged_pow':errors['queries_after_unchanged_pow']}
        if i==0:
            errors.update(two_vector_proximity_transfer=F(E,q),
                          vector_evaluation_rlc_cancellation=F(1,q),
                          two_forms_plus_ood_rlc_cancellation=F(2,q))
            historical_errors.update(
                two_vector_proximity_transfer=F(old_E,q),
                vector_evaluation_rlc_cancellation=F(1,q),
                two_forms_plus_ood_rlc_cancellation=F(2,q))
            assert F(E+1,q)<=TARGET
        if previous is not None:
            errors['incoming_target_list_combination']=F(2*(previous+1)*L,q)
            historical_errors['incoming_target_list_combination']=F(2*(previous+1)*old_L,q)
        for name,error in errors.items():
            assert error<=historical_errors[name]<=TARGET
            assert str(historical_errors[name])==row['errors'][name]['exact']
        assert sum(e for name,e in errors.items() if name!='queries_after_unchanged_pow')<=TARGET
        sharp_revalidation.append({
            'n':n,'k':k,'agreement_numerator':A,
            'selected_transfer_method':c['selected_transfer_method'],
            'selected_list_method':c['selected_list_method'],
            'exceptional_count_upper':E,'list_size_upper':L,
            'historical_capped_exceptional_count_upper':old_E,
            'historical_capped_list_size_upper':old_L})
        previous=row['queries_after']
    assert F(3,q)<=TARGET
    expected=2*sum((old-new)*width*32+32*(expected_auth_hashes(n,old)-expected_auth_hashes(n,new))
                   for n,old,new,width in zip([4096,2048,1024,512],[127,62,41,31],[109,55,37,26],[16,8,8,8]))
    return {'certificate':profile,'sharp_revalidation':sharp_revalidation,
            'expected_additional_raw_saving_exact':str(expected),
            'expected_additional_raw_saving':float(expected),
            'expected_full_raw_saving_exact':str(F(check_passport()['expected_raw_saving_exact'])+expected),
            'expected_full_raw_saving':float(F(check_passport()['expected_raw_saving_exact'])+expected)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compare-only',action='store_true',
                        help='run all exact checks without rewriting stored JSON')
    args=parser.parse_args()
    result={'passport':check_passport(),'passport_internal':check_passport_internal(),'goldilocks':check_goldilocks()}
    if not args.compare_only:
        (DATA/'checked-budgets.json').write_text(json.dumps(result,indent=2)+'\n')
    print('All passport and Goldilocks local inequalities pass exactly.')
    print('Expected raw saving: full passport',result['passport_internal']['expected_full_raw_saving'],'Goldilocks lookup',result['goldilocks']['expected_raw_saving']['24']['bytes'])

if __name__=='__main__':main()
