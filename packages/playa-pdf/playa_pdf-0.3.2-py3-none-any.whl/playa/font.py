import logging
import struct
from collections import deque
from io import BytesIO
from typing import (
    Any,
    BinaryIO,
    Deque,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
    cast,
)

from playa.cmapdb import (
    CMap,
    CMapBase,
    CMapDB,
    parse_tounicode,
    parse_encoding,
    UnicodeMap,
    ToUnicodeMap,
)
from playa.encodingdb import EncodingDB, name2unicode
from playa.fontmetrics import FONT_METRICS
from playa.parser import (
    KWD,
    LIT,
    Lexer,
    PSLiteral,
    Token,
    literal_name,
    PDFObject,
)
from playa.pdftypes import (
    ContentStream,
    dict_value,
    int_value,
    list_value,
    num_value,
    resolve1,
    resolve_all,
    stream_value,
)
from playa.utils import (
    Matrix,
    Point,
    Rect,
    apply_matrix_norm,
    choplist,
    nunpack,
    decode_text,
)

log = logging.getLogger(__name__)


def get_widths(seq: Iterable[PDFObject]) -> Dict[int, float]:
    """Build a mapping of character widths for horizontal writing."""
    widths: Dict[int, float] = {}
    r: List[float] = []
    for v in seq:
        if isinstance(v, list):
            if r:
                char1 = r[-1]
                for i, w in enumerate(v):
                    widths[int_value(char1) + i] = w
                r = []
        elif isinstance(v, (int, float)):  # == utils.isnumber(v)
            r.append(v)
            if len(r) == 3:
                (char1, char2, w) = r
                for i in range(int_value(char1), int_value(char2) + 1):
                    widths[i] = w
                r = []
    return widths


def get_widths2(seq: Iterable[PDFObject]) -> Dict[int, Tuple[float, Point]]:
    """Build a mapping of character widths for vertical writing."""
    widths: Dict[int, Tuple[float, Point]] = {}
    r: List[float] = []
    for v in seq:
        if isinstance(v, list):
            if r:
                char1 = r[-1]
                for i, (w, vx, vy) in enumerate(choplist(3, v)):
                    widths[int(char1) + i] = (
                        num_value(w),
                        (int_value(vx), int_value(vy)),
                    )
                r = []
        elif isinstance(v, (int, float)):  # == utils.isnumber(v)
            r.append(v)
            if len(r) == 5:
                (char1, char2, w, vx, vy) = r
                for i in range(int(char1), int(char2) + 1):
                    widths[i] = (w, (vx, vy))
                r = []
    return widths


KEYWORD_BEGIN = KWD(b"begin")
KEYWORD_END = KWD(b"end")
KEYWORD_DEF = KWD(b"def")
KEYWORD_PUT = KWD(b"put")
KEYWORD_DICT = KWD(b"dict")
KEYWORD_ARRAY = KWD(b"array")
KEYWORD_READONLY = KWD(b"readonly")
KEYWORD_FOR = KWD(b"for")


class Type1FontHeaderParser:
    def __init__(self, data: bytes) -> None:
        self._lexer = Lexer(data)
        self._cid2unicode: Dict[int, str] = {}
        self._tokq: Deque[Token] = deque([], 2)

    def get_encoding(self) -> Dict[int, str]:
        """Parse the font encoding.

        The Type1 font encoding maps character codes to character names. These
        character names could either be standard Adobe glyph names, or
        character names associated with custom CharStrings for this font. A
        CharString is a sequence of operations that describe how the character
        should be drawn. Currently, this function returns '' (empty string)
        for character names that are associated with a CharStrings.

        Reference: Adobe Systems Incorporated, Adobe Type 1 Font Format

        :returns mapping of character identifiers (cid's) to unicode characters
        """
        for _, tok in self._lexer:
            # Ignore anything that isn't INT NAME put
            if tok is KEYWORD_PUT:
                try:
                    cid, name = self._tokq
                    if isinstance(cid, int) and isinstance(name, PSLiteral):
                        self._cid2unicode[cid] = name2unicode(name.name)
                except KeyError:
                    log.warning("Unknown CID %d", cid)
            else:
                self._tokq.append(tok)
        return self._cid2unicode


NIBBLES = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "e", "e-", None, "-")


def getdict(data: bytes) -> Dict[int, List[Union[float, int]]]:
    d: Dict[int, List[Union[float, int]]] = {}
    fp = BytesIO(data)
    stack: List[Union[float, int]] = []
    while 1:
        c = fp.read(1)
        if not c:
            break
        b0 = ord(c)
        if b0 <= 21:
            d[b0] = stack
            stack = []
            continue
        if b0 == 30:
            s = ""
            loop = True
            while loop:
                b = ord(fp.read(1))
                for n in (b >> 4, b & 15):
                    if n == 15:
                        loop = False
                    else:
                        nibble = NIBBLES[n]
                        assert nibble is not None
                        s += nibble
            value = float(s)
        elif b0 >= 32 and b0 <= 246:
            value = b0 - 139
        else:
            b1 = ord(fp.read(1))
            if b0 >= 247 and b0 <= 250:
                value = ((b0 - 247) << 8) + b1 + 108
            elif b0 >= 251 and b0 <= 254:
                value = -((b0 - 251) << 8) - b1 - 108
            else:
                b2 = ord(fp.read(1))
                if b1 >= 128:
                    b1 -= 256
                if b0 == 28:
                    value = b1 << 8 | b2
                else:
                    value = b1 << 24 | b2 << 16 | struct.unpack(">H", fp.read(2))[0]
        stack.append(value)
    return d


class CFFFont:
    STANDARD_STRINGS = (
        ".notdef",
        "space",
        "exclam",
        "quotedbl",
        "numbersign",
        "dollar",
        "percent",
        "ampersand",
        "quoteright",
        "parenleft",
        "parenright",
        "asterisk",
        "plus",
        "comma",
        "hyphen",
        "period",
        "slash",
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "colon",
        "semicolon",
        "less",
        "equal",
        "greater",
        "question",
        "at",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "bracketleft",
        "backslash",
        "bracketright",
        "asciicircum",
        "underscore",
        "quoteleft",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "braceleft",
        "bar",
        "braceright",
        "asciitilde",
        "exclamdown",
        "cent",
        "sterling",
        "fraction",
        "yen",
        "florin",
        "section",
        "currency",
        "quotesingle",
        "quotedblleft",
        "guillemotleft",
        "guilsinglleft",
        "guilsinglright",
        "fi",
        "fl",
        "endash",
        "dagger",
        "daggerdbl",
        "periodcentered",
        "paragraph",
        "bullet",
        "quotesinglbase",
        "quotedblbase",
        "quotedblright",
        "guillemotright",
        "ellipsis",
        "perthousand",
        "questiondown",
        "grave",
        "acute",
        "circumflex",
        "tilde",
        "macron",
        "breve",
        "dotaccent",
        "dieresis",
        "ring",
        "cedilla",
        "hungarumlaut",
        "ogonek",
        "caron",
        "emdash",
        "AE",
        "ordfeminine",
        "Lslash",
        "Oslash",
        "OE",
        "ordmasculine",
        "ae",
        "dotlessi",
        "lslash",
        "oslash",
        "oe",
        "germandbls",
        "onesuperior",
        "logicalnot",
        "mu",
        "trademark",
        "Eth",
        "onehalf",
        "plusminus",
        "Thorn",
        "onequarter",
        "divide",
        "brokenbar",
        "degree",
        "thorn",
        "threequarters",
        "twosuperior",
        "registered",
        "minus",
        "eth",
        "multiply",
        "threesuperior",
        "copyright",
        "Aacute",
        "Acircumflex",
        "Adieresis",
        "Agrave",
        "Aring",
        "Atilde",
        "Ccedilla",
        "Eacute",
        "Ecircumflex",
        "Edieresis",
        "Egrave",
        "Iacute",
        "Icircumflex",
        "Idieresis",
        "Igrave",
        "Ntilde",
        "Oacute",
        "Ocircumflex",
        "Odieresis",
        "Ograve",
        "Otilde",
        "Scaron",
        "Uacute",
        "Ucircumflex",
        "Udieresis",
        "Ugrave",
        "Yacute",
        "Ydieresis",
        "Zcaron",
        "aacute",
        "acircumflex",
        "adieresis",
        "agrave",
        "aring",
        "atilde",
        "ccedilla",
        "eacute",
        "ecircumflex",
        "edieresis",
        "egrave",
        "iacute",
        "icircumflex",
        "idieresis",
        "igrave",
        "ntilde",
        "oacute",
        "ocircumflex",
        "odieresis",
        "ograve",
        "otilde",
        "scaron",
        "uacute",
        "ucircumflex",
        "udieresis",
        "ugrave",
        "yacute",
        "ydieresis",
        "zcaron",
        "exclamsmall",
        "Hungarumlautsmall",
        "dollaroldstyle",
        "dollarsuperior",
        "ampersandsmall",
        "Acutesmall",
        "parenleftsuperior",
        "parenrightsuperior",
        "twodotenleader",
        "onedotenleader",
        "zerooldstyle",
        "oneoldstyle",
        "twooldstyle",
        "threeoldstyle",
        "fouroldstyle",
        "fiveoldstyle",
        "sixoldstyle",
        "sevenoldstyle",
        "eightoldstyle",
        "nineoldstyle",
        "commasuperior",
        "threequartersemdash",
        "periodsuperior",
        "questionsmall",
        "asuperior",
        "bsuperior",
        "centsuperior",
        "dsuperior",
        "esuperior",
        "isuperior",
        "lsuperior",
        "msuperior",
        "nsuperior",
        "osuperior",
        "rsuperior",
        "ssuperior",
        "tsuperior",
        "ff",
        "ffi",
        "ffl",
        "parenleftinferior",
        "parenrightinferior",
        "Circumflexsmall",
        "hyphensuperior",
        "Gravesmall",
        "Asmall",
        "Bsmall",
        "Csmall",
        "Dsmall",
        "Esmall",
        "Fsmall",
        "Gsmall",
        "Hsmall",
        "Ismall",
        "Jsmall",
        "Ksmall",
        "Lsmall",
        "Msmall",
        "Nsmall",
        "Osmall",
        "Psmall",
        "Qsmall",
        "Rsmall",
        "Ssmall",
        "Tsmall",
        "Usmall",
        "Vsmall",
        "Wsmall",
        "Xsmall",
        "Ysmall",
        "Zsmall",
        "colonmonetary",
        "onefitted",
        "rupiah",
        "Tildesmall",
        "exclamdownsmall",
        "centoldstyle",
        "Lslashsmall",
        "Scaronsmall",
        "Zcaronsmall",
        "Dieresissmall",
        "Brevesmall",
        "Caronsmall",
        "Dotaccentsmall",
        "Macronsmall",
        "figuredash",
        "hypheninferior",
        "Ogoneksmall",
        "Ringsmall",
        "Cedillasmall",
        "questiondownsmall",
        "oneeighth",
        "threeeighths",
        "fiveeighths",
        "seveneighths",
        "onethird",
        "twothirds",
        "zerosuperior",
        "foursuperior",
        "fivesuperior",
        "sixsuperior",
        "sevensuperior",
        "eightsuperior",
        "ninesuperior",
        "zeroinferior",
        "oneinferior",
        "twoinferior",
        "threeinferior",
        "fourinferior",
        "fiveinferior",
        "sixinferior",
        "seveninferior",
        "eightinferior",
        "nineinferior",
        "centinferior",
        "dollarinferior",
        "periodinferior",
        "commainferior",
        "Agravesmall",
        "Aacutesmall",
        "Acircumflexsmall",
        "Atildesmall",
        "Adieresissmall",
        "Aringsmall",
        "AEsmall",
        "Ccedillasmall",
        "Egravesmall",
        "Eacutesmall",
        "Ecircumflexsmall",
        "Edieresissmall",
        "Igravesmall",
        "Iacutesmall",
        "Icircumflexsmall",
        "Idieresissmall",
        "Ethsmall",
        "Ntildesmall",
        "Ogravesmall",
        "Oacutesmall",
        "Ocircumflexsmall",
        "Otildesmall",
        "Odieresissmall",
        "OEsmall",
        "Oslashsmall",
        "Ugravesmall",
        "Uacutesmall",
        "Ucircumflexsmall",
        "Udieresissmall",
        "Yacutesmall",
        "Thornsmall",
        "Ydieresissmall",
        "001.000",
        "001.001",
        "001.002",
        "001.003",
        "Black",
        "Bold",
        "Book",
        "Light",
        "Medium",
        "Regular",
        "Roman",
        "Semibold",
    )

    class INDEX:
        def __init__(self, fp: BinaryIO) -> None:
            self.fp = fp
            self.offsets: List[int] = []
            (count, offsize) = struct.unpack(">HB", self.fp.read(3))
            for i in range(count + 1):
                self.offsets.append(nunpack(self.fp.read(offsize)))
            self.base = self.fp.tell() - 1
            self.fp.seek(self.base + self.offsets[-1])

        def __repr__(self) -> str:
            return "<INDEX: size=%d>" % len(self)

        def __len__(self) -> int:
            return len(self.offsets) - 1

        def __getitem__(self, i: int) -> bytes:
            self.fp.seek(self.base + self.offsets[i])
            return self.fp.read(self.offsets[i + 1] - self.offsets[i])

        def __iter__(self) -> Iterator[bytes]:
            return iter(self[i] for i in range(len(self)))

    def __init__(self, name: str, fp: BinaryIO) -> None:
        self.name = name
        self.fp = fp
        # Header
        (_major, _minor, hdrsize, offsize) = struct.unpack("BBBB", self.fp.read(4))
        self.fp.read(hdrsize - 4)
        # Name INDEX
        self.name_index = self.INDEX(self.fp)
        # Top DICT INDEX
        self.dict_index = self.INDEX(self.fp)
        # String INDEX
        self.string_index = self.INDEX(self.fp)
        # Global Subr INDEX
        self.subr_index = self.INDEX(self.fp)
        # Top DICT DATA
        self.top_dict = getdict(self.dict_index[0])
        (charset_pos,) = self.top_dict.get(15, [0])
        (encoding_pos,) = self.top_dict.get(16, [0])
        (charstring_pos,) = self.top_dict.get(17, [0])
        # CharStrings
        self.fp.seek(int(charstring_pos))
        self.charstring = self.INDEX(self.fp)
        self.nglyphs = len(self.charstring)
        # Encodings
        self.code2gid = {}
        self.gid2code = {}
        self.fp.seek(int(encoding_pos))
        format = self.fp.read(1)
        if format == b"\x00":
            # Format 0
            (n,) = struct.unpack("B", self.fp.read(1))
            for code, gid in enumerate(struct.unpack("B" * n, self.fp.read(n))):
                self.code2gid[code] = gid
                self.gid2code[gid] = code
        elif format == b"\x01":
            # Format 1
            (n,) = struct.unpack("B", self.fp.read(1))
            code = 0
            for i in range(n):
                (first, nleft) = struct.unpack("BB", self.fp.read(2))
                for gid in range(first, first + nleft + 1):
                    self.code2gid[code] = gid
                    self.gid2code[gid] = code
                    code += 1
        else:
            raise ValueError("unsupported encoding format: %r" % format)
        # Charsets
        self.name2gid = {}
        self.gid2name = {}
        self.fp.seek(int(charset_pos))
        format = self.fp.read(1)
        if format == b"\x00":
            # Format 0
            n = self.nglyphs - 1
            for gid, sid in enumerate(
                struct.unpack(">" + "H" * n, self.fp.read(2 * n))
            ):
                gid += 1
                sidname = self.getstr(sid)
                self.name2gid[sidname] = gid
                self.gid2name[gid] = sidname
        elif format == b"\x01":
            # Format 1
            (n,) = struct.unpack("B", self.fp.read(1))
            sid = 0
            for i in range(n):
                (first, nleft) = struct.unpack("BB", self.fp.read(2))
                for gid in range(first, first + nleft + 1):
                    sidname = self.getstr(sid)
                    self.name2gid[sidname] = gid
                    self.gid2name[gid] = sidname
                    sid += 1
        elif format == b"\x02":
            # Format 2
            assert False, str(("Unhandled", format))
        else:
            raise ValueError("unsupported charset format: %r" % format)

    def getstr(self, sid: int) -> Union[str, bytes]:
        # This returns str for one of the STANDARD_STRINGS but bytes otherwise,
        # and appears to be a needless source of type complexity.
        if sid < len(self.STANDARD_STRINGS):
            return self.STANDARD_STRINGS[sid]
        return self.string_index[sid - len(self.STANDARD_STRINGS)]


class TrueTypeFontProgram:
    """Read TrueType font programs to get Unicode mappings."""

    def __init__(self, name: str, fp: BinaryIO) -> None:
        self.name = name
        self.fp = fp
        self.tables: Dict[bytes, Tuple[int, int]] = {}
        self.fonttype = fp.read(4)
        try:
            (ntables, _1, _2, _3) = struct.unpack(">HHHH", fp.read(8))
            for _ in range(ntables):
                (name_bytes, tsum, offset, length) = struct.unpack(
                    ">4sLLL", fp.read(16)
                )
                self.tables[name_bytes] = (offset, length)
        except struct.error:
            # Do not fail if there are not enough bytes to read. Even for
            # corrupted PDFs we would like to get as much information as
            # possible, so continue.
            pass

    def create_tounicode(self) -> Union[ToUnicodeMap, None]:
        """Recreate a ToUnicode mapping from a TrueType font program."""
        if b"cmap" not in self.tables:
            log.debug("TrueType font program has no character mapping")
            return None
        (base_offset, length) = self.tables[b"cmap"]
        fp = self.fp
        fp.seek(base_offset)
        (version, nsubtables) = struct.unpack(">HH", fp.read(4))
        subtables: List[Tuple[int, int, int]] = []
        for i in range(nsubtables):
            subtables.append(struct.unpack(">HHL", fp.read(8)))
        char2gid: Dict[int, int] = {}
        # Only supports subtable type 0, 2 and 4.
        for platform_id, encoding_id, st_offset in subtables:
            # Skip non-Unicode cmaps.
            # https://docs.microsoft.com/en-us/typography/opentype/spec/cmap
            if not (platform_id == 0 or (platform_id == 3 and encoding_id in [1, 10])):
                continue
            fp.seek(base_offset + st_offset)
            (fmttype, fmtlen, fmtlang) = struct.unpack(">HHH", fp.read(6))
            if fmttype == 0:
                char2gid.update(enumerate(struct.unpack(">256B", fp.read(256))))
            elif fmttype == 2:
                subheaderkeys = struct.unpack(">256H", fp.read(512))
                firstbytes = [0] * 8192
                for i, k in enumerate(subheaderkeys):
                    firstbytes[k // 8] = i
                nhdrs = max(subheaderkeys) // 8 + 1
                hdrs: List[Tuple[int, int, int, int, int]] = []
                for i in range(nhdrs):
                    (firstcode, entcount, delta, offset) = struct.unpack(
                        ">HHhH", fp.read(8)
                    )
                    hdrs.append((i, firstcode, entcount, delta, fp.tell() - 2 + offset))
                for i, firstcode, entcount, delta, pos in hdrs:
                    if not entcount:
                        continue
                    first = firstcode + (firstbytes[i] << 8)
                    fp.seek(pos)
                    for c in range(entcount):
                        gid = struct.unpack(">H", fp.read(2))[0]
                        if gid:
                            gid += delta
                        char2gid[first + c] = gid
            elif fmttype == 4:
                (segcount, _1, _2, _3) = struct.unpack(">HHHH", fp.read(8))
                segcount //= 2
                ecs = struct.unpack(">%dH" % segcount, fp.read(2 * segcount))
                fp.read(2)
                scs = struct.unpack(">%dH" % segcount, fp.read(2 * segcount))
                idds = struct.unpack(">%dh" % segcount, fp.read(2 * segcount))
                pos = fp.tell()
                idrs = struct.unpack(">%dH" % segcount, fp.read(2 * segcount))
                for ec, sc, idd, idr in zip(ecs, scs, idds, idrs):
                    if idr:
                        fp.seek(pos + idr)
                        for c in range(sc, ec + 1):
                            b = struct.unpack(">H", fp.read(2))[0]
                            char2gid[c] = (b + idd) & 0xFFFF
                    else:
                        for c in range(sc, ec + 1):
                            char2gid[c] = (c + idd) & 0xFFFF
            else:
                # FIXME: support at least format 12 for non-BMP chars
                # (probably rare in real life since there should be a
                # ToUnicode mapping already)
                assert False, str(("Unhandled", fmttype))
        if not char2gid:
            log.debug("unicode mapping is empty")
            return None
        # Create unicode map - as noted above we don't yet support
        # Unicode outside the BMP, so this is 16-bit only.
        tounicode = ToUnicodeMap()
        tounicode.add_code_range(b"\x00\x00", b"\xff\xff")
        for char, gid in char2gid.items():
            tounicode.add_code2code(gid, char, 2)
        return tounicode


LITERAL_STANDARD_ENCODING = LIT("StandardEncoding")


class Font:
    vertical = False
    multibyte = False

    def __init__(
        self,
        descriptor: Mapping[str, Any],
        widths: Dict[int, float],
        default_width: Optional[float] = None,
    ) -> None:
        self.descriptor = descriptor
        self.widths = resolve_all(widths)
        self.fontname = resolve1(descriptor.get("FontName", "unknown"))
        if isinstance(self.fontname, PSLiteral):
            self.fontname = literal_name(self.fontname)
        self.flags = int_value(descriptor.get("Flags", 0))
        self.ascent = num_value(descriptor.get("Ascent", 0))
        self.descent = num_value(descriptor.get("Descent", 0))
        self.italic_angle = num_value(descriptor.get("ItalicAngle", 0))
        if default_width is None:
            self.default_width = num_value(descriptor.get("MissingWidth", 0))
        else:
            self.default_width = default_width
        self.default_width = resolve1(self.default_width)
        self.leading = num_value(descriptor.get("Leading", 0))
        self.bbox = cast(
            Rect,
            list_value(resolve_all(descriptor.get("FontBBox", (0, 0, 0, 0)))),
        )
        self.hscale = self.vscale = 0.001

        # PDF RM 9.8.1 specifies /Descent should always be a negative number.
        # PScript5.dll seems to produce Descent with a positive number, but
        # text analysis will be wrong if this is taken as correct. So force
        # descent to negative.
        if self.descent > 0:
            self.descent = -self.descent

    def __repr__(self) -> str:
        return "<Font>"

    def decode(self, data: bytes) -> Iterable[Tuple[int, str]]:
        # Default to an Identity map
        log.debug("decode with identity: %r", data)
        return ((cid, chr(cid)) for cid in data)

    def get_ascent(self) -> float:
        """Ascent above the baseline, in text space units"""
        return self.ascent * self.vscale

    def get_descent(self) -> float:
        """Descent below the baseline, in text space units; always negative"""
        return self.descent * self.vscale

    def get_width(self) -> float:
        w = self.bbox[2] - self.bbox[0]
        if w == 0:
            w = -self.default_width
        return w * self.hscale

    def get_height(self) -> float:
        h = self.bbox[3] - self.bbox[1]
        if h == 0:
            h = self.ascent - self.descent
        return h * self.vscale

    def char_width(self, cid: int) -> float:
        """Get the width of a character from its CID."""
        if cid not in self.widths:
            return self.default_width * self.hscale
        return self.widths[cid] * self.hscale

    def char_disp(self, cid: int) -> Union[float, Tuple[Optional[float], float]]:
        """Returns an integer for horizontal fonts, a tuple for vertical fonts."""
        return 0

    def string_width(self, s: bytes) -> float:
        return sum(self.char_width(cid) for cid, _ in self.decode(s))


class SimpleFont(Font):
    def __init__(
        self,
        descriptor: Mapping[str, Any],
        widths: Dict[int, float],
        spec: Mapping[str, Any],
    ) -> None:
        # Font encoding is specified either by a name of
        # built-in encoding or a dictionary that describes
        # the differences.
        if "Encoding" in spec:
            encoding = resolve1(spec["Encoding"])
        else:
            encoding = LITERAL_STANDARD_ENCODING
        if isinstance(encoding, dict):
            name = literal_name(encoding.get("BaseEncoding", LITERAL_STANDARD_ENCODING))
            diff = list_value(encoding.get("Differences", []))
            self.cid2unicode = EncodingDB.get_encoding(name, diff)
        else:
            self.cid2unicode = EncodingDB.get_encoding(literal_name(encoding))
        self.tounicode: Optional[ToUnicodeMap] = None
        if "ToUnicode" in spec:
            strm = stream_value(spec["ToUnicode"])
            self.tounicode = parse_tounicode(strm.buffer)
            if self.tounicode.code_lengths != [1]:
                log.debug(
                    "Technical Note #5144 Considered Harmful: A simple font's "
                    "code space must be single-byte, not %r",
                    self.tounicode.code_space,
                )
                self.tounicode.code_lengths = [1]
                self.tounicode.code_space = [(b"\x00", b"\xff")]
        if self.tounicode:
            log.debug("ToUnicode: %r", vars(self.tounicode))
        Font.__init__(self, descriptor, widths)

    def decode(self, data: bytes) -> Iterable[Tuple[int, str]]:
        if self.tounicode is not None:
            log.debug("decode with ToUnicodeMap: %r", data)
            return zip(data, self.tounicode.decode(data))
        else:
            log.debug("decode with BaseEncoding: %r", data)
            return ((cid, self.cid2unicode.get(cid, "")) for cid in data)


class Type1Font(SimpleFont):
    char_widths: Union[Dict[str, int], None] = None

    def __init__(self, spec: Mapping[str, Any]) -> None:
        try:
            self.basefont = literal_name(resolve1(spec["BaseFont"]))
        except KeyError:
            log.warning("Font spec is missing BaseFont: %r", spec)
            self.basefont = "unknown"

        widths: Dict[int, float]
        if self.basefont in FONT_METRICS:
            (descriptor, self.char_widths) = FONT_METRICS[self.basefont]
            widths = {}
        else:
            descriptor = dict_value(spec.get("FontDescriptor", {}))
            firstchar = int_value(spec.get("FirstChar", 0))
            # lastchar = int_value(spec.get('LastChar', 255))
            width_list = list_value(spec.get("Widths", [0] * 256))
            widths = {i + firstchar: resolve1(w) for (i, w) in enumerate(width_list)}
        SimpleFont.__init__(self, descriptor, widths, spec)
        if "Encoding" not in spec and "FontFile" in descriptor:
            # try to recover the missing encoding info from the font file.
            self.fontfile = stream_value(descriptor.get("FontFile"))
            length1 = int_value(self.fontfile["Length1"])
            data = self.fontfile.buffer[:length1]
            parser = Type1FontHeaderParser(data)
            self.cid2unicode = parser.get_encoding()

    def char_width(self, cid: int) -> float:
        """Get the width of a character from its CID."""
        if self.char_widths is not None:
            if cid not in self.cid2unicode:
                width = self.default_width
            else:
                width = self.char_widths.get(self.cid2unicode[cid], self.default_width)
        else:
            width = self.widths.get(cid, self.default_width)
        return width * self.hscale

    def __repr__(self) -> str:
        return "<Type1Font: basefont=%r>" % self.basefont


class TrueTypeFont(Type1Font):
    def __repr__(self) -> str:
        return "<TrueTypeFont: basefont=%r>" % self.basefont


class Type3Font(SimpleFont):
    def __init__(self, spec: Mapping[str, Any]) -> None:
        firstchar = int_value(spec.get("FirstChar", 0))
        # lastchar = int_value(spec.get('LastChar', 0))
        width_list = list_value(spec.get("Widths", [0] * 256))
        widths = {i + firstchar: w for (i, w) in enumerate(width_list)}
        if "FontDescriptor" in spec:
            descriptor = dict_value(spec["FontDescriptor"])
        else:
            descriptor = {"Ascent": 0, "Descent": 0, "FontBBox": spec["FontBBox"]}
        SimpleFont.__init__(self, descriptor, widths, spec)
        self.matrix = cast(Matrix, tuple(list_value(spec.get("FontMatrix"))))
        (_, self.descent, _, self.ascent) = self.bbox
        (self.hscale, self.vscale) = apply_matrix_norm(self.matrix, (1, 1))

    def __repr__(self) -> str:
        return "<Type3Font>"


# Mapping of cmap names. Original cmap name is kept if not in the mapping.
# (missing reference for why DLIdent is mapped to Identity)
IDENTITY_ENCODER = {
    "DLIdent-H": "Identity-H",
    "DLIdent-V": "Identity-V",
}


class CIDFont(Font):
    default_disp: Union[float, Tuple[Optional[float], float]]

    def __init__(
        self,
        spec: Mapping[str, Any],
    ) -> None:
        try:
            self.basefont = literal_name(spec["BaseFont"])
        except KeyError:
            log.warning("Font spec is missing BaseFont: %r", spec)
            self.basefont = "unknown"
        self.cidsysteminfo = dict_value(spec.get("CIDSystemInfo", {}))
        # These are *supposed* to be ASCII (PDF 1.7 section 9.7.3),
        # but for whatever reason they are sometimes UTF-16BE
        cid_registry = decode_text(
            resolve1(self.cidsysteminfo.get("Registry", b"unknown"))
        )
        cid_ordering = decode_text(
            resolve1(self.cidsysteminfo.get("Ordering", b"unknown"))
        )
        self.cidcoding = f"{cid_registry.strip()}-{cid_ordering.strip()}"
        self.cmap: CMapBase = self.get_cmap_from_spec(spec)

        try:
            descriptor = dict_value(spec["FontDescriptor"])
        except KeyError:
            log.warning("Font spec is missing FontDescriptor: %r", spec)
            descriptor = {}
        self.tounicode: Optional[ToUnicodeMap] = None
        self.unicode_map: Optional[UnicodeMap] = None
        # Since None is equivalent to an identity map, avoid warning
        # in the case where there was some kind of explicit Identity
        # mapping (even though this is absolutely not standards compliant)
        identity_map = False
        # First try to use an explicit ToUnicode Map
        if "ToUnicode" in spec:
            if "Encoding" in spec and spec["ToUnicode"] == spec["Encoding"]:
                log.debug(
                    "ToUnicode and Encoding point to the same object, using an "
                    "identity mapping for Unicode instead of this nonsense: %r",
                    spec["ToUnicode"],
                )
                identity_map = True
            elif isinstance(spec["ToUnicode"], ContentStream):
                strm = stream_value(spec["ToUnicode"])
                log.debug("Parsing ToUnicode from stream %r", strm)
                self.tounicode = parse_tounicode(strm.buffer)
            # If there is no stream, consider it an Identity mapping
            elif (
                isinstance(spec["ToUnicode"], PSLiteral)
                and "Identity" in spec["ToUnicode"].name
            ):
                log.debug("Using identity mapping for ToUnicode %r", spec["ToUnicode"])
                identity_map = True
            else:
                log.warning("Unparseable ToUnicode in %r", spec)
        # If there is no ToUnicode, then try TrueType font tables
        elif "FontFile2" in descriptor:
            self.fontfile = stream_value(descriptor.get("FontFile2"))
            log.debug("Parsing ToUnicode from TrueType font %r", self.fontfile)
            # FIXME: Utterly gratuitous use of BytesIO
            ttf = TrueTypeFontProgram(self.basefont, BytesIO(self.fontfile.buffer))
            self.tounicode = ttf.create_tounicode()
        # Or try to get a predefined UnicodeMap (not to be confused
        # with a ToUnicodeMap)
        if self.tounicode is None:
            try:
                self.unicode_map = CMapDB.get_unicode_map(
                    self.cidcoding,
                    self.cmap.is_vertical(),
                )
            except KeyError:
                pass
        if self.unicode_map is None and self.tounicode is None and not identity_map:
            log.debug(
                "Unable to find/create/guess unicode mapping for CIDFont, "
                "using identity mapping: %r",
                spec,
            )

        # FIXME: Verify that self.tounicode's code space corresponds
        # to self.cmap (this is actually quite hard because the code
        # spaces have been lost in the precompiled CMaps...)

        self.multibyte = True
        self.vertical = self.cmap.is_vertical()
        if self.vertical:
            # writing mode: vertical
            widths2 = get_widths2(list_value(spec.get("W2", [])))
            self.disps = {cid: (vx, vy) for (cid, (_, (vx, vy))) in widths2.items()}
            (vy, w) = resolve1(spec.get("DW2", [880, -1000]))
            self.default_disp = (None, vy)
            widths = {cid: w for (cid, (w, _)) in widths2.items()}
            default_width = w
        else:
            # writing mode: horizontal
            self.disps = {}
            self.default_disp = 0
            widths = get_widths(list_value(spec.get("W", [])))
            default_width = spec.get("DW", 1000)
        Font.__init__(self, descriptor, widths, default_width=default_width)

    def get_cmap_from_spec(self, spec: Mapping[str, Any]) -> CMapBase:
        """Get cmap from font specification

        For certain PDFs, Encoding Type isn't mentioned as an attribute of
        Encoding but as an attribute of CMapName, where CMapName is an
        attribute of spec['Encoding'].
        The horizontal/vertical modes are mentioned with different name
        such as 'DLIdent-H/V','OneByteIdentityH/V','Identity-H/V'.
        """
        cmap_name = self._get_cmap_name(spec)

        try:
            return CMapDB.get_cmap(cmap_name)
        except KeyError as e:
            # Parse an embedded CMap if necessary
            if isinstance(spec["Encoding"], ContentStream):
                strm = stream_value(spec["Encoding"])
                return parse_encoding(strm.buffer)
            else:
                log.warning("Failed to get cmap %s: %s", cmap_name, e)
                return CMap()

    @staticmethod
    def _get_cmap_name(spec: Mapping[str, Any]) -> str:
        """Get cmap name from font specification"""
        cmap_name = "unknown"  # default value
        try:
            spec_encoding = spec["Encoding"]
            if hasattr(spec_encoding, "name"):
                cmap_name = literal_name(spec["Encoding"])
            else:
                cmap_name = literal_name(spec_encoding["CMapName"])
        except KeyError:
            log.warning("Font spec is missing Encoding: %r", spec)
        return IDENTITY_ENCODER.get(cmap_name, cmap_name)

    def decode(self, data: bytes) -> Iterable[Tuple[int, str]]:
        if self.tounicode is not None:
            log.debug("decode with ToUnicodeMap: %r", data)
            # FIXME: Should verify that the codes are actually the
            # same (or just trust the codes that come from the cmap)
            return zip(
                (cid for _, cid in self.cmap.decode(data)), self.tounicode.decode(data)
            )
        elif self.unicode_map is not None:
            log.debug("decode with UnicodeMap: %r", data)
            return (
                (cid, self.unicode_map.get_unichr(cid))
                for (_, cid) in self.cmap.decode(data)
            )
        else:
            log.debug("decode with identity unicode map: %r", data)
            return (
                (cid, chr(int.from_bytes(substr, "big")))
                for substr, cid in self.cmap.decode(data)
            )

    def __repr__(self) -> str:
        return f"<CIDFont: basefont={self.basefont!r}, cidcoding={self.cidcoding!r}>"

    def char_disp(self, cid: int) -> Union[float, Tuple[Optional[float], float]]:
        """Returns 0 for horizontal fonts, a tuple for vertical fonts."""
        return self.disps.get(cid, self.default_disp)
