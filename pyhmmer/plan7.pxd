# coding: utf-8
# cython: language_level=3, linetrace=True

# --- C imports --------------------------------------------------------------

from libc.stdint cimport uint32_t
from posix.types cimport off_t

from libeasel.sq cimport ESL_SQ
from libhmmer.p7_alidisplay cimport P7_ALIDISPLAY
from libhmmer.p7_bg cimport P7_BG
from libhmmer.p7_builder cimport P7_BUILDER
from libhmmer.p7_domain cimport P7_DOMAIN
from libhmmer.p7_hit cimport P7_HIT
from libhmmer.p7_hmm cimport P7_HMM
from libhmmer.p7_hmmfile cimport P7_HMMFILE
from libhmmer.p7_pipeline cimport P7_PIPELINE, p7_pipemodes_e, p7_zsetby_e
from libhmmer.p7_profile cimport P7_PROFILE
from libhmmer.p7_scoredata cimport P7_SCOREDATA
from libhmmer.p7_tophits cimport P7_TOPHITS
from libhmmer.p7_trace cimport P7_TRACE

IF HMMER_IMPL == "VMX":
    from libhmmer.impl_vmx.p7_oprofile cimport P7_OPROFILE
ELIF HMMER_IMPL == "SSE":
    from libhmmer.impl_sse.p7_oprofile cimport P7_OPROFILE

from .easel cimport Alphabet, DigitalSequence, DigitalMSA, KeyHash, MSA, Randomness, VectorF


cdef extern from "hmmer.h" nogil:
    DEF p7_NOFFSETS = 3
    DEF p7_NEVPARAM = 6
    DEF p7_NCUTOFFS = 6


# --- Cython classes ---------------------------------------------------------


cdef class Alignment:
    cdef readonly Domain domain
    cdef P7_ALIDISPLAY* _ad


cdef class Background:
    cdef readonly bint     uniform
    cdef readonly Alphabet alphabet
    cdef readonly VectorF  residue_frequencies
    cdef          P7_BG*   _bg
    cdef          int      _L

    cpdef Background copy(self)


cdef class Builder:
    cdef readonly object prior_scheme
    cdef readonly object effective_number
    cdef readonly object architecture
    cdef readonly object weighting
    cdef public   str    score_matrix
    cdef public   double popen
    cdef public   double pextend
    cdef readonly Alphabet alphabet
    cdef readonly Randomness randomness

    cdef uint32_t    _seed    # the seed passed at builder initialization
    cdef P7_BUILDER* _bld

    cpdef tuple build(self, DigitalSequence sequence, Background background)
    cpdef tuple build_msa(self, DigitalMSA msa, Background background)
    cpdef Builder copy(self)


cdef class Cutoffs:
    cdef object              _owner
    cdef int*                _flags
    cdef bint                _is_profile
    cdef float[p7_NCUTOFFS]* _cutoffs

    cpdef VectorF as_vector(self)
    cpdef bint gathering_available(self)
    cpdef bint trusted_available(self)
    cpdef bint noise_available(self)


cdef class Domain:
    cdef readonly Alignment alignment
    cdef readonly Hit hit
    cdef P7_DOMAIN* _dom


cdef class Domains:
    cdef readonly Hit hit


cdef class EvalueParameters:
    cdef object              _owner
    cdef float[p7_NEVPARAM]* _evparams

    cpdef VectorF as_vector(self)


cdef class Hit:
    # a reference to the TopHits that owns the wrapped P7_HIT, kept so that
    # the internal data is never deallocated before the Python class.
    cdef readonly TopHits hits
    cdef P7_HIT* _hit

    cpdef bint is_included(self)
    cpdef bint is_reported(self)
    cpdef bint is_new(self)
    cpdef bint is_dropped(self)
    cpdef bint is_duplicate(self)

    cpdef void manually_drop(self)
    cpdef void manually_include(self)


cdef class HMM:
    cdef P7_HMM* _hmm
    # a reference to the Alphabet Python object to avoid deallocation of the
    # inner ESL_ALPHABET; the Python object provides reference counting for free
    cdef readonly Alphabet          alphabet

    cpdef dict __getstate__(self)
    cpdef object __setstate__(self, dict state)

    cpdef HMM copy(self)
    cpdef VectorF match_occupancy(self)
    cpdef double mean_match_entropy(self) except *
    cpdef double mean_match_information(self, Background background) except *
    cpdef double mean_match_relative_entropy(self, Background background) except *
    cpdef void renormalize(self)
    cpdef void scale(self, double scale, bint exponential=?)
    cpdef void set_composition(self)
    cpdef void write(self, object fh, bint binary=*) except *
    cpdef void zero(self)


cdef class HMMFile:
    cdef P7_HMMFILE* _hfp
    cdef Alphabet    _alphabet
    cdef object      _file

    cpdef HMM read(self)
    cpdef void close(self)
    cpdef bint is_pressed(self)
    cpdef HMMPressedFile optimized_profiles(self)

    @staticmethod
    cdef P7_HMMFILE* _open_fileobj(object fh) except *


cdef class HMMPressedFile:
    cdef P7_HMMFILE* _hfp
    cdef Alphabet _alphabet
    cdef HMMFile _hmmfile

    cpdef OptimizedProfile read(self)


cdef class IterationResult:
    cdef readonly TopHits    hits
    cdef readonly DigitalMSA msa
    cdef readonly HMM        hmm
    cdef readonly bint       converged
    cdef readonly size_t     iteration


cdef class IterativeSearch:
    cdef readonly object                query
    cdef readonly Pipeline              pipeline
    cdef readonly Background            background
    cdef readonly Builder               builder
    cdef readonly bint                  converged
    cdef readonly PipelineSearchTargets targets
    cdef readonly KeyHash               ranking
    cdef readonly size_t                iteration
    cdef          DigitalMSA            msa
    cdef          object                select_hits

    cpdef TopHits _search_hmm(self, HMM hmm)


cdef class OptimizedProfile:
    cdef P7_OPROFILE* _om
    cdef readonly Alphabet alphabet

    cpdef OptimizedProfile copy(self)
    cpdef bint is_local(self)
    cpdef void write(self, object fh_filter, object fh_profile) except *

    # @staticmethod
    cdef int _convert(self, P7_PROFILE* gm) nogil except 1

    cpdef object ssv_filter(self, DigitalSequence seq)


cdef class Offsets:
    cdef object              _owner
    cdef off_t[p7_NOFFSETS]* _offs


cdef class PipelineSearchTargets:
    cdef const    ESL_SQ**   _refs         # the array to pass the sequence references to the C code
    cdef          size_t     _nref         # the total size of `self._refs`
    cdef          list       _storage      # the actual Python list where `Sequence` objects are stored
    cdef          ssize_t    _max_len      # the length of the largest sequence in the array
    cdef          object     _owner        # the owner, if the object is just a shallow copy
    cdef readonly Alphabet   alphabet      # the target alphabets


cdef class Pipeline:
    cdef          object     _Z            # either `Z` as an int, or `None`
    cdef          object     _domZ         # either `domZ` as an int, or `None`
    cdef          uint32_t   _seed         # the seed passed at pipeline initialization
    cdef          dict       _cutoff_save  # a local save of the reporting parameters

    cdef readonly Alphabet         alphabet
    cdef readonly Background       background
    cdef readonly Profile          profile
    cdef readonly OptimizedProfile opt
    cdef readonly Randomness       randomness

    cdef OptimizedProfile _optimized
    cdef P7_PIPELINE* _pli

    cdef int _save_cutoff_parameters(self) except 1
    cdef int _restore_cutoff_parameters(self) except 1
    cdef P7_OPROFILE* _get_om_from_query(self, object query, int L = *) except NULL
    cpdef list    arguments(self)
    cpdef void    clear(self)
    cpdef TopHits search_hmm(self, object query, object seqs)
    cpdef TopHits search_msa(self, DigitalMSA query, object seqs, Builder builder = ?)
    cpdef TopHits search_seq(self, DigitalSequence query, object seqs, Builder builder = ?)
    @staticmethod
    cdef  int  _search_loop(
              P7_PIPELINE* pli,
              P7_OPROFILE* om,
              P7_BG*       bg,
        const ESL_SQ**     sq,
              P7_TOPHITS*  th,
    ) nogil except 1
    cpdef TopHits scan_seq(self, DigitalSequence query, object hmms)
    cdef int _scan_loop(
                           self,
              P7_PIPELINE* pli,
              ESL_SQ*      sq,
              P7_BG*       bg,
              P7_HMM*      hm,
              P7_TOPHITS*  th,
              object       hmm_iter,
              Alphabet     hmm_alphabet
    ) except 1


cdef class LongTargetsPipeline(Pipeline):
    cdef DigitalSequence _tmpsq

    @staticmethod
    cdef int _search_loop_longtargets(
              P7_PIPELINE*  pli,
              P7_OPROFILE*  om,
              P7_BG*        bg,
        const ESL_SQ**      sq,
              P7_TOPHITS*   th,
              P7_SCOREDATA* scoredata,
              ESL_SQ*       tmpsq,
    ) nogil except 1


cdef class Profile:
    cdef P7_PROFILE* _gm
    cdef readonly Alphabet          alphabet

    cdef int _clear(self) nogil except 1
    cdef int _configure(self, HMM hmm, Background background, int L, bint multihit=*, bint local=*) nogil except 1

    cpdef Profile copy(self)
    cpdef bint is_local(self)
    cpdef bint is_multihit(self)
    cpdef OptimizedProfile optimized(self)


cdef class ScoreData:
    cdef P7_SCOREDATA* _sd
    cdef readonly int  Kp

    cpdef ScoreData copy(self)


cdef class TopHits:

    # NOTE(@althonos): this is not a full pipeline, but a local copy of the
    #                  accounting parameters so that the e-value can be
    #                  computed and thresholding can be done correctly.
    cdef P7_PIPELINE _pli
    cdef P7_TOPHITS* _th

    cdef int _threshold(self, Pipeline pipeline) nogil except 1
    cdef int _sort_by_key(self) nogil except 1
    cdef int _sort_by_seqidx(self) nogil except 1

    cpdef void sort(self, str by=*) except *
    cpdef bint is_sorted(self, str by=*) except *
    cpdef int compare_ranking(self, KeyHash) except -1
    cpdef TopHits copy(self)
    cpdef MSA to_msa(self, Alphabet alphabet, list sequences=?, list traces=?, bint trim=*, bint digitize=?, bint all_consensus_cols=?)


cdef class Trace:
    cdef readonly Traces traces
    cdef P7_TRACE* _tr

    cpdef float expected_accuracy(self)


cdef class Traces:
    cdef P7_TRACE** _traces
    cdef size_t     _ntraces


cdef class TraceAligner:
    cdef ESL_SQ** _seqs
    cdef size_t   _nseq

    cpdef Traces compute_traces(self, HMM hmm, object sequences)
    cpdef MSA align_traces(
        self,
        HMM hmm,
        object sequences,
        Traces traces,
        bint trim=*,
        bint digitize=*,
        bint all_consensus_cols=*
    )
