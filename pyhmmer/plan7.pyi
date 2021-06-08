# coding: utf-8
import collections.abc
import os
import types
import typing

from .easel import (
    Alphabet,
    Sequence,
    DigitalSequence,
    MSA,
    DigitalMSA,
    Randomness,
    VectorF,
    VectorU8,
)

class Alignment(collections.abc.Sized):
    domain: Domain
    def __len__(self) -> int: ...
    @property
    def hmm_accession(self) -> bytes: ...
    @property
    def hmm_from(self) -> int: ...
    @property
    def hmm_name(self) -> bytes: ...
    @property
    def hmm_sequence(self) -> str: ...
    @property
    def hmm_to(self) -> int: ...
    @property
    def target_from(self) -> int: ...
    @property
    def target_name(self) -> bytes: ...
    @property
    def target_sequence(self) -> str: ...
    @property
    def target_to(self) -> int: ...
    @property
    def identity_sequence(self) -> str: ...

class Background(object):
    def __init__(self, alphabet: Alphabet, uniform: bool = False) -> None: ...
    def __copy__(self) -> Background: ...
    @property
    def L(self) -> int: ...
    @L.setter
    def L(self, L: int) -> None: ...
    @property
    def residue_frequencies(self) -> VectorF: ...
    @property
    def transition_probability(self) -> float: ...
    @property
    def omega(self) -> float: ...
    @omega.setter
    def omega(self, omega: float) -> None: ...
    def copy(self) -> Background: ...

class Builder(object):
    def __init__(
        self,
        alphabet: Alphabet,
        *,
        architecture: str = "fast",
        weighting: str = "pb",
        effective_number: typing.Union[str, int, float] = "entropy",
        prior_scheme: typing.Optional[str] = "alphabet",
        symfrac: float = 0.5,
        fragthresh: float = 0.5,
        wid: float = 0.62,
        esigma: float = 45.0,
        eid: float = 0.62,
        EmL: int = 200,
        EmN: int = 200,
        EvL: int = 200,
        EvN: int = 200,
        EfL: int = 100,
        EfN: int = 200,
        Eft: float = 0.04,
        seed: int = 42,
        ere: typing.Optional[float] = None,
        popen: typing.Optional[float] = None,
        pextend: typing.Optional[float] = None,
    ) -> None: ...
    def __copy__(self) -> Builder: ...
    def build(
        self,
        sequence: DigitalSequence,
        background: Background,
    ) -> typing.Tuple[HMM, Profile, OptimizedProfile]: ...
    def build_msa(
        self,
        msa: DigitalMSA,
        background: Background,
    ) -> typing.Tuple[HMM, Profile, OptimizedProfile]: ...
    def copy(self) -> Builder: ...

class Domain(object):
    alignment: Alignment
    hit: Hit
    @property
    def env_from(self) -> int: ...
    @property
    def env_to(self) -> int: ...
    @property
    def score(self) -> float: ...
    @property
    def bias(self) -> float: ...
    @property
    def correction(self) -> float: ...
    @property
    def envelope_score(self) -> float: ...
    @property
    def c_evalue(self) -> float: ...
    @property
    def i_evalue(self) -> float: ...

class Domains(typing.Sequence[Domain]):
    hit: Hit
    def __len__(self) -> int: ...
    @typing.overload
    def __getitem__(self, index: int) -> Domain: ...
    @typing.overload
    def __getitem__(self, index: slice) -> typing.Sequence[Domain]: ...

class Hit(object):
    hits: TopHits
    @property
    def name(self) -> bytes: ...
    @property
    def accession(self) -> bytes: ...
    @property
    def description(self) -> bytes: ...
    @property
    def score(self) -> float: ...
    @property
    def pre_score(self) -> float: ...
    @property
    def bias(self) -> float: ...
    @property
    def evalue(self) -> float: ...
    @property
    def domains(self) -> Domains: ...
    def is_included(self) -> bool: ...
    def is_reported(self) -> bool: ...
    def is_new(self) -> bool: ...
    def is_dropped(self) -> bool: ...
    def is_duplicate(self) -> bool: ...

class HMM(object):
    alphabet: Alphabet
    def __init__(self, M: int, alphabet: Alphabet) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __copy__(self) -> HMM: ...
    @property
    def M(self) -> int: ...
    @property
    def name(self) -> typing.Optional[bytes]: ...
    @name.setter
    def name(self, names: typing.Optional[bytes]) -> None: ...
    @property
    def accession(self) -> typing.Optional[bytes]: ...
    @accession.setter
    def accession(self, accession: typing.Optional[bytes]) -> None: ...
    @property
    def checksum(self) -> typing.Optional[int]: ...
    @property
    def composition(self) -> typing.Optional[VectorF]: ...
    @property
    def description(self) -> typing.Optional[bytes]: ...
    @description.setter
    def description(self, description: typing.Optional[bytes]) -> None: ...
    @property
    def consensus(self) -> typing.Optional[str]: ...
    @property
    def consensus_structure(self) -> typing.Optional[str]: ...
    @property
    def consensus_accessibility(self) -> typing.Optional[str]: ...
    @property
    def command_line(self) -> typing.Optional[str]: ...
    @command_line.setter
    def command_line(self, cli: typing.Optional[str]) -> None: ...
    @property
    def nseq(self) -> typing.Optional[int]: ...
    @property
    def nseq_effective(self) -> typing.Optional[int]: ...
    def copy(self) -> HMM: ...
    def write(self, fh: typing.BinaryIO, binary: bool = False) -> None: ...
    def zero(self) -> None: ...
    def renormalize(self) -> None: ...
    def scale(self, scale: float, exponential: bool = False) -> None: ...
    def set_composition(self) -> None: ...

class HMMFile(typing.ContextManager[HMMFile], typing.Iterator[HMM]):
    def __init__(
        self,
        file: typing.Union[typing.AnyStr, os.PathLike[typing.AnyStr], typing.BinaryIO],
        db: bool = True
    ) -> None: ...
    def __enter__(self) -> HMMFile: ...
    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_value: typing.Optional[BaseException],
        traceback: typing.Optional[types.TracebackType],
    ) -> bool: ...
    def __iter__(self) -> HMMFile: ...
    def __next__(self) -> HMM: ...
    def close(self) -> None: ...

class OptimizedProfile(object):
    def __init__(self, M: int, abc: Alphabet) -> None: ...
    def __copy__(self) -> OptimizedProfile: ...
    def is_local(self) -> bool: ...
    def copy(self) -> OptimizedProfile: ...
    @property
    def offsets(self) -> _Offsets: ...
    @property
    def M(self) -> int: ...
    @property
    def L(self) -> int: ...
    @L.setter
    def L(self, L: int) -> None: ...
    @property
    def tbm(self) -> int: ...
    @property
    def tec(self) -> int: ...
    @property
    def tjb(self) -> int: ...
    @property
    def base(self) -> int: ...
    @property
    def bias(self) -> int: ...
    @property
    def sbv(self) -> VectorU8: ...
    def write(self, fh_filter: typing.BinaryIO, fh_profile: typing.BinaryIO) -> None: ...

class _Offsets(object):
    def __copy__(self) -> _Offsets: ...
    @property
    def model(self) -> typing.Optional[int]: ...
    @model.setter
    def model(self, model: typing.Optional[int]) -> None: ...
    @property
    def filter(self) -> typing.Optional[int]: ...
    @filter.setter
    def filter(self, filter: typing.Optional[int]) -> None: ...
    @property
    def profile(self) -> typing.Optional[int]: ...
    @profile.setter
    def profile(self, profile: typing.Optional[int]) -> None: ...

class Pipeline(object):
    M_HINT: typing.ClassVar[int] = 100
    L_HINT: typing.ClassVar[int] = 100
    LONG_TARGETS: typing.ClassVar[bool] = False
    alphabet: Alphabet
    background: Background
    profile: typing.Optional[Profile]
    randomness: Randomness
    def __init__(
        self,
        alphabet: Alphabet,
        background: typing.Optional[Background] = None,
        *,
        bias_filter: bool = True,
        report_e: float = 10.0,
        null2: bool = True,
        seed: typing.Optional[int] = None,
        Z: typing.Optional[float] = None,
        domZ: typing.Optional[float] = None,
    ) -> None: ...
    @property
    def Z(self) -> typing.Optional[float]: ...
    @Z.setter
    def Z(self, Z: typing.Optional[float]) -> None: ...
    @property
    def domZ(self) -> typing.Optional[float]: ...
    @domZ.setter
    def domZ(self, domZ: typing.Optional[float]) -> None: ...
    @property
    def null2(self) -> bool: ...
    @null2.setter
    def null2(self, null2: bool) -> None: ...
    @property
    def bias_filter(self) -> bool: ...
    @bias_filter.setter
    def bias_filter(self, bias_filter: bool) -> None: ...
    @property
    def F1(self) -> float: ...
    @F1.setter
    def F1(self, F1: float) -> None: ...
    @property
    def F2(self) -> float: ...
    @F2.setter
    def F2(self, F2: float) -> None: ...
    @property
    def F3(self) -> float: ...
    @F3.setter
    def F3(self, F3: float) -> None: ...
    def clear(self) -> None: ...
    def search_hmm(
        self,
        query: HMM,
        sequences: typing.Iterable[DigitalSequence],
    ) -> TopHits: ...
    def search_msa(
        self,
        query: DigitalMSA,
        sequences: typing.Iterable[DigitalSequence],
        builder: typing.Optional[Builder] = None,
    ) -> TopHits: ...
    def search_seq(
        self,
        query: DigitalSequence,
        sequences: typing.Iterable[DigitalSequence],
        builder: typing.Optional[Builder] = None,
    ) -> TopHits: ...
    def scan_hmm(
        self,
        query: DigitalSequence,
        hmms: typing.Iterable[HMM],
    ) -> TopHits: ...

class Profile(object):
    alphabet: Alphabet
    def __init__(self, M: int, alphabet: Alphabet) -> None: ...
    def __copy__(self) -> Profile: ...
    @property
    def M(self) -> int: ...
    @property
    def name(self) -> typing.Optional[bytes]: ...
    @property
    def accession(self) -> typing.Optional[bytes]: ...
    @property
    def description(self) -> typing.Optional[bytes]: ...
    @property
    def consensus(self) -> typing.Optional[str]: ...
    @property
    def consensus_structure(self) -> typing.Optional[str]: ...
    @property
    def offsets(self) -> _Offsets: ...
    def clear(self) -> None: ...
    def configure(
        self,
        hmm: HMM,
        background: Background,
        L: int,
        multihit: bool = True,
        local: bool = True,
    ) -> None: ...
    def copy(self) -> Profile: ...
    def is_local(self) -> bool: ...
    def is_multihit(self) -> bool: ...
    def optimized(self) -> OptimizedProfile: ...

class TopHits(typing.Sequence[Hit]):
    Z: float
    domZ: float
    long_targets: bool
    def __init__(self) -> None: ...
    def __bool__(self) -> bool: ...
    def __len__(self) -> int: ...
    @typing.overload
    def __getitem__(self, index: int) -> Hit: ...
    @typing.overload
    def __getitem__(self, index: slice) -> typing.Sequence[Hit]: ...
    def __iadd__(self, other: TopHits) -> TopHits: ...
    def sort(self, by: str = "key") -> None: ...
    def is_sorted(self, by: str = "key") -> bool: ...
    def to_msa(
        self,
        alphabet: Alphabet,
        trim: bool = False,
        digitize: bool = False,
        all_consensus_cols: bool = False
    ) -> MSA: ...
